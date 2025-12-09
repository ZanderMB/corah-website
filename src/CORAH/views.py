from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import SignupForm, EventForm
from .models import Event
from .services import RegistrationService

#Home View
def home(request):
    return render(request, "home.html")

# Auth Views
def signup_view(request):
    if request.user.is_authenticated:
        return redirect("events:event_list")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Ensure Attendee profile is created via signal; update names if provided
            if form.cleaned_data.get("first_name") or form.cleaned_data.get("last_name"):
                user.first_name = form.cleaned_data.get("first_name", "")
                user.last_name  = form.cleaned_data.get("last_name", "")
                user.save()
            login(request, user)
            messages.success(request, "Account created. You are now logged in.")
            return redirect("events:event_list")
    else:
        form = SignupForm()

    return render(request, "auth/signup.html", {"form": form})

# vent Views
def event_list_view(request):
    events = Event.objects.all().order_by("date")
    return render(request, "events/event_list.html", {"events": events})

@login_required(login_url="auth:login")
def register_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    error = None

    if request.method == "POST":
        # Don't need the name email rwos here anymore with the linked Auth_User
        svc = RegistrationService()
        try:
            svc.register_logged_in_user_for_event(request.user, event.id)
            messages.success(request, "Registration successful!")
            return redirect("events:event_register_success", event_id=event.id)
        except ValueError as e:
            error = str(e)
            messages.error(request, error)

    return render(request, "events/register.html", {"event": event, "error": error})

@login_required(login_url="auth:login")
def register_success_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, "events/register_success.html", {"event": event})


# Creating Event Form

@login_required(login_url="auth:login")
def create_event_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, "Event created successfully!")
            return redirect('events:event_list')
    else:
        form = EventForm()
    
    return render(request, 'events/create_event.html', {'form': form})