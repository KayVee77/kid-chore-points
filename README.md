# Taškų Nuotykis (ChorePoints)

> Django 5 MVP for managing kids' chores and reward points with a **Lithuanian-first UI**. Parents manage via Django Admin, kids use a fun Lithuanian interface with PIN authentication.

## 🌐 Production App

**Live at:** https://elija-agota.azurewebsites.net/

- **Hosted on:** Azure App Service (North Central US)
- **Database:** PostgreSQL 15
- **Auto-deployment:** GitHub Actions from `main` branch
- **Login:** Ask admin for credentials

**Production Notes:**
- Session timeout: 1 hour
- Sessions expire on browser close (for security)
- HTTPS only with secure cookies
- Static/media files served from Azure Blob Storage

## 💻 Local Development

### Requirements
- Python 3.11+ (tested with 3.13)
- Windows PowerShell

### Quick Start (Recommended)

```powershell
cd chorepoints
./dev.ps1
```

The script automatically:
1. Creates/activates `.venv` (if missing)
2. Installs dependencies (only if `requirements.txt` changed)
3. Runs migrations
4. Opens browser at http://localhost:8000/
5. Starts Django dev server (stop with `CTRL+C`)

**Additional Options:**
```powershell
./dev.ps1 -Reset      # Recreate venv from scratch
./dev.ps1 -Port 8010  # Start on different port
```

### Quick Daily Start

```powershell
cd chorepoints
./run.ps1             # Just activate venv and start server
```

### Manual Setup (if not using scripts)

```powershell
cd chorepoints
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 🔐 Authentication

### Parent Access (Django Admin)
```powershell
python manage.py createsuperuser
```
Then visit: http://localhost:8000/admin/

**Forgot password?**
```powershell
python manage.py changepassword <username>
```

### Kid Access (PIN-based)
- Kids don't use Django User accounts - PIN-based session auth
- Visit: http://localhost:8000/kid/login/
- Select kid card (photo → emoji → letter fallback) and enter PIN
- PIN managed in admin (plaintext for MVP - security limitation noted)

## 🌱 Demo Data Seeding

```powershell
python manage.py seed_demo_lt --username <parent_username>
```

Creates sample data:
- Kids: Elija (M, Island theme, PIN 1234), Agota (F, Space theme, PIN 1234)
- 34 Lithuanian chores from CSV with emoji icons
- 21 rewards from CSV with emoji icons

## 🎯 How It Works

### Parent Workflow
1. Log into `/admin/` as superuser
2. Create Kids (set name, gender, PIN, theme, optional photo)
3. Create Chores (title, points, emoji/icon)
4. Create Rewards (title, cost, emoji/icon)
5. Approve or reject pending chore submissions and reward requests

### Kid Workflow
1. Log in at `/kid/login/` (select name, enter PIN)
2. View points balance and adventure map progress
3. Submit completed chores (creates PENDING ChoreLog)
4. Request rewards (creates PENDING Redemption)
5. See confetti animation when parents approve! 🎉

### Approval System
- Kid submits → creates `PENDING` record (no immediate point change)
- Prevents duplicate PENDING submissions for same chore/reward
- Parent approves via admin bulk actions → calls `approve()` method
- Points updated atomically with `transaction.atomic()`
- Confetti triggers when kid returns and sees new approvals

## 📊 Points System

### Two Separate Counters
1. **points_balance**: Current spendable points (increases with chores/adjustments, decreases with rewards)
2. **map_position**: Total lifetime earned points (only increases, powers adventure map)

### Point Values Guide
- **Guideline:** 5 points ≈ €1 (for parent budgeting)
- Actual values defined per chore/reward in CSV files

### Adventure Map
- Kid advances along themed path (Island/Space/Rainbow)
- Unlocks milestones at specific positions (50, 100, 200, 300, etc.)
- Each milestone awards bonus points
- Infinite progression system (bonuses every 500 points after last milestone)

## 🖼️ Photos & Icons

### Kid Avatars
1. Go to `/admin/` → Kids
2. Upload square JPG/PNG/WebP (~300x300 recommended)
3. Auto-resizes to 400x400 on save
4. Fallback: emoji → first letter monogram
5. Files saved to: `media/kid_avatars/`

### Chore/Reward Icons
- Choose emoji OR upload image (auto-resizes to 128x128)
- Seed command pre-fills with emoji (🗑️, 🧸, 🍬, etc.)
- Files saved to: `media/chore_icons/`, `media/reward_icons/`
- DEBUG mode: Django serves media files automatically

## 🌍 Lithuanian Localization

- **LANGUAGE_CODE=lt** set in settings.py
- All kid-facing messages in Lithuanian
- Gender-aware greetings: "Sveikas, Elija!" (boy) vs "Sveika, Agota!" (girl)
- Admin action descriptions translated: "Patvirtinti pasirinktus laukiančius darbus"
- Model help texts in Lithuanian

## 🚀 Deployment (Azure)

**⚠️ IMPORTANT:** `main` branch auto-deploys to production!

### Branch Strategy
- **`main`**: Production - triggers GitHub Actions → Azure deployment
- **Feature branches**: For development (`feature/my-feature`)
- **Always test locally before merging to main!**

### Azure Management

```bash
# SSH into production (requires Azure CLI)
az webapp ssh --name elija-agota --resource-group chorepoints-rg-us

# Restart app
az webapp restart --name elija-agota --resource-group chorepoints-rg-us

# View logs
az webapp log tail --name elija-agota --resource-group chorepoints-rg-us

# Run migrations (inside SSH)
cd /home/site/wwwroot
python manage.py migrate core
```

### Environment Settings
- Production uses `settings_production.py` (overwrites base settings)
- Environment variables: `DJANGO_SECRET_KEY`, `DB_*`, `AZURE_ACCOUNT_*`
- `startup.sh` runs on Azure startup: deps → collectstatic → migrate → gunicorn

## 🛠️ Development Tips

### Project Structure
- Single app: `core/` (models, views, admin, templates, management commands)
- Templates: `core/templates/` (base.html, index.html, kid/login.html, kid/home.html)
- Media uploads: Auto-served in DEBUG mode
- CSV data: `initial_data/chores.csv`, `initial_data/rewards.csv`

### Migrations
```powershell
python manage.py makemigrations core
python manage.py migrate core
```
Current: 12 migrations (0001-0012)

### Useful Commands

```powershell
# Change kid PIN
python manage.py shell
>>> from core.models import Kid
>>> kid = Kid.objects.get(name="Elija")
>>> kid.pin = "4321"
>>> kid.save()

# Refresh demo data (overwrites existing)
python manage.py seed_demo_lt --username tevai

# Stop dev server
CTRL+C in PowerShell
```

## 🔐 Known Limitations (MVP)

- **PIN stored plaintext** (not hashed) - documented security limitation
- No rate limiting on submissions (duplicate prevention in views only)
- No unique DB constraint for PENDING duplicates
- No REST API - server-rendered templates with minimal JS
- No automated tests yet
- Session-based auth only (no JWT/OAuth)

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Test locally with `./dev.ps1`
3. Commit changes with clear messages
4. **Do NOT push directly to `main`** (triggers production deploy)
5. Open PR for review

## 📚 Documentation

- **Production Docs**: `AZURE_DEPLOYMENT_GUIDE.md`
- **Copilot Instructions**: `.github/copilot-instructions.md`
- **CSV Format**: `chorepoints/initial_data/README.md`

## 🎮 User Accounts

### Production (Azure)
- Parent: `tevai` (password not in repo)
- Kids: Elija (M, PIN 1234), Agota (F, PIN 1234)
- Admin: https://elija-agota.azurewebsites.net/admin/

### Local Development
- Create superuser: `python manage.py createsuperuser`
- Seed demo kids: `python manage.py seed_demo_lt --username <your_username>`

---

**Enjoy your Taškų Nuotykis! 🚀**

Questions? Open an issue on GitHub!
