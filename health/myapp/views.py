import json
import math
import os
import random
from sys import flags

import dateutil
from django.conf import settings
from google.auth.transport.requests import Request
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.http import JsonResponse, QueryDict
from django.http import HttpResponseRedirect
from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string, get_template
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google.protobuf import service
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from openpyxl.workbook import Workbook
from xhtml2pdf import pisa

from .forms import *
from .models import *
from .tokens import account_activation_token
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime

SCOPES = 'https://www.googleapis.com/auth/calendar'

UserDetails.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


@csrf_exempt
# @login_required(login_url='/myapp/login/')
# @allowed_users(allowed_roles=['admin'])
def registration_user(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            # username=request.POST.get('username')
            # first_name=request.POST.get('first_name')
            # second_name=request.POST.get('second_name')
            # last_name=request.POST.get('last_name')
            # email=request.POST.get('email')
            # password1=request.POST.get('password1')
            # password2=request.POST.get('password2')
            # UserDetails.objects.create(username='username', password=make_password(password1),is_active=False)
            # print(username)
            user = form.save(commit=False)
            user.is_active = False
            form.save()
            subject = "Activate your account"
            message = render_to_string('verificationemail.html', {
                'user': user,
                'domain': get_current_site(request).domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('/myapp/login/')
        else:
            messages.error(request, 'Registration failed')

    form = UserCreateForm()

    return render(request, "registration.html", {'usercreateform': form, 'user': UserDetails, 'user': get_user_model()})


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserDetails.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('activation_success')
    else:
        return redirect('activation_failure')


def send_email(**kwargs):
    email_from = settings.EMAIL_HOST_USER
    subject = "registration"
    message = kwargs.get('message')
    recipient_list = (kwargs.get('recipient_email'),)

    if not subject or not message or not email_from or not recipient_list:
        raise Exception("You have not entered subject or message")
    send_mail(subject, message, email_from, recipient_list)


@csrf_exempt
def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm()
        username = request.POST['username']
        password = request.POST['password']
        user = UserDetails.objects.get(username=username)
        # userdetails = UserDetails.objects.get(id=user.id)
        # print(user.isauthenticated)
        if user:
            print(user)
            if not user.check_password(password):
                form.add_error(None, "Invalid login credentials")
                # Render the login form page with custom error message
                return render(request, "login.html", {"loginform": form})
            login(request, user)
            print(user.is_authenticated)
            print(user.is_admin())
            print(user.is_patient())
            print(user.is_doctor())
            if user.is_admin():
                return redirect("/myapp/dashboard/")
            elif user.is_patient():
                return redirect("/myapp/patient_page/")
            elif user.is_doctor():
                return redirect('/myapp/medicalrecord/')
        # Return a response even in the case of an invalid form
    form = AuthenticationForm()
    return render(request, "login.html", {"loginform": form})


def logout_user(request):
    logout(request)
    return redirect("/myapp/login/")


def medication(request):
    if request.method == "POST":
        form = MedicationForm(request.POST)
        if form.is_valid():
            patient = form.cleaned_data["patient"]
            form.save()
            patient = UserDetails.objects.get(id=patient.id)
    form = MedicationForm()
    messages.success(request, f"You have succesfully added medication of ")
    context_data = {
        'myform': form,
        'patient': UserDetails,
    }
    return render(request, "medication.html", context_data)


# @login_required(login_url='/myapp/login/')
# @login_required()
# @allowed_users(allowed_roles=['admin'])
def dashboard(request):
    my_user = request.user
    context = {}
    if request.user.is_authenticated:
        doctor = Doctor.objects.all()
        users = UserDetails.objects.all()
        appoint = appointment.objects.all()

        admin_count = UserDetails.objects.filter(role='admin').count()
        doctor_count = UserDetails.objects.filter(role='doctor').count()
        patient_count = UserDetails.objects.filter(role='patient').count()

        context = {
            "Doctor": doctor,
            "myusers": users,
            "appointment": appoint,
            "my_user": my_user,
            'admin_count': admin_count,
            'doctor_count': doctor_count,
            'patient_count': patient_count
        }
    return render(request, "dashboard.html", context)


# @login_required(login_url='/myapp/login/')
# @allowed_users(allowed_roles=['doctor'])
def home(request):
    return render(request, 'home.html', )


def doctor(request):
    return render(request, 'doctor.html', )


# def create_event_on_google_calendar(appointment_date, appointment_time, doctor):
# 	if credentials_data:
# 		credentials_data=doctor.google_credentials
#     	service = build('calendar', 'v3', credentials=credentials)
#
# 		event = {
# 			'summary': f'Appointment with {doctor.first_name} {doctor.last_name}',
# 			'description': f'Appointment with {doctor.first_name} {doctor.last_name}',
# 			'start': {
# 				'dateTime': f'{appointment_date}T{appointment_time}',
# 				'timeZone': 'EAT',
# 			},
# 			'end': {
# 				'dateTime': f'{appointment_date}T{appointment_time}',  # Adjust the end time if needed
# 				'timeZone': 'EAT',
# 			},
# 		}
#
#     event = service.events().insert(calendarId='primary', body=event).execute()
#     print('Event created: %s' % (event.get('htmlLink')))


# @login_required(login_url='/myapp/login/')
# @allowed_users(allowed_roles=['patient'])
def Appointment(request):
    context = {}

    if request.method == 'POST':
        form = PatientForm(request.POST)

        if form.is_valid():
            doctor = form.cleaned_data["doctor"]
            first_name = form.cleaned_data["first_name"]
            second_name = form.cleaned_data["second_name"]
            email = form.cleaned_data["email"]
            start = form.cleaned_data["start"]
            end = form.cleaned_data["end"]
            location = form.cleaned_data['location']
            description = form.cleaned_data['description']

            # Create event in Google Calendar
            k = {"start": start, "end": end, 'location': location, 'description': description, 'doctor': doctor.email,
                 'patient': email}
            context = create_event(**k)

            # Send email notification to the doctor
            doctor_email = {
                "recipient_email": doctor.email,
                "message": f"You have an appointment with {first_name} {second_name} from {start} to {end}"
            }
            send_email(**doctor_email)

            # Send email notification to the patient
            patient_email = {
                "recipient_email": email,
                "message": f"You have successfully booked an appointment with Dr. {doctor.first_name} from {start} to {end}"
            }
            send_email(**patient_email)

            messages.success(request, f"You have successfully booked your appointment with Dr. {doctor.first_name}")
            return render(request, "appointment.html", context)
        else:
            print(form.errors)

    form = PatientForm()
    context_data = {
        'my_form': form,
        'doctor': Doctor,
    }
    return render(request, "appointment.html", context_data)


def get_doctors(request):
    doctors = UserDetails.objects.filter(group='doctor')
    return render(request, 'home.html', {'doctors': doctors})


def doctor_appointment(request):
    appoint = None

    if request.user.is_authenticated:
        appoint = appointment.objects.all()

    return render(request, 'doctor_appointment.html', {"appointment": appoint})


def send_email(**kwargs):
    email_from = settings.EMAIL_HOST_USER
    subject = "Appointment"
    message = kwargs.get('message')
    recipient_list = (kwargs.get('recipient_email'),)

    if not subject or not message or not email_from or not recipient_list:
        raise Exception("You have not entered subject or message")
    send_mail(subject, message, email_from, recipient_list)


def user(request, user_id):
    user = UserDetails.objects.get(id=user_id)
    if user != None:
        return render(request, "", {'user': user})


def edit_user(request, pk):
    user = get_object_or_404(UserDetails, id=pk)
    form = UserProfileForm(instance=user)
    if request.method == "POST":
        form = UserCreateForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            form.save()
            return redirect('/myapp/dashboard/')
    return render(request, 'EditUser.html', {'form': form, 'pk': pk})


def delete_user(request, user_id):
    user = get_object_or_404(UserDetails, id=user_id)
    if request.method == 'POST':
        user.delete()
        # id= data.get('id')
        # user=user.objects.get(id=id)
        return redirect('/myapp/dashboard/')
    return render(request, 'user_delete.html', {'user': user})


# @login_required(login_url='/myapp/login/')
# @allowed_users(allowed_roles=['patient'])
def medical_record(request):
    all_users = UserDetails.objects.all()
    print(all_users)  # Print all users

    med = Medicalrecord.objects.all()  # Initialize 'med' outside the if block

    patients = UserDetails.objects.filter(role='patient')
    print(patients)  # Print patients

    if request.method == "POST":
        form = MedicalRecordForm(request.POST)
        medicate = Medication.objects.all()
        if form.is_valid():
            form.save()
            med = Medicalrecord.objects.all()
            messages.success(request, "You have successfully recorded", {'patients': patients})
        else:
            print(form.errors)
    else:
        # If the request method is not "POST," you still need to define 'medicate'
        medicate = Medication.objects.all()

    form = MedicalRecordForm()
    return render(request, 'medical_records.html',
                  {'medform': form, 'medical': med, 'medic': medicate, 'patients': patients})


def view_medical_record(request):
    patient_group = Group.objects.get(name='Patient')
    patients = UserDetails.objects.filter(groups__in=[patient_group])
    medical_record = Medicalrecord.objects.all()
    return render(request, view_medical_record.html, {'medical_record': medical_record})


@login_required(login_url='/myapp/login/')
# @allowed_users(allowed_roles=['patient', 'admin'])
def update_appointment(request, pk):
    appoint = get_object_or_404(appointment, id=pk)
    form = PatientForm(instance=appoint)

    if request.method == 'POST':
        form = PatientForm(request.POST, instance=appoint)
        if form.is_valid():
            appoint.save()

            # Debugging: Print the generated URL
            print(reverse('/myapp/dashboard/'))

            # Use reverse to dynamically generate the URL for the dashboard
            return HttpResponseRedirect('/myapp/dashboard/')

    context = {'my_form': form, 'pk': pk}
    return render(request, 'appointment.html', context)


def delete_appointment(request, pk):
    appoint = get_object_or_404(appointment, id=pk)
    if request.method == 'POST':
        appoint.delete()
        return redirect('/myapp/dashboard/')
    return render(request, 'delete_appointment.html', {'appoint': appoint})


def update_doctor(request, pk):
    doctor = get_object_or_404(Doctor, id=pk)
    # appoint = appointment.objects.get(id=pk)
    form = PatientForm(instance=doctor)

    if request.method == 'POST':
        form = PatientForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'my_form': form, 'pk': pk}
    return render(request, 'appointment.html', context)

def patient_page(request):
    med = Medicalrecord.objects.none()  # Initialize 'med' with an empty queryset
    medicate = Medication.objects.none()  # Initialize 'medicate' with an empty queryset

    if request.user.is_authenticated:
        med = Medicalrecord.objects.all()
        medicate = Medication.objects.all()

    return render(request, 'patient_page.html', {'medical': med, 'medic': medicate})


def edit_medicalrecords(request, pk):
    med = get_object_or_404(Medicalrecord, id=pk)
    form = MedicalRecordForm(instance=med)

    if request.method == "POST":
        form = MedicalRecordForm(request.POST, instance=med)
        if form.is_valid():
            med = form.save(commit=False)
            med.save()
            form.save()
        else:

            return redirect('/myapp/patient_page')

    return render(request, 'medical_records.html', {'form': form, 'pk': pk})


def delete_medicalrecords(request, pk):
    medrecord = get_object_or_404(Medicalrecord, id=pk)
    if request.method == 'POST':
        medrecord.delete()
        return redirect('/myapp/patient_page/')
    return render(request, 'delete_medicalrecords.html', {'medrecord': medrecord})


def edit_medicationrecords(request, pk):
    medication = get_object_or_404(Medication, id=pk)

    form = MedicationForm(instance=medication)

    if request.method == 'POST':
        form = MedicationForm(request.POST, instance=medication)
        if form.is_valid():
            # medication = form.save(commit=False)
            # medication.save()
            form.save()
            return redirect('/')
    context = {'myform': form, 'pk': pk}
    return render(request, 'medication.html', context)


def delete_medicationrecords(request, pk):
    medrecord = get_object_or_404(Medicalrecord, id=pk)
    if request.method == 'POST':
        medrecord.delete()
        return redirect('/myapp/patient_page/')
    return render(request, 'delete_medicalrecords.html', {'medrecord': medrecord})


def generate_excel(request):
    # Create Excel workbook and sheet
    wb = Workbook()
    ws = wb.active

    # Add headers
    headers = ["First Name", "Second Name", "Email", "Date", "Time"]
    ws.append(headers)

    # Retrieve appointment data from the database
    appointments = appointment.objects.values_list(
        'first_name', 'second_name', 'email', 'appointment_date', 'appointment_time'
    )

    for appoint in appointments:
        ws.append(appoint)

    # Create response with Excel content type
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # Set the content-disposition header to force download
    response['Content-Disposition'] = 'attachment; filename=appointments.xlsx'

    # Save workbook to response
    wb.save(response)

    return response


class GenerateIndividualPDF(View):
    template_name = 'individual_pdf_template.html'


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json


def get_context_data(self, medication_id, **kwargs):
    medicate = get_object_or_404(Medication, id=medication_id)
    return {'medicate': medicate}

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'token.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

def get(self, request, medication_id, *args, **kwargs):
    template = get_template(self.medicationdetails.html)
    context = self.get_context_data(medication_id)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="medication_report_{medication_id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def get_event(request):
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "myapp/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        if not events:
            print("No upcoming events found.")
            return
        context = {'events': events}

        now_datetime = datetime.datetime.utcnow()
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            event_datetime = dateutil.parser.parse(start)
            if event_datetime > now_datetime:
                print(start, event["summary"])
        return render(request, 'appointment.html', context=context)

    # Replace the above code with the modified code snippet here...

    except HttpError as error:
        print(f"An error occurred: {error}")


def get_saved_credentials(filename='token.json'):
    file_data = {}
    try:
        with open(filename, 'r') as file:
            file_data = json.load(file)
    except FileNotFoundError:
        print("Credentials file not found.")
        return None

    if 'refresh_token' in file_data and 'client_id' in file_data and 'client_secret' in file_data:
        credentials = Credentials(**file_data)

        # Check if the credentials are valid
        if not credentials.valid:
            try:
                credentials.refresh(Request())
                # Save the refreshed credentials
                with open(filename, 'w') as file:
                    json.dump(credentials.to_json(), file)
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                return None

        return credentials
    else:
        print("Credentials incomplete.")
        return None




def create_event(**kwargs):
    """Shows basic usage of the Google Calendar API.
    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    creds = {"token": "ya29.a0AfB_byCqGWxGP7Fnug6LkJKpNEpZl-PU_8X6AObUjYkEYiuElNRjB80lOUOH9MSOM0snMh5XQpBIuDQRZLNl1h8mPkfEC-12giLXAPFYlJPWAJR4-189ErR-F_FyLh4tnTENaAItO04DHNzTaQoR0zSzLRJlcLY2mF-XaCgYKAQISARASFQHGX2MiVHq-YbyAWjRT5Jg_UVRzKg0171",
             "refresh_token": "1//03PnflHUx1-zGCgYIARAAGAMSNwF-L9IrK5eQ6pHoRNmeVqyY43H_p54HlxZKso0AFBlnRMoyNnTZL6DguVH_mrAlbWWB5xFWu1U",
             "token_uri": "https://oauth2.googleapis.com/token",
             "client_id": "254113491331-amuct4esb33nfopc3m9s1ig82d3g6ign.apps.googleusercontent.com",
             "client_secret": "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",
             "scopes": ["https://www.googleapis.com/auth/calendar.readonly"],
             # "expiry": "2023-11-28T16:18:24.919719Z"
             }
    http = Credentials(**creds)
    print(http)
    dev_key = "AIzaSyCfMqMg-ihuDHvvLz7Q9mZ6bfvTPI4VyEQ"
    service = discovery.build('calendar', 'v3', credentials=http, developerKey=dev_key)
    print(service)
    location = kwargs.get('location')
    description = kwargs.get('description')
    start = kwargs.get('start')
    end = kwargs.get('end')
    patient = kwargs.get('patient')
    doctor = kwargs.get('doctor')
    event = {
        'summary': 'Google I/O 2015',
        'location': location,
        'description': description,
        'start': {
            'dateTime': start,
            'timeZone': 'Africa/Nairobi',
        },
        'end': {
            'dateTime': end,
            'timeZone': 'Africa/Nairobi',
        },
        'recurrence': [
            'RRULE:FREQ=DAILY;COUNT=2'
        ],
        'attendees': [
            {'email': patient},
            {'email': doctor},
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    print(start)
    print(end)

    events_result = service.events().list(calendarId='primary').execute()
    events = events_result.get('items', [])
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(start)

    return event
