from django.urls import path
from.import views
from .views import *

app_name = 'myapp'
urlpatterns = [
    # path("index", views.index, name="index"),
    path('register/', registration_user, name="registration_user"),
    path('login/', login_user, name='login_user'),
    path('logout/', logout_user, name='logout_user'),
    path('medication/', medication, name='medication'),
    path('dashboard/', dashboard, name='dashboard'),
    path('medicalrecord/', medical_record, name='medical_record'),
    path('Appointment/', Appointment, name='Appointment'),
    path('home/', home, name='home'),
    path('edit/<int:user_id>/', edit_user, name='edit_user'),
    path('delete/<int:user_id>/', delete_user, name='delete_user'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate_account'),
    path('view_medical_record/', view_medical_record, name='view_medical_record'),
    path('delete_appointment/<str:pk>/', delete_appointment, name='delete_appointment'),
    path('delete_medicalrecords/<str:pk>/', delete_medicalrecords, name='delete_medicalrecords'),
    path('update_appointment/<str:pk>/', update_appointment, name='update_appointment'),
    path('edit_medicalrecords/<str:pk>/', edit_medicalrecords, name='edit_medicalrecords'),
    path('doctor_appointment/', doctor_appointment, name='doctor_appointment'),
    path('edit_medicationrecords/<str:pk>/', edit_medicationrecords, name='edit_medicationrecords'),
    path('delete_medicationrecords/<str:pk>/', doctor_appointment, name='delete_medicationrecords'),
    path('patient_page/', patient_page, name='patient_page'),


]