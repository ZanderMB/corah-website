from django.db import models

from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    location = models.CharField(max_length=150, blank=True, null=True)
    capacity = models.PositiveIntegerField(default=50)
    seats_taken = models.PositiveIntegerField(default=0)

    @property
    def seats_available(self):
        return self.capacity - self.seats_taken

    def __str__(self):
        return f"{self.title} ({self.date})"


class Attendee(models.Model):
    # NEW: link to Django auth user (one profile per user)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="attendee")
    # Keep name/email for convenience & denormalized display
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Registration(models.Model):
    attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("attendee", "event")

    def __str__(self):
        return f"{self.attendee} -> {self.event}"