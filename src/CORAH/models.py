from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

try:
    import bleach
except ImportError:
    bleach = None

class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=150, blank=True, null=True)
    capacity = models.PositiveIntegerField(default=50)
    seats_taken = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    description_html = models.TextField(blank=True)

    ALLOWED_TAGS_TITLE = ["strong", "em", "b", "i", "br", "span"]
    ALLOWED_ATTRS_TITLE = {"span": ["class", "style"]}
    ALLOWED_TAGS_DESC = ["strong", "em", "b", "i", "u", "br", "span", "p", "ul", "ol", "li", "a"]
    ALLOWED_ATTRS_DESC = {"a": ["href", "title", "target", "rel"], "span": ["class", "style"]}

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")
        if self.seats_taken < 0 or self.seats_taken > (self.capacity or 0):
            raise ValidationError("Seats taken out of range.")
        if (self.price or 0) < 0:
            raise ValidationError("Price cannot be negative.")
        if bleach:
            self.title = bleach.clean(
                self.title or "", 
                tags=self.ALLOWED_TAGS_TITLE, 
                attributes=self.ALLOWED_ATTRS_TITLE, 
                strip=True
            )
    
            self.description_html = bleach.clean(
            self.description_html or "", 
            tags=self.ALLOWED_TAGS_DESC, 
            attributes=self.ALLOWED_ATTRS_DESC, 
            strip=True
        )

    @property
    def seats_available(self): return max((self.capacity or 0) - (self.seats_taken or 0), 0)
    @property
    def is_free(self): return (self.price or 0) == 0
    @property
    def price_display(self): return "FREE" if self.is_free else f"${self.price:.2f}"

    def __str__(self):
        from django.utils.html import strip_tags
        return strip_tags(self.title)[:60]


class Attendee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="attendee")
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