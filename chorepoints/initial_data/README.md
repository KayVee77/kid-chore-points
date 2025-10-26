# Initial Data Setup

This folder contains the initial setup data for the ChorePoints system that can be reused for database rebuilds.

## Files

- **`users.json`** - Admin users and kids configuration (editable!)
- **`chores.csv`** - Available chores with points and emojis (20 chores)
- **`rewards.csv`** - Available rewards with costs and emojis (15 rewards)

## Default Setup (Edit users.json to customize!)

### Admin Users (from users.json)
```json
{
  "admin_users": [
    {
      "username": "tevai",
      "password": "tevai123",
      "email": "tevai@example.com",
      "is_staff": true,
      "is_superuser": true
    }
  ]
}
```

### Kids (from users.json)
```json
{
  "kids": [
    {
      "name": "Elija",
      "pin": "1234",
      "avatar_emoji": "🚀",
      "map_theme": "SPACE"
    },
    {
      "name": "Agota",
      "pin": "1234",
      "avatar_emoji": "🌸",
      "map_theme": "ISLAND"
    }
  ]
}
```

**Map themes:** `ISLAND`, `SPACE`, `RAINBOW`

### Chores (from chores.csv)
20 chores loaded with emojis - easy to edit in CSV format!

### Rewards (from rewards.csv)
15 rewards loaded with emojis - easy to edit in CSV format!

## Usage

### Load Initial Data

```powershell
# Load with default settings from JSON/CSV files
python manage.py load_initial_data

# Reset all data and load fresh
python manage.py load_initial_data --reset
```

### Customize Your Setup

**1. Edit users.json** to add/modify admin users and kids:
```json
{
  "admin_users": [
    {
      "username": "your_username",
      "password": "your_password",
      "email": "you@example.com",
      "is_staff": true,
      "is_superuser": true
    }
  ],
  "kids": [
    {
      "name": "YourKid",
      "pin": "5678",
      "avatar_emoji": "🦄",
      "map_theme": "RAINBOW"
    }
  ]
}
```

**2. Edit chores.csv** to add/modify chores:
```csv
title,points,icon_emoji,description
My Custom Chore,15,⭐,Description here
```

**3. Edit rewards.csv** to add/modify rewards:
```csv
title,cost_points,icon_emoji,description
My Custom Reward,100,🏆,Description here
```

**4. Run the command:**
```powershell
python manage.py load_initial_data --reset
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

Simply edit the JSON/CSV files and run:

```powershell
python manage.py load_initial_data --reset
```

## File Formats

### users.json Format
```json
{
  "admin_users": [
    {
      "username": "string",
      "password": "string",
      "email": "string",
      "is_staff": true,
      "is_superuser": true
    }
  ],
  "kids": [
    {
      "name": "string",
      "pin": "string (4 digits recommended)",
      "avatar_emoji": "emoji character",
      "map_theme": "ISLAND|SPACE|RAINBOW"
    }
  ]
}
```

### chores.csv Format
```csv
title,points,icon_emoji,description
```

**Required columns:**
- `title` - Chore name (string)
- `points` - Points awarded (integer: 5, 10, 15, etc.)
- `icon_emoji` - Emoji to display (any emoji)
- `description` - Optional description (not used in app currently)

### rewards.csv Format
```csv
title,cost_points,icon_emoji,description
```

**Required columns:**
- `title` - Reward name (string)
- `cost_points` - Points cost (integer: 10, 20, 50, etc.)
- `icon_emoji` - Emoji to display (any emoji)
- `description` - Optional description (not used in app currently)

## Security Notes

⚠️ **Important:**
- Default password `tevai123` is for development only
- Change passwords immediately in production
- PINs should be unique for each child
- Edit `users.json` to set your own credentials before first run
- Keep `users.json` out of public repositories if it contains real passwords

## Customization Tips

### Add More Admins
Edit `users.json` and add another object to the `admin_users` array:
```json
{
  "admin_users": [
    { "username": "tevai", "password": "tevai123", ... },
    { "username": "mama", "password": "mama123", "email": "mama@example.com", "is_staff": true, "is_superuser": true }
  ]
}
```

### Add More Kids
Edit `users.json` and add to the `kids` array:
```json
{
  "kids": [
    { "name": "Elija", ... },
    { "name": "Agota", ... },
    { "name": "Jonas", "pin": "4567", "avatar_emoji": "⚽", "map_theme": "SPACE" }
  ]
}
```

### Customize Chores/Rewards
Simply edit the CSV files in Excel, LibreOffice, or any text editor. Make sure to keep the header row!
