import math
import random
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail

from django.http import HttpResponseRedirect
from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from google.oauth2.credentials import Credentials
from google.protobuf import service
from googleapiclient.discovery import build

from .forms import *
from .models import *
from .decorator import allowed_users
from .tokens import account_activation_token
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
@csrf_exempt
def registration_user(request):
	if request.method == 'POST':
		form = UserCreateForm(request.POST)
		if form.is_valid():
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

	return render(request, "registration.html", {'usercreateform':form, 'user': UserDetails, 'user': get_user_model()})

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('activation_success')  # Redirect to a success page
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
		username = request.POST.get('username')
		password = request.POST.get('password')
		form = AuthenticationForm(data=request.POST)
		user = authenticate(username=username, password=password)
		print(user)
		if form.is_valid():
			# user = request.user
			print(user.groups.all())
			if user.groups.filter(name__iexact="admin").exists():
				login(request, user)
				return HttpResponseRedirect('/myapp/dashboard/')
			elif user.groups.filter(name__iexact="doctor").exists():
				login(request, user)
				return HttpResponseRedirect('/myapp/home/')
			elif user.groups.filter(name__iexact="patient").exists():
				login(request, user)
				return HttpResponseRedirect('/myapp/Appointment/')
			else:
				login(request, user)
				return HttpResponseRedirect('/myapp/login/')

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
	context_data = {
		'myform': form,
		'patient': UserDetails,
	}
	return render(request, "medication.html", context_data)



@login_required(login_url='/myapp/login/')
@allowed_users(allowed_roles=['admin'])
def dashboard(request):
	my_user = request.user
	if request.user.is_authenticated:
		doctor = Doctor.objects.all()
		users = UserDetails.objects.all()
		appoint = appointment.objects.all()

		admin_count = UserDetails.objects.filter(group='admin').count()
		doctor_count = UserDetails.objects.filter(group='doctor').count()
		patient_count = UserDetails.objects.filter(group='patient').count()

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
@login_required(login_url='/myapp/login/')
@allowed_users(allowed_roles=['doctor'])
def home(request):
	return render(request,'home.html')


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


@login_required(login_url='/myapp/login/')
@allowed_users(allowed_roles=['patient'])
def Appointment(request):
	if request.method == 'POST':
		form = PatientForm(request.POST)
		if form.is_valid():
			doctor = form.cleaned_data["doctor"]
			first_name = form.cleaned_data["first_name"]
			second_name = form.cleaned_data["second_name"]
			third_name = form.cleaned_data["last_name"]
			appointment_date = form.cleaned_data["appointment_date"]
			appointment_time = form.cleaned_data["appointment_time"]
			print('value', doctor.id)
			# print(date.today())

			form.save()
			doctor = Doctor.objects.get(id=doctor.id)
			# create_event_on_google_calendar(appointment_date, appointment_time, doctor)
			email = {
				"recipient_email": doctor.email,
				"message": f"you have an appointment with {third_name} {first_name} {second_name} on {appointment_date} at {appointment_time}"
			}
			send_email(**email)
			messages.success(request, f"You have succesfully booked your appointment with {doctor.first_name}")
		else:
			print(form.errors)
	form = PatientForm()
	context_data = {
		'my_form': form,
		'doctor': Doctor,
	}
	return render(request, "appointment.html", context_data)

def send_email(**kwargs):
	email_from = settings.EMAIL_HOST_USER
	subject = "Appointment"
	message = kwargs.get('message')
	recipient_list = (kwargs.get('recipient_email'),)

	if not subject or not message or not email_from or not recipient_list:
		raise Exception("You have not entered subject or message")
	send_mail(subject, message, email_from, recipient_list)

def user(request, user_id):
	user=UserDetails.objects.get(id=user_id)
	if user != None:
		return render(request, "", {'user': user})

def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            form.save()
            return redirect('/myapp/dashboard/')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'EditUser.html', {'form': form, 'user_id': user_id})
def delete_user(request, user_id):
	user = get_object_or_404(User, id=user_id)
	if request.method == 'POST':
		user.delete()
		return redirect('/myapp/dashboard/')
	return render(request,'dashboard.html', {'user': user})

# @login_required(login_url='/myapp/login/')
# @allowed_users(allowed_roles=['patient'])
def medical_record(request):
	if request.method == "POST":
		form = MedicalRecordForm(request.POST)
		if form.is_valid():
			form.save()
			# return HttpResponseRedirect()
	form = MedicalRecordForm()
	return render(request, 'medical_records.html', {'medform': form})
def view_medical_record(request):
	patient_group = Group.objects.get(name='Patient')
	patients = User.objects.filter(groups__in=[patient_group])
	return render(request, view_medical_record.html, {'medical_record': medical_record})