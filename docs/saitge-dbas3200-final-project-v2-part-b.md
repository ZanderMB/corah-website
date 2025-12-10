![alt text](image.png)

---

# Workshop B — Corah Front-End Integration (WEBD3100)

**Goal:** Apply a clean, tokenized **CSS design system** (brand + neutral ramps) and reusable **partials** (header, footer, messages) to your Django event app. Style the **auth** pages and the events UI without overriding the HTML stored in `title_html` and `description_html`.

**You’ll build:**

* `templates/partials/_header.html`, `_footer.html`, `_messages.html`
* `templates/auth/login.html`, `signup.html`, `logout.html`
* `templates/base.html` wired to partials + static assets
* Tokenized CSS: `static/css/tokens.css`, `components.css`, `theme-light.css`, `utilities.css`

**Pre-reqs:** Your Django starter runs and serves static files.

---

## 1) File Map (what you’ll add)

```
templates/
├─ base.html                  # includes partials + loads tokenized CSS
├─ partials/
│  ├─ _header.html
│  ├─ _footer.html
│  └─ _messages.html
└─ auth/
   ├─ login.html
   ├─ signup.html
   └─ logout.html

static/
└─ css/
   ├─ tokens.css             # design tokens: brand + neutral ramps, spacing, radius, etc.
   ├─ components.css         # buttons, cards, grids, forms, auth-form, event-card
   ├─ theme-light.css        # light theme values, prefers-color-scheme hook
   └─ utilities.css          # helpers (mt-*, flex, grid, etc.)
```

---

## 2) Add partials

### `templates/partials/_header.html`

```html
<header class="site-header">
  <div class="wrap header-inner">
    <!-- Corah header/hero placeholder — swap with WEBD mockup later -->
    <a href="{% url 'events:event_list' %}" class="brand">
      <!-- logo placeholder -->
      <span class="brand-mark" aria-hidden="true">❤️</span>
      <span class="brand-text">Corah</span>
    </a>

    <nav aria-label="Main" class="nav">
      <a href="{% url 'events:event_list' %}" class="nav-link">Events</a>
      {% if user.is_authenticated %}
        <span class="nav-meta">Hi, {{ user.get_username }}!</span>
        <a href="{% url 'events:logout' %}" class="btn secondary">Logout</a>
      {% else %}
        <a href="{% url 'events:login' %}" class="btn">Login</a>
        <a href="{% url 'events:signup' %}" class="btn ghost">Sign Up</a>
      {% endif %}
    </nav>
  </div>
</header>
```

### `templates/partials/_footer.html`

```html
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <p class="muted small">© 2025 NSCC — Corah</p>
      <p class="muted small"><a href="#" class="unstyled-link">Privacy</a> · <a href="#" class="unstyled-link">Terms</a></p>
    </div>
    <div class="right small muted">Built for DBAS3200 + WEBD3100</div>
  </div>
</footer>
```

### `templates/partials/_messages.html`

```html
{% if messages %}
  <div class="messages wrap">
    {% for m in messages %}
      <div class="alert {{ m.tags|default:'info' }}">{{ m }}</div>
    {% endfor %}
  </div>
{% endif %}
```

---

## 3) Update base layout

### `templates/base.html`

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{% block title %}Corah Events{% endblock %}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <!-- Tokenized CSS -->
  <link rel="stylesheet" href="{% static 'css/tokens.css' %}">
  <link rel="stylesheet" href="{% static 'css/theme-light.css' %}">
  <link rel="stylesheet" href="{% static 'css/components.css' %}">
  <link rel="stylesheet" href="{% static 'css/utilities.css' %}">
</head>
<body>
  {% include "partials/_header.html" %}
  {% include "partials/_messages.html" %}

  <main class="wrap">
    {% block content %}{% endblock %}
  </main>

  {% include "partials/_footer.html" %}
</body>
</html>
```

> **Note:** Event titles/descriptions remain unstyled where rendered (you’ve already used `|safe` without extra classes).

---

## 4) Auth templates

### `templates/auth/login.html`

```html
{% extends "base.html" %}
{% block title %}Sign In — Corah{% endblock %}
{% block content %}
<section class="form-card">
  <h2 class="mt-0">Sign In</h2>
  <form method="post" class="auth-form" action="{% url 'events:login' %}">
    {% csrf_token %}
    {{ form.non_field_errors }}
    <label for="{{ form.username.id_for_label }}"><strong>Username</strong></label>
    {{ form.username }}
    <label for="{{ form.password.id_for_label }}"><strong>Password</strong></label>
    {{ form.password }}
    <button type="submit" class="btn">Sign In</button>
    <a href="{% url 'events:signup' %}" class="btn secondary">Create Account</a>
  </form>
</section>
{% endblock %}
```

### `templates/auth/signup.html`

```html
{% extends "base.html" %}
{% block title %}Create Account — Corah{% endblock %}
{% block content %}
<section class="form-card">
  <h2 class="mt-0">Create Account</h2>
  <form method="post" class="auth-form">
    {% csrf_token %}
    {{ form.non_field_errors }}

    <label for="{{ form.username.id_for_label }}"><strong>Username</strong></label>
    {{ form.username }}

    <label for="{{ form.email.id_for_label }}"><strong>Email</strong></label>
    {{ form.email }}

    <div class="grid-2">
      <div>
        <label for="{{ form.first_name.id_for_label }}"><strong>First name</strong></label>
        {{ form.first_name }}
      </div>
      <div>
        <label for="{{ form.last_name.id_for_label }}"><strong>Last name</strong></label>
        {{ form.last_name }}
      </div>
    </div>

    <label for="{{ form.password1.id_for_label }}"><strong>Password</strong></label>
    {{ form.password1 }}

    <label for="{{ form.password2.id_for_label }}"><strong>Confirm password</strong></label>
    {{ form.password2 }}

    <button type="submit" class="btn">Create Account</button>
    <a href="{% url 'events:login' %}" class="btn secondary">Back to Sign In</a>
  </form>
</section>
{% endblock %}
```

### `templates/auth/logout.html`

```html
{% extends "base.html" %}
{% block title %}Signed Out — Corah{% endblock %}
{% block content %}
<section class="card center">
  <h2>You’ve been signed out</h2>
  <p class="mb-4 muted">Thanks for visiting. Come back soon!</p>
  <a class="btn" href="{% url 'events:login' %}">Sign In</a>
  <a class="btn secondary" href="{% url 'events:event_list' %}">Browse Events</a>
</section>
{% endblock %}
```

---

## 5) Tokenized CSS

> Keep this simple and explainable for WEBD students. Tokens first, then components, then utilities.

### `static/css/tokens.css`

```css
:root {
  /* brand seed */
  --brand-500: #7B458F;

  /* brand ramp (approx; students may refine from Figma) */
  --brand-50:  #f7f1f9;
  --brand-100: #efdef6;
  --brand-200: #e1c5ee;
  --brand-300: #cda0df;
  --brand-400: #a96fcb;
  --brand-500: #7B458F;
  --brand-600: #663974;
  --brand-700: #52305e;
  --brand-800: #41264b;
  --brand-900: #2e1c35;

  /* neutral ramp */
  --neutral-0:   #ffffff;
  --neutral-50:  #f8f9fa;
  --neutral-100: #f1f3f5;
  --neutral-200: #e9ecef;
  --neutral-300: #dee2e6;
  --neutral-400: #ced4da;
  --neutral-500: #adb5bd;
  --neutral-600: #868e96;
  --neutral-700: #495057;
  --neutral-800: #343a40;
  --neutral-900: #212529;

  /* text */
  --text:         var(--neutral-900);
  --text-muted:   var(--neutral-600);
  --bg:           var(--neutral-0);
  --card:         var(--neutral-50);
  --border:       var(--neutral-200);

  /* spacing + radius */
  --space-1: .25rem;
  --space-2: .5rem;
  --space-3: .75rem;
  --space-4: 1rem;
  --space-5: 1.5rem;
  --space-6: 2rem;

  --radius-sm: .5rem;
  --radius: .75rem;
  --radius-lg: 1rem;

  /* typography */
  --font-sans: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
  --fs-sm: .9rem;
  --fs-base: 1rem;
  --fs-md: 1.125rem;
  --fs-lg: 1.25rem;
  --fs-xl: 1.5rem;
  --fs-2xl: 2rem;

  /* states */
  --ok: #157347;
  --warn: #b58900;
  --err: #b00020;

  /* buttons */
  --btn-fg: #fff;
  --btn-bg: var(--brand-500);
  --btn-bg-hover: var(--brand-600);
  --btn-secondary-fg: var(--brand-600);
  --btn-secondary-bg: #fff;
  --btn-secondary-border: var(--brand-300);
  --btn-ghost-fg: var(--brand-600);
}
```

### `static/css/theme-light.css`

```css
@media (prefers-color-scheme: light) {
  :root {
    /* override tokens here if needed for light */
  }
}

html, body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
  font-size: var(--fs-base);
  line-height: 1.5;
  margin: 0;
}

.wrap { max-width: 72rem; margin: 0 auto; padding: 0 var(--space-4); }
.site-header { background: var(--neutral-0); border-bottom: 1px solid var(--border); }
.header-inner { display: flex; align-items: center; justify-content: space-between; padding: var(--space-3) 0; }

.brand { display: inline-flex; align-items: center; gap: var(--space-2); text-decoration: none; color: var(--text); }
.brand-mark { display: inline-grid; place-items: center; width: 28px; height: 28px; background: var(--brand-500); color: #fff; border-radius: 50%; font-size: .9rem; }
.brand-text { font-weight: 700; letter-spacing: .2px; }

.nav { display: flex; align-items: center; gap: var(--space-3); }
.nav-link { text-decoration: none; color: var(--text); }
.nav-meta { color: var(--text-muted); font-size: var(--fs-sm); }

.site-footer { margin-top: var(--space-6); padding: var(--space-4) 0; border-top: 1px solid var(--border); }
.footer-grid { display: flex; gap: var(--space-4); align-items: center; justify-content: space-between; }

.messages { margin: var(--space-3) auto; }
.alert { padding: var(--space-2) var(--space-3); border-radius: var(--radius-sm); background: var(--neutral-100); border: 1px solid var(--border); }
.alert.success { background: #e6f4ea; border-color: #c6e9d1; }
.alert.error { background: #fdeaea; border-color: #f5c2c7; }
```

### `static/css/components.css`

```css
/* links */
.unstyled-link { color: inherit; text-decoration: none; }
.unstyled-link:hover, .unstyled-link:focus-visible { text-decoration: underline; }

/* buttons */
.btn {
  appearance: none; border: 1px solid transparent; color: var(--btn-fg);
  background: var(--btn-bg); padding: .55rem .9rem; border-radius: var(--radius-sm);
  text-decoration: none; display: inline-flex; align-items: center; gap: .5rem;
}
.btn:hover, .btn:focus-visible { background: var(--btn-bg-hover); }
.btn[disabled], .btn.disabled { opacity: .6; pointer-events: none; }

.btn.secondary {
  color: var(--btn-secondary-fg); background: var(--btn-secondary-bg);
  border-color: var(--btn-secondary-border);
}
.btn.ghost {
  color: var(--btn-ghost-fg); background: transparent; border-color: transparent;
}

/* cards & grids */
.card, .form-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: var(--space-4);
}
.event-card { border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; background: var(--neutral-0); }
.event-card .body { padding: var(--space-4); }

.grid { display: grid; gap: var(--space-4); grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }
.grid-2 { display: grid; gap: var(--space-3); grid-template-columns: repeat(2, minmax(0,1fr)); }

/* meta/badges */
.meta { color: var(--text-muted); font-size: var(--fs-sm); }
.badge { display: inline-block; padding: .2rem .5rem; border-radius: 999px; border: 1px solid var(--border); }
.badge.available { background: #e6f4ea; border-color: #c6e9d1; color: #0f5132; }
.badge.full { background: #f6e7ff; border-color: #e3ccff; color: #44215f; }

/* forms */
.auth-form, form {
  display: grid; gap: .6rem;
}
input[type="text"], input[type="email"], input[type="password"],
input[type="date"], input[type="time"], input[type="number"], textarea, select {
  width: 100%; padding: .55rem .7rem; border-radius: var(--radius-sm);
  border: 1px solid var(--border); background: var(--neutral-0); color: var(--text);
}
label { color: var(--text); }
.form-error { color: var(--err); font-size: var(--fs-sm); }

/* layout helpers */
.center { text-align: center; }
.right { text-align: right; }
```

### `static/css/utilities.css`

```css
.mt-0 { margin-top: 0; }
.mt-4 { margin-top: var(--space-4); }
.mt-6 { margin-top: var(--space-6); }
.mb-0 { margin-bottom: 0; }
.mb-4 { margin-bottom: var(--space-4); }
.small { font-size: var(--fs-sm); }
.muted { color: var(--text-muted); }
```

---

## 6) Keep event title/description unstyled

You already render with:

```django
{{ e.title_html|safe }}
{{ e.description_html|safe }}
```

No extra classes around those elements. The rest of the card/layout uses your tokens/components.

---

## 7) Validation / Accessibility quick checks

* Links have clear focus states (inherited underline on focus/hover).
* Buttons have sufficient contrast (tokens ensure that).
* Labels are associated with inputs via Django forms.
* Header `<nav>` has `aria-label`.

---

## 8) Deliverables (WEBD3100 focus)

* Updated repo with `templates/partials`, `templates/auth`, and `static/css/*`.
* 3 screenshots: Header + Events grid, Login, Signup.
* Short README section: “Front-End Tokens & Components” (list what you implemented).
* Reflection (5–8 bullets): How tokens/components improved consistency; decisions about unstyled HTML fields; responsive choices.

---

## 9) Mini-Rubric (WEBD3100 slice)

| Area                 | A                                          | B                           | C                              |
| -------------------- | ------------------------------------------ | --------------------------- | ------------------------------ |
| Tokens & Components  | Cohesive system, applied consistently      | Mostly consistent           | Fragmented styles              |
| Partials & Structure | Clean includes; DRY header/footer/messages | Minor duplication           | Repetition; partials underused |
| Accessibility        | Clear focus, labels, contrast              | Minor issues                | Multiple gaps                  |
| Visual Quality       | Polished, on-brand                         | Good with minor rough edges | Inconsistent or unbalanced     |
