import math
import random
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail

from django.http import HttpResponseRedirect
from django.shortcuts import HttpResponse, render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django_otp.plugins.otp_email.models import EmailDevice
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User,Group
from .forms import UserCreateForm,PatientForm
from .models import *
from .decorator import allowed_users

# admin_group, created = Group.objects.get_or_create(name='admin')
# doctor_group, created = Group.objects.get_or_create(name='doctor')
# patient_group, created = Group.objects.get_or_create(name='patient')
#
# from django.contrib.auth.models import User
#
# user_admin.groups.add(admin_group)
# user_doctor.groups.add(doctor_group)
# user_patient.groups.add(patient_group)
@csrf_exempt
def otp_provider():
	corpus = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	generate_OTP = ""
	size = 7
	length = len(corpus)
	for i in range(size):
		generate_OTP += corpus[math.floor(random.random() * length)]
	return generate_OTP
	return generated_otp





@csrf_exempt
def registration_user(request):
	if request.method == 'POST':
		form = UserCreateForm(request.POST)

		if form.is_valid():
			username = form.cleaned_data["username"]
			email = form.cleaned_data["email"]
			form.save()
			user =UserDetails.objects.get(email=email,username=username)
			messages.success(request, 'registration successful')
			email = {"recipient_email": user.email,
					 "message": f'{username}Click the link to verify your account: '}
			send_email(**email)
			return redirect('/myapp/login/')
		else:
			messages.error(request, 'Registration failed')

	form = UserCreateForm()
	context_data = {
		'usercreateform': form,
		'user': UserDetails,
	}

	return render(request, "registration.html", context_data)

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
		# if (username == "") or (password == ""):
		# 	messages.error(request, 'Missing email or password')
		# 	redirect('/')
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
				return HttpResponseRedirect('/myapp/appointment/')
			else:
				login(request, user)
				return HttpResponseRedirect('/myapp/login/')

	form = AuthenticationForm()
	return render(request, "login.html", {"loginform": form})

# def send_email(**kwargs):
# 	email_from = settings.EMAIL_HOST_USER
# 	subject = "verification code"
# 	message = kwargs.get('message')
# 	recipient_list = (kwargs.get('recipient_email'),)
#
# 	if not subject or not message or not email_from or not recipient_list:
# 		raise Exception("You have not entered subject or message")
# 	send_mail(subject, message, email_from, recipient_list)

@csrf_exempt
def twofactor(request):
	user = request.user
	# otp_model = OtpModel.objects
	# otp_object = otp_model.filter(user=user).first()
	# if not otp_object:
	# 	otp_model.create(user=user, otp=otp_provider())
	# print(otp_object)
	# user.save()
	# email = {"recipient_email": user.email,
	# 		 "message": f'{user.email}Your Authentication Code is: {otp_object.otp}'}
	# send_email(**email)
	# context = {"otp":otp_object.otp}
	# return render(request, "verification.html", context)



@csrf_exempt
@login_required(login_url='/myapp/login/')
def Otp(request):
	request_method = request.method
	post_request_data = request.POST
	get_request_data = post_request_data.get
	otp_model = OtpModel.objects
	if request_method == "POST":
		otp = get_request_data('otp')
		verify_otp = otp_model(otp=otp)
		if verify_otp.exists():
			login(request, verify_otp[0].user)
			return redirect('/home/')
		messages.error(request, "Invalid otp!")
		return redirect('/myapp/otp/')
	return render(request, 'verification.html')

def logout_user(request):
	logout(request)
	return redirect("/myapp/login/")
@login_required
@allowed_users(allowed_roles=['admin'])
def dashboard(request):
	my_user = request.user
	if request.user.is_authenticated:
		doctor = Doctor.objects.all()
		users = UserDetails.objects.all()
		appoint=appointment.objects.all()

		context = {
			"Doctor": doctor,
			"myusers": users,
			"appointment": appoint,
			"my_user": my_user,
		}
		return render(request, "dashboard.html", context)
@login_required
@allowed_users(allowed_roles=['doctor'])
def home(request):
	return render(request,'home.html')
@login_required
def Appointment(request):
	if request.method == 'POST':
		form = PatientForm(request.POST)
		if form.is_valid():
			doctor = form.cleaned_data["doctor"]
			first_name = form.cleaned_data["first_name"]
			second_name = form.cleaned_data["second_name"]
			third_name = form.cleaned_data["last_name"]
			dateofappointment = form.cleaned_data["dateofappointment"]
			timeofappointment = form.cleaned_data["timeofappointment"]
			print('value', doctor.id)
			# print(date.today())

			form.save()
			doctor = Doctor.objects.get(id=doctor.id)
			email = {
				"recipient_email": doctor.email,
				"message": f"you have an appointment with {third_name} {first_name} {second_name} on {dateofappointment} at {timeofappointment}"
			}
			send_email(**email)
			messages.success(request, f"You have succesfully booked your appointment with {doctor.first_name}")
		else:
			print(form.errors)
	form = PatientForm()
	context_data = {
		'my_form': form,
		'doctor':Doctor,
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
