# Database Rebuild Quick Reference

## When Database Gets Wiped

If migrations wipe your data, quickly rebuild with:

```powershell
cd chorepoints
python manage.py load_initial_data --reset
```

This recreates:
- ✅ Parent user: `tevai` / `tevai123`
- ✅ Kids: Elija & Agota (PIN: 1234)
- ✅ 20 Chores (from CSV)
- ✅ 15 Rewards (from CSV)

## Quick Commands

### Full Reset & Reload
```powershell
# Delete database
Remove-Item db.sqlite3

# Recreate tables
python manage.py migrate

# Load all initial data
python manage.py load_initial_data
```

### Update Just the Data
```powershell
# Keep database, just refresh chores/rewards
python manage.py load_initial_data --reset
```

### Custom Parent Account
```powershell
python manage.py load_initial_data --parent-username myname --parent-password mypass123
```

## Login Info

After running `load_initial_data`:

**Admin Panel:**
- URL: http://127.0.0.1:8000/admin/
- User: `tevai`
- Pass: `tevai123`

**Kids Login:**
- URL: http://127.0.0.1:8000/kid/login/
- Elija: PIN `1234` 🚀
- Agota: PIN `1234` 🌸

## CSV Files Location

Edit these to customize initial data:
- `chorepoints/initial_data/Darbai__5_8_m_____prad_ios_paketas.csv` (chores)
- `chorepoints/initial_data/Apdovanojimai___prad_ios_paketas.csv` (rewards)

See `chorepoints/initial_data/README.md` for CSV format details.
