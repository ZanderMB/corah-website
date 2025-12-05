from django.db import transaction, IntegrityError
from django.contrib.auth.models import User
from .models import Event, Attendee, Registration

class RegistrationService:

    @transaction.atomic
    def register_logged_in_user_for_event(self, user: User, event_id: int):
        """
        Registration flow for authenticated users.
        Uses the user's Attendee profile and enforces capacity & uniqueness.
        """
        # Get attendee profile (created via signal). Guard if missing:
        try:
            attendee = user.attendee
        except Attendee.DoesNotExist:
            # Create on-the-fly (defensive)
            attendee = Attendee.objects.create(
                user=user,
                name=user.get_full_name() or user.username,
                email=user.email or f"{user.username}@example.com"
            )

        event = Event.objects.select_for_update().get(id=event_id)
        if event.seats_available <= 0:
            raise ValueError("Event is full. No seats available.")

        try:
            Registration.objects.create(attendee=attendee, event=event)
        except IntegrityError:
            raise ValueError("You are already registered for this event.")

        event.seats_taken += 1
        event.save()

        return {"attendee": attendee.name, "event": event.title}