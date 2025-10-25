# ChorePoints AI Agent Instructions

## Project Overview
Django 5 MVP for managing kids' chores & rewards with approval workflow. **Lithuanian-first UI** (LANGUAGE_CODE=lt) for kids; admin uses Django default. Session-based kid authentication via PIN (no Django User).

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

### Quick Start (Windows PowerShell)
```powershell
./chorepoints/dev.ps1          # Auto venv, deps, migrate, runserver, opens browser
./chorepoints/dev.ps1 -Reset   # Recreate venv from scratch
```
Script uses requirements.txt hash caching (`.venv/.req_hash`) to skip reinstalls.

### Essential Commands
```bash
# Seed Lithuanian demo data (Elija, Agota, default chores/rewards with emoji)
python manage.py seed_demo_lt --username <parent_username>

# Migrations (6 total as of 0006)
python manage.py makemigrations core
python manage.py migrate core

# Create parent account
python manage.py createsuperuser
```

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
- Exclude: `*.pyc`, `__pycache__/`, `db.sqlite3`, `media/`, `.venv/` (see .gitignore)
- Migrations committed (0001-0006); db.sqlite3 ignored
- One nested .git was removed (chorepoints/.git) - repo root is parent folder

## Known Limitations (MVP Scope)
- PIN stored plaintext (no hashing)
- No rate limiting on chore submissions
- No unique DB constraint for PENDING duplicates (logic in views only)
- SQLite only (not production-ready)
- No REST API; server-rendered Django templates with minimal JS (confetti canvas, avatar selection)
