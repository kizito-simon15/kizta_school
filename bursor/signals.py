from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.finance.models import Invoice


@receiver(post_save, sender=Invoice)
def after_creating_bursor_invoice(sender, instance, created, **kwargs):
    if created:
        previous_inv = (
            Invoice.objects.filter(student=instance.student)
            .exclude(id=instance.id)
            .last()
        )
        if previous_inv:
            previous_inv.status = "closed"
            previous_inv.save()
            instance.balance_from_previous_install = previous_inv.balance()
            instance.save()
