from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponse

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
    form = SignupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()

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

# Event Views
def event_list_view(request):
    events = Event.objects.all().order_by("date", "start_time")
    paginator = Paginator(events, 3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'paginator': paginator,
    }

    return render(request, "events/event_list.html", context)

def event_detail_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, "events/events_detail.html", {"event": event})

@staff_member_required(login_url="auth:login")
def event_update_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    form = EventForm(request.POST or None, instance=event)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Event updated.")
        return redirect("events:event_list")
    return render(request, "events/event_form.html", {"form": form, "mode": "edit", "event": event})

@staff_member_required(login_url="auth:login")
def event_delete_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == "POST":
        title = str(event)
        event.delete()
        messages.success(request, f"Deleted event: {title}")
        return redirect("events:event_list")
    return render(request, "events/event_confirm_delete.html", {"event": event})

@login_required(login_url="auth:login")
def register_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    error = None

    if request.method == "POST":
        # Don't need the name email rwos here anymore with the linked Auth_User
        try:
            RegistrationService().register_logged_in_user_for_event(request.user, event.id)
            messages.success(request, "Registration successful!")
            return redirect("events:register_success", event_id=event.id)
        except ValueError as e:
            error = str(e)
            messages.error(request, error)
    return render(request, "events/register.html", {"event": event, "error": error})

@login_required(login_url="auth:login")
def register_success_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, "events/register_success.html", {"event": event})

def logout_page(request):
    logout(request)
    return render(request, "auth/logout.html", status=200)

# Creating Event Form

@staff_member_required(login_url="auth:login")
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