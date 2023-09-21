from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserDetails


class UserCreateForm(UserCreationForm):
	class Meta:
		fields = ['username', 'first_name', 'last_name', 'second_name', 'email', 'password1', 'password2', 'role']
		model = UserDetails