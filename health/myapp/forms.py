from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone

from .models import *
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
        fields = ['username', 'first_name', 'last_name', 'email', ]


class PatientForm(forms.ModelForm):
    class Meta:
        model = appointment
        fields = ['first_name', 'location', 'second_name', "id_number", 'email', 'phone_number', 'description',
                  'doctor', 'start', 'end']

        labels = {
            'first_name': 'First Name', 'second_name': 'Second Name', 'description': 'Description',
            'location': 'Location',
            'id_number': 'ID Number', 'phone_number': 'Phone Number', 'doctor': 'Doctor',
            'start': 'Start', 'end': 'End',
        }

        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'second_name': forms.TextInput(attrs={'placeholder': 'Second name'}),
            'description': forms.Textarea(attrs={'placeholder': 'description'}),
            'location': forms.TextInput(attrs={'placeholder': 'location'}),
            'id_number': forms.NumberInput(attrs={'placeholder': 'ID number'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'phone_number': forms.NumberInput(attrs={'placeholder': 'Phone number'}),
            'doctor': forms.Select(attrs={'placeholder': 'Doctor'}),
            'start': forms.TextInput(attrs={'type': 'datetime-local', 'min': datetime.datetime.now()}),
            'end': forms.TextInput(attrs={'type': 'datetime-local', 'min': datetime.datetime.now()}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the min attribute for start and end fields to restrict past dates in the HTML form
        self.fields['start'].widget.attrs['min'] = timezone.now().strftime('%Y-%m-%dT%H:%M')
        self.fields['end'].widget.attrs['min'] = timezone.now().strftime('%Y-%m-%dT%H:%M')

    def clean_start(self):
        start = self.cleaned_data.get('start')
        if start < timezone.now():
            raise forms.ValidationError("Please choose a future date and time.")
        return start

    def clean_end(self):
        end = self.cleaned_data.get('end')
        if end < timezone.now():
            raise forms.ValidationError("Please choose a future date and time.")
        return end

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        doctor = cleaned_data.get('doctor')

        if start and end and doctor:
            # Check if the chosen time slot is available
            conflicting_appointments = UserDetails.objects.filter(doctor=doctor, start__lt=end, end__gt=start)
            if conflicting_appointments.exists():
                raise forms.ValidationError("This time slot is already booked. Please choose another time.")

        return cleaned_data

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
        fields = ['patient', 'dateofbirth', 'gender', 'contact', 'email', 'treatment', 'medication', 'dateofvisit']
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
        dateofvisit = self.cleaned_data['dateofvisit']
        if dateofvisit < datetime.date.today():
            raise ValidationError("Date cannot be in the past")
        return dateofvisit
