from django.db import transaction, IntegrityError
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from .models import Event, Attendee, Registration

def _unique_fallback_email(user: User) -> str:
    base = (user.email or "").split("@")[0] or user.username
    return f"{base}+uid{user.id}@example.local"

class RegistrationService:
    @transaction.atomic
    def register_logged_in_user_for_event(self, user: User, event_id: int):
        # Resolve attendee
        try:
            attendee = user.attendee
        except Attendee.DoesNotExist:
            attendee = None
        if attendee is None:
            if user.email:
                try:
                    ex = Attendee.objects.select_for_update().get(email=user.email)
                    if ex.user_id in (None, user.id):
                        ex.user = user
                        if not ex.name:
                            ex.name = user.get_full_name() or user.username
                        ex.save()
                        attendee = ex
                    else:
                        attendee = Attendee.objects.create(
                            user=user, name=user.get_full_name() or user.username,
                            email=_unique_fallback_email(user)
                        )
                except Attendee.DoesNotExist:
                    attendee = Attendee.objects.create(
                        user=user, name=user.get_full_name() or user.username, email=user.email
                    )
            else:
                attendee = Attendee.objects.create(
                    user=user, name=user.get_full_name() or user.username, email=_unique_fallback_email(user)
                )

        event = Event.objects.select_for_update().get(id=event_id)
        if event.seats_available <= 0:
            raise ValueError("Event is full. No seats available.")
        try:
            Registration.objects.create(attendee=attendee, event=event)
        except IntegrityError:
            raise ValueError("You are already registered for this event.")
        event.seats_taken += 1
        event.full_clean()
        event.save()
        return {"attendee": attendee.name, "event": strip_tags(event.title)}