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
    path('activate/<uidb64>/<token>/',activate_account, name='activate_account'),
    path('view_medical_record/', view_medical_record, name='view_medical_record'),
]