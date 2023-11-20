from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *
from datetime import date, datetime
import datetime
from werkzeug.routing import ValidationError
from django.utils.crypto import get_random_string
class UserCreateForm(UserCreationForm):
	# group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label='Group')
	class Meta:
		fields = ['username', 'first_name', 'last_name', 'second_name', 'email', 'password1', 'password2', 'role']
		model = UserDetails



	def save(self, commit=True):
		user = super().save(commit=False)
		user.is_active = False
		user.save()


		verification_token = get_random_string(length=40)
		user.profile.verification_token = verification_token
		user.profile.save()

		return user
class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = UserDetails
        fields = ['username', 'password']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserDetails
        fields = ['username', 'first_name', 'last_name', 'email',]


class PatientForm(forms.ModelForm):
    class Meta:
        model = appointment
        fields = ['first_name', 'last_name', 'second_name', "id_number", 'email', 'phone_number',
                  'doctor', 'appointment_date', 'appointment_time']

        labels = {
            'first_name': 'First Name', 'second_name': 'Second Name', 'last_name': 'Last Name',
            'id_number': 'ID Number', 'phone_number': 'Phone Number', 'doctor': 'Doctor',
            'appointment_date': 'Date of Appointment', 'appointment_time': 'Time of Appointment',
        }

        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'second_name': forms.TextInput(attrs={'placeholder': 'Second name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
            'id_number': forms.NumberInput(attrs={'placeholder': 'ID number'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'phone_number': forms.NumberInput(attrs={'placeholder': 'Phone number'}),
            'doctor': forms.Select(attrs={'placeholder': 'Doctor'}),
            'appointment_date': forms.DateInput(format=('%d/%b/%Y'), attrs={'type': 'date', 'min': datetime.date.today()}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data['appointment_date']
        if appointment_date < datetime.date.today():
            raise ValidationError("Date cannot be in the past")
        return appointment_date
class MedicationForm(forms.ModelForm):
	class Meta:
		fields = ['patient', 'date_of_visit', 'diagnosis', 'medication']
		model = Medication

		widgets = {
			'date_of_visit': forms.DateInput(format=('%d/%b/%Y'), attrs={'type': 'date', 'min': datetime.date.today()}),
		}

class MedicalRecordForm(forms.ModelForm):
	class Meta:
		fields = ['patient','dateofbirth', 'gender', 'contact', 'email', 'treatment', 'medication', 'dateofvisit']
		model = Medicalrecord

		widgets = {
		'dateofbirth': forms.DateInput(format=('%d/%b/%Y'), attrs={'type': 'date', 'max': datetime.date.today()}),
		'dateofvisit': forms.DateInput(format=('%d/%b/%Y'), attrs={'type': 'date', 'min': datetime.date.today()}),
		'email': forms.EmailInput(attrs={'': 'email'}),
	    }
	def clean_date_of_birth(self):
		dateofbirth = self.cleaned_data['dateofbirth']
		if dateofbirth > datetime.date.today():
			raise ValidationError("Date of Birth Cannot Be in the future")
		return dateofbirth

	def clean_dateofvisit(self):
		dateofvisit = self.cleaned_data['appointment_date']
		if dateofvisit < datetime.date.today():
			raise ValidationError("Date cannot be in the past")
		return dateofvisit