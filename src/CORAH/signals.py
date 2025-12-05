from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Attendee

@receiver(post_save, sender=User)
def ensure_attendee_profile(sender, instance, created, **kwargs):
    """
    Ensure every User has a matching Attendee profile.
    Keep name/email in sync on first creation; update email thereafter.
    """
    if created:
        Attendee.objects.create(
            user=instance,
            name=instance.get_full_name() or instance.username,
            email=instance.email or f"{instance.username}@example.com"
        )
    else:
        # keep email updated if user changes it
        attendee = getattr(instance, "attendee", None)
        if attendee and instance.email and attendee.email != instance.email:
            attendee.email = instance.email
            attendee.save()