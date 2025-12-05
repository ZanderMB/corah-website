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
        fields = ['title', 'date', 'location', 'capacity']
    
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        
        labels = {
            'title': 'Event Title',
            'date': 'Event Date',
            'location': 'Location',
            'capacity': 'Event Capacity',
        }