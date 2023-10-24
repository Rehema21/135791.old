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
		user.is_active = False
		user.save()


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
				  'doctor', 'appointment_date','appointment_time']

		labels = {
			'first_name': 'First Name', 'second_name': 'Second Name', 'last_name': 'Last Name',
			'id_number': 'ID Number', 'phone_number': 'Phone Number', 'doctor': 'Doctor',
			'appointment_date': 'Date of Appointment', 'appointment_time': 'Time of Appointment',

		}
		widgets = {
			'first_name': forms.TextInput(attrs={'': 'first name'}),
			'second_name': forms.TextInput(attrs={'': 'second name'}),
			'last_name': forms.TextInput(attrs={'': 'last name'}),
			'id_number': forms.NumberInput(attrs={'': 'id number'}),
			'email': forms.EmailInput(attrs={'': 'email'}),
			'phone_number': forms.NumberInput(attrs={'': 'phone number'}),
			'doctor': forms.Select(attrs={'': 'doctor'}),
			'appointment_date': forms.DateInput(format=('%d/%b/%Y'), attrs={'type': 'date'}),
			'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
		}

		def clean_date(self):
			dateofvisit = self.cleaned_data['dateofvisit']
			if dateofvisit < datetime.date.today():
				raise ValidationError("Date cannot be in the past")
			return date

class MedicationForm(forms.ModelForm):
	class Meta:
		fields = ['patient', 'date_of_visit', 'diagnosis', 'medication']
		model = Medication

		widgets = {
			'date_of_visit': forms.DateInput(format=('%d/%b/%Y'), attrs={'type': 'date'}),
		}

class MedicalRecordForm(forms.ModelForm):
	class Meta:
		fields = ['patient','dateofbirth', 'gender', 'contact', 'email', 'treatment', 'medication', 'dateofvisit']
		model = Medicalrecord

		widgets = {
		'dateofbirth': forms.DateInput(format=('%d/%b/%Y'), attrs={'type': 'date'}),
		'dateofvisit': forms.DateInput(format=('%d/%b/%Y'), attrs={'type': 'date'}),
		'email': forms.EmailInput(attrs={'': 'email'}),
	    }