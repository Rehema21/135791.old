import math
import random
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password, check_password
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

UserDetails.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
@csrf_exempt
# @login_required(login_url='/myapp/login/')
# @allowed_users(allowed_roles=['admin'])
def registration_user(request):
	if request.method == 'POST':
		form = UserCreateForm(request.POST)
		if form.is_valid():
			username=request.POST.get('username')
			first_name=request.POST.get('first_name')
			second_name=request.POST.get('second_name')
			last_name=request.POST.get('last_name')
			email=request.POST.get('email')
			password1=request.POST.get('password1')
			password2=request.POST.get('password2')
			UserDetails.objects.create(username='username', password=make_password(password1),is_active=False)
			print(username)
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
				return redirect("/myapp/home/")
			elif user.is_doctor():
				return redirect('/myapp/patient_page/')
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
# @login_required(login_url='/myapp/login/')
# @allowed_users(allowed_roles=['doctor'])
def home(request):



	return render(request,'home.html', )


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

def get_doctors(request):
    doctors = UserDetails.objects.filter(group='doctor')
    return render(request, 'home.html', {'doctors': doctors})

def doctor_appointment(request):
	if request.user.is_authenticated:
		appoint = appointment.objects.all()


	return render(request, 'doctor_appointment.html',{"appointment": appoint,} )

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
	if request.method == "POST":
		form = MedicalRecordForm(request.POST)
		if form.is_valid():
			patients = UserDetails.objects.filter(group='patient')
			form.save()
			messages.success(request, f"You have succesfully recorded", {'patients': patients})
		else:
			print(form.errors)
	form = MedicalRecordForm()
	return render(request, 'medical_records.html', {'medform': form})
def view_medical_record(request):
	patient_group = Group.objects.get(name='Patient')
	patients = UserDetails.objects.filter(groups__in=[patient_group])
	return render(request, view_medical_record.html, {'medical_record': medical_record})

@login_required(login_url='/myapp/login/')
@allowed_users(allowed_roles=['patient', 'admin'])
def update_appointment(request, pk):
	appoint = get_object_or_404(appointment, id=pk)  # Use "Appointment" with a capital letter
	form = PatientForm(instance=appoint)

	if request.method == 'POST':
		form = PatientForm(request.POST, instance=appoint)
		if form.is_valid():
			form.save()  # Save the form with commit=True

			return redirect('/myapp/dashboard/')

	context = {'my_form': form, 'pk': pk}
	return render(request, 'appointment.html', context)
def delete_appointment(request, pk):
	appoint = get_object_or_404(appointment, id=pk)
	if request.method == 'POST':
		appoint.delete()
		return redirect('/myapp/dashboard/')
	return render(request, 'delete_appointment.html', {'appoint': appoint})

# def update_doctor(request, pk):
# 	doctor = get_object_or_404(Doctor, id=pk)
# 	# appoint = appointment.objects.get(id=pk)
# 	form = PatientForm(instance=doctor)
#
# 	if request.method == 'POST':
# 		form = PatientForm(request.POST, instance=doctor)
# 		if form.is_valid():
# 			form.save()
# 			return redirect('/')
# 	context = {'my_form': form, 'pk': pk}
# 	return render(request, 'appointment.html', context)
# def delete_doctor(request, pk):
# 	appoint = get_object_or_404(appointment, id=pk)
# 	if request.method == 'POST':
# 		appoint.delete()
# 		return redirect('/myapp/dashboard/')
# 	return render(request, 'delete_appointment.html', {'appoint': appoint})
def patient_page(request):
	if request.user.is_authenticated:
		med = Medicalrecord.objects.all()
		medicate = Medication.objects.all()

	return render(request,'patient_page.html', {'medical': med,'medic':medicate})


def edit_medicalrecords(request, pk):
	medr = get_object_or_404(appointment, id=pk)
	user = get_object_or_404(UserDetails, id=pk)

	if request.method == "POST":
		form = UserProfileForm(request.POST, instance=medr)
		if form.is_valid():
			medr = form.save(commit=False)
			medr.save()
			form.save()
		else:
			form = UserProfileForm(instance=medr)

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

#
# @csrf_exempt
# @login_required(login_url='login')
# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# def home(request, pk):
# 	if request.user.is_patient:
# 		User = get_user_model()
# 		users = User.objects.all()
# 		patients = Patient.objects.get(user_id=pk)
# 		# doctor = Doctor_Information.objects.all()
# 		appointments = Appointment.objects.filter(patient=patients).filter(appointment_status='confirmed')
# 		doctor = Doctor_Information.objects.filter(appointment__in=appointments)
#
# 		chats = {}
# 		if request.method == 'GET' and 'u' in request.GET:
# 			# chats = chatMessages.objects.filter(Q(user_from=request.user.id & user_to=request.GET['u']) | Q(user_from=request.GET['u'] & user_to=request.user.id))
# 			chats = chatMessages.objects.filter(
# 				Q(user_from=request.user.id, user_to=request.GET['u']) | Q(user_from=request.GET['u'],
# 																		   user_to=request.user.id))
# 			chats = chats.order_by('date_created')
# 			doc = Doctor_Information.objects.get(user_id=request.GET['u'])
#
# 			context = {
# 				"page": "home",
# 				"users": users,
# 				"chats": chats,
# 				"patient": patients,
# 				"doctor": doctor,
# 				"doc": doc,
# 				"app": appointments,
#
# 				"chat_id": int(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0)
# 			}
# 		elif request.method == 'GET' and 'search' in request.GET:
# 			query = request.GET.get('search')
# 			doctor = Doctor_Information.objects.filter(
# 				Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query))
# 			# chats = chatMessages.objects.filter(Q(user_from=request.user.id, user_to=request.GET['u']) | Q(user_from=request.GET['u'], user_to=request.user.id))
# 			# chats = chats.order_by('date_created')
# 			# doc = Doctor_Information.objects.get(username=request.GET['search'])
# 			context = {
# 				"page": "home",
# 				"users": users,
#
# 				"patient": patients,
#
# 				"doctor": doctor,
#
# 			}
# 		else:
#
# 			context = {
# 				"page": "home",
# 				"users": users,
# 				"chats": chats,
# 				"patient": patients,
# 				"doctor": doctor,
# 				"app": appointments,
# 				"chat_id": int(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0)
# 			}
# 		print(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0)
# 		return render(request, "chat.html", context)
# 	elif request.user.is_doctor:
# 		User = get_user_model()
# 		users = User.objects.all()
# 		# patients = Patient.objects.all()
# 		doctor = Doctor_Information.objects.get(user_id=pk)
# 		appointments = Appointment.objects.filter(doctor=doctor).filter(appointment_status='confirmed')
# 		patients = Patient.objects.filter(appointment__in=appointments)
#
# 		chats = {}
# 		if request.method == 'GET' and 'u' in request.GET:
# 			# chats = chatMessages.objects.filter(Q(user_from=request.user.id & user_to=request.GET['u']) | Q(user_from=request.GET['u'] & user_to=request.user.id))
# 			chats = chatMessages.objects.filter(
# 				Q(user_from=request.user.id, user_to=request.GET['u']) | Q(user_from=request.GET['u'],
# 																		   user_to=request.user.id))
# 			chats = chats.order_by('date_created')
# 			pat = Patient.objects.get(user_id=request.GET['u'])
#
# 			context = {
# 				"page": "home",
# 				"users": users,
# 				"chats": chats,
# 				"patient": patients,
# 				"doctor": doctor,
# 				"pat": pat,
# 				"app": appointments,
#
# 				"chat_id": int(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0)
# 			}
# 		elif request.method == 'GET' and 'search' in request.GET:
# 			query = request.GET.get('search')
# 			patients = Patient.objects.filter(
# 				Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query))
# 			# chats = chatMessages.objects.filter(Q(user_from=request.user.id, user_to=request.GET['u']) | Q(user_from=request.GET['u'], user_to=request.user.id))
# 			# chats = chats.order_by('date_created')
# 			# doc = Doctor_Information.objects.get(username=request.GET['search'])
# 			context = {
# 				"page": "home",
# 				"users": users,
#
# 				"patient": patients,
# 				"app": appointments,
# 				"doctor": doctor,
#
# 			}
#
#
#
# 		else:
#
# 			context = {
# 				"page": "home",
# 				"users": users,
# 				"chats": chats,
# 				"patient": patients,
# 				"doctor": doctor,
# 				"chat_id": int(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0)
# 			}
# 		print(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0)
# 		return render(request, "chat-doctor.html", context)
#
#
# @csrf_exempt
# @login_required
# def profile(request):
# 	context = {
# 		"page": "profile",
# 	}
# 	return render(request, "chat/profile.html", context)
#
#
# @csrf_exempt
# @login_required(login_url='login')
# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# def get_messages(request):
# 	chats = chatMessages.objects.filter(Q(id__gt=request.POST['last_id']),
# 										Q(user_from=request.user.id, user_to=request.POST['chat_id']) | Q(
# 											user_from=request.POST['chat_id'], user_to=request.user.id))
# 	new_msgs = []
# 	for chat in list(chats):
# 		data = {}
# 		data['id'] = chat.id
# 		data['user_from'] = chat.user_from.id
# 		data['user_to'] = chat.user_to.id
# 		data['message'] = chat.message
# 		data['date_created'] = chat.date_created.strftime("%b-%d-%Y %H:%M")
# 		print(data)
# 		new_msgs.append(data)
# 	return HttpResponse(json.dumps(new_msgs), content_type="application/json")
#
#
# @csrf_exempt
# @login_required(login_url='login')
# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# def send_chat(request):
# 	resp = {}
# 	User = get_user_model()
# 	if request.method == 'POST':
# 		post = request.POST
#
# 		u_from = User.objects.get(id=post['user_from'])
# 		u_to = User.objects.get(id=post['user_to'])
# 		insert = chatMessages(user_from=u_from, user_to=u_to, message=post['message'])
# 		try:
# 			insert.save()
# 			resp['status'] = 'success'
# 		except Exception as ex:
# 			resp['status'] = 'failed'
# 			resp['mesg'] = ex
# 	else:
# 		resp['status'] = 'failed'
#
# 	return HttpResponse(json.dumps(resp), content_type="application/json")
#



