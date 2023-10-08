from django.urls import path
from.import views
from .views import *

app_name = 'myapp'
urlpatterns = [
    path("index", views.index, name="index"),
    path('register/', registration_user, name="registration_user"),
    path('login/', login_user, name='login_user'),
    path('logout/', logout_user, name='logout_user'),
    path('Otp/', Otp, name='Otp'),
    path('verification/', twofactor, name='twofactor'),
    path('dashboard/', dashboard, name='dashboard'),
    path('appointment/', appointment, name='appointment'),

]