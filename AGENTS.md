# AGENTS.md — ChorePoints (Taškų Nuotykis)

**Mission-Critical Agent Guide** for AI coding assistants (GitHub Copilot, OpenAI Codex, ChatGPT Code Interpreter, VS Code agents).
This document defines absolute requirements, expert-level patterns, and autonomous execution protocols.

## 🎯 Core Principles for Agents

### 1. Autonomous Completion Protocol
**YOU MUST** complete ALL planned tasks in a single session without asking the user to continue. This saves tokens and provides better UX.

**Planning Requirements**:
- Break complex tasks into 5-15 atomic subtasks (each max 15 minutes)
- Identify dependencies explicitly (DB schema → models → migrations → views → templates → tests)
- Validate after each subtask (run dev server, test manually, check for errors)
- Track progress internally and continue until 100% complete
- Only stop if blocked by missing information or external dependencies (user credentials, API keys)

**Execution Pattern**:
```
1. Read task requirements
2. Plan ALL subtasks upfront (write them down)
3. Execute subtask 1 → validate → execute subtask 2 → validate → ...
4. When all done, summarize what was completed
5. NEVER say "let me know if you want me to continue" - just continue
```

### 2. Python/Django Genius-Level Expertise
Agents on this project MUST demonstrate mastery of:
- **Django ORM**: QuerySets, F() expressions, select_related(), prefetch_related(), aggregate(), annotate()
- **Transactions**: atomic(), select_for_update(), savepoints, isolation levels
- **Migrations**: Zero-downtime strategies, data migrations, RunPython, safe rollback patterns
- **Signals**: post_save, pre_delete, transaction hooks, async signal handlers
- **Middleware**: Request/response processing, session management, custom middleware
- **Security**: OWASP Top 10, CSRF, XSS, SQL injection prevention, secure session management

### 3. Azure Cloud & DevOps Mastery
**Production Environment**: https://elija-agota.azurewebsites.net/ (live app, treat with care)

**Infrastructure Knowledge**:
- App Service B1 (1.75GB RAM, 1 core, Linux, Python 3.11)
- PostgreSQL Flexible Server v15 (Burstable B1ms, 32GB storage, 120 IOPS, SSL required)
- Blob Storage (Standard_LRS, Hot tier, 3 containers: static, media, backups)
- GitHub Actions CI/CD (auto-deploy on `main` push, ~2-3 min deployment)
- Gunicorn WSGI (2 workers, 4 threads each, 120s timeout)

**Cost Awareness**: ~$25-30/month total. Avoid expensive operations (excessive storage, premium tiers).

## Project Overview (for agents)
- **Repo**: kid-chore-points — Django 5 production app for kids' chore management with gamification
- **Language**: Python 3.11
- **Architecture**: Monolithic Django (single `core/` app, server-side rendering, minimal JavaScript)
- **Production**: Azure App Service (`elija-agota`), PostgreSQL (`chorepoints-db`), Blob Storage (`chorepointsstorage`)
- **CI/CD**: GitHub Actions auto-deploys `main` branch to Azure (see `.github/workflows/deploy.yml`)
- **Deployment**: Direct to Azure App Service (no Docker, no containers)
- **Users**: Parent admin (`tevai`), Kids with PIN login (Elija, Agota)
- **Localization**: Lithuanian-first UI for kids, English admin interface

> **Agents**: Always check for the nearest `AGENTS.md` in subfolders for context-specific guidance. This file is the global default.

## 🚀 Quick Setup Commands (Local Dev — PowerShell on Windows)

### One-Command Setup (Recommended)
```powershell
cd chorepoints
./dev.ps1          # Auto: create venv, install deps, migrate, runserver, open browser
```

**What dev.ps1 does**:
1. Creates `.venv/` virtual environment (if not exists)
2. Installs `requirements.txt` (caches hash in `.venv/.req_hash` to skip reinstalls)
3. Runs `python manage.py migrate` (applies all pending migrations)
4. Starts `python manage.py runserver` (localhost:8000)
5. Opens http://localhost:8000 in default browser

**Troubleshooting dev.ps1**:
```powershell
./dev.ps1 -Reset   # Force recreate venv from scratch (if dependencies broken)
./run.ps1          # Fast start: activate venv + runserver (skip setup if already done)
```

### Manual Setup (if dev.ps1 fails)
```powershell
cd chorepoints
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate core
python manage.py createsuperuser           # Create parent admin account
python manage.py seed_demo_lt --username tevai  # Load demo kids + chores
python manage.py runserver
```

### Essential Management Commands
```bash
# Seed Lithuanian demo data (Elija, Agota, default chores/rewards with emoji)
python manage.py seed_demo_lt --username <parent_username>

# Load production CSV data (19 chores, 21 rewards)
python manage.py load_initial_data

# Create/apply migrations
python manage.py makemigrations core
python manage.py migrate core

# Check migration status
python manage.py showmigrations core

# Interactive Django shell (ORM access)
python manage.py shell

# Database shell (SQLite locally, PostgreSQL in production)
python manage.py dbshell

# Collect static files (no-op in dev, uploads to Azure Blob in production)
python manage.py collectstatic --noinput
```

## 📦 Local Development (No Docker)

**IMPORTANT**: This project does NOT use Docker or containerization. It runs directly on the host machine.

### Why No Docker?
- Pure Python Django app deployed directly to Azure App Service
- Local development uses SQLite (simple, no container needed)
- Production uses Azure PostgreSQL Flexible Server (managed service)
- Azure App Service handles deployment without Docker images
- Simpler development workflow: `./dev.ps1` and you're running

## 🧪 Testing Strategy

### Unit Tests (Django TestCase)
**Current Status**: Test files exist in `core/tests/` but need implementation.

```bash
# Install pytest + django plugin (optional - can use Django's built-in unittest)
pip install pytest pytest-django

# Run all core tests
pytest core/tests
# OR use Django's test runner:
python manage.py test core

# Run specific test file
pytest core/tests/test_models.py
# OR:
python manage.py test core.tests.test_models

# Run with coverage
pytest --cov=core core/tests
```

**Existing test files** (`core/tests/`):
- `test_models.py`: Model methods (`approve()`, `reject()`, milestone calculations)
- `test_views.py`: View logic (kid auth, chore submission, duplicate prevention)
- `test_forms.py`: Form validation (PIN length, confirm PIN matching)
- `test_integration.py`: End-to-end workflows (PENDING → APPROVED → balance update)
- `test_security.py`: CSRF, session security, access control
- `test_performance.py`: N+1 query detection, large dataset handling
- `test_error_handling.py`: Error handling and edge cases

### Manual Testing Workflow
**Primary testing approach**: Manual testing via local dev server
1. Run `./dev.ps1` to start development server
2. Test kid login flow at http://localhost:8000/kid/login/
3. Test chore submission and approval workflow
4. Verify confetti animations and milestone unlocks
5. Test admin approval actions in Django admin

**No E2E automation yet**: Project uses manual testing instead of Playwright/Selenium

## 💻 Code Style & Linting

### Python Style (PEP 8 + Django Conventions)
- **Indentation**: 4 spaces (no tabs)
- **Line length**: 100 characters (Django convention, not strict 79)
- **Imports**: Group by standard library → third-party → local, alphabetical within groups
- **Naming**:
  - Classes: `PascalCase` (Kid, ChoreLog, PointAdjustment)
  - Functions/methods: `snake_case` (complete_chore, get_greeting, approve)
  - Constants: `UPPER_SNAKE_CASE` (ACHIEVEMENT_MILESTONES, STATUS_PENDING)
  - Private: `_leading_underscore` (_get_kid, _calculate_bonus)

**Linting tools** (recommended):
```bash
pip install black flake8 isort

# Auto-format code
black chorepoints/core/

# Check style violations
flake8 chorepoints/core/

# Sort imports
isort chorepoints/core/
```

**flake8 config** (`.flake8` or `setup.cfg`):
```ini
[flake8]
max-line-length = 100
exclude = .venv,migrations,__pycache__
ignore = E203,W503  # Black compatibility
```

### Django-Specific Patterns
- **Fat models, thin views**: Business logic in model methods (`approve()`, `reject()`)
- **Atomic transactions**: Use `transaction.atomic()` for balance mutations
- **Query optimization**: Always use `select_related()` for FK, `prefetch_related()` for reverse FK
- **F() expressions**: For atomic updates without race conditions
- **get_object_or_404**: Fail gracefully (404) instead of raising exceptions (500)

### Template Style (Django Templates)
- **Indentation**: 2 spaces
- **Template tags**: `{% load static %}` at top of file
- **Comments**: `{# Single-line comment #}`, `{% comment %}Multi-line{% endcomment %}`
- **Variables**: Always escape by default (`{{ kid.name }}`), use `|safe` filter sparingly
- **Filters**: Use Lithuanian date format (`{{ log.logged_at|date:"Y-m-d H:i" }}`)

### Lithuanian Localization Rules
- **Kid-facing UI**: 100% Lithuanian strings (buttons, messages, labels)
- **Admin interface**: English (Django default, can stay English for parent)
- **Model verbose names**: Lithuanian (`verbose_name = "Vaikas"`, `verbose_name_plural = "Vaikai"`)
- **Admin action descriptions**: Lithuanian (`short_description = "Patvirtinti pasirinktus laukiančius darbus"`)
- **Gender-specific greetings**: Use `Kid.get_greeting()` method (Sveikas/Sveika)
- **Messages**: Always Lithuanian for kid views (`messages.success(request, "Sėkmingai pateikta!")`)

**No `.po` files yet** (hardcoded strings). Future internationalization:
```bash
# Extract translatable strings
python manage.py makemessages -l en

# Compile translations
python manage.py compilemessages
```

## 📦 PR Instructions (Agent-Friendly — CRITICAL)

### Branch Strategy (NEVER PUSH TO MAIN)
**Agent workflow** (strict order):
1. **Create feature branch**: `git checkout -b feature/<descriptive-name>`
2. **Make changes**: Edit files, add tests, run dev.ps1
3. **Verify locally**:
   - [ ] Run `./chorepoints/dev.ps1` and test on http://localhost:8000
   - [ ] Check all routes: `/`, `/admin/`, `/kid/login/`, `/kid/home/`
   - [ ] Apply migrations: `python manage.py migrate core`
   - [ ] Load seed data: `python manage.py seed_demo_lt --username tevai`
   - [ ] Test approval workflow: Submit chore → Approve in admin → Verify balance update
4. **Commit with descriptive message**: `git add . && git commit -m "[scope] Description"`
5. **Push feature branch**: `git push origin feature/<descriptive-name>`
6. **Create PR** (GitHub CLI or instruct user):
   ```bash
   gh pr create --title "[Feature] Add X" --body "### Changes\n- Item 1\n\n### Testing\n- Tested locally\n\n### Migration\n- Run migrate core"
   ```
7. **STOP HERE** - User reviews and merges PR (agent must NOT merge automatically)
8. **Auto-deployment**: GitHub Actions deploys to Azure after merge to `main` (~2-3 min)
9. **Post-deployment** (user runs manually if needed):
   ```bash
   az webapp ssh --name elija-agota --resource-group chorepoints-rg-us
   cd /home/site/wwwroot
   python manage.py migrate core
   python manage.py load_initial_data  # If CSV changed
   ```

### PR Template (What to Include)
```markdown
## Description
Brief summary of what changed and why.

## Changes
- [ ] Added/modified models: Kid, ChoreLog, etc.
- [ ] Added/modified views: kid_home, complete_chore
- [ ] Added/modified templates: kid/home.html
- [ ] Database migrations: 0013_add_field_x
- [ ] Updated CSV data: chores.csv, rewards.csv

## Testing Steps
1. Run `./dev.ps1` to start local server
2. Navigate to http://localhost:8000/kid/login/
3. Login as Elija (PIN: 1234)
4. Submit chore "Pavalyti kambarį"
5. Admin approve → Verify points balance updated
6. Check confetti animation on kid home page

## Migration Steps (if applicable)
- [ ] Run `python manage.py migrate core` locally
- [ ] After deployment, SSH to Azure and run migrate
- [ ] If CSV changed, run `python manage.py load_initial_data` in Azure

## Checklist
- [ ] Code follows PEP 8 style
- [ ] Lithuanian strings for kid-facing UI
- [ ] No sensitive data committed (passwords, API keys)
- [ ] Migrations applied locally
- [ ] Tested end-to-end locally
- [ ] No direct push to `main` (feature branch only)
```

### Commit Message Format
```
[scope] Short description (50 chars max)

Longer explanation (wrap at 72 chars):
- Why this change is needed
- What behavior changes
- Any side effects or migration steps

Fixes #123 (if applicable)
```

**Examples**:
```
[models] Add milestone bonus logic to ChoreLog.approve()

- Check for crossed milestones when approving chores
- Award bonus points for each milestone (10-50 pts depending on tier)
- Update highest_milestone field on Kid model
- Handles infinite progression beyond 3000 pts (500pt intervals)

[views] Prevent duplicate PENDING chore submissions

- Check for existing PENDING logs before creating new ChoreLog
- Show Lithuanian message "Šis darbas jau laukia patvirtinimo."
- Prevents kids from spamming chore submissions
- Applies to both chores and reward redemptions

[deployment] Increase Gunicorn workers from 2 to 4

- Better concurrency for multiple simultaneous kid sessions
- Increase timeout from 60s to 120s for slow PostgreSQL queries
- Update startup.sh with new worker/thread config
- No migration required (deployment config only)
```

## 🔒 Environments & Secrets (NEVER COMMIT SECRETS)

### Local Development (dev.ps1)
- **Database**: SQLite (`db.sqlite3` — gitignored)
- **Storage**: Local filesystem (`media/` — gitignored)
- **DEBUG**: True
- **SECRET_KEY**: Hardcoded dev key (insecure, OK for local only)

### Production (Azure App Service)
**Environment variables** (set in Azure Portal > Configuration > Application settings):
- `DJANGO_SETTINGS_MODULE=chorepoints.settings_production`
- `DJANGO_SECRET_KEY=<secret>` (50-char random string, never commit)
- `DB_NAME=chorepoints`
- `DB_USER=chorepoints_admin`
- `DB_PASSWORD=<secret>` (strong password, never commit)
- `DB_HOST=chorepoints-db.postgres.database.azure.com`
- `AZURE_ACCOUNT_NAME=chorepointsstorage`
- `AZURE_ACCOUNT_KEY=<secret>` (storage account key, never commit)
- `WEBSITE_HOSTNAME=elija-agota.azurewebsites.net` (auto-set by Azure)

**How to add/update secrets** (agent cannot do this automatically):
```bash
# User must run manually (agent cannot access secrets)
az webapp config appsettings set \
  --name elija-agota \
  --resource-group chorepoints-rg-us \
  --settings DB_PASSWORD="<new_password>"
```

**Never do this**:
- ❌ Commit `.env` files with secrets
- ❌ Hardcode passwords in `settings.py` or `settings_production.py`
- ❌ Include API keys in code comments
- ❌ Push `db.sqlite3` or `media/` folders to repo

## 🚀 Deployment Steps (for Agents to Prepare PRs)

### GitHub Actions CI/CD (Automatic on `main` push)
**Workflow**: `.github/workflows/deploy.yml`

**Triggers**:
- Push to `main` branch (auto-deploys to production)
- Pull request to `main` (runs tests only, no deployment)
- Manual workflow_dispatch (via GitHub UI)

**Steps**:
1. Checkout source code
2. Setup Python 3.11
3. Install dependencies (`pip install -r requirements.txt`)
4. Run unit tests (currently skipped - `continue-on-error: true`)
5. Archive application (zip `chorepoints/` folder, exclude __pycache__)
6. Azure login (uses `AZURE_CREDENTIALS` secret — service principal JSON)
7. Deploy to Azure Web App (`azure/webapps-deploy@v3`, slot: Production)
8. Startup command: `bash startup.sh` (runs on Azure App Service)
9. Azure logout

**Deployment Type**: Direct to Azure App Service (no Docker containers)
- Azure unpacks zip to `/home/site/wwwroot`
- Runs `startup.sh`: installs deps → collectstatic → migrate → gunicorn
- Total deployment time: ~2-3 minutes

**What agents should do**:
1. Create feature branch and make changes
2. Test locally with `dev.ps1`
3. Push feature branch to remote
4. Create PR (DO NOT MERGE)
5. Instruct user: "Please review PR and merge to main when ready. GitHub Actions will auto-deploy to Azure."

**What agents should NOT do**:
- ❌ Merge PR automatically (user must review and approve)
- ❌ Push directly to `main` branch
- ❌ Modify `.github/workflows/deploy.yml` without user approval
- ❌ Run `az webapp ssh` commands automatically (always ask user to run manually)

### Azure startup.sh (Runs on Container Startup)
**Script**: `chorepoints/startup.sh`

```bash
#!/bin/bash
pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --noinput  # Upload to Azure Blob Storage
python manage.py migrate --noinput        # Apply pending migrations
gunicorn chorepoints.wsgi:application \
  --bind=0.0.0.0:8000 \
  --workers=2 \
  --threads=4 \
  --timeout=120 \
  --access-logfile '-' \
  --error-logfile '-' \
  --log-level info
```

**Deployment timeline**:
- Merge PR to `main` → GitHub Actions triggers
- Upload zip to Azure → Azure unpacks to `/home/site/wwwroot`
- Run `startup.sh` → Install deps, collect static, migrate, start Gunicorn
- Azure swaps traffic to new workers (graceful restart, ~30s)
- Total time: ~2-3 minutes from merge to live

### Post-Deployment Manual Steps (User Runs via SSH)
**When CSV data changed**:
```bash
az webapp ssh --name elija-agota --resource-group chorepoints-rg-us
cd /home/site/wwwroot
python manage.py load_initial_data  # Reloads chores.csv and rewards.csv
```

**When migrations added**:
```bash
az webapp ssh --name elija-agota --resource-group chorepoints-rg-us
cd /home/site/wwwroot
python manage.py migrate core  # Apply new migrations
python manage.py showmigrations core  # Verify migration status
```

**Checking logs**:
```bash
az webapp log tail --name elija-agota --resource-group chorepoints-rg-us
# Or via Azure Portal > Log stream
```

## 💾 Data & Migrations

### Initial Data Loading (CSV Files)
**Location**: `chorepoints/initial_data/`

**Files**:
- `chores.csv`: 19 default chores with emoji icons (🧹, 🗑️, 🍽️, etc.)
- `rewards.csv`: 21 default rewards with emoji icons (🍕, 🎮, 🎬, etc.)

**CSV format** (chores.csv):
```csv
Pavalyti kambarį,5,🧹,Sutvarkyti žaislus ir sukrauti lovą
Išnešti šiukšles,3,🗑️,Išnešti šiukšlių maišą į konteinerį
Plauti indus,4,🍽️,Išplauti ir sudėti indus į spintą
```

**Loading command**:
```bash
python manage.py load_initial_data
```

**What it does**:
- Reads CSV files (skip header row)
- Parses: title, points, icon_emoji, description (optional)
- Uses `get_or_create()` with title as unique key (safe to run multiple times)
- Assigns to current user (parent) or first User if not specified
- Marks all as `active=True`

**Migration 0011** (auto-loads CSV on first run):
```python
def load_initial_data(apps, schema_editor):
    # Runs load_initial_data command during migration
    # Safe to run even if chores/rewards already exist
```

### Creating New Migrations
**After model changes**:
```bash
python manage.py makemigrations core
```

**Migration naming**:
- `0001_initial.py`: Initial models (Kid, Chore, Reward, ChoreLog, Redemption)
- `0002_chorelog_redemption_status.py`: Add status field
- `0009_add_milestone_system.py`: Add map_position, highest_milestone
- `0012_add_kid_gender.py`: Add gender field for Lithuanian greetings

**Data migrations** (when changing data, not schema):
```python
# Example: 0013_update_chore_icons.py
from django.db import migrations

def update_icons(apps, schema_editor):
    Chore = apps.get_model('core', 'Chore')
    Chore.objects.filter(title="Pavalyti kambarį").update(icon_emoji="🧹")

class Migration(migrations.Migration):
    dependencies = [('core', '0012_add_kid_gender')]
    operations = [migrations.RunPython(update_icons)]
```

**Migration best practices**:
- Always test locally before pushing
- Never delete old migrations (breaks production DB)
- Use `RunPython` for data migrations (allows reverse operation)
- Check `showmigrations` before and after: `python manage.py showmigrations core`
- If migration fails in production, rollback: `python manage.py migrate core 0012_previous`

### Avoiding CSV Format Changes
- **DO NOT** change CSV column order without updating `load_initial_data.py`
- **DO NOT** remove columns (breaks existing CSV files)
- **CAN** add new columns at end (make them optional in code)
- **CAN** add new rows (new chores/rewards)
- **CAN** modify existing rows (updates will be applied on next load)

## 🔐 Security & Best Practices

### Production Security (Already Implemented)
- ✅ `DEBUG=False` (no stack traces exposed)
- ✅ `SECRET_KEY` from environment variable (50-char random)
- ✅ `ALLOWED_HOSTS` restricted to production domain
- ✅ `SECURE_SSL_REDIRECT=True` (HTTPS only)
- ✅ `SESSION_COOKIE_SECURE=True` (HTTPS cookies only)
- ✅ `CSRF_COOKIE_SECURE=True` (HTTPS CSRF tokens only)
- ✅ `SESSION_EXPIRE_AT_BROWSER_CLOSE=True` (force re-login)
- ✅ `SESSION_COOKIE_AGE=3600` (1 hour timeout)
- ✅ PostgreSQL SSL required (`sslmode=require`)
- ✅ TLS 1.2+ enforced (Azure App Service default)
- ✅ Azure Blob public access = blob level only (not container)

### Known Security Limitations (MVP — Document for Future)
- ⚠️ **Kid PINs stored plaintext** (no hashing) - OK for MVP, kids manage their own PINs
- ⚠️ **No rate limiting** on chore submissions - Could add Django Ratelimit middleware
- ⚠️ **No PENDING duplicate constraint** at DB level - Enforced in views only (race condition possible)
- ⚠️ **No 2FA for parent admin** - Relies on Django admin password strength

### OWASP Top 10 Coverage
1. **Injection**: Django ORM (parameterized queries), no raw SQL
2. **Broken Authentication**: Session-based auth, secure cookies, expiration
3. **Sensitive Data Exposure**: Env vars for secrets, HTTPS, SSL to DB
4. **XML External Entities**: N/A (no XML parsing)
5. **Broken Access Control**: `_get_kid()` checks, `on_delete=PROTECT` for FK
6. **Security Misconfiguration**: Separate production settings, DEBUG=False
7. **XSS**: Django auto-escapes templates, `mark_safe` only for admin icons
8. **Insecure Deserialization**: No pickle/yaml, only JSON session data
9. **Using Components with Known Vulnerabilities**: Dependabot enabled, update dependencies
10. **Insufficient Logging & Monitoring**: Azure App Service logs, Gunicorn access/error logs

### Transaction Safety Patterns
**Always use atomic transactions for balance mutations**:
```python
from django.db import transaction

def approve(self):
    if self.status != self.Status.PENDING:
        return False
    with transaction.atomic():
        # Refresh from DB to avoid race conditions
        self.child.refresh_from_db()
        
        # Update balance atomically
        self.child.points_balance += self.points_awarded
        self.child.map_position += self.points_awarded
        
        # Check milestones and award bonuses
        # ... milestone logic ...
        
        # Save all changes within transaction
        self.child.save(update_fields=["points_balance", "map_position", "highest_milestone"])
        self.status = self.Status.APPROVED
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "processed_at"])
    return True
```

**Why atomic()?**
- Prevents partial updates if error occurs mid-execution
- Ensures balance and status always stay in sync
- Protects against race conditions when approving multiple logs simultaneously
- Database-level isolation (serializable by default in PostgreSQL)

## 🎓 Agent-Specific Tips

### When to Use Which Tools
- **Code edits**: Use file editing tools, not terminal commands
- **Migrations**: Always use `python manage.py makemigrations`, not manual SQL
- **Testing**: Run `dev.ps1` locally, not direct pytest (ensures env setup)
- **Deployment**: Push to feature branch, create PR, let GitHub Actions handle deployment
- **Azure commands**: Read-only commands OK (show, list), write commands require user approval

### Adding/Modifying Tests
**When modifying behavior** (models, views, approval flow):
1. Add test case to appropriate `core/tests/test_*.py` file
2. Use Django TestCase or pytest fixtures
3. Test both success and failure paths
4. Include docstrings explaining what is being tested

**Test pattern example**:
```python
from django.test import TestCase
from core.models import Kid, Chore, ChoreLog

class ChoreLogApprovalTestCase(TestCase):
    def setUp(self):
        self.parent = User.objects.create_user('test_parent')
        self.kid = Kid.objects.create(parent=self.parent, name="Test Kid", pin="1234")
        self.chore = Chore.objects.create(parent=self.parent, title="Test Chore", points=5)
    
    def test_approve_pending_log_updates_balance(self):
        """Test that approving a PENDING log awards points to kid"""
        log = ChoreLog.objects.create(child=self.kid, chore=self.chore, points_awarded=5)
        old_balance = self.kid.points_balance
        
        success = log.approve()
        self.kid.refresh_from_db()
        
        self.assertTrue(success)
        self.assertEqual(log.status, ChoreLog.Status.APPROVED)
        self.assertEqual(self.kid.points_balance, old_balance + 5)
    
    def test_approve_already_approved_log_returns_false(self):
        """Test that approving an already APPROVED log does nothing"""
        log = ChoreLog.objects.create(child=self.kid, chore=self.chore, points_awarded=5)
        log.approve()  # First approval
        old_balance = self.kid.points_balance
        
        success = log.approve()  # Second approval attempt
        self.kid.refresh_from_db()
        
        self.assertFalse(success)
        self.assertEqual(self.kid.points_balance, old_balance)  # Balance unchanged
```

### UI Changes (Templates)
**When updating templates**:
1. Add ARIA labels for accessibility: `aria-label="Patvirtinti darbą"`, `role="button"`
2. Use semantic HTML: `<button>`, `<form>`, `<nav>`, not `<div onclick="">`
3. Keep JavaScript minimal (confetti animation, avatar selection only)
4. Test on mobile (responsive CSS, touch targets min 44x44px)
5. Ensure forms work without JS (progressive enhancement)

**Template pattern** (kid/home.html):
```django
{% for chore in chores %}
<form method="post" action="{% url 'complete_chore' chore.id %}">
  {% csrf_token %}
  <button type="submit" 
          class="chore-card"
          {% if chore.id in pending_chore_ids %}disabled{% endif %}
          aria-label="Užbaigti darbą: {{ chore.title }}, {{ chore.points }} taškai">
    <span class="icon" aria-hidden="true">{{ chore.display_icon }}</span>
    <span class="title">{{ chore.title }}</span>
    <span class="points">+{{ chore.points }} tšk</span>
    {% if chore.id in pending_chore_ids %}
    <span class="badge badge-pending">Laukia</span>
    {% endif %}
  </button>
</form>
{% endfor %}
```

### Writing Reversible Migrations
**Always include reverse operation**:
```python
class Migration(migrations.Migration):
    dependencies = [('core', '0012_previous')]
    
    operations = [
        migrations.AddField(
            model_name='kid',
            name='preferred_theme',
            field=models.CharField(max_length=20, default='default'),
        ),
        # Reverse: RemoveField
    ]
```

**For data migrations**:
```python
def forward(apps, schema_editor):
    Kid = apps.get_model('core', 'Kid')
    Kid.objects.filter(name__icontains='agota').update(gender='F')

def reverse(apps, schema_editor):
    Kid = apps.get_model('core', 'Kid')
    Kid.objects.filter(name__icontains='agota').update(gender='M')

class Migration(migrations.Migration):
    operations = [migrations.RunPython(forward, reverse)]
```

### Production Configuration (Minimal Changes)
**Agents should avoid modifying**:
- `.github/workflows/deploy.yml` (CI/CD pipeline)
- `startup.sh` (Azure startup script)
- `settings_production.py` (production Django settings)
- Azure App Service configuration (requires user approval)

**If changes needed**:
1. Document in PR why change is necessary
2. Test locally with equivalent configuration
3. Include rollback plan in PR description
4. Let user review and approve before merging

## 📚 References

### Documentation Links
- **`.github/copilot-instructions.md`**: Master reference (comprehensive agent guide with all architecture details)
- **`chorepoints/initial_data/README.md`**: CSV format specification
- **`chorepoints/core/models.py`**: Model definitions and approval workflow logic
- **`chorepoints/core/views.py`**: View patterns and session management
- **`chorepoints/core/admin.py`**: Admin actions and bulk approval logic
- **Django 5.0 Docs**: https://docs.djangoproject.com/en/5.0/
- **Azure App Service**: https://docs.microsoft.com/en-us/azure/app-service/
- **PostgreSQL 15**: https://www.postgresql.org/docs/15/

### Quick Troubleshooting
**Problem**: venv activation fails
**Solution**: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Problem**: Migrations conflict
**Solution**: `python manage.py showmigrations core`, check for branching, resolve with `--merge`

**Problem**: Static files 404 in production
**Solution**: Check Azure Blob container public access, verify `AZURE_ACCOUNT_KEY` set

**Problem**: Database connection timeout
**Solution**: Check PostgreSQL firewall rules, ensure Azure services allowed

**Problem**: Gunicorn worker timeout
**Solution**: Increase `--timeout` in startup.sh (currently 120s)

---

**Last Updated**: 2025-11-19  
**Version**: 2.0 (Comprehensive Agent Guide)  
**Maintainers**: AI Coding Agents (GitHub Copilot, ChatGPT, VS Code Agents)

## Quick Setup commands (local dev; PowerShell on Windows)
- Install dependencies, create virtual env, apply migrations and start dev server:
```powershell
cd chorepoints
./dev.ps1
```
- Fast start (activate venv + start server if already created):
```powershell
cd chorepoints
./run.ps1
```
- Seed local demo (seed_demo_lt loads a small set of data for testing):
```powershell
python manage.py seed_demo_lt --username <parent_username>
# Or load from CSV for production-like data
python manage.py load_initial_data
```

## Build / Docker
- Dockerfile exists at `chorepoints/Dockerfile` — use for containerizing app.
- Build and run locally using docker-compose declared in `docker-compose.yml` (top-level); if not, build image manually:
```bash
cd chorepoints
docker build -t kid-chore:local .
# Run the container (expose port 8000) and postgres
docker-compose up -d
```

## Tests & Playwright E2E
- Unit tests live under `core/tests/` — run with pytest (placeholder)
```bash
# (Optional) install pytest
pip install pytest pytest-django
pytest core/tests
```
- End-to-end tests (Playwright) are recommended to cover: kid login, chore submission, parent approval, confetti trigger.
  - Tests should be in `e2e/tests/` and follow UID/data-test attributes where possible.
  - To run local, start app then run the Playwright environment:
```bash
# Install node & playwright
cd e2e
npm install
npx playwright install --with-deps
npx playwright test
```
- In CI: run Playwright tests against staging App Service or a container running the `chorepoints` image.

## Code style & linting
- Python: follow PEP8. Use `black` and `flake8` if present.
- Keep template strings localized to Lithuanian for kid-facing UI. Admin text can be English.
- Use atomic DB transactions for any balance/money-like updates — see `models.py` (`transaction.atomic()` pattern used for approve()/reject() methods).

## PR instructions (agent-friendly)
- Always branch from `main`: `git checkout -b feature/<short-descr>`
- Run `./dev.ps1` locally and verify the following:
  - migrations applied
  - local HTTP routes operate: `/`, `/admin/`, `/kid/login/`
  - seed data present (run `seed_demo_lt` or `load_initial_data`)
- Commit descriptive messages with the format: `[<scope>] <short change> — <why>`
- Create PR, set reviewers, and include: 'What I changed' + 'Testing steps' + 'Any migration steps'
- DO NOT merge to `main` - user or maintainer will merge for production. Agents must stop at creating a PR.

## Environments & secrets
- Do not store secrets in the repo. Use Azure App Service settings for production secrets.
- Production required envs: `DJANGO_SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `AZURE_ACCOUNT_NAME`, `AZURE_ACCOUNT_KEY`.
- For local dev, `dev.ps1` handles a local SQLite DB. Add `.env` values or use `./dev.ps1` default.

## Deployment steps (for agents to prepare PRs)
- CI will auto-build and deploy `main` to Azure App Service. Agents should:
  1. Create a feature branch.
  2. Make changes locally and add tests.
  3. Create PR and let user/maintainer review & merge.
  4. After merge, deployment happens automatically. The human should ssh and run `python manage.py load_initial_data` if CSV changed.
- For containerization, we use `Dockerfile` + `docker-compose.yml` for local testing and GitHub Actions to push images to ACR then App Service.

## Data & migrations
- CSV data in `chorepoints/initial_data/` — `load_initial_data` loads them; `seed_demo_lt` seeds demonstration data.
- Avoid changing CSV format unless you update `load_initial_data` accordingly.
- When adding new model fields, add migrations: `python manage.py makemigrations core` → `python manage.py migrate`.

## Security & Best Practices
- PINs are plaintext for MVP and documented as such — don't change this without a migration plan.
- Always use `transaction.atomic()` when altering `Kid.points_balance` or `Kid.map_position`.
- Admin actions should require a review step before mass `approve()` operations.

## What agents must not do (policy)
- Never push directly to `main`. Always open a PR.
- Do not change production secrets or Azure config without explicit human approval.
- Do not run `az webapp ssh` or remote commands yourself — instead, include instructions and ask the human to run them (Copilot-instructions: rules around SSH are in `.github/copilot-instructions.md`).

## Agent-specific tips
- Use short, actionable commits and split changes into minimal PRs.
- Add or update tests whenever you modify behaviour (models, views, approval flow).
- For UI changes, add snapshot or functional tests in Playwright or update templates accordingly.
- When writing migration changes, include a reversible migration if possible.
- Keep changes to production configuration minimal and clearly documented in PR description.

## 🎯 Extra: How to Run a Smoke Test Locally

### Complete Smoke Test Procedure
```powershell
# 1. Start development server
cd chorepoints
./dev.ps1

# 2. Create parent admin account (if not exists)
python manage.py createsuperuser
# Username: tevai
# Email: (optional)
# Password: (secure password)

# 3. Seed demo data
python manage.py seed_demo_lt --username tevai
# Creates: Elija (M, PIN 1234, Island theme), Agota (F, PIN 1234, Space theme)
# Loads: 19 chores, 21 rewards with Lithuanian emoji icons

# 4. Test kid login flow
# Open: http://localhost:8000/kid/login/
# Select: Elija
# PIN: 1234
# Expected: Redirect to /kid/home/ with greeting "Sveikas, Elija!"

# 5. Submit chore as kid
# Click: "Pavalyti kambarį" (+5 tšk)
# Expected: PENDING badge appears, message "Pateikta patvirtinimui"
# Verify: Chore card shows "Laukia" badge

# 6. Approve chore in admin
# Open: http://localhost:8000/admin/
# Login as tevai
# Navigate: Core → Chore logs
# Filter: Status = Laukia (PENDING)
# Select: Elija's "Pavalyti kambarį" log
# Action: "Patvirtinti pasirinktus laukiančius darbus"
# Expected: Success message, log status = APPROVED

# 7. Verify points awarded
# Return to kid home: http://localhost:8000/kid/home/
# Expected: 
#   - Confetti animation (approved_new=True)
#   - Points balance increased by 5
#   - Map position increased by 5
#   - Chore "Pavalyti kambarį" no longer shows PENDING badge
#   - Approved history shows completed chore

# 8. Test milestone unlock (if crossing 50pts)
# Approve multiple chores until map_position >= 50
# Expected:
#   - Bronze badge (🥉) animation
#   - Bonus +10 points awarded automatically
#   - "Bronzos ženkliukas" milestone shown as achieved
```

### Automated Smoke Test (Future — pytest-based)
```python
# core/tests/test_smoke.py
import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from core.models import Kid, Chore, ChoreLog

User = get_user_model()

@pytest.mark.django_db
class TestSmokeTest:
    def test_complete_workflow(self):
        # Setup
        client = Client()
        parent = User.objects.create_user('smoke_parent', password='testpass')
        kid = Kid.objects.create(parent=parent, name="Smoke Kid", pin="1234", gender="M")
        chore = Chore.objects.create(parent=parent, title="Smoke Chore", points=5, icon_emoji="🧹")
        
        # Kid login
        response = client.post('/kid/login/', {'kid': kid.id, 'pin': '1234'})
        assert response.status_code == 302  # Redirect to home
        
        # Submit chore
        response = client.post(f'/kid/chore/{chore.id}/complete/')
        assert response.status_code == 302
        assert ChoreLog.objects.filter(child=kid, status=ChoreLog.Status.PENDING).count() == 1
        
        # Approve chore
        log = ChoreLog.objects.get(child=kid, chore=chore)
        success = log.approve()
        assert success
        assert log.status == ChoreLog.Status.APPROVED
        
        # Verify balance
        kid.refresh_from_db()
        assert kid.points_balance == 5
        assert kid.map_position == 5
```

## 🔄 Conflict Resolution (Agents)

### When Tests Fail on CI
**Scenario**: Tests fail after PR merge

**Agent action**:
1. Pull `main` and rebase feature branch:
   ```bash
   git checkout feature/my-branch
   git fetch origin
   git rebase origin/main
   ```
2. Run tests locally: `python manage.py test core` or `pytest core/tests`
3. If failure reproduces:
   - Debug test failure (check assertion, data setup, fixtures)
   - Fix code or test (not both if avoidable)
   - Commit fix: `[tests] Fix flaky test_approve_pending_log`
   - Push feature branch (do not merge yet)
4. If failure is intermittent/flaky:
   - Add test isolation (ensure test DB is clean between tests)
   - Use `TransactionTestCase` for tests that need committed data
   - Check for race conditions in approval workflow tests

### When Merge Conflict Occurs
**Scenario**: Another PR merged to `main`, conflicts with your feature branch

**Agent action**:
1. Fetch latest `main`:
   ```bash
   git fetch origin main
   ```
2. Rebase feature branch:
   ```bash
   git checkout feature/my-branch
   git rebase origin/main
   ```
3. Resolve conflicts manually:
   - Open conflicting files in editor
   - Look for `<<<<<<<`, `=======`, `>>>>>>>` markers
   - Choose correct version or merge both changes
   - Remove conflict markers
4. Continue rebase:
   ```bash
   git add .
   git rebase --continue
   ```
5. Force push rebased branch:
   ```bash
   git push --force-with-lease origin feature/my-branch
   ```
6. Update PR (GitHub automatically updates after force push)

### When Migration Conflicts Arise
**Scenario**: Two PRs both add migration 0013, creating duplicate migration files

**Agent action**:
1. Rename conflicting migration:
   ```bash
   mv core/migrations/0013_add_field_x.py core/migrations/0014_add_field_x.py
   ```
2. Update dependencies in migration file:
   ```python
   dependencies = [
       ('core', '0013_other_migration'),  # Update to previous migration
   ]
   ```
3. Recreate migrations (if complex):
   ```bash
   python manage.py makemigrations core --name add_field_x
   ```
4. Test locally: `python manage.py migrate core`
5. Commit: `[migrations] Resolve migration conflict, renumber to 0014`

---

**End of AGENTS.md**

If you need subfolder-specific `AGENTS.md` (e.g., `core/AGENTS.md` for model/view-specific tasks), let me know and I can create a scoped version with:
- Model-specific testing: `python manage.py test core.tests.test_models`
- View-specific debugging: Session handling, request.session inspection
- Admin customization: List filters, actions, inline forms
- Template debugging: Template tags, filters, context variables

**Current AGENTS.md is comprehensive and covers all essential agent workflows.**

