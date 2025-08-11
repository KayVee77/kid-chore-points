# ChorePoints

Local Django MVP for managing kids' chores and reward points. UI tekstai lokalizuoti į lietuvių kalbą (LANGUAGE_CODE=lt). Vaikai mato lietuviškas etiketes ir aprašus.

## Quickstart

```bash
python -m venv .venv
# Windows PowerShell activate:
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit http://127.0.0.1:8000/

### Admin (Tėvų) eiga
1. Log into /admin/ with superuser (parent).
2. Create Kids (set PIN, parent auto = current user if you leave parent manual selection accordingly).
3. Create Chores + Rewards.
4. Vaikas prisijungia /kid/login/ pasirinkdamas savo kortelę (emoji arba nuotrauka) ir įvesdamas PIN.
5. Vaikas /kid/home/ puslapyje pateikia darbus patvirtinimui ir prašo apdovanojimų.
6. Tėvai admin'e patvirtina arba atmeta laukiančius įrašus.

Data persists in SQLite (db.sqlite3). For local demo only.

## Nuotraukų (avatarų) įkėlimas
1. Nueikite į /admin/ -> Kids.
2. Pasirinkite vaiką arba sukurkite naują.
3. Laukelyje "Photo" pasirinkite JPG/PNG/WebP (rekomenduojama kvadratinė ~300x300).
4. Išsaugokite. Prisijungimo puslapyje bus rodoma nuotrauka (jei nėra – emoji).
5. Norėdami pašalinti nuotrauką – pažymėkite "Clear" ir išsaugokite (grįš emoji).

Failai saugomi `media/kid_avatars/`. (DEBUG režime media pateikiamas automatiškai.)

## Lokalizacija
- LANGUAGE_CODE=lt nustatyta `settings.py`.
- Sistemos pranešimai vaikui (sėkmės, klaidos) rodomi lietuviškai.
- Admin veiksmų pavadinimai (patvirtinti/atmesti) išversti.

## Starto PowerShell skriptas
Galite susikurti paprastą paleidimo skriptą `dev.ps1`:

```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Paleidimas:

```powershell
./dev.ps1
```

## Ateities idėjos
- Tėvų prietaisų skydelis be admin.
- Taškų serijos ir ženkleliai.
- PIN maišymas, unikalūs PENDING constraint'ai.
