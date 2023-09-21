from django.urls import path

from.import views
from .views import *

app_name = 'myapp'
urlpatterns = [
    # path("", views.index, name="index"),
    path('register/', registration_user, name="registration_user"),
    path('login/', login_user, name='login_user'),
    path('otp/', OtpVerifyView, name='otp'),
    path('verification/', two_factor, name='two_factor'),

]