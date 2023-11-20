# myapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def assign_user_to_groups(sender, instance, created, **kwargs):
    if created:
        # Assign the user to groups
        patient_group = Group.objects.get(name='patient')
        admin_group = Group.objects.get(name='admin')
        doctor_group = Group.objects.get(name='doctor')

        instance.groups.add(patient_group, admin_group, doctor_group)
