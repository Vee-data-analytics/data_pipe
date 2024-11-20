from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Employee
from rest_framework.authtoken.models import Token
import qrcode
from io import BytesIO
from django.core.files import File


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Employee.objects.create(user=instance)


@receiver(post_save, sender=Employee)
def generate_qr_code(sender, instance, created, **kwargs):
    if created:
        instance.generate_qr_code()