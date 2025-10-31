# ChorePoints AI Agent Instructions

## Project Overview
Django 5 MVP for managing kids' chores & rewards with approval workflow. **Lithuanian-first UI** (LANGUAGE_CODE=lt) for kids; admin uses Django default. Session-based kid authentication via PIN (no Django User).

## 🚀 Production Environment (Azure)

**CRITICAL**: Production app is live at **https://elija-agota.azurewebsites.net/**

### Production Details
- **App Name**: elija-agota
- **Resource Group**: chorepoints-rg-us
- **Region**: North Central US
- **Runtime**: Python 3.11 on Linux
- **Database**: Azure PostgreSQL Flexible Server v15 (`chorepoints-db`)
- **Storage**: Azure Blob Storage (`chorepointsstorage`, Standard_LRS)
- **Parent Login**: `tevai` (password stored securely, not in repo)
- **Kids**: Elija (PIN: 1234, Theme: ISLAND, Gender: M), Agota (PIN: 1234, Theme: SPACE, Gender: F)

### Deployment Pipeline
- **GitHub Actions** auto-deploys from `main` branch to Azure
- `startup.sh` runs on Azure startup: installs deps → collectstatic → migrate → starts Gunicorn
- **DO NOT push directly to `main`** - create feature branches and test locally first
- All changes to `main` trigger immediate production deployment

### Production Settings (`settings_production.py`)
- `DEBUG=False`
- Uses environment variables: `DJANGO_SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `AZURE_ACCOUNT_NAME`
- Session security: 1-hour timeout, expires on browser close, secure HTTPS-only cookies
- Static files served from Azure Blob Storage

### Azure Management Commands
```bash
# SSH into production (requires Azure CLI)
az webapp ssh --name elija-agota --resource-group chorepoints-rg-us

# Restart production app
az webapp restart --name elija-agota --resource-group chorepoints-rg-us

# View logs
az webapp log tail --name elija-agota --resource-group chorepoints-rg-us

# Run migrations on production (inside SSH)
cd /home/site/wwwroot
python manage.py migrate core
```

### Localhost vs Production
- **Localhost** (`./chorepoints/dev.ps1`): SQLite, DEBUG=True, no Azure storage, for development only
- **Production** (Azure): PostgreSQL, DEBUG=False, Azure Blob Storage, HTTPS required
- Never test database migrations directly on production - test locally first

## Architecture & Key Patterns

### Core Domain Models (`core/models.py`)
- **Kid**: Has `points_balance`, plaintext PIN (MVP only), photo/emoji avatars with auto-resize on save (400x400 max)
- **Chore/Reward**: Have icon_emoji or icon_image (128x128 auto-resize), parent (FK to User)
- **ChoreLog/Redemption**: Status-based approval workflow (PENDING/APPROVED/REJECTED) with `approve()`/`reject()` methods that atomically update balances
- **PointAdjustment**: Ad-hoc parent point grants; side-effect applies balance change in `save()` override

**Critical**: All balance mutations use `transaction.atomic()` in model methods, not views. Views only create PENDING records; admin actions call `approve()`/`reject()`.

### Approval Workflow Pattern
1. Kid submits chore/reward → creates PENDING ChoreLog/Redemption (no immediate balance change)
2. Duplicate prevention: views check existing PENDING records before creating new ones
3. Parent approves via admin actions → `approve()` atomically updates `Kid.points_balance` and sets status to APPROVED
4. Confetti animation triggers when kid sees new approvals since last visit (tracked via session timestamp)

### Session-Based Kid Auth (`views.py`)
- No Django User model for kids; `request.session["kid_id"]` stores authenticated kid
- Helper `_get_kid(request)` used in all kid views
- PIN comparison is plaintext (MVP limitation documented)

### Image Handling Pattern
Models with ImageField (Kid.photo, Chore/Reward.icon_image) override `save()` to auto-resize using Pillow after DB save:
```python
def save(self, *args, **kwargs):
    super().save(*args, **kwargs)  # Save first to get path
    if self.photo and Image:
        # Resize logic using Path(self.photo.path)
```
Fallback: emoji → monogram (first letter) for avatars; default emoji for chore/reward icons.

## Development Workflow

### Branch Strategy
- **`main` branch**: Auto-deploys to production Azure - DO NOT push untested code
- **Feature branches**: Create for all development work (`git checkout -b feature/my-feature`)
- **Testing**: Always test locally with `dev.ps1` before merging to main

### Quick Start (Windows PowerShell - Local Development Only)
```powershell
./chorepoints/dev.ps1          # Auto venv, deps, migrate, runserver, opens browser
./chorepoints/dev.ps1 -Reset   # Recreate venv from scratch
```
Script uses requirements.txt hash caching (`.venv/.req_hash`) to skip reinstalls.
**Localhost**: http://localhost:8000/ (SQLite, DEBUG mode)

### Essential Commands (Local Development)
```bash
# Seed Lithuanian demo data (Elija, Agota, default chores/rewards with emoji)
python manage.py seed_demo_lt --username <parent_username>

# Migrations (12 total as of 0012_add_kid_gender)
python manage.py makemigrations core
python manage.py migrate core

# Create local parent account for testing
python manage.py createsuperuser
```

### Data Migrations
- **Migration 0011**: Loads initial chores (34) and rewards (21) from CSV files in `initial_data/`
- CSV files define Lithuanian chores/rewards with emoji icons and point values
- Safe to run multiple times (uses `get_or_create`)

### File Structure Convention
- **Single app**: `core/` (models, views, admin, templates, management commands)
- **Templates**: `core/templates/` (base.html, index.html, kid/login.html, kid/home.html)
- **Media uploads**: Auto-served in DEBUG; `media/kid_avatars/`, `media/chore_icons/`, `media/reward_icons/`
- **Settings**: LANGUAGE_CODE=lt, LOGOUT_REDIRECT_URL='/', MEDIA_URL/MEDIA_ROOT configured

## Lithuanian Localization
- **Hardcoded strings** in templates/views (no Django i18n `.po` files yet)
- Admin action descriptions translated: "Patvirtinti pasirinktus laukiančius darbus"
- All kid-facing messages use Lithuanian: `messages.success(request, f"Sveikas, {kid.name}!")`
- Model help_text in Lithuanian: `help_text="Nuotrauka (jei nenaudojamas emoji)"`

## Common Modifications

### Adding New Approval-Based Feature
1. Create model with Status choices (PENDING/APPROVED/REJECTED), processed_at timestamp
2. Add `approve()`/`reject()` methods with atomic balance logic
3. Register in admin.py with custom actions calling those methods
4. Create view that checks for duplicate PENDING before creating record
5. Update kid/home.html to show pending/approved lists with icons

### Adding Image Field
1. Add ImageField with upload_to="<folder>/"
2. Override model `save()` to resize after `super().save()` (see Kid/Chore examples)
3. Update .gitignore to exclude media folder
4. Ensure Pillow in requirements.txt

### Extending Seed Command
Edit `core/management/commands/seed_demo_lt.py` to add tuples like `("Title", points, "emoji")` and use `get_or_create()` with icon_emoji in defaults.

## Testing & Debugging
- No automated tests yet (MVP)
- Use Django admin to inspect ChoreLog/Redemption status transitions
- Session key `last_seen_approval_ts` controls confetti (ISO format timestamp)
- Check pending duplicate prevention: submit same chore twice → should show "Šis darbas jau laukia patvirtinimo."

## Git Conventions
- Exclude: `*.pyc`, `__pycache__/`, `db.sqlite3`, `media/`, `.venv/`, `staticfiles/`, `azure-logs.zip` (see .gitignore)
- Migrations committed (0001-0012); db.sqlite3 never committed (local only)
- **Never commit secrets**: passwords, API keys, database credentials
- Repo root: `django_kid_rewards/` (not `chorepoints/` subfolder)
- Always create feature branches for development: `git checkout -b feature/description`
- Test changes locally before pushing to `main` (auto-deploys to production)

## Security Features
- **Session Security**: 1-hour timeout, expires on browser close, HttpOnly cookies, SameSite=Lax
- **Kid Gender Field**: For Lithuanian gender-specific greetings (Sveikas/Sveika)
- **HTTPS Only** in production with secure cookies
- **CSRF Protection**: Django middleware + SameSite cookies

## Known Limitations (MVP Scope)
- Kid PIN stored plaintext (no hashing) - document as security limitation
- No rate limiting on chore submissions
- No unique DB constraint for PENDING duplicates (logic in views only)
- No REST API; server-rendered Django templates with minimal JS (confetti canvas, avatar selection)
- No automated tests yet

## Quick Reference: User Accounts

### Production (Azure)
- **Parent**: `tevai` (admin account, password NOT in repo)
- **Kids**: 
  - Elija (M, PIN 1234, Island theme)
  - Agota (F, PIN 1234, Space theme)
- **Admin URL**: https://elija-agota.azurewebsites.net/admin/
- **Kid Login**: https://elija-agota.azurewebsites.net/kid/login/

### Local Development
- Create your own test accounts with `python manage.py createsuperuser`
- Use `seed_demo_lt` command to populate test kids and chores/rewards
