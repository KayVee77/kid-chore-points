# Super Prompt — Django MVP: Local Chore & Rewards (“PrivilegePoints”-style)

You are **GitHub Copilot Agent**. Generate a complete, runnable **Django** MVP (local laptop use) where:
- **Parents** manage kids, chores, and rewards using **Django Admin**.
- **Kids** log in with a simple **PIN** and:
  - mark chores as done → earn points
  - redeem rewards → spend points
- Everything persists in **SQLite** (default). Keep it simple; local-only. Minimal security is fine for this toy app.

## Stack & decisions
- Django 5.x project with one app: `core`.
- Use **Django Admin** for parent CRUD (models auto-exposed).
- Use **SQLite** (default DB, zero setup).
- Use **sessions** to track the logged-in kid (store only `kid_id`).
- Server-rendered templates (no SPA). Keep UI minimal.

---

## Create this structure

```
chorepoints/
  manage.py
  chorepoints/
    __init__.py
    settings.py
    urls.py
    wsgi.py
  core/
    __init__.py
    admin.py
    apps.py
    models.py
    urls.py
    views.py
    forms.py
    templates/
      base.html
      index.html
      kid/
        login.html
        home.html
  requirements.txt
  README.md
```

---

## requirements.txt

```
Django>=5.0
```

---

## settings.py (key bits)

- Add to `INSTALLED_APPS`:
  ```py
  "core",
  "django.contrib.admin",
  "django.contrib.auth",
  "django.contrib.contenttypes",
  "django.contrib.sessions",
  "django.contrib.messages",
  "django.contrib.staticfiles",
  ```
- Leave default **SQLite** DB configuration.
- Keep default middleware (includes sessions, auth, CSRF, messages).
- Templates/Static: defaults are fine.

---

## Models (`core/models.py`)

Define these models:

```python
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Kid(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="kids")
    name = models.CharField(max_length=100)
    pin = models.CharField(max_length=20)  # Plaintext for local MVP (OK for toy use)
    points_balance = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.parent.username})"

class Chore(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chores")
    title = models.CharField(max_length=200)
    points = models.IntegerField(default=1)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} (+{self.points} pts)"

class Reward(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rewards")
    title = models.CharField(max_length=200)
    cost_points = models.IntegerField(default=5)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} (-{self.cost_points} pts)"

class ChoreLog(models.Model):
    child = models.ForeignKey(Kid, on_delete=models.CASCADE, related_name="chore_logs")
    chore = models.ForeignKey(Chore, on_delete=models.PROTECT)
    logged_at = models.DateTimeField(auto_now_add=True)
    points_awarded = models.IntegerField()

    def save(self, *args, **kwargs):
        if self._state.adding and not self.points_awarded:
            self.points_awarded = self.chore.points
        super().save(*args, **kwargs)

class Redemption(models.Model):
    child = models.ForeignKey(Kid, on_delete=models.CASCADE, related_name="redemptions")
    reward = models.ForeignKey(Reward, on_delete=models.PROTECT)
    redeemed_at = models.DateTimeField(auto_now_add=True)
    cost_points = models.IntegerField()

    def save(self, *args, **kwargs):
        if self._state.adding and not self.cost_points:
            self.cost_points = self.reward.cost_points
        super().save(*args, **kwargs)
```

Notes:
- `Kid.pin` stored as plaintext for simplicity (local-only). For real use, hash it.
- `ChoreLog.points_awarded` and `Redemption.cost_points` copy values at the time of action.

---

## Admin (`core/admin.py`)

```python
from django.contrib import admin
from .models import Kid, Chore, Reward, ChoreLog, Redemption

@admin.register(Kid)
class KidAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "points_balance", "active", "created_at")
    list_filter = ("active", "parent")
    search_fields = ("name", "parent__username")

@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ("title", "points", "parent", "active")
    list_filter = ("active", "parent")
    search_fields = ("title",)

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ("title", "cost_points", "parent", "active")
    list_filter = ("active", "parent")
    search_fields = ("title",)

@admin.register(ChoreLog)
class ChoreLogAdmin(admin.ModelAdmin):
    list_display = ("child", "chore", "points_awarded", "logged_at")
    list_filter = ("child", "chore")

@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ("child", "reward", "cost_points", "redeemed_at")
    list_filter = ("child", "reward")
```

---

## URLs

**Project `chorepoints/urls.py`**

```python
from django.contrib import admin
from django.urls import path, include
from core.views import index

urlpatterns = [
    path("", index, name="index"),
    path("admin/", admin.site.urls),
    path("kid/", include("core.urls")),
]
```

**App `core/urls.py`**

```python
from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.kid_login, name="kid_login"),
    path("logout/", views.kid_logout, name="kid_logout"),
    path("home/", views.kid_home, name="kid_home"),
    path("chore/<int:chore_id>/complete/", views.complete_chore, name="complete_chore"),
    path("reward/<int:reward_id>/redeem/", views.redeem_reward, name="redeem_reward"),
]
```

---

## Forms (`core/forms.py`)

```python
from django import forms
from .models import Kid

class KidLoginForm(forms.Form):
    kid = forms.ModelChoiceField(queryset=Kid.objects.filter(active=True))
    pin = forms.CharField(widget=forms.PasswordInput, max_length=20)
```

---

## Views (`core/views.py`)

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from .forms import KidLoginForm
from .models import Kid, Chore, Reward, ChoreLog, Redemption

def index(request):
    return render(request, "index.html")

@require_http_methods(["GET", "POST"])
def kid_login(request):
    form = KidLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        kid = form.cleaned_data["kid"]
        pin = form.cleaned_data["pin"]
        if kid.active and kid.pin == pin:
            request.session["kid_id"] = kid.id
            messages.success(request, f"Welcome, {kid.name}!")
            return redirect("kid_home")
        messages.error(request, "Invalid PIN or inactive account.")
    return render(request, "kid/login.html", {"form": form})

def kid_logout(request):
    request.session.pop("kid_id", None)
    messages.info(request, "Logged out.")
    return redirect("kid_login")

def _get_kid(request):
    kid_id = request.session.get("kid_id")
    if not kid_id:
        return None
    return get_object_or_404(Kid, pk=kid_id, active=True)

def kid_home(request):
    kid = _get_kid(request)
    if not kid:
        return redirect("kid_login")
    chores = Chore.objects.filter(parent=kid.parent, active=True).order_by("title")
    rewards = Reward.objects.filter(parent=kid.parent, active=True).order_by("cost_points")
    return render(request, "kid/home.html", {"kid": kid, "chores": chores, "rewards": rewards})

@require_http_methods(["POST"])
def complete_chore(request, chore_id):
    kid = _get_kid(request)
    if not kid:
        return redirect("kid_login")
    chore = get_object_or_404(Chore, pk=chore_id, parent=kid.parent, active=True)
    ChoreLog.objects.create(child=kid, chore=chore, points_awarded=chore.points)
    kid.points_balance += chore.points
    kid.save(update_fields=["points_balance"])
    messages.success(request, f"Completed '{chore.title}' (+{chore.points} pts).")
    return redirect("kid_home")

@require_http_methods(["POST"])
def redeem_reward(request, reward_id):
    kid = _get_kid(request)
    if not kid:
        return redirect("kid_login")
    reward = get_object_or_404(Reward, pk=reward_id, parent=kid.parent, active=True)
    if kid.points_balance >= reward.cost_points:
        Redemption.objects.create(child=kid, reward=reward, cost_points=reward.cost_points)
        kid.points_balance -= reward.cost_points
        kid.save(update_fields=["points_balance"])
        messages.success(request, f"Redeemed '{reward.title}' (-{reward.cost_points} pts).")
    else:
        messages.error(request, "Not enough points to redeem this reward.")
    return redirect("kid_home")
```

---

## Templates

**`templates/base.html`** (super simple):
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>ChorePoints</title>
    <style>
      body { font-family: system-ui, sans-serif; margin: 2rem; }
      .btn { padding: .5rem 1rem; border: 1px solid #111; background: #f3f3f3; cursor: pointer; }
      .btn[disabled] { opacity: .5; cursor: not-allowed; }
      .card { border:1px solid #ddd; padding:1rem; margin:.5rem 0; border-radius:.5rem; }
      .row { display:flex; gap:1rem; flex-wrap:wrap; }
      .grow { flex:1 1 300px; }
      .flash { padding:.5rem 1rem; margin:.5rem 0; border-left: 4px solid #333; background:#fafafa; }
    </style>
  </head>
  <body>
    {% for msg in messages %}
      <div class="flash">{{ msg }}</div>
    {% endfor %}
    {% block content %}{% endblock %}
  </body>
</html>
```

**`templates/index.html`**
```html
{% extends "base.html" %}
{% block content %}
  <h1>ChorePoints</h1>
  <p>Local-only demo. Use the admin for parent setup.</p>
  <p>
    <a class="btn" href="{% url 'kid_login' %}">Kid Portal</a>
    <a class="btn" href="/admin/">Parent Admin</a>
  </p>
{% endblock %}
```

**`templates/kid/login.html`**
```html
{% extends "base.html" %}
{% block content %}
  <h2>Kid Login</h2>
  <form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button class="btn" type="submit">Log in</button>
  </form>
{% endblock %}
```

**`templates/kid/home.html`**
```html
{% extends "base.html" %}
{% block content %}
  <h2>Hello, {{ kid.name }}! Points: {{ kid.points_balance }}</h2>

  <div class="row">
    <div class="grow">
      <h3>Chores</h3>
      {% for chore in chores %}
        <div class="card">
          <div><strong>{{ chore.title }}</strong> (+{{ chore.points }} pts)</div>
          <form method="post" action="{% url 'complete_chore' chore.id %}">
            {% csrf_token %}
            <button class="btn" type="submit">Complete</button>
          </form>
        </div>
      {% empty %}
        <p>No chores yet.</p>
      {% endfor %}
    </div>

    <div class="grow">
      <h3>Rewards</h3>
      {% for reward in rewards %}
        <div class="card">
          <div><strong>{{ reward.title }}</strong> ({{ reward.cost_points }} pts)</div>
          <form method="post" action="{% url 'redeem_reward' reward.id %}">
            {% csrf_token %}
            <button class="btn" type="submit" {% if kid.points_balance < reward.cost_points %}disabled{% endif %}>Redeem</button>
          </form>
        </div>
      {% empty %}
        <p>No rewards yet.</p>
      {% endfor %}
    </div>
  </div>

  <p><a class="btn" href="{% url 'kid_logout' %}">Log out</a></p>
{% endblock %}
```

---

## README.md (Quickstart)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Create project & app (if not already present)
django-admin startproject chorepoints .
python manage.py startapp core

# (Paste/create files per this prompt)

python manage.py migrate
python manage.py createsuperuser  # parent admin account

# Run dev server
python manage.py runserver
```

**Admin usage**
1) Log into `/admin/` as the parent.  
2) Create **Kids** (name, PIN, parent=self).  
3) Create **Chores** (title, points, parent=self).  
4) Create **Rewards** (title, cost, parent=self).  
5) Kids go to `/kid/login/`, pick their name, enter PIN, and use `/kid/home/` to complete chores or redeem rewards.

---

## MVP Acceptance
- Parent (via Admin) can CRUD kids, chores, rewards.
- Kid can log in with PIN, complete chores (points go up), redeem rewards (points go down).
- Data persists in `db.sqlite3`. Light, local, fun.
