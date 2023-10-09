import math
import random
import uuid
from django.contrib.auth.models import User,Group
from django.db import models

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
	# group =models.Ch(queryset=Group.objects.all(), required=True, label='Group')
	group=models.CharField(max_length=20)

	def __str__(self):
		return self.username

class OtpModel(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    otp = models.CharField(max_length=7)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.otp
class Doctor(BaseModel):
	first_name = models.CharField(max_length=20)
	second_name = models.CharField(max_length=20)
	phone_number = models.IntegerField(default=0)
	email = models.EmailField(max_length=50)
	speciality = models.CharField(max_length=20)

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
	dateofappointment = models.DateField(null=True)
	timeofappointment = models.TimeField(null=True)

	def __str__(self):
		return str(self.phone_number + self.id_number)

