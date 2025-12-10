![alt text](image.png)

---

## Assignment Details

* **Courses:** DBAS 3200 (Data-Driven Application Programming) + WEBD 3100 (Web Design Fundamentals)
* **Instructor:** Davis Boudreau
* **Project Type:** Final Project (individual; full-stack)
* **Estimated Time:** 12–18 hours (spread across Weeks 10–14)
* **Pre-Requisites:** Python 3.12+, Docker/Compose, PostgreSQL basics, Git/GitHub, Django fundamentals, WEBD 3100 MP3 tokens/components
* **Points / Weight:** See Brightspace (Final Project)
* **Due Date:** See Brightspace
* **Submission:** GitHub repository link + short video demo + Brightspace upload (reflection PDF + screenshots)

---

## 1) Overview / Purpose / Objectives

**Purpose.** Build a small, production-style **Event Management System** where authenticated users can browse events and register. You’ll implement a robust **Data Access Layer** with transactions and capacity control (DBAS 3200), and a clean, responsive **front-end** using the Corah header/hero/footer and tokenized CSS (WEBD 3100).

**Key objectives (DBAS 3200):**

* Implement a Data Access Layer (Django ORM models + services)
* Create/manage secure DB connections and migrations
* Manipulate data with CRUD (events, registrations)
* Exercise application-level **transactional control** (seat counts, uniqueness, capacity)
* Deliver professional code, docs, and reflection

**Key objectives (WEBD 3100):**

* Integrate **Corah header/hero/footer** and **tokenized CSS** (brand + neutral ramps)
* Apply semantic HTML, accessibility, responsive layout, and consistent components
* Style authentication and events UI (cards, lists, detail, forms) with your tokens

---

## 2) Learning Outcomes Addressed

**DBAS 3200**

1. Implement a Data Access Layer (ORM).
2. Create and manage a data connection.
3. Use a language-specific DB API (Django ORM, psycopg2 under the hood).
4. Manipulate data (CRUD).
5. Exercise application-level transactional control.
6. Develop professionalism in a project-managed context.
7. Enhance your professional portfolio.
8. Produce professional communication & presentation.

**WEBD 3100**

1. Apply design principles to web content presentation.
2. Design and implement UI mockups/components into a working app.
3. Implement semantic, accessible, responsive front-end with CSS tokens/components.

---

## 3) Background: What the Starter App Teaches

* **Django ORM models** (`Event`, `Attendee`, `Registration`) show relational design (one-to-one user→attendee; many-to-many attendee↔event via Registration).
* **Services layer** (`RegistrationService`) encapsulates **business rules**: capacity checks, duplicate prevention, row-level locks (`select_for_update()`), and atomic transactions.
* **Signals** auto-provision an `Attendee` when a `User` is created—this mirrors real systems that sync profiles.
* **Auth integration** uses Django’s built-in views for login/logout and a custom signup.
* **Templates** demonstrate clean separation of concerns; HTML title/description fields allow curated markup (bleach sanitized) while the page structure remains consistent.
* **CSS tokens & components** (WEBD 3100) teach scalable styling: brand/neutral ramps, buttons, cards, badges, forms—applied to the events grid, detail, auth screens.
* **Transactions** ensure **consistency**: registration increments `seats_taken` exactly once, avoids overbooking, and rolls back on error.

---

## 4) Use Case

A campus **Corah** site lists events. Authenticated students can register for an event (until full). Staff can create/edit/delete events. The UI uses the Corah brand system (tokens), a responsive layout, and accessible forms.

---

## 5) Step-by-Step Build (From Scratch)

> **Two on-ramps**
> **Option A (recommended):** Start from the provided **Starter Template** (faster).
> **Option B:** Build from scratch below. Use “corah” as the Django **project** and “events” as the **app**.

### 5.1 Project scaffold (Option B: scratch)

```bash
# 1) Folder & virtual environment (if not using Docker):
mkdir corah-final && cd corah-final

# 2) If using Docker/Compose (recommended)
# docker-compose.yml will define web (Django) + db (Postgres)
```

**docker-compose.yml (example)**

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: django_starter
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports: ["5432:5432"]

  web:
    build: .
    command: bash -lc "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
    volumes:
      - .:/app
    ports: ["8000:8000"]
    depends_on: [db]
    environment:
      DJANGO_SETTINGS_MODULE: core.settings
      POSTGRES_HOST: db
      POSTGRES_DB: django_starter
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_PORT: 5432
volumes:
  pgdata:
```

**Dockerfile (example)**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
```

**requirements.txt**

```
Django==5.1.1
psycopg2-binary==2.9.9
bleach==6.1.0
```

```bash
# 3) Create project + app
docker compose run --rm web bash -lc "django-admin startproject core ."
docker compose run --rm web bash -lc "python manage.py startapp events"
```

**core/settings.py (Postgres + templates + auth)**

```python
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "change-me"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin","django.contrib.auth","django.contrib.contenttypes",
    "django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles",
    "events",  # our app
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("POSTGRES_HOST","localhost"),
        "NAME": os.getenv("POSTGRES_DB","django_starter"),
        "USER": os.getenv("POSTGRES_USER","postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD","postgres"),
        "PORT": os.getenv("POSTGRES_PORT","5432"),
    }
}

TEMPLATES = [{
  "BACKEND":"django.template.backends.django.DjangoTemplates",
  "DIRS":[BASE_DIR/"templates"],  # project-level templates
  "APP_DIRS":True,
  "OPTIONS":{"context_processors":[
    "django.template.context_processors.debug",
    "django.template.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
  ]}
}]

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR/"static"]

LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = None
```

**core/urls.py**

```python
from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("events.urls", namespace="events")),
]
```

### 5.2 Data model (Django ORM)

**events/models.py**

```python
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

try:
    import bleach
except ImportError:
    bleach = None

class Event(models.Model):
    # Allow limited HTML in title/description (sanitized in clean()).
    title_html = models.TextField(max_length=400, help_text="Supports limited HTML.")
    date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time   = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=150, blank=True, null=True)
    capacity = models.PositiveIntegerField(default=50)
    seats_taken = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    description_html = models.TextField(blank=True)

    # allow-lists for HTML
    ALLOWED_TAGS_TITLE = ["strong","em","b","i","br","span"]
    ALLOWED_ATTRS_TITLE = {"span":["class","style"]}
    ALLOWED_TAGS_DESC = ["strong","em","b","i","u","br","span","p","ul","ol","li","a"]
    ALLOWED_ATTRS_DESC = {"a":["href","title","target","rel"],"span":["class","style"]}

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")
        if self.seats_taken < 0 or self.seats_taken > (self.capacity or 0):
            raise ValidationError("Seats taken out of range.")
        if (self.price or 0) < 0:
            raise ValidationError("Price cannot be negative.")
        if bleach:
            self.title_html = bleach.clean(self.title_html or "", tags=self.ALLOWED_TAGS_TITLE,
                                           attributes=self.ALLOWED_ATTRS_TITLE, strip=True)
            self.description_html = bleach.clean(self.description_html or "", tags=self.ALLOWED_TAGS_DESC,
                                                 attributes=self.ALLOWED_ATTRS_DESC, strip=True)
        else:
            from django.utils.html import strip_tags
            self.title_html = strip_tags(self.title_html or "")
            self.description_html = strip_tags(self.description_html or "")

    @property
    def seats_available(self): return max((self.capacity or 0) - (self.seats_taken or 0), 0)
    @property
    def is_free(self): return (self.price or 0) == 0
    @property
    def price_display(self): return "FREE" if self.is_free else f"${self.price:.2f}"
    def __str__(self):
        from django.utils.html import strip_tags
        return strip_tags(self.title_html)[:60]

class Attendee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="attendee", null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    def __str__(self): return f"{self.name} <{self.email}>"

class Registration(models.Model):
    attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = ("attendee","event")
    def __str__(self): return f"{self.attendee} -> {self.event}"
```

```bash
docker compose exec web bash -lc "python manage.py makemigrations && python manage.py migrate"
```

### 5.3 Signals (auto-create Attendee for each User)

**events/signals.py**

```python
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Attendee

@receiver(post_save, sender=User)
def ensure_attendee(sender, instance, created, **kwargs):
    if created:
        Attendee.objects.create(
            user=instance,
            name=instance.get_full_name() or instance.username,
            email=instance.email or f"{instance.username}@example.com"
        )
    else:
        a = getattr(instance, "attendee", None)
        if a and instance.email and a.email != instance.email:
            a.email = instance.email
            a.save()
```

**events/apps.py**

```python
from django.apps import AppConfig
class EventsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "events"
    def ready(self):
        from . import signals  # ensure signals load
```

**core/settings.py** → in `INSTALLED_APPS` use `"events.apps.EventsConfig"`.

### 5.4 Forms (event create/edit; signup)

**events/forms.py**

```python
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
        fields = ("username","email","first_name","last_name","password1","password2")

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title_html","date","start_time","end_time","location","capacity","price","description_html"]
        widgets = {
            "title_html": forms.TextInput(attrs={"placeholder":"<strong>Corah</strong> Orientation"}),
            "date": forms.DateInput(attrs={"type":"date"}),
            "start_time": forms.TimeInput(attrs={"type":"time"}),
            "end_time": forms.TimeInput(attrs={"type":"time"}),
            "capacity": forms.NumberInput(attrs={"min":1}),
            "price": forms.NumberInput(attrs={"min":0,"step":"0.01"}),
            "description_html": forms.Textarea(attrs={"rows":6}),
        }
    def clean(self):
        cleaned = super().clean()
        s, e = cleaned.get("start_time"), cleaned.get("end_time")
        if s and e and s >= e:
            self.add_error("end_time","End time must be after start time.")
        return cleaned
```

### 5.5 Service (transaction-safe registration)

**events/services.py**

```python
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

        # Lock event row & enforce capacity
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
        return {"attendee": attendee.name, "event": strip_tags(event.title_html)}
```

### 5.6 Views & URLs

**events/views.py** (comments included)

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse
from .forms import SignupForm, EventForm
from .models import Event
from .services import RegistrationService

def hello(request):  # sanity ping
    return HttpResponse("Hello from Django in Docker 👋")

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("events:event_list")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        # optional: store names
        if form.cleaned_data.get("first_name") or form.cleaned_data.get("last_name"):
            user.first_name = form.cleaned_data.get("first_name","")
            user.last_name  = form.cleaned_data.get("last_name","")
            user.save()
        login(request, user)
        messages.success(request, "Account created. You are now logged in.")
        return redirect("events:event_list")
    return render(request, "auth/signup.html", {"form": form})

def event_list_view(request):
    events = Event.objects.order_by("date","start_time")
    return render(request, "events/event_list.html", {"events": events})

def event_detail_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, "events/event_detail.html", {"event": event})

@staff_member_required(login_url="/auth/login/")
def event_create_view(request):
    form = EventForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Event created.")
        return redirect("events:event_list")
    return render(request, "events/event_form.html", {"form": form, "mode": "create"})

@staff_member_required(login_url="/auth/login/")
def event_update_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    form = EventForm(request.POST or None, instance=event)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Event updated.")
        return redirect("events:event_list")
    return render(request, "events/event_form.html", {"form": form, "mode": "edit", "event": event})

@staff_member_required(login_url="/auth/login/")
def event_delete_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == "POST":
        title = str(event)
        event.delete()
        messages.success(request, f"Deleted event: {title}")
        return redirect("events:event_list")
    return render(request, "events/event_confirm_delete.html", {"event": event})

@login_required()  # uses settings.LOGIN_URL
def register_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    error = None
    if request.method == "POST":
        try:
            RegistrationService().register_logged_in_user_for_event(request.user, event.id)
            messages.success(request, "Registration successful!")
            return redirect("events:event_register_success", event_id=event.id)
        except ValueError as e:
            error = str(e)
            messages.error(request, error)
    return render(request, "events/register.html", {"event": event, "error": error})

@login_required()
def register_success_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, "events/register_success.html", {"event": event})

def logout_page(request):
    logout(request)
    return render(request, "auth/logout.html", status=200)
```

**events/urls.py**

```python
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "events"

urlpatterns = [
    path("", views.event_list_view, name="event_list"),
    path("events/<int:event_id>/", views.event_detail_view, name="event_detail"),
    path("events/<int:event_id>/register/", views.register_view, name="event_register"),
    path("events/<int:event_id>/register/success/", views.register_success_view, name="event_register_success"),

    path("events/new/", views.event_create_view, name="event_create"),
    path("events/<int:event_id>/edit/", views.event_update_view, name="event_update"),
    path("events/<int:event_id>/delete/", views.event_delete_view, name="event_delete"),

    path("auth/login/",  auth_views.LoginView.as_view(template_name="auth/login.html"),  name="login"),
    path("auth/logout/", views.logout_page, name="logout"),
    path("auth/signup/", views.signup_view, name="signup"),
]
```

### 5.7 Templates (minimal, with comments)

**templates/base.html**

```html
{% load static %}
<!DOCTYPE html><html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{% block title %}Corah Events{% endblock %}</title>
  <link rel="stylesheet" href="{% static 'css/styles.css' %}">
  <link rel="stylesheet" href="{% static 'css/theme-light.css' %}">
</head>
<body>
<header>
  <!-- Corah header/hero placeholder (replace with your WEBD 3100 header/hero) -->
  <div class="wrap">
    <nav aria-label="Main Navigation">
      <ul>
        <li><a href="{% url 'events:event_list' %}">Events</a></li>
        {% if user.is_authenticated %}
          <li><span>Welcome, {{ user.get_username }}!</span></li>
          <li><a href="{% url 'events:logout' %}">Logout</a></li>
        {% else %}
          <li><a href="{% url 'events:login' %}">Login</a></li>
          <li><a href="{% url 'events:signup' %}">Sign Up</a></li>
        {% endif %}
      </ul>
    </nav>
  </div>
  <hr>
</header>

<main class="wrap">
  {% if messages %}
    <ul class="messages">{% for m in messages %}<li>{{ m }}</li>{% endfor %}</ul>
  {% endif %}
  {% block content %}{% endblock %}
</main>

<footer><div class="wrap">
  <!-- Corah footer placeholder -->
  <p class="center">© 2025 NSCC — Corah</p>
</div></footer>
</body>
</html>
```

**Event list/detail/register/register_success**
(Use the neutral versions we produced earlier—titles/description render `|safe` without extra styling; buttons/badges use theme tokens.)

**Auth templates**

* `templates/auth/login.html`, `auth/signup.html`, `auth/logout.html` — simple forms using `.auth-form` classes (WEBD tokens apply).

### 5.8 Seed data (optional)

Create a small seed script or add via Django admin.

---

## 6) Deliverables

1. **GitHub repository URL** (public or class org):

   * Must contain Docker/Compose, Django project, app, templates, static, README.
2. **Working site demo video (2–4 minutes)**

   * Show: login → list → detail → register → success; staff CRUD; capacity/duplicate handling.
3. **Reflection (PDF, 1–2 pages)**

   * Answer the reflection prompts (below).
4. **Screenshots**

   * At least 3: Events list, Event detail, Registration success (plus one CRUD screen if staff).

---

## 7) Reflection Questions (submit as PDF)

1. Explain how your **transactional registration** prevents overbooking and duplicates.
2. Where and why do you use **`select_for_update()`** and **`@transaction.atomic`**?
3. In what ways do your **CSS tokens/components** improve maintainability and consistency?
4. Describe how **sanitization** works for `title_html`/`description_html`. Why is this critical?
5. If this app scaled to thousands of users, what **performance** improvements would you consider?

---

## 8) Evaluation Criteria Summary

* **DBAS 3200 (60%)**

  * Data model & migrations (10)
  * CRUD & services correctness (15)
  * Transactions/concurrency (row locks, atomicity) (20)
  * Code quality & structure (5)
  * Documentation & reflection quality (10)

* **WEBD 3100 (40%)**

  * Corah header/hero/footer integration (10)
  * Tokens/components CSS, responsive layout, accessibility (20)
  * Visual polish & usability (10)

**Total: 100%** (course-level weights per Brightspace)

---

## 9) Detailed Rubric

| Criterion                                | Exemplary (A)                                                                                      | Proficient (B)                           | Developing (C)                              | Beginning (D/F)                               |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------- | ---------------------------------------- | ------------------------------------------- | --------------------------------------------- |
| **DB: Models & Migrations (10)**         | Correct relational design; clean migrations; sanity constraints validated                          | Minor schema issues; migrations OK       | Gaps in relationships or constraints        | Broken migrations; incorrect schema           |
| **CRUD & Services (15)**                 | Full CRUD; service encapsulates rules; code commented & testable                                   | CRUD mostly correct; some logic in views | Coupling between layers; missing edge cases | CRUD broken; business logic scattered         |
| **Transactions & Concurrency (20)**      | Uses `@transaction.atomic`, `select_for_update()`, capacity logic, duplicate guard; no overbooking | Mostly correct; minor gaps               | Incomplete; race conditions possible        | No transactions; duplicates/overbooking occur |
| **Code Quality (5)**                     | Clean structure, comments, clear naming, DRY                                                       | Mostly clean; some duplication           | Messy or unclear in places                  | Disorganized, hard to follow                  |
| **Docs & Reflection (10)**               | Clear README, setup steps, architecture notes; reflective insight                                  | README OK; basic reflection              | Minimal docs and reflection                 | Missing docs or reflection                    |
| **Corah Header/Hero/Footer (10)**        | Integrated, responsive, semantic                                                                   | Integrated but minor issues              | Partially integrated                        | Missing or non-functional                     |
| **Tokens/Components/Accessibility (20)** | Consistent tokens; responsive; good contrast; keyboard-friendly                                    | Mostly consistent; a11y minor fixes      | Inconsistent tokens; responsive gaps        | Little to no styling discipline               |
| **Visual Polish & UX (10)**              | Cohesive, tidy, professional                                                                       | Good, small inconsistencies              | Rough edges                                 | Poor usability/visuals                        |

---

## 10) Submission Guidelines

* **Repo name:** `wXXXXXXX_dbas3200_final_corah`
* **ZIP upload to Brightspace:** same name; include `reflection.pdf` and screenshots inside `/docs/`
* **README.md** must include: stack, setup, how to run, credentials (demo), and known issues.

---

## 11) Resources / Equipment

* Software: Docker/Compose, Python 3.12, VS Code, Git/GitHub
* Libraries: Django 5.1, psycopg2-binary, bleach
* Your WEBD 3100 MP3 token CSS and components

---

## 12) Academic Policies

* Follow NSCC academic integrity policy.
* Cite any external references.
* Individual work unless otherwise approved by instructor.

---

## 13) File Map — Recommended Repository Structure

```
corah-final/
├─ docker-compose.yml
├─ Dockerfile
├─ requirements.txt
├─ Makefile                 # optional: up/down/seed helpers
├─ .env                     # if used (DO NOT COMMIT real secrets)
├─ core/
│  ├─ __init__.py
│  ├─ settings.py           # Postgres, templates, static, auth redirects
│  ├─ urls.py               # includes events.urls
│  └─ wsgi.py / asgi.py
├─ events/
│  ├─ __init__.py
│  ├─ apps.py               # loads signals
│  ├─ models.py             # Event, Attendee, Registration
│  ├─ forms.py              # SignupForm, EventForm
│  ├─ services.py           # RegistrationService (atomic)
│  ├─ signals.py            # auto-create Attendee for new User
│  ├─ views.py              # list/detail/register/CRUD/auth glue
│  ├─ urls.py               # routes incl. auth/login/logout/signup
│  └─ admin.py              # optional: register models
├─ templates/
│  ├─ base.html             # Corah header/footer placeholders
│  ├─ auth/
│  │  ├─ login.html
│  │  ├─ signup.html
│  │  └─ logout.html
│  └─ events/
│     ├─ event_list.html
│     ├─ event_detail.html
│     ├─ register.html
│     ├─ register_success.html
│     ├─ event_form.html
│     └─ event_confirm_delete.html
├─ static/
│  └─ css/
│     ├─ styles.css         # your base styles
│     └─ theme-light.css    # tokens/components (light)
└─ docs/
   ├─ reflection.pdf        # to submit
   └─ screenshots/          # list/detail/success/CRUD
```

---

## Final notes to students

* **DBAS 3200 focus:** clean ORM + services, transactions, correctness.
* **WEBD 3100 focus:** cohesive visual system via tokens/components, accessibility, responsive patterns.
* **Professionalism:** Treat this like a portfolio piece—your README and polish matter.
