from django.contrib import admin
from.models import *
@admin.register(UserDetails)
class StaffAdmin(admin.ModelAdmin):
	list_filter = ("email",)
	list_display = ("first_name", "second_name", "last_name", "email",)
	search_fields = ("email",)

@admin.register(OtpModel)
class OtpModelAdmin(admin.ModelAdmin):
    list_display = ("created_at", "is_active", "otp", "user","id")[::-1]
