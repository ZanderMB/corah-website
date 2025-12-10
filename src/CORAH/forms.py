from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Event

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    
    class Meta:
        model = User
        fields = (
            "username", 
            "email", 
            "first_name", 
            "last_name", 
            "password1", 
            "password2"
            )

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 
                  'date',
                  'start_time',
                  'end_time',
                  'location', 
                  'capacity',
                  'price',
                  'description_html']
    
        widgets = {
            'title': forms.TextInput(attrs={'placeholder':"<strong>Corah</strong> Orientation"}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            "start_time": forms.TimeInput(attrs={"type":"time"}),
            "end_time": forms.TimeInput(attrs={"type":"time"}),
            "capacity": forms.NumberInput(attrs={"min":1}),
            "price": forms.NumberInput(attrs={"min":0,"step":"0.01"}),
            "description_html": forms.Textarea(attrs={"rows":6}),
        }
        
        labels = {
            'title': 'Event Title',
            'date': 'Event Date',
            'location': 'Location',
            'capacity': 'Event Capacity',
        }

        def clean(self):
            cleaned = super().clean()
            s, e = cleaned.get("start_time"), cleaned.get("end_time")
            if s and e and s >= e:
                self.add_error("end_time","End time must be after start time.")
            return cleaned