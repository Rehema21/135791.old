import math
import random
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

class BaseModel(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	date_modified = models.DateTimeField(auto_now=True)
	date_created = models.DateTimeField(auto_now_add=True)

	class Meta:
		abstract = True

	def __str__(self):
		return self.date_created + self.date_modified



class UserDetails(User):
	second_name = models.CharField(max_length=20)
	ROLE_CHOICES = [
		('admin', 'Admin'),
		('patient', 'Patient'),
		('doctor', 'Doctor'),
	]

	role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
	def is_admin(self):
		return self.role == 'admin'

	def is_patient(self):
		return self.role == 'patient'

	def is_doctor(self):
		return self.role == 'doctor'

	def __str__(self):
		return self.username
class UserProfile(models.Model):
    user = models.OneToOneField(UserDetails, on_delete=models.CASCADE)
    verification_token = models.CharField(max_length=40, blank=True, null=True)

class OtpModel(models.Model):
    user = models.OneToOneField(UserDetails, on_delete=models.CASCADE)
    otp = models.CharField(max_length=7)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.otp
class Doctor(models.Model):
	first_name = models.CharField(max_length=20)
	second_name = models.CharField(max_length=20)
	phone_number = models.IntegerField(default=0)
	email = models.EmailField(max_length=50)
	speciality = models.CharField(max_length=20)
	# google_credentials = models.JSONField(null=True, blank=True)


	def __str__(self):
		return "%s  %s" % (self.first_name, self.second_name)
class appointment(BaseModel):
	first_name = models.CharField(max_length=20)
	second_name = models.CharField(max_length=20)
	last_name = models.CharField(max_length=20)
	id_number = models.IntegerField(default=0)
	phone_number = models.IntegerField(default=0)
	email = models.EmailField(max_length=50)
	doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
	appointment_date = models.DateField(null=True)
	appointment_time = models.TimeField(null=True)

	def __str__(self):
		return str(self.phone_number + self.id_number)

class Medication(BaseModel):
	patient = models.OneToOneField(UserDetails, on_delete=models.CASCADE)
	date_of_visit = models.DateField(null=True)
	diagnosis = models.TextField(max_length=1000)
	medication = models.TextField(max_length=600)
	def __str__(self):
		return str(self.date_of_visit + self.diagnosis)

class Medicalrecord(BaseModel):
	GENDER = [
		("F", "Female"),
		("M", "Male"),
	]

	patient = models.OneToOneField(UserDetails, on_delete=models.CASCADE)
	dateofbirth = models.DateField(null=True)
	gender = models.CharField(max_length=20, choices=GENDER)
	contact = models.IntegerField(default=0)
	email = models.EmailField(max_length=60)
	treatment = models.TextField(max_length=20)
	medication = models.TextField(max_length=20)
	dateofvisit = models.DateField(null=True)

# class Conversation(models.Model):
#     participants = models.ManyToManyField(User)
#
# class Message(models.Model):
#     conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
#     sender = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     is_read = models.BooleanField(default=False)

