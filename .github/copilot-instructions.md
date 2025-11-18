# ChorePoints AI Agent Instructions — Master Reference

## 🎯 Agent Behavior Framework

### Autonomous Execution Protocol
**CRITICAL**: When assigned a task, agents must:
1. **Plan completely** before starting implementation - break down into atomic subtasks
2. **Execute iteratively** - complete each subtask fully before moving to next
3. **Continue autonomously** until ALL planned tasks are 100% complete
4. **Never ask user to continue** - save prompts by working through entire plan
5. **Validate continuously** - test after each significant change with local dev server
6. **Document decisions** - explain non-obvious choices inline in code comments

### Task Planning Methodology
For ANY non-trivial task:
- Break into atomic, testable subtasks (max 15 minutes each)
- Identify dependencies and sequence properly (database → models → views → templates → tests)
- Plan validation steps for each subtask (migrate, runserver, manual testing)
- Estimate completion realistically (complex features = 60-120 min total)
- Commit to completing ALL subtasks in single session without interruption

### Expert Knowledge Domains
Agents working on this project must demonstrate **genius-level expertise** in:
- **Python/Django**: Advanced ORM, migrations, signals, middleware, custom managers, atomic transactions, querysets
- **Azure Cloud**: App Service (Linux), PostgreSQL Flexible Server, Blob Storage, networking, scaling, cost optimization
- **DevOps**: GitHub Actions workflows, CI/CD pipelines, zero-downtime deployments, rollback strategies, secrets management
- **Database**: PostgreSQL 15 tuning, indexing strategies, transaction isolation, connection pooling, backup/restore
- **Frontend**: Progressive enhancement, ARIA accessibility, responsive CSS, minimal JavaScript, server-side rendering
- **Security**: OWASP Top 10, Django security hardening, session management, CSRF/XSS prevention, secure cookies
- **Performance**: Query optimization, N+1 problem prevention, caching strategies, CDN, lazy loading, image optimization
- **Testing**: Unit tests with Django TestCase/pytest, integration tests, manual E2E testing, test coverage

## 📋 Project Overview

**ChorePoints (Taškų Nuotykis)** - Production Django 5.x app for managing kids' chores & rewards with gamified achievement system.

### Core Features
- **Kids login with PIN** (session-based, no Django User model for kids)
- **Chores submission** → pending approval workflow → points awarded
- **Rewards redemption** → pending approval → points deducted
- **Achievement milestones** with bonus points (Bronze 🥉 → Legend 🔥)
- **Adventure map** with progress tracking and theme customization (Island/Space/Rainbow)
- **Parent admin** for approval workflow, point adjustments, kid management
- **Lithuanian-first UI** for kids (Sveikas/Sveika greetings, Lithuanian strings)
- **Confetti animations** on approval, milestone unlocks, new affordable rewards

### Architecture Summary
- **Single Django app**: `core/` contains all models, views, admin, templates
- **Session-based auth**: Kids authenticated via `request.session["kid_id"]`
- **Atomic transactions**: All balance mutations use `transaction.atomic()`
- **Approval workflow**: PENDING → APPROVED/REJECTED via admin actions
- **Image optimization**: Auto-resize on save (400x400 avatars, 128x128 icons)
- **Lithuanian localization**: Hardcoded strings (no .po files), LANGUAGE_CODE='lt'

## 🚀 Production Environment (Azure)

**CRITICAL**: Live production app at **https://elija-agota.azurewebsites.net/**

### Azure Infrastructure
| Resource | Details |
|----------|---------|
| **App Service** | `elija-agota` (B1 Basic, Linux, Python 3.11) |
| **App Service Plan** | `chorepoints-plan` (B1, 1 worker, North Central US) |
| **PostgreSQL** | `chorepoints-db` (Flexible Server v15, Standard_B1ms Burstable, 32GB, 120 IOPS) |
| **Storage Account** | `chorepointsstorage` (StorageV2, Standard_LRS, Hot tier) |
| **Containers** | `static/` (blob public), `media/` (blob public), `backups/` (private) |
| **Resource Group** | `chorepoints-rg-us` (North Central US region) |
| **Domain** | `elija-agota.azurewebsites.net` (HTTPS only, TLS 1.2+) |

### Production Configuration
```python
# settings_production.py (key settings)
DEBUG = False
ALLOWED_HOSTS = ['elija-agota.azurewebsites.net', '*.azurewebsites.net']
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.environ['DB_NAME'],
    'USER': os.environ['DB_USER'],
    'PASSWORD': os.environ['DB_PASSWORD'],
    'HOST': os.environ['DB_HOST'],  # chorepoints-db.postgres.database.azure.com
    'PORT': '5432',
    'OPTIONS': {'sslmode': 'require'},
}
STATICFILES_STORAGE = 'chorepoints.storage_backends.AzureStaticStorage'
DEFAULT_FILE_STORAGE = 'chorepoints.storage_backends.AzureMediaStorage'
STATIC_URL = 'https://chorepointsstorage.blob.core.windows.net/static/'
MEDIA_URL = 'https://chorepointsstorage.blob.core.windows.net/media/'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
```

### Environment Variables (Production)
Set in Azure App Service > Configuration > Application settings:
- `DJANGO_SETTINGS_MODULE=chorepoints.settings_production`
- `DJANGO_SECRET_KEY=<secret>` (never commit to repo)
- `DB_NAME=chorepoints` (PostgreSQL database name)
- `DB_USER=chorepoints_admin` (PostgreSQL admin user)
- `DB_PASSWORD=<secret>` (never commit to repo)
- `DB_HOST=chorepoints-db.postgres.database.azure.com`
- `AZURE_ACCOUNT_NAME=chorepointsstorage`
- `AZURE_ACCOUNT_KEY=<secret>` (storage access key, never commit)
- `WEBSITE_HOSTNAME=elija-agota.azurewebsites.net` (auto-set by Azure)

### Deployment Pipeline (GitHub Actions)

**Workflow**: `.github/workflows/deploy.yml`

```yaml
# Triggers: push to main, PR to main, manual dispatch
# Steps:
1. Checkout source
2. Setup Python 3.11
3. Install dependencies (pip install -r requirements.txt)
4. Run unit tests (pytest core/tests, continue-on-error: true)
5. Archive application (zip chorepoints/ excluding __pycache__, *.pyc)
6. Azure login (AZURE_CREDENTIALS secret)
7. Deploy to Azure Web App (azure/webapps-deploy@v3, slot: Production)
8. Startup command: "bash startup.sh"
9. Azure logout
```

**startup.sh** (runs on Azure App Service startup):
```bash
pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --noinput  # Upload to Azure Blob
python manage.py migrate --noinput        # Apply DB migrations
gunicorn chorepoints.wsgi:application --bind=0.0.0.0:8000 --workers=2 --threads=4 --timeout=120
```

**Deployment time**: ~2-3 minutes from merge to live

### Azure Management Commands

**CRITICAL**: Never attempt to run `az webapp ssh` automatically. Always instruct user to run SSH commands manually.

**Agent can run** (non-SSH):
```bash
# Restart app (useful after config changes)
az webapp restart --name elija-agota --resource-group chorepoints-rg-us

# Stream logs (for debugging deployment issues)
az webapp log tail --name elija-agota --resource-group chorepoints-rg-us

# Show app status
az webapp show --name elija-agota --resource-group chorepoints-rg-us --query "state"

# List configuration (no sensitive values)
az webapp config appsettings list --name elija-agota --resource-group chorepoints-rg-us --query "[].name"
```

**User must run manually** (SSH required):
```bash
# SSH into production container
az webapp ssh --name elija-agota --resource-group chorepoints-rg-us

# Inside SSH session:
cd /home/site/wwwroot
python manage.py migrate core                    # Apply new migrations
python manage.py load_initial_data               # Reload CSV data
python manage.py createsuperuser                 # Create admin account
python manage.py shell                           # Interactive Python shell
python manage.py dbshell                         # PostgreSQL psql shell
```

### Production Users
- **Parent**: `tevai` (admin account, password stored securely, NOT in repo)
- **Kids**: 
  - Elija (M, PIN: 1234, Theme: ISLAND, Gender: M)
  - Agota (F, PIN: 1234, Theme: SPACE, Gender: F)
- **Admin URL**: https://elija-agota.azurewebsites.net/admin/
- **Kid Login**: https://elija-agota.azurewebsites.net/kid/login/

## 🏗️ Architecture & Technical Patterns

### Core Domain Models (`core/models.py`)

#### Kid Model
```python
class Kid(models.Model):
    parent = ForeignKey(User)                    # Parent who manages this kid
    name = CharField(max_length=100)
    gender = CharField(choices=Gender.choices)   # M/F/O for Lithuanian greetings
    pin = CharField(max_length=20)               # Plaintext (MVP limitation)
    points_balance = IntegerField(default=0)     # Spendable points
    map_position = IntegerField(default=0)       # Total lifetime points (for milestones)
    highest_milestone = IntegerField(default=0)  # Track milestone progress
    avatar_emoji = CharField(max_length=4)       # Optional emoji avatar
    photo = ImageField(upload_to="kid_avatars/") # Auto-resized to 400x400
    map_theme = CharField(choices=MapTheme)      # ISLAND/SPACE/RAINBOW
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Resize photo after save to get file path
        if self.photo and Image:
            with Image.open(Path(self.photo.path)) as img:
                if img.width > 400 or img.height > 400:
                    img.thumbnail((400, 400))
                    img.save(Path(self.photo.path))
    
    def get_greeting(self) -> str:
        """Gender-specific Lithuanian greeting"""
        return f"Sveika, {self.name}!" if self.gender == "F" else f"Sveikas, {self.name}!"
    
    def get_map_progress(self) -> dict:
        """Calculate milestone progress and achievement status"""
        # Returns: current_milestone, next_milestone, progress_percentage, milestones list
```

**Achievement Milestones** (infinite progression):
```python
ACHIEVEMENT_MILESTONES = [
    {'position': 50, 'name': 'Bronzos ženkliukas', 'icon': '🥉', 'bonus': 10},
    {'position': 100, 'name': 'Sidabro ženkliukas', 'icon': '🥈', 'bonus': 10},
    {'position': 200, 'name': 'Aukso ženkliukas', 'icon': '🥇', 'bonus': 15},
    # ... up to position 3000
    # After 3000: bonus every 500 points (50 pts each)
]
```

#### Chore/Reward Models
```python
class Chore(models.Model):
    parent = ForeignKey(User)
    title = CharField(max_length=200)
    points = IntegerField(default=1)
    active = BooleanField(default=True)
    icon_emoji = CharField(max_length=8)               # Optional emoji
    icon_image = ImageField(upload_to="chore_icons/")  # Auto-resized to 128x128
    
    @property
    def display_icon(self):
        return self.icon_emoji or "🧹"  # Default icon

class Reward(models.Model):
    # Similar structure, cost_points instead of points
    cost_points = IntegerField(default=5)
```

#### Approval Workflow Models
```python
class ChoreLog(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Laukia"
        APPROVED = "APPROVED", "Patvirtinta"
        REJECTED = "REJECTED", "Atmesta"
    
    child = ForeignKey(Kid)
    chore = ForeignKey(Chore, on_delete=PROTECT)  # Prevent deletion of used chores
    points_awarded = IntegerField()
    status = CharField(choices=Status.choices, default=Status.PENDING)
    logged_at = DateTimeField(auto_now_add=True)
    processed_at = DateTimeField(null=True, blank=True)
    
    def approve(self):
        """Atomically approve and award points (with milestone bonuses)"""
        if self.status != self.Status.PENDING:
            return False
        with transaction.atomic():
            self.child.refresh_from_db()  # Prevent race conditions
            old_position = self.child.map_position
            self.child.points_balance += self.points_awarded
            self.child.map_position += self.points_awarded
            
            # Check for milestone crossings and award bonuses
            milestones_crossed = [m for m in ACHIEVEMENT_MILESTONES 
                                  if old_position < m['position'] <= self.child.map_position]
            for milestone in milestones_crossed:
                self.child.points_balance += milestone['bonus']
                self.child.map_position += milestone['bonus']
                self.child.highest_milestone = milestone['position']
            
            self.child.save(update_fields=["points_balance", "map_position", "highest_milestone"])
            self.status = self.Status.APPROVED
            self.processed_at = timezone.now()
            self.save(update_fields=["status", "processed_at"])
        return True
    
    def reject(self):
        """Reject without awarding points"""
        if self.status != self.Status.PENDING:
            return False
        self.status = self.Status.REJECTED
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "processed_at"])
        return True

class Redemption(models.Model):
    # Similar structure for reward redemptions
    def approve(self):
        """Atomically approve and deduct points (check sufficient balance)"""
        with transaction.atomic():
            self.child.refresh_from_db()
            if self.child.points_balance < self.cost_points:
                return False  # Insufficient points
            self.child.points_balance -= self.cost_points
            self.child.save(update_fields=["points_balance"])
            # ... set status to APPROVED
```

#### Point Adjustments
```python
class PointAdjustment(models.Model):
    parent = ForeignKey(User)
    kid = ForeignKey(Kid)
    points = IntegerField()  # Positive = add, negative = deduct
    reason = CharField(max_length=255)  # Shown to kid
    created_at = DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            # Apply adjustment as side effect (with milestone checks)
            self.kid.points_balance += self.points
            if self.points > 0:
                self.kid.map_position += self.points
                # Check milestones and award bonuses...
            self.kid.save()
```

### View Patterns (`core/views.py`)

#### Session-Based Kid Authentication
```python
def _get_kid(request):
    """Helper to get authenticated kid from session"""
    kid_id = request.session.get("kid_id")
    if not kid_id:
        return None
    return get_object_or_404(Kid, pk=kid_id, active=True)

def kid_login(request):
    if request.method == "POST":
        kid = form.cleaned_data["kid"]
        pin = form.cleaned_data["pin"]
        if kid.active and kid.pin == pin:  # Plaintext comparison
            request.session["kid_id"] = kid.id
            messages.success(request, kid.get_greeting())
            return redirect("kid_home")
    # ...

def kid_home(request):
    kid = _get_kid(request)
    if not kid:
        return redirect("kid_login")
    # Load chores, rewards, pending items, approved history
    # Detect confetti trigger, milestone unlocks, newly affordable rewards
    # Track session state: last_seen_approval_ts, last_seen_map_position, last_seen_balance
```

#### Approval Workflow Pattern
```python
def complete_chore(request, chore_id):
    kid = _get_kid(request)
    chore = get_object_or_404(Chore, pk=chore_id, parent=kid.parent, active=True)
    
    # Prevent duplicate PENDING submissions
    if ChoreLog.objects.filter(child=kid, chore=chore, status=ChoreLog.Status.PENDING).exists():
        messages.info(request, "Šis darbas jau laukia patvirtinimo.")
        return redirect("kid_home")
    
    # Create PENDING log (no immediate balance change)
    ChoreLog.objects.create(child=kid, chore=chore, points_awarded=chore.points)
    messages.success(request, f"Pateikta patvirtinimui: '{chore.title}' (+{chore.points} tšk)")
    return redirect("kid_home")

def redeem_reward(request, reward_id):
    # Similar pattern: create PENDING redemption, check for duplicates
```

### Admin Interface (`core/admin.py`)

```python
@admin.register(ChoreLog)
class ChoreLogAdmin(admin.ModelAdmin):
    list_display = ("child", "chore", "points_awarded", "status", "logged_at", "processed_at")
    list_filter = ("child", "chore", "status")
    actions = ["approve_selected", "reject_selected"]
    
    def approve_selected(self, request, queryset):
        """Bulk approve pending chore logs"""
        count = 0
        for log in queryset:
            if log.approve():  # Calls model method with atomic transaction
                count += 1
        self.message_user(request, f"Patvirtinta {count} darbų įrašų.")
    approve_selected.short_description = "Patvirtinti pasirinktus laukiančius darbus"
```

### Frontend Patterns

#### Confetti Animation Trigger
Session tracking for "new approvals since last visit":
```python
# In kid_home view:
last_seen_iso = request.session.get("last_seen_approval_ts")
if last_seen_iso:
    last_seen_dt = timezone.datetime.fromisoformat(last_seen_iso)
    new_approved_logs = kid.chore_logs.filter(
        status=ChoreLog.Status.APPROVED, 
        processed_at__gt=last_seen_dt
    ).exists()
    approved_new = new_approved_logs  # Trigger confetti in template
request.session["last_seen_approval_ts"] = timezone.now().isoformat()
```

#### Milestone Unlock Detection
```python
last_seen_map_position = request.session.get("last_seen_map_position", 0)
milestone_unlocked = kid.map_position > last_seen_map_position
if milestone_unlocked:
    newly_unlocked_milestones = [m for m in ACHIEVEMENT_MILESTONES 
                                  if last_seen_map_position < m['position'] <= kid.map_position]
request.session["last_seen_map_position"] = kid.map_position
# Pass to template for animation
```

#### Progressive Enhancement
- **Server-side rendering** (no SPA framework)
- **Minimal JavaScript** (confetti canvas animation, avatar selection, toast notifications)
- **Forms submit via POST** (no AJAX, full page refresh)
- **ARIA labels** for accessibility (screen readers, keyboard navigation)
- **Responsive CSS** (mobile-first, tested on tablets/phones)

## 💻 Development Workflow

### Branch Strategy & PR Workflow

**CRITICAL**: AI agents must NEVER push directly to `main` branch

**Agent workflow for ALL changes**:
1. **Create feature branch**: `git checkout -b feature/descriptive-name`
2. **Make changes**: Edit files, add tests
3. **Test locally**: Run `./chorepoints/dev.ps1` and verify on http://localhost:8000
4. **Commit to feature branch**: `git add . && git commit -m "Descriptive message"`
5. **Push feature branch**: `git push origin feature/descriptive-name`
6. **Create PR**: `gh pr create --title "..." --body "..." --base main`
7. **STOP HERE** - User reviews, approves, and merges PR
8. **Auto-deployment**: GitHub Actions deploys to Azure (~2-3 min)
9. **User runs post-deployment commands** (if needed): SSH to Azure, run migrations/data loads

**Never perform these actions**:
- ❌ `git push origin main` (direct push to main)
- ❌ `git merge feature-branch` while on main branch
- ❌ Auto-merging PRs without user approval
- ❌ Running `az webapp ssh` automatically (always instruct user)

### Local Development Setup

**Quick Start** (Windows PowerShell):
```powershell
cd chorepoints
./dev.ps1          # Auto: create venv, install deps, migrate, runserver, open browser
./dev.ps1 -Reset   # Recreate venv from scratch (if dependencies broken)
./run.ps1          # Fast start: activate venv + runserver (if already setup)
```

**dev.ps1 features**:
- Creates `.venv/` virtual environment
- Installs `requirements.txt` (caches hash to skip reinstalls)
- Runs `python manage.py migrate`
- Starts `python manage.py runserver`
- Opens `http://localhost:8000` in default browser

**Manual setup**:
```bash
cd chorepoints
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo_lt --username <your_username>
python manage.py runserver
```

### Essential Management Commands

```bash
# Seed demo data (Elija, Agota, default chores/rewards)
python manage.py seed_demo_lt --username tevai

# Load production-like data from CSV
python manage.py load_initial_data

# Create migrations after model changes
python manage.py makemigrations core

# Apply migrations
python manage.py migrate core

# Show migration status
python manage.py showmigrations core

# Create superuser (parent account)
python manage.py createsuperuser

# Interactive shell with ORM access
python manage.py shell

# Database shell (PostgreSQL psql in production, SQLite in dev)
python manage.py dbshell

# Collect static files (dev: no-op, production: uploads to Azure Blob)
python manage.py collectstatic --noinput
```

### Testing Strategy

**Current state**: Test files exist but need implementation (MVP phase)

**Testing approach**:
1. **Unit tests** (`core/tests/test_*.py`):
   - Model methods: `approve()`, `reject()`, milestone calculations
   - Form validation: PIN length, duplicate prevention
   - View helpers: `_get_kid()`, session handling
   - Files: test_models.py, test_views.py, test_forms.py, test_integration.py, test_security.py, test_performance.py, test_error_handling.py

2. **Integration tests**:
   - Approval workflow: create PENDING → approve → verify balance
   - Milestone bonuses: cross threshold → verify bonus awarded
   - Duplicate prevention: submit same chore twice → verify one PENDING

3. **Manual E2E testing** (no automation yet):
   - Kid login flow: select kid → enter PIN → land on home
   - Chore submission: click chore → verify PENDING badge
   - Parent approval: admin login → approve chore → verify kid sees confetti
   - Milestone unlock: approve chores → cross 50 pts → verify Bronze badge

**Running tests**:
```bash
# Unit tests (Django's test runner)
python manage.py test core

# OR with pytest
pip install pytest pytest-django
pytest core/tests

# Run specific test file
python manage.py test core.tests.test_models

# Manual testing: run dev server
./dev.ps1  # Opens http://localhost:8000
```

### Data Migrations & CSV Management

**Initial data loading** (migration 0011):
- Loads chores (19 items) from `chorepoints/initial_data/chores.csv`
- Loads rewards (21 items) from `chorepoints/initial_data/rewards.csv`
- Safe to run multiple times (uses `get_or_create`)

**CSV format** (chores.csv):
```csv
Pavalyti kambarį,5,🧹,Sutvarkyti žaislus ir sukrauti lovą
Išnešti šiukšles,3,🗑️,Išnešti šiukšlių maišą į konteinerį
# ... 17 more
```

**Updating CSV data in production**:
1. Edit `chorepoints/initial_data/chores.csv` or `rewards.csv` locally
2. Test with `python manage.py load_initial_data` (creates/updates chores)
3. Commit to feature branch: `git add chorepoints/initial_data/*.csv`
4. Push and create PR (user merges → auto-deploys)
5. **User must SSH and reload**:
   ```bash
   az webapp ssh --name elija-agota --resource-group chorepoints-rg-us
   cd /home/site/wwwroot
   python manage.py load_initial_data  # Reloads CSV into PostgreSQL
   ```

### File Structure & Conventions

```
django_kid_rewards/                    # Repo root
├── .github/
│   ├── workflows/deploy.yml           # GitHub Actions CI/CD
│   └── copilot-instructions.md        # This file (agent instructions)
├── chorepoints/                       # Django project root
│   ├── chorepoints/                   # Project settings
│   │   ├── settings.py                # Dev settings (SQLite, DEBUG=True)
│   │   ├── settings_production.py     # Prod settings (PostgreSQL, Azure Blob)
│   │   ├── storage_backends.py        # AzureStaticStorage, AzureMediaStorage
│   │   ├── urls.py                    # Root URL config
│   │   └── wsgi.py                    # WSGI entry point (Gunicorn)
│   ├── core/                          # Single Django app
│   │   ├── models.py                  # Kid, Chore, Reward, ChoreLog, Redemption, PointAdjustment
│   │   ├── views.py                   # kid_login, kid_home, complete_chore, redeem_reward
│   │   ├── admin.py                   # Admin interface with approval actions
│   │   ├── forms.py                   # KidLoginForm, ChangePinForm
│   │   ├── urls.py                    # URL patterns for /kid/
│   │   ├── templates/                 # Django templates
│   │   │   ├── base.html              # Base layout with CSS/JS
│   │   │   ├── index.html             # Landing page
│   │   │   └── kid/
│   │   │       ├── login.html         # Kid PIN login
│   │   │       ├── home.html          # Kid dashboard (chores, rewards, map)
│   │   │       └── change_pin.html    # Kid PIN change form
│   │   ├── management/commands/
│   │   │   ├── seed_demo_lt.py        # Seed Elija/Agota demo data
│   │   │   └── load_initial_data.py   # Load chores/rewards from CSV
│   │   ├── migrations/                # Django migrations (0001-0012)
│   │   └── tests/                     # Unit/integration tests (placeholder)
│   ├── initial_data/
│   │   ├── chores.csv                 # Default chores (19 items)
│   │   ├── rewards.csv                # Default rewards (21 items)
│   │   └── README.md                  # CSV format documentation
│   ├── media/                         # User uploads (kid avatars, chore/reward icons)
│   │   └── kid_avatars/               # Auto-resized to 400x400
│   ├── staticfiles/                   # collectstatic output (gitignored)
│   ├── .venv/                         # Python virtual environment (gitignored)
│   ├── db.sqlite3                     # Dev database (gitignored)
│   ├── requirements.txt               # Python dependencies
│   ├── startup.sh                     # Azure startup script (Gunicorn)
│   ├── dev.ps1                        # Dev environment setup script
│   └── run.ps1                        # Fast dev server start
├── AGENTS.md                          # Agent-specific documentation
├── .gitignore                         # Exclude .venv, db.sqlite3, media, staticfiles
└── README.md                          # Project documentation
```

### Dependencies (`requirements.txt`)

**Core**:
- Django>=5.0,<5.3
- Pillow>=10.4,<11.0 (image processing)
- django-extensions>=3.2,<4.0 (runserver_plus for HTTPS dev)
- werkzeug>=3.0,<4.0 (dev server utilities)
- pyOpenSSL>=24.0,<25.0 (HTTPS dev certificates)

**Production**:
- gunicorn>=21.0,<22.0 (WSGI server)
- psycopg2-binary>=2.9,<3.0 (PostgreSQL adapter)
- django-storages[azure]>=1.14,<2.0 (Azure Blob Storage backend)
- whitenoise>=6.6,<7.0 (static file serving fallback)
- python-decouple>=3.8,<4.0 (environment variable parsing)

## 🔒 Security Best Practices

### Production Security Checklist
- ✅ `DEBUG=False` (no error pages with tracebacks)
- ✅ `SECRET_KEY` from environment variable (never committed)
- ✅ `ALLOWED_HOSTS` restricted to production domain
- ✅ `SECURE_SSL_REDIRECT=True` (HTTPS only)
- ✅ `SESSION_COOKIE_SECURE=True` (HTTPS only)
- ✅ `CSRF_COOKIE_SECURE=True` (HTTPS only)
- ✅ `SESSION_EXPIRE_AT_BROWSER_CLOSE=True` (force re-login)
- ✅ `SESSION_COOKIE_AGE=3600` (1 hour timeout)
- ✅ PostgreSQL SSL required (`sslmode=require`)
- ✅ TLS 1.2+ enforced (Azure App Service)
- ✅ Azure Blob public access = blob level only (not container)
- ✅ Passwords never committed (use Azure App Settings)

### Known Security Limitations (MVP)
- ⚠️ **Kid PINs stored plaintext** (no hashing) - acceptable for MVP, document for future improvement
- ⚠️ **No rate limiting** on chore submissions - could add throttling in future
- ⚠️ **No PENDING duplicate constraint** at DB level - enforced in views only
- ⚠️ **No 2FA for parent admin** - relies on Django admin password

### OWASP Top 10 Mitigations
1. **Injection**: Django ORM (parameterized queries), no raw SQL
2. **Broken Auth**: Session-based auth, secure cookies, expiration
3. **Sensitive Data**: Env vars for secrets, HTTPS, SSL to DB
4. **XML External Entities**: N/A (no XML parsing)
5. **Broken Access Control**: `_get_kid()` checks, `on_delete=PROTECT`
6. **Security Misconfiguration**: Production settings separate, DEBUG=False
7. **XSS**: Django auto-escapes templates, `mark_safe` only for admin icons
8. **Insecure Deserialization**: No pickle/yaml, only JSON for session data
9. **Using Components with Known Vulnerabilities**: Dependabot enabled, regular updates
10. **Insufficient Logging**: Azure App Service logs, Gunicorn access/error logs

## 🚀 DevOps & Deployment

### CI/CD Pipeline Details

**GitHub Actions Workflow** (`.github/workflows/deploy.yml`):
- **Triggers**: Push to main, PR to main, manual workflow_dispatch
- **Environment**: Ubuntu-latest, Python 3.11
- **Steps**:
  1. Checkout repository
  2. Setup Python and install dependencies
  3. Run unit tests (continue-on-error for now)
  4. Zip application (exclude cache files)
  5. Azure login via service principal (AZURE_CREDENTIALS secret)
  6. Deploy to App Service (slot: Production, startup: bash startup.sh)
  7. Azure logout

**Secrets** (GitHub repo settings > Secrets):
- `AZURE_CREDENTIALS`: Service principal JSON (`{"clientId": ..., "clientSecret": ..., "subscriptionId": ..., "tenantId": ...}`)
- `AZURE_WEBAPP_NAME`: Variable set to `elija-agota`

**Deployment slots**: Currently using Production slot only (no staging slot for cost optimization)

### Zero-Downtime Deployment Strategy
1. GitHub Actions uploads new code as zip to Azure App Service
2. Azure unpacks zip to `/home/site/wwwroot`
3. `startup.sh` runs: install deps, collectstatic, migrate, start Gunicorn
4. Azure swaps traffic to new Gunicorn workers (graceful restart)
5. Old workers drain connections (~30 sec timeout)

**Rollback strategy**:
- Revert PR merge in GitHub (creates new commit)
- Push to main triggers new deployment with previous code
- OR: Use Azure Portal > Deployment Center > Redeploy previous version

### Performance Optimization

**Database**:
- PostgreSQL connection pooling (Gunicorn workers reuse connections)
- Indexing on foreign keys (Django auto-creates)
- `select_related()` for single-valued FK (Kid.parent, ChoreLog.child)
- `prefetch_related()` for reverse FK (kid.chore_logs)
- Avoid N+1 queries (use `queryset.count()` instead of `len()`)

**Static/Media Files**:
- Azure Blob Storage CDN (fast global delivery)
- `collectstatic` uploads to blob container (public read access)
- Image optimization: Pillow auto-resize (400x400, 128x128)
- WhiteNoise fallback for static files (if blob unavailable)

**Caching** (future):
- Django cache framework (Redis on Azure Cache for Redis)
- Cache kid home page data (chores, rewards list)
- Cache milestone calculations (expensive for high positions)

**Monitoring** (future):
- Application Insights (Azure monitoring, log analytics)
- Custom metrics: approval rate, milestone unlock rate, session duration
- Alerts: high error rate, slow response times, DB connection pool exhaustion

### Cost Optimization

**Current monthly cost** (~$25-30 USD):
- App Service Plan B1: ~$13/month (1 core, 1.75 GB RAM)
- PostgreSQL B1ms: ~$12/month (1 vCore, 2 GB RAM, 32 GB storage)
- Blob Storage Standard_LRS: ~$1-2/month (Hot tier, minimal usage)

**Cost reduction strategies**:
1. **Stop app when not in use** (dev/test periods):
   ```bash
   az webapp stop --name elija-agota --resource-group chorepoints-rg-us
   az webapp start --name elija-agota --resource-group chorepoints-rg-us
   ```
2. **Use Free tier for testing** (separate test resource group):
   - App Service Free F1: Free (60 min/day limit)
   - Azure Database for PostgreSQL Single Server Burstable B1ms: ~$12/month
3. **Scheduled scaling** (Azure Automation Runbooks):
   - Scale down to Free/Shared tier during nights/weekends
   - Scale up to B1 during peak usage hours

### Backup & Disaster Recovery

**Database backups** (automated):
- PostgreSQL Flexible Server: 7-day retention (automatic backups)
- Point-in-time restore available (restore to any point in last 7 days)
- Manual backup: `az postgres flexible-server backup create`

**Media file backups** (manual):
- Azure Blob Storage snapshots (create snapshot of media container)
- Download backups locally: `az storage blob download-batch`

**Application code backup**:
- GitHub repository (primary source of truth)
- Azure App Service maintains deployment history (last 50 deployments)

**Disaster recovery plan**:
1. Restore PostgreSQL database from backup
2. Redeploy application from GitHub (latest main or specific commit)
3. Restore media files from blob snapshot (if needed)
4. Verify data integrity (check kid balances, pending approvals)

## 🌐 Lithuanian Localization

### Language Settings
```python
# settings.py
LANGUAGE_CODE = 'lt'
TIME_ZONE = 'Europe/Vilnius'
USE_I18N = True
USE_L10N = True  # Localized number/date formatting
USE_TZ = True    # Timezone-aware datetimes

LANGUAGES = [
    ('lt', 'Lietuvių'),
    ('en', 'English'),
]
```

### Localization Strategy
**Current approach**: Hardcoded Lithuanian strings (no .po files)
- Kid-facing UI: 100% Lithuanian (buttons, messages, field labels)
- Admin interface: English (Django default)
- Model verbose names: Lithuanian (`verbose_name = "Vaikas"`)
- Admin action descriptions: Lithuanian (`approve_selected.short_description = "Patvirtinti..."`)

**Gender-specific greetings**:
```python
def get_greeting(self) -> str:
    if self.gender == self.Gender.FEMALE:
        return f"Sveika, {self.name}!"  # Feminine
    else:
        return f"Sveikas, {self.name}!"  # Masculine (default)
```

**Future internationalization** (if English support needed):
1. Extract strings to .po files: `python manage.py makemessages -l en`
2. Translate strings in `locale/en/LC_MESSAGES/django.po`
3. Compile: `python manage.py compilemessages`
4. Use `{% trans %}` and `{% blocktrans %}` in templates

## 📝 Code Style & Conventions

### Python Style (PEP 8)
- **Indentation**: 4 spaces (no tabs)
- **Line length**: 100 characters (Django convention)
- **Imports**: Standard library → third-party → local, alphabetical within groups
- **Naming**:
  - Classes: PascalCase (`Kid`, `ChoreLog`)
  - Functions/methods: snake_case (`complete_chore`, `get_greeting`)
  - Constants: UPPER_SNAKE_CASE (`ACHIEVEMENT_MILESTONES`)
  - Private: Leading underscore (`_get_kid`)

**Linting** (future):
```bash
pip install black flake8 isort
black chorepoints/core/  # Auto-format
flake8 chorepoints/core/  # Check style
isort chorepoints/core/  # Sort imports
```

### Django Patterns
- **Fat models, thin views**: Business logic in model methods
- **Atomic transactions**: Wrap balance mutations in `transaction.atomic()`
- **F() expressions**: For atomic updates (e.g., `Kid.objects.filter(id=kid_id).update(points_balance=F('points_balance') + points)`)
- **select_related/prefetch_related**: Optimize queries
- **get_object_or_404**: Fail gracefully with 404 instead of 500

### Template Conventions
- **Indentation**: 2 spaces
- **Template tags**: `{% load static %}` at top
- **Comments**: `{# Comment #}` for single-line, `{% comment %}...{% endcomment %}` for multi-line
- **Variables**: `{{ kid.name }}` (auto-escaped), `{{ kid.photo.url|safe }}` if needed
- **Filters**: `{{ kid.created_at|date:"Y-m-d" }}` (Lithuanian format: "2025-11-19")

### JavaScript Conventions
- **Minimal JS**: Only for animations, no business logic
- **ES6+**: Use modern syntax (const, let, arrow functions, template literals)
- **No frameworks**: Vanilla JS only (no React/Vue/Angular)
- **Progressive enhancement**: Ensure functionality without JS (forms still submit)

### Git Commit Messages
```
[scope] Short description (50 chars)

Longer explanation (wrap at 72 chars):
- Why this change is needed
- What behavior changes
- Any migration steps required

Fixes #123 (if applicable)
```

**Examples**:
```
[models] Add milestone bonus logic to ChoreLog.approve()

- Check for crossed milestones when approving chores
- Award bonus points for each milestone crossed
- Update highest_milestone field for kid

[views] Fix duplicate chore submission prevention

- Check for existing PENDING logs before creating new ones
- Show Lithuanian message "Šis darbas jau laukia patvirtinimo."

[deployment] Update startup.sh Gunicorn worker count

- Increase from 2 to 4 workers for better concurrency
- Add --timeout=120 to prevent worker timeouts on slow queries
```

## 🐛 Common Troubleshooting

### Local Development Issues

**Problem**: `ModuleNotFoundError: No module named 'django'`
**Solution**: Activate virtual environment and install dependencies
```powershell
cd chorepoints
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Problem**: `django.db.utils.OperationalError: no such table: core_kid`
**Solution**: Run migrations
```bash
python manage.py migrate core
```

**Problem**: Images not displaying (`/media/kid_avatars/photo.jpg` returns 404)
**Solution**: Ensure `DEBUG=True` and `MEDIA_URL/MEDIA_ROOT` configured
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# urls.py (dev only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Production Issues

**Problem**: App returns 500 after deployment
**Solution**: Check logs for traceback
```bash
az webapp log tail --name elija-agota --resource-group chorepoints-rg-us
```
Common causes:
- Missing environment variable (`DJANGO_SECRET_KEY`, `DB_PASSWORD`)
- Migration not applied (`python manage.py migrate` in SSH)
- Static files not collected (`python manage.py collectstatic` in startup.sh)

**Problem**: Static files missing (CSS not loading)
**Solution**: Verify Azure Blob Storage configuration
```python
# Check storage backends environment variables
az webapp config appsettings list --name elija-agota --resource-group chorepoints-rg-us --query "[?name=='AZURE_ACCOUNT_NAME' || name=='AZURE_ACCOUNT_KEY']"

# Test blob container public access
curl https://chorepointsstorage.blob.core.windows.net/static/admin/css/base.css
```

**Problem**: Database connection timeout
**Solution**: Check PostgreSQL firewall rules
```bash
az postgres flexible-server firewall-rule list --name chorepoints-db --resource-group chorepoints-rg-us

# Allow Azure services (if blocked)
az postgres flexible-server firewall-rule create \
  --name AllowAzureServices \
  --resource-group chorepoints-rg-us \
  --name chorepoints-db \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

**Problem**: Session expires immediately
**Solution**: Verify session settings in production
```python
# settings_production.py
SESSION_COOKIE_SECURE = True  # Must be True on HTTPS
SESSION_COOKIE_AGE = 3600     # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

### Migration Issues

**Problem**: `django.db.migrations.exceptions.InconsistentMigrationHistory`
**Solution**: Check migration history in database
```bash
python manage.py showmigrations core
# If migrations out of sync, fake to current state (DANGER: only if DB matches code)
python manage.py migrate core --fake
```

**Problem**: Data loss after migration
**Solution**: Rollback migration and restore from backup
```bash
# Rollback to previous migration
python manage.py migrate core 0011_previous_migration

# Restore database from Azure backup
az postgres flexible-server restore \
  --name chorepoints-db-restore \
  --resource-group chorepoints-rg-us \
  --source-server chorepoints-db \
  --restore-time "2025-11-19T10:00:00Z"
```

## 🎓 Learning Resources

### Django Documentation
- [Models](https://docs.djangoproject.com/en/5.0/topics/db/models/)
- [Queries](https://docs.djangoproject.com/en/5.0/topics/db/queries/)
- [Transactions](https://docs.djangoproject.com/en/5.0/topics/db/transactions/)
- [Admin](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/)
- [Security](https://docs.djangoproject.com/en/5.0/topics/security/)

### Azure Documentation
- [App Service for Linux](https://docs.microsoft.com/en-us/azure/app-service/quickstart-python)
- [PostgreSQL Flexible Server](https://docs.microsoft.com/en-us/azure/postgresql/flexible-server/)
- [Blob Storage](https://docs.microsoft.com/en-us/azure/storage/blobs/)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/)

### Best Practices
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x) (book)
- [Django Best Practices](https://learndjango.com/tutorials/django-best-practices)
- [OWASP Django Security](https://owasp.org/www-project-web-security-testing-guide/)

---

## 📋 Quick Reference Checklists

### Before Creating PR
- [ ] Tested locally with `./chorepoints/dev.ps1`
- [ ] All URLs accessible (/, /admin/, /kid/login/, /kid/home/)
- [ ] New migrations created (`python manage.py makemigrations core`)
- [ ] Migrations applied locally (`python manage.py migrate core`)
- [ ] No sensitive data committed (passwords, API keys)
- [ ] Code follows PEP 8 style (indentation, naming)
- [ ] Lithuanian strings for kid-facing UI
- [ ] Admin interface tested (if applicable)
- [ ] Duplicate prevention tested (if modifying submission views)

### After PR Merge (User Checklist)
- [ ] Monitor GitHub Actions deployment (~2-3 min)
- [ ] Verify app running: `az webapp show --name elija-agota --query "state"`
- [ ] Test production URL: https://elija-agota.azurewebsites.net/
- [ ] If migrations added: SSH and run `python manage.py migrate core`
- [ ] If CSV updated: SSH and run `python manage.py load_initial_data`
- [ ] Test kid login, chore submission, admin approval
- [ ] Check Azure logs if errors: `az webapp log tail --name elija-agota`

### Adding New Feature (Agent Checklist)
- [ ] Plan feature completely (models, views, templates, tests)
- [ ] Create feature branch: `git checkout -b feature/feature-name`
- [ ] Add model fields (if needed) and create migrations
- [ ] Implement view logic with proper error handling
- [ ] Add template with Lithuanian strings and ARIA labels
- [ ] Update admin interface (if applicable)
- [ ] Add duplicate prevention (if submission-based)
- [ ] Test locally end-to-end
- [ ] Commit, push, create PR
- [ ] STOP - wait for user to merge

---

**Last Updated**: 2025-11-19
**Agent Version**: Master Reference v2.0
**Maintainer**: AI Coding Agents (GitHub Copilot, ChatGPT, VS Code Agents)
