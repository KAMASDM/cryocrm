from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Appointment, AppointmentHistory


@receiver(pre_save, sender=Appointment)
def track_status_change(sender, instance, **kwargs):
    """Track appointment status changes"""
    if instance.pk:
        try:
            old_appointment = Appointment.objects.get(pk=instance.pk)
            if old_appointment.status != instance.status:
                # Will be saved after the appointment is saved
                instance._status_changed = True
                instance._old_status = old_appointment.status
        except Appointment.DoesNotExist:
            pass


@receiver(post_save, sender=Appointment)
def save_status_history(sender, instance, created, **kwargs):
    """Save status change to history"""
    if hasattr(instance, '_status_changed') and instance._status_changed:
        AppointmentHistory.objects.create(
            appointment=instance,
            previous_status=instance._old_status,
            new_status=instance.status
        )
