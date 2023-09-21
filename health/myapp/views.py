import math
import random
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import HttpResponse, render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django_otp.plugins.otp_email.models import EmailDevice

from .forms import UserCreateForm
from .models import OtpModel


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
def two_factor(request):
	user = request.user
	otp_model = OtpModel.objects
	otp_object = otp_model.filter(user=user).first()
	if not otp_object:
		otp_model.create(user=user, otp=otp_provider())
	print(otp_object)
	email = user.email
	email_from = settings.EMAIL_HOST_USER
	subject = 'verification code'
	message = f'{user.email}Your Authentication Code is: {otp_object.otp}'
	recipient_list = [email]
	send_mail(subject, message, email_from, recipient_list)
	context = {"otp":otp_object.otp}
	return render(request, "verification.html", context)



def index(request):
	return HttpResponse("hello world")


@csrf_exempt
def registration_user(request):
	if request.method == 'POST':
		form = UserCreateForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'registration successful')
			return redirect('/myapp/login/')
		else:
			messages.error(request, 'Registration failed')
	form = UserCreateForm()
	context_data = {
		'usercreateform': form,
	}
	return render(request, "registration.html", context_data)


@csrf_exempt
def login_user(request):
	request_method = request.method
	post_request_data = request.POST
	get_request_data = post_request_data.get
	if request_method == "POST":
		email = get_request_data('email')
		password = get_request_data('password')
		if (email == "") or (password == ""):
			messages.error(request, 'Missing email or password')
			redirect('/')
		user = authenticate(email=email, password=password)
		print(user)
		if not user:
			messages.error(request, ' Enter Correct Credinatial')
		messages.success(request, 'Please verify otp')
		form = AuthenticationForm(data=post_request_data)
		if form.is_valid():
			if user.groups.filter(name="admin"):
				login(request, user)
				return HttpResponseRedirect('')
			login(request, user)
			return HttpResponseRedirect('')
	form = AuthenticationForm()
	return render(request, "login.html", {"loginform": form})


@csrf_exempt
@login_required(login_url='/myapp/login/')
def OtpVerifyView(request):
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
