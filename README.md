# Taškų Nuotykis (ChorePoints)

> **Django 5 MVP** for managing kids' chores and reward points with a **Lithuanian-first UI**. Parents manage via Django Admin, kids use a fun Lithuanian interface with PIN authentication and themed adventure maps.

## 📋 Table of Contents
- [Production Environment](#-production-environment)
- [Architecture Overview](#-architecture-overview)
- [Local Development](#-local-development)
- [Data Models](#-data-models)
- [Authentication System](#-authentication-system)
- [Points & Approval Workflow](#-points--approval-workflow)
- [Adventure Map System](#-adventure-map-system)
- [Database & Migrations](#-database--migrations)
- [Deployment Process](#-deployment-process)
- [File Structure](#-file-structure)
- [Testing Strategy](#-testing-strategy)
- [Known Limitations](#-known-limitations)

## 🌐 Production Environment

### Live Application
**URL:** https://elija-agota.azurewebsites.net/

### Infrastructure Stack
- **Hosting:** Azure App Service (Linux, North Central US)
- **App Name:** `elija-agota`
- **Resource Group:** `chorepoints-rg-us`
- **Runtime:** Python 3.11 on Linux
- **Web Server:** Gunicorn (2 workers, 4 threads per worker)
- **Database:** Azure PostgreSQL Flexible Server v15 (`chorepoints-db`)
- **Storage:** Azure Blob Storage (`chorepointsstorage`, Standard_LRS)
  - Container `static/`: CSS, JS, collected static files
  - Container `media/`: User uploads (kid photos, chore/reward icons)
- **CI/CD:** GitHub Actions (auto-deploy from `main` branch)

### Security Configuration
- **HTTPS:** Enforced with secure cookies (`SECURE_SSL_REDIRECT=True`)
- **Session Security:** 1-hour timeout, expires on browser close, HttpOnly cookies
- **CSRF Protection:** Django middleware + SameSite=Lax cookies
- **Database:** SSL required (`sslmode=require`)
- **Secrets Management:** Environment variables in Azure App Service settings

### Production Users
- **Parent Account:** `tevai` (password stored securely in Azure, NOT in repo)
- **Kids:**
  - **Elija:** Male, PIN 1234, Island theme (🏝️)
  - **Agota:** Female, PIN 1234, Space theme (🚀)


### Environment Variables (Azure)
**Required in App Service Configuration:**
```bash
DJANGO_SECRET_KEY=<production-secret-key>
DJANGO_SETTINGS_MODULE=chorepoints.settings_production

# Database (PostgreSQL)
DB_NAME=chorepoints_db
DB_USER=chorepoints_admin
DB_PASSWORD=<secure-password>
DB_HOST=chorepoints-db.postgres.database.azure.com

# Azure Blob Storage
AZURE_ACCOUNT_NAME=chorepointsstorage
AZURE_ACCOUNT_KEY=<storage-account-key>

# Auto-provided by Azure
WEBSITE_HOSTNAME=elija-agota.azurewebsites.net
```

## 🏗️ Architecture Overview

### Technology Stack
```
Frontend:  Server-rendered Django templates + minimal JavaScript
           └─ Lithuanian localization (LANGUAGE_CODE='lt')
           └─ Confetti.js for celebration animations
           └─ Responsive CSS with emoji/image avatars

Backend:   Django 5.0+ (Python 3.11)
           └─ Single app architecture (`core/`)
           └─ Session-based kid authentication (no Django User for kids)
           └─ Parent authentication via Django Admin

Database:  SQLite (local dev) / PostgreSQL 15 (production)
           └─ 12 migrations (0001-0012)
           └─ Status-based approval workflow (PENDING/APPROVED/REJECTED)

Storage:   FileSystemStorage (local) / Azure Blob (production)
           └─ django-storages with custom backends
           └─ Auto-resize images on upload (Pillow)

Deployment: GitHub Actions → Azure App Service
            └─ Triggers on push to `main` branch
            └─ Oryx build system with `clean: true` parameter
            └─ startup.sh orchestration (pip → collectstatic → migrate → gunicorn)
```

### Request Flow
```
┌─────────────────────────────────────────────────────────────┐
│ Kid Login (/kid/login/) → PIN verification → Session       │
│   └─ request.session["kid_id"] = kid.id                    │
│   └─ Themed adventure map based on Kid.map_theme           │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ Submit Chore → Check for duplicate PENDING → Create        │
│   ChoreLog(status=PENDING, processed_at=None)              │
│   └─ NO immediate points change                            │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ Parent Approves (Admin Bulk Action) → ChoreLog.approve()   │
│   └─ transaction.atomic():                                  │
│       ├─ Kid.points_balance += points                       │
│       ├─ Kid.map_position += points                         │
│       ├─ Check for milestone unlocks                        │
│       ├─ status = APPROVED, processed_at = now()            │
│       └─ save()                                             │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ Kid Returns → Confetti Animation (if new approvals)        │
│   └─ Tracked via session["last_seen_approval_ts"]          │
└─────────────────────────────────────────────────────────────┘
```

## 💻 Local Development

### System Requirements
- **Python:** 3.11+ (tested with 3.11 and 3.13)
- **OS:** Windows (PowerShell scripts), Linux/Mac (manual setup)
- **Dependencies:** See `chorepoints/requirements.txt`


### Quick Start (Windows - Recommended)

```powershell
cd chorepoints
./dev.ps1
```

**What it does:**
1. ✅ Creates/activates `.venv` (if missing)
2. ✅ Installs dependencies (only if `requirements.txt` changed)
   - Uses hash caching (`.venv/.req_hash`) to skip redundant installs
3. ✅ Runs migrations (`python manage.py migrate`)
4. ✅ Opens browser at http://localhost:8000/
5. ✅ Starts Django dev server (stop with `CTRL+C`)

**Additional Options:**
```powershell
./dev.ps1 -Reset      # Recreate venv from scratch (clears cache)
./dev.ps1 -Port 8010  # Start on different port
```

### Quick Daily Start (Skip Setup)

```powershell
cd chorepoints
./run.ps1             # Just activate venv and start server
```

### Manual Setup (Linux/Mac or Without Scripts)

```bash
cd chorepoints
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
# Visit http://localhost:8000/
```

### Local Environment Details
- **Settings:** Uses `chorepoints/settings.py` (DEBUG=True)
- **Database:** SQLite (`chorepoints/db.sqlite3`, gitignored)
- **Static Files:** Served by Django dev server
- **Media Files:** Stored in `chorepoints/media/` (gitignored)
- **Port:** 8000 (default) or specify with `-Port` flag
- **Network Access:** Accessible from LAN (ALLOWED_HOSTS includes '192.168.0.35')


## 🗄️ Data Models

### Core Models (`core/models.py`)

#### 1. Kid
**Purpose:** Represents a child user in the system
```python
class Kid(models.Model):
    parent = ForeignKey(User)          # Django admin user
    name = CharField(max_length=100)
    gender = CharField(choices=Gender) # M/F/O (for greetings)
    pin = CharField(max_length=20)     # Plaintext (MVP limitation)
    points_balance = IntegerField       # Spendable points
    map_position = IntegerField         # Lifetime earned (adventure map)
    highest_milestone = IntegerField    # Tracking milestone progress
    avatar_emoji = CharField            # Emoji avatar (fallback: first letter)
    photo = ImageField                  # Optional photo (auto-resized 400x400)
    map_theme = CharField               # ISLAND/SPACE/RAINBOW
    active = BooleanField               # Soft delete
    created_at = DateTimeField
```
**Key Methods:**
- `get_greeting()`: Returns "Sveikas, {name}!" or "Sveika, {name}!" based on gender
- `get_current_milestone()`: Returns highest achieved milestone
- `get_next_milestone()`: Returns next milestone to unlock (infinite progression)
- `save()`: Auto-resizes photo to 400x400 using Pillow

#### 2. Chore
**Purpose:** Defines available chores kids can complete
```python
class Chore(models.Model):
    parent = ForeignKey(User)
    title = CharField(max_length=200)
    points = IntegerField                # Award amount
    icon_emoji = CharField(max_length=4) # Emoji icon (preferred)
    icon_image = ImageField              # Alternative to emoji (128x128)
    active = BooleanField
    created_at = DateTimeField
```
**CSV Data:** 18 chores loaded from `initial_data/chores.csv`
- Examples: "Sutvarkyti žaislus" (5 pts 🧸), "Knygos skaitymas - 6 lapai" (5 pts 📖)

#### 3. Reward
**Purpose:** Defines rewards kids can redeem
```python
class Reward(models.Model):
    parent = ForeignKey(User)
    title = CharField(max_length=200)
    cost_points = IntegerField           # Redemption cost
    icon_emoji = CharField(max_length=4)
    icon_image = ImageField              # Alternative (128x128)
    active = BooleanField
    created_at = DateTimeField
```
**CSV Data:** 15 rewards loaded from `initial_data/rewards.csv`
- Examples: "Papildomos 10 min. ekrano laiko" (50 pts 📱), "€5 kišenpinigiai" (100 pts 💶)

#### 4. ChoreLog
**Purpose:** Tracks chore submissions and approval status
```python
class ChoreLog(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Laukiama"
        APPROVED = "APPROVED", "Patvirtinta"
        REJECTED = "REJECTED", "Atmesta"
    
    kid = ForeignKey(Kid)
    chore = ForeignKey(Chore)
    status = CharField(choices=Status, default=PENDING)
    submitted_at = DateTimeField
    processed_at = DateTimeField(null=True)  # Approval/rejection timestamp
```
**Key Methods:**
- `approve()`: Atomically updates `Kid.points_balance` and `Kid.map_position`, checks milestones
- `reject()`: Sets status to REJECTED without point changes

#### 5. Redemption
**Purpose:** Tracks reward requests and approval status
```python
class Redemption(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Laukiama"
        APPROVED = "APPROVED", "Patvirtinta"
        REJECTED = "REJECTED", "Atmesta"
    
    kid = ForeignKey(Kid)
    reward = ForeignKey(Reward)
    status = CharField(choices=Status, default=PENDING)
    requested_at = DateTimeField
    processed_at = DateTimeField(null=True)
```
**Key Methods:**
- `approve()`: Atomically deducts `Reward.cost_points` from `Kid.points_balance`
- `reject()`: Sets status to REJECTED, restores points

#### 6. PointAdjustment
**Purpose:** Manual point adjustments by parents
```python
class PointAdjustment(models.Model):
    kid = ForeignKey(Kid)
    adjusted_by = ForeignKey(User)
    amount = IntegerField               # Can be negative
    reason = CharField(max_length=500)
    created_at = DateTimeField
```
**Behavior:** `save()` method automatically updates `Kid.points_balance` and `Kid.map_position`

### Model Relationships
```
User (Django Admin)
  ├─ Kid (1:N)
  ├─ Chore (1:N)
  ├─ Reward (1:N)
  └─ PointAdjustment (1:N, via adjusted_by)

Kid
  ├─ ChoreLog (1:N)
  ├─ Redemption (1:N)
  └─ PointAdjustment (1:N)

Chore
  └─ ChoreLog (1:N)

Reward
  └─ Redemption (1:N)
```

## 🔐 Authentication System

### Two Separate Auth Systems

#### Parent Authentication (Django Admin)
```bash
# Create parent/admin account
python manage.py createsuperuser
# Enter username, email, password

# Login at: http://localhost:8000/admin/
```

**Features:**
- Full Django User model with password hashing
- Staff/superuser permissions
- Password reset available: `python manage.py changepassword <username>`
- Session-based authentication
- Logout redirects to landing page (`LOGOUT_REDIRECT_URL='/'`)

#### Kid Authentication (Session-Based PIN)
```python
# Login flow (views.py)
def kid_login(request):
    if request.method == "POST":
        kid_id = request.POST.get("kid_id")
        pin = request.POST.get("pin")
        kid = Kid.objects.get(id=kid_id, active=True)
        
        if kid.pin == pin:  # Plaintext comparison (MVP)
            request.session["kid_id"] = kid.id
            request.session["last_seen_approval_ts"] = None
            return redirect("kid_home")
```

**Features:**
- No Django User model for kids (session-only)
- PIN stored as plaintext (documented security limitation)
- Helper function `_get_kid(request)` used in all kid views
- Visual card selection interface (photo → emoji → letter monogram fallback)
- Session expires after 1 hour or browser close
- Kids can change PIN via `/kid/change-pin/`

**Security Notes (MVP Limitations):**
- ⚠️ Plaintext PIN storage (use hashing in production)
- ⚠️ No rate limiting on PIN attempts
- ⚠️ No account lockout mechanism

## 💰 Points & Approval Workflow

### Two-Counter System

#### 1. `points_balance` (Spendable Points)
- **Increases:** Approved chores, parent adjustments (positive)
- **Decreases:** Approved reward redemptions, parent adjustments (negative)
- **Display:** Shown prominently on kid home page
- **Can go negative:** Yes, if parent adjusts

#### 2. `map_position` (Lifetime Earned Points)
- **Increases:** Approved chores, positive parent adjustments, milestone bonuses
- **Decreases:** Never (monotonically increasing)
- **Display:** Drives adventure map progress
- **Purpose:** Long-term achievement tracking

### Approval Workflow Pattern

#### Phase 1: Kid Submission (PENDING)
```python
# views.py - submit_chore()
# 1. Check for existing PENDING
existing_pending = ChoreLog.objects.filter(
    kid=kid, chore=chore, status=ChoreLog.Status.PENDING
).exists()

if existing_pending:
    messages.warning(request, "Šis darbas jau laukia patvirtinimo.")
    return redirect("kid_home")

# 2. Create PENDING record (NO points change yet)
ChoreLog.objects.create(
    kid=kid,
    chore=chore,
    status=ChoreLog.Status.PENDING,
    submitted_at=timezone.now()
)
```

#### Phase 2: Parent Approval (Admin Action)
```python
# admin.py - approve_pending_chores()
@admin.action(description="Patvirtinti pasirinktus laukiančius darbus")
def approve_pending_chores(modeladmin, request, queryset):
    with transaction.atomic():
        for log in queryset.filter(status=ChoreLog.Status.PENDING):
            log.approve()  # Calls model method

# models.py - ChoreLog.approve()
def approve(self):
    with transaction.atomic():
        # Update status
        self.status = self.Status.APPROVED
        self.processed_at = timezone.now()
        
        # Award points
        self.kid.points_balance += self.chore.points
        self.kid.map_position += self.chore.points
        
        # Check for milestone unlocks
        self._check_and_award_milestones()
        
        self.kid.save()
        self.save()
```

#### Phase 3: Kid Sees Approval (Confetti!)
```javascript
// base.html - Confetti animation
// Triggers when kid returns and has new approvals since last visit
// Tracked via session["last_seen_approval_ts"]
if (shouldShowConfetti) {
    const confettiSettings = { /* ... */ };
    confetti(confettiSettings);
}
```

### Duplicate Prevention
- **Views layer:** Check for existing `PENDING` records before creating new ones
- **Database:** No unique constraint (allows multiple submissions after processing)
- **User feedback:** "Šis darbas jau laukia patvirtinimo."

### Point Value Guidelines
**Informal standard:** ~5 points ≈ €1 (for parent budgeting)
- Small chores (2-5 pts): Quick tasks like "Nusinešti lėkštę" (2 pts)
- Medium chores (10-15 pts): More effort like "Sukrauti indaplovę" (10 pts)
- Large chores (20+ pts): Significant work like "Išsiurbti kambarį" (20 pts)
- Rewards range: 15-300 pts (15 pts for story choice, 300 pts for major goal)

## 🗺️ Adventure Map System

### Themed Maps (Kid.map_theme)
- **ISLAND** (🏝️): Tropical island journey
- **SPACE** (🚀): Cosmic exploration
- **RAINBOW** (🌈): Colorful path adventure

### Milestone Configuration (`models.py`)
```python
ACHIEVEMENT_MILESTONES = [
    {'position': 50, 'name': 'Bronzos ženkliukas', 'icon': '🥉', 'bonus': 10},
    {'position': 100, 'name': 'Sidabro ženkliukas', 'icon': '🥈', 'bonus': 10},
    {'position': 200, 'name': 'Aukso ženkliukas', 'icon': '🥇', 'bonus': 15},
    {'position': 300, 'name': 'Deimanto ženkliukas', 'icon': '💎', 'bonus': 15},
    {'position': 500, 'name': 'Karūnos ženkliukas', 'icon': '👑', 'bonus': 20},
    {'position': 750, 'name': 'Žvaigždės ženkliukas', 'icon': '⭐', 'bonus': 20},
    {'position': 1000, 'name': 'Superžvaigždė', 'icon': '🌟', 'bonus': 25},
    {'position': 1500, 'name': 'Čempionas', 'icon': '🏆', 'bonus': 30},
    {'position': 2000, 'name': 'Legenda', 'icon': '🔥', 'bonus': 40},
    {'position': 3000, 'name': 'Herojus', 'icon': '🚀', 'bonus': 50},
]
```

### Infinite Progression
After reaching the last milestone (3000 pts), bonuses continue every 500 points:
```python
def get_next_milestone(self) -> dict:
    # ... check defined milestones ...
    
    # If beyond all defined milestones
    if self.map_position >= ACHIEVEMENT_MILESTONES[-1]['position']:
        next_interval = ((self.map_position // 500) + 1) * 500
        return {
            'position': next_interval,
            'name': 'Bonus',
            'icon': '🎁',
            'bonus': 50
        }
```

### Milestone Unlocking
```python
def _check_and_award_milestones(self):
    """Called during ChoreLog.approve() to award milestone bonuses."""
    for milestone in ACHIEVEMENT_MILESTONES:
        if (self.kid.map_position >= milestone['position'] and 
            self.kid.highest_milestone < milestone['position']):
            
            # Award bonus points
            self.kid.points_balance += milestone['bonus']
            self.kid.highest_milestone = milestone['position']
            
            # Create audit record
            PointAdjustment.objects.create(
                kid=self.kid,
                adjusted_by=self.kid.parent,
                amount=milestone['bonus'],
                reason=f"Milestone: {milestone['name']}"
            )
```

## 🗃️ Database & Migrations

### Migration History (12 Total)
```
0001_initial.py                    - Base models (Kid, Chore, Reward)
0002_chorelog_redemption_status.py - Add Status choices
0003_kid_avatar_emoji.py           - Add emoji avatars
0004_pointadjustment.py            - Manual point adjustments
0005_kid_photo.py                  - Photo upload field
0006_chore_icon_emoji_...py        - Icon fields for chores/rewards
0007_kid_map_position.py           - Adventure map tracking
0008_kid_map_theme.py              - Themed maps
0009_add_milestone_system.py       - Milestone configuration
0010_make_adjustment_reason_...py  - Required reason field
0011_load_initial_data.py          - CSV data migration (34 chores, 21 rewards)
0012_add_kid_gender.py             - Gender field for greetings
```

### Running Migrations
```bash
# Create new migrations
python manage.py makemigrations core

# Apply migrations
python manage.py migrate core

# View migration history
python manage.py showmigrations core
```

### CSV Data Loading
**Files:** `chorepoints/initial_data/chores.csv`, `rewards.csv`

**Structure:**
```csv
# chores.csv
title,points,icon_emoji,description
Sutvarkyti žaislus,5,🧸,Sudėti žaislus į dėžes ar lentynas

# rewards.csv
title,cost_points,icon_emoji,description
Papildomos 10 min. ekrano laiko,50,📱,Laikytis šeimos taisyklių
```

**Loading Command:**
```bash
python manage.py load_initial_data        # Load from CSV
python manage.py load_initial_data --reset # Clear and reload
```

**Note:** CSV files are version-controlled. To update production data:
1. Edit CSV files locally
2. Create feature branch: `git checkout -b feature/update-chores`
3. Commit and push: `git add initial_data/*.csv && git commit -m "..."`
4. Create PR and wait for merge
5. After deployment, SSH into Azure and run: `python manage.py load_initial_data`

## 🚀 Deployment Process

### GitHub Actions Workflow (`.github/workflows/deploy.yml`)

#### Trigger Events
- **Push to `main` branch** → Auto-deploy to production
- **Pull request to `main`** → Run tests (optional)
- **Manual dispatch** → Trigger via GitHub UI

#### Workflow Steps
```yaml
1. Checkout source (actions/checkout@v4)
2. Set up Python 3.11 (actions/setup-python@v5)
3. Install dependencies (pip install -r requirements.txt)
4. Run unit tests (pytest - currently placeholder)
5. Archive application (zip -r chorepoints-package.zip)
6. Azure login (service principal via AZURE_CREDENTIALS secret)
7. Deploy to Azure (azure/webapps-deploy@v3 with clean: true)
8. Logout (cleanup)
```

#### Critical Parameter: `clean: true`
**Problem Solved:** Azure Oryx build system was selectively copying files, causing incomplete deployments.
**Solution:** `clean: true` forces full directory wipe before extracting zip, ensuring all files deploy.

```yaml
- name: Deploy to Azure Web App
  uses: azure/webapps-deploy@v3
  with:
    app-name: ${{ vars.AZURE_WEBAPP_NAME }}
    package: chorepoints-package.zip
    slot-name: Production
    startup-command: "bash startup.sh"
    clean: true  # ← CRITICAL: Forces full deployment
```

### Startup Sequence (`startup.sh`)
**Executed on every Azure app start:**
```bash
#!/bin/bash
echo "Starting ChorePoints Django App..."

# 1. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 2. Collect static files (to Azure Blob)
python manage.py collectstatic --noinput

# 3. Run database migrations
python manage.py migrate --noinput

# 4. Start Gunicorn
gunicorn chorepoints.wsgi:application \
    --bind=0.0.0.0:8000 \
    --workers=2 \
    --threads=4 \
    --timeout=120 \
    --access-logfile '-' \
    --error-logfile '-' \
    --log-level info
```

### Branch Strategy & PR Workflow
**CRITICAL: Never push directly to `main` branch**

#### Standard Workflow
```bash
# 1. Create feature branch
git checkout -b feature/descriptive-name

# 2. Make changes and test locally
./chorepoints/dev.ps1
# ... test changes ...

# 3. Commit to feature branch
git add .
git commit -m "Clear description of changes"

# 4. Push feature branch
git push origin feature/descriptive-name

# 5. Create PR via GitHub UI or CLI
gh pr create --title "Feature: Description" --body "Details..."

# 6. STOP - Wait for user to review and merge
# (GitHub Actions auto-deploys after merge to main)
```

#### Post-Deployment Tasks
```bash
# 1. SSH into Azure (run manually)
az webapp ssh --name elija-agota --resource-group chorepoints-rg-us

# 2. Inside SSH session
cd /home/site/wwwroot

# 3. Run migrations if needed
python manage.py migrate core

# 4. Reload CSV data if updated
python manage.py load_initial_data
```

### Azure Management Commands

#### Restart Application
```bash
az webapp restart --name elija-agota --resource-group chorepoints-rg-us
```

#### View Logs
```bash
# Tail logs in real-time
az webapp log tail --name elija-agota --resource-group chorepoints-rg-us

# Download logs
az webapp log download --name elija-agota \
    --resource-group chorepoints-rg-us \
    --log-file azure-logs.zip
```

#### SSH Access (User Only)
**IMPORTANT:** AI agents should never attempt SSH commands automatically. Always instruct user to run these manually.

```bash
# User runs this manually
az webapp ssh --name elija-agota --resource-group chorepoints-rg-us

# Then inside SSH session
cd /home/site/wwwroot
python manage.py shell  # Django shell
python manage.py migrate  # Run migrations
python manage.py load_initial_data  # Reload CSV data
```

### Environment Settings Priority
```
Production: settings_production.py (overwrites base settings.py)
            └─ Triggered by DJANGO_SETTINGS_MODULE=chorepoints.settings_production

Local Dev:  settings.py (DEBUG=True, SQLite, FileSystemStorage)
            └─ Default when DJANGO_SETTINGS_MODULE not set
```

## 📁 File Structure

```
django_kid_rewards/               # Repo root
├── .github/
│   ├── workflows/
│   │   └── deploy.yml           # CI/CD pipeline
│   └── copilot-instructions.md  # AI agent instructions
├── chorepoints/                  # Django project root
│   ├── chorepoints/             # Django config package
│   │   ├── settings.py          # Base settings (local dev)
│   │   ├── settings_production.py # Production overrides
│   │   ├── storage_backends.py  # Azure Blob custom backends
│   │   ├── urls.py              # URL routing
│   │   ├── wsgi.py              # WSGI entry point
│   │   └── asgi.py              # ASGI entry point
│   ├── core/                    # Main application
│   │   ├── models.py            # 6 models (Kid, Chore, Reward, etc.)
│   │   ├── views.py             # Session-based kid views
│   │   ├── admin.py             # Django admin customization
│   │   ├── admin_site.py        # Custom admin site config
│   │   ├── forms.py             # Form definitions
│   │   ├── urls.py              # App URL patterns
│   │   ├── templates/           # Lithuanian templates
│   │   │   ├── base.html        # Base template (confetti JS)
│   │   │   ├── index.html       # Landing page
│   │   │   └── kid/
│   │   │       ├── login.html   # Kid PIN login
│   │   │       ├── home.html    # Kid dashboard (chores/rewards)
│   │   │       └── change_pin.html
│   │   ├── management/
│   │   │   └── commands/
│   │   │       ├── seed_demo_lt.py      # Quick demo seeding
│   │   │       └── load_initial_data.py # CSV data loading
│   │   ├── migrations/          # 12 migration files
│   │   └── tests/               # Test suite (placeholder)
│   ├── initial_data/
│   │   ├── chores.csv           # 18 Lithuanian chores
│   │   ├── rewards.csv          # 15 Lithuanian rewards
│   │   ├── users.json           # User seed data
│   │   └── README.md            # CSV format docs
│   ├── media/                   # User uploads (gitignored)
│   │   ├── kid_avatars/         # Kid photos (400x400)
│   │   ├── chore_icons/         # Chore images (128x128)
│   │   └── reward_icons/        # Reward images (128x128)
│   ├── staticfiles/             # Collected static (gitignored)
│   ├── ssl/                     # Local HTTPS certs (gitignored)
│   ├── db.sqlite3              # Local database (gitignored)
│   ├── requirements.txt         # Python dependencies
│   ├── manage.py                # Django CLI
│   ├── startup.sh               # Azure startup script
│   ├── dev.ps1                  # Quick start (Windows)
│   └── run.ps1                  # Daily start (Windows)
├── README.md                    # This file
├── .gitignore                   # Excludes venv, media, db, etc.
└── *.md                         # Additional documentation
```

### Key Files for AI Agents

#### Must Read First
1. **`.github/copilot-instructions.md`** - Complete project context and conventions
2. **`README.md`** - Architecture overview and quick reference
3. **`chorepoints/core/models.py`** - Data model definitions
4. **`chorepoints/settings_production.py`** - Production configuration

#### Deployment & Workflow
5. **`.github/workflows/deploy.yml`** - CI/CD pipeline
6. **`chorepoints/startup.sh`** - Azure startup sequence

#### Data & Localization
7. **`chorepoints/initial_data/chores.csv`** - Chore definitions
8. **`chorepoints/initial_data/rewards.csv`** - Reward definitions
9. **`chorepoints/core/templates/`** - Lithuanian UI templates

## 🧪 Testing Strategy

### Current State (MVP)
- **Automated Tests:** Placeholder test suite in `core/tests/` (not yet implemented)
- **Manual Testing:** Local testing via `dev.ps1` before creating PRs
- **Production Testing:** Verify changes on live site after deployment

### Test Files (Placeholders)
```
core/tests/
├── test_models.py         # Model methods and validations
├── test_views.py          # View logic and routing
├── test_forms.py          # Form validation
├── test_integration.py    # End-to-end workflows
├── test_security.py       # Authentication and CSRF
└── test_performance.py    # Query optimization
```

### Testing Workflow
```bash
# 1. Local testing (required before PR)
cd chorepoints
./dev.ps1
# Manual testing: login, submit chores, approve in admin, etc.

# 2. Run placeholder tests (future)
pip install pytest pytest-django
pytest core/tests

# 3. Production testing (after deployment)
# Visit https://elija-agota.azurewebsites.net/
# Test critical paths: login, chore submission, approval, milestone unlocks
```

### Test Data Commands
```bash
# Quick demo seeding (4 chores, 3 rewards, 2 kids)
python manage.py seed_demo_lt --username <parent>

# Full CSV data (18 chores, 15 rewards)
python manage.py load_initial_data

# Reset and reload
python manage.py load_initial_data --reset
```

## 🚨 Known Limitations (MVP Scope)

### Security
- ⚠️ **Plaintext PIN Storage**: Kid PINs stored without hashing (use bcrypt in production)
- ⚠️ **No Rate Limiting**: Unlimited PIN attempts (add rate limiting)
- ⚠️ **No Account Lockout**: No protection against brute force attacks

### Functionality
- ❌ **No REST API**: Server-rendered templates only (add DRF if needed)
- ❌ **No Real-Time Updates**: Requires page refresh (consider WebSockets/polling)
- ❌ **No Automated Tests**: Manual testing only (add pytest coverage)
- ❌ **No Email Notifications**: Parents not notified of submissions (add Sendgrid/similar)

### Data Integrity
- ⚠️ **No DB Constraint for Duplicates**: Duplicate prevention in views only (add unique constraint)
- ⚠️ **No Soft Delete Cascade**: Deleting parent deletes kids (use `on_delete=PROTECT`)

### Scalability
- ⚠️ **Single Database**: No read replicas (consider PostgreSQL replication)
- ⚠️ **No Caching**: No Redis/Memcached (add for performance)
- ⚠️ **No CDN**: Azure Blob direct access (consider Azure CDN)

### UI/UX
- ❌ **Minimal JavaScript**: No SPA framework (plain JS with confetti.js only)
- ❌ **No Offline Support**: Requires network connection (add PWA capabilities)
- ❌ **No Multi-Language**: Lithuanian only (i18n infrastructure exists but not used)

## 📚 Additional Documentation

- **Production Docs:** `AZURE_DEPLOYMENT_GUIDE.md` - Detailed Azure setup
- **Copilot Instructions:** `.github/copilot-instructions.md` - AI agent conventions
- **CSV Format:** `chorepoints/initial_data/README.md` - Data file specs
- **Database Guide:** `DATABASE_REBUILD_GUIDE.md` - Migration troubleshooting
- **HTTPS Setup:** `HTTPS_SETUP.md` - Local SSL configuration

## 🎮 Quick Reference

### Production URLs
- **App:** https://elija-agota.azurewebsites.net/
- **Admin:** https://elija-agota.azurewebsites.net/admin/
- **Kid Login:** https://elija-agota.azurewebsites.net/kid/login/

### Local URLs
- **App:** http://localhost:8000/
- **Admin:** http://localhost:8000/admin/
- **Kid Login:** http://localhost:8000/kid/login/

### Useful Commands

#### User Management
```bash
# Create parent/admin
python manage.py createsuperuser

# Change password
python manage.py changepassword <username>

# Change kid PIN (Django shell)
python manage.py shell
>>> from core.models import Kid
>>> kid = Kid.objects.get(name="Elija")
>>> kid.pin = "4321"
>>> kid.save()
```

#### Data Management
```bash
# Seed demo data
python manage.py seed_demo_lt --username tevai

# Load CSV data
python manage.py load_initial_data

# Reset database (local only)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python manage.py load_initial_data
```

#### Development
```bash
# Start dev server (automated)
./chorepoints/dev.ps1

# Start dev server (manual)
cd chorepoints
.venv\Scripts\Activate.ps1  # Windows
python manage.py runserver

# Create migrations
python manage.py makemigrations core

# Apply migrations
python manage.py migrate core

# Django shell
python manage.py shell
```

#### Azure Management
```bash
# Restart app
az webapp restart --name elija-agota --resource-group chorepoints-rg-us

# View logs
az webapp log tail --name elija-agota --resource-group chorepoints-rg-us

# SSH (user only - manual)
az webapp ssh --name elija-agota --resource-group chorepoints-rg-us
```

## 🤝 Contributing

### Workflow for Changes
1. **Create feature branch:** `git checkout -b feature/descriptive-name`
2. **Test locally:** `./chorepoints/dev.ps1`
3. **Commit changes:** `git add . && git commit -m "Description"`
4. **Push branch:** `git push origin feature/descriptive-name`
5. **Create PR:** Via GitHub UI or `gh pr create`
6. **Wait for review:** User merges PR (triggers auto-deployment)

### PR Requirements
- ✅ Test locally before creating PR
- ✅ Clear commit messages
- ✅ Update documentation if needed
- ✅ No direct pushes to `main` branch

### Code Conventions
- **Python:** PEP 8 style (use `black` formatter)
- **Templates:** Lithuanian strings, semantic HTML
- **Models:** Atomic transactions for balance updates
- **Views:** Use `_get_kid(request)` helper for kid auth
- **Admin:** Translate action descriptions to Lithuanian

## 📝 License & Credits

**License:** Not specified (private project)

**Technologies:**
- Django 5.0+ (Web framework)
- PostgreSQL 15 (Production database)
- Azure App Service (Hosting)
- Azure Blob Storage (Media/static files)
- GitHub Actions (CI/CD)
- Pillow (Image processing)
- Gunicorn (WSGI server)

---

**Built with ❤️ for Elija and Agota's chore adventure!** 🚀

Questions or issues? Check `.github/copilot-instructions.md` or open a GitHub issue.
