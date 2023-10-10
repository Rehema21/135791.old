from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from datetime import date, datetime
from time import timezone
from werkzeug.routing import ValidationError
from django.utils.crypto import get_random_string
class UserCreateForm(UserCreationForm):
	group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label='Group')
	class Meta:
		fields = ['username', 'first_name', 'last_name', 'second_name', 'email', 'password1', 'password2', 'group']
		model = UserDetails

	def save(self, commit=True):
		user = super().save(commit=False)
		user.is_active = False  # User is not active until they verify their email
		user.save()

		# Generate a verification token
		verification_token = get_random_string(length=40)
		user.profile.verification_token = verification_token
		user.profile.save()

		return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',]

class PatientForm(forms.ModelForm):

	def clean_date(self):
		dateofappointment = self.cleaned_data['dateofappointment']
		if dateofappointment < datetime.date.today():
			raise ValidationError("Date cannot be in the past")
		return date

	class Meta:
		model = appointment

		fields = ['first_name', 'last_name', 'second_name', "id_number", 'email', 'phone_number',
				  'doctor', 'dateofappointment','timeofappointment']

		labels = {
			'first_name': 'First Name', 'second_name': 'Second Name', 'last_name': 'Last Name',
			'id_number': 'ID Number', 'phone_number': 'Phone Number', 'doctor': 'Doctor',
			'dateofappointment': 'date of appointment', 'timeofappointment': 'time of appointment',

		}
		widgets = {
			'first_name': forms.TextInput(attrs={'': 'first name'}),
			'second_name': forms.TextInput(attrs={'': 'second name'}),
			'last_name': forms.TextInput(attrs={'': 'last name'}),
			'id_number': forms.NumberInput(attrs={'': 'id number'}),
			'email': forms.EmailInput(attrs={'': 'email'}),
			'phone_number': forms.NumberInput(attrs={'': 'phone number'}),
			'doctor': forms.Select(attrs={'': 'doctor'}),
			'dateofappointment': forms.DateInput(format=('%d/%b/%Y'), attrs={'type': 'date'}),
			'timeofappointment': forms.TimeInput(attrs={'type': 'time'}),
		}

		def clean_date(self):
			dateofvisit = self.cleaned_data['dateofvisit']
			if dateofvisit < datetime.date.today():
				raise ValidationError("Date cannot be in the past")
			return date