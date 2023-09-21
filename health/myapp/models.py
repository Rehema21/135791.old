import math
import random

from django.contrib.auth.models import User
from django.db import models

class UserDetails(User):
	second_name = models.CharField(max_length=20)
	role=models.CharField(max_length=20)

	def __str__(self):
		return self.username

class OtpModel(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    otp = models.CharField(max_length=7)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.otp

