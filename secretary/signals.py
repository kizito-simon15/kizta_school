# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StudentComments, SecretaryNotification
from django.contrib.auth import get_user_model


@receiver(post_save, sender=StudentComments)
def create_notification(sender, instance, created, **kwargs):
    if created:
        # Assuming there is only one secretary for simplicity
        secretary_user = get_user_model().objects.filter(is_staff=True, is_active=True).first()
        if secretary_user:
            SecretaryNotification.objects.create(secretary=secretary_user, comment=instance)
