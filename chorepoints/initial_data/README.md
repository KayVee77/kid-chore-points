# Initial Data Setup

This folder contains the initial setup data for the ChorePoints system that can be reused for database rebuilds.

## Files

- `Darbai__5_8_m_____prad_ios_paketas.csv` - Chores for kids aged 5-8 (20 chores)
- `Apdovanojimai___prad_ios_paketas.csv` - Rewards (15 rewards)

## Default Setup

### Parent User
- **Username:** `tevai`
- **Password:** `tevai123` (change after first login!)
- **Email:** `tevai@example.com`
- **Role:** Admin/Superuser

### Kids
| Name | PIN | Emoji |
|------|-----|-------|
| Elija | 1234 | 🚀 |
| Agota | 1234 | 🌸 |

### Chores (20 total)
Loaded from `Darbai__5_8_m_____prad_ios_paketas.csv`
- **Easy (🟢):** 5 points each (8 chores)
- **Medium (🟡):** 10 points each (7 chores)
- **Hard (🔴):** 15 points each (5 chores)

Categories: bedroom, self-care, kitchen, home maintenance, laundry, pets, school

### Rewards (15 total)
Loaded from `Apdovanojimai___prad_ios_paketas.csv`
- **Experience (🌟):** 10-120 points
- **Items (🎁):** 10-200 points
- **Privileges (👑):** 20 points

## Usage

### Load Initial Data (Fresh Start)

```powershell
# Load with default settings
python manage.py load_initial_data

# Reset all data and load fresh
python manage.py load_initial_data --reset

# Custom parent credentials
python manage.py load_initial_data --parent-username mano_vardas --parent-password slaptazodis123
```

### Quick Database Rebuild

If you need to start fresh after migrations:

```powershell
# Delete old database
Remove-Item db.sqlite3

# Run migrations
python manage.py migrate

# Load initial data
python manage.py load_initial_data
```

### Update Kids or Chores

To modify the initial setup:

1. Edit the CSV files in this folder
2. Run: `python manage.py load_initial_data --reset`

## CSV Format

### Chores CSV (Darbai__5_8_m_____prad_ios_paketas.csv)
```
id,pavadinimas,aprašymas,kategorija,sudėtingumas,taškai,dažnumas,amžMin,amžMaks,saugosPastabos
```

**sudėtingumas values:**
- `lengva` → 🟢 (Easy)
- `vidutinė` → 🟡 (Medium)
- `didelė` → 🔴 (Hard)

### Rewards CSV (Apdovanojimai___prad_ios_paketas.csv)
```
id,pavadinimas,tipas,taškai,pastabos
```

**tipas values:**
- `daiktinis` → 🎁 (Item)
- `patirtis` → 🌟 (Experience)
- `privilegija` → 👑 (Privilege)

## Security Notes

⚠️ **Important:**
- Default password `tevai123` is for development only
- Change passwords immediately in production
- PINs (1234) should be unique for each child in production
- Keep CSV files out of version control if they contain sensitive data

## Customization

To customize the default setup, edit the `load_initial_data.py` command:
```
chorepoints/core/management/commands/load_initial_data.py
```

You can modify:
- Default parent credentials
- Kids names, PINs, and emojis
- Emoji mappings for difficulty/types
- CSV file paths and parsing logic
