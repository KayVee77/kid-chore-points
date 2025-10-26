# Taškų nuotykis (ChorePoints)

> Linksmas Django 5 MVP, skirtas vaikų darbelių bei apdovanojimų taškų valdymui. Vaikų sąsaja visiškai lietuviška (LANGUAGE_CODE=lt), tėvai naudoja standartinį Django admin.

## 💻 Reikalavimai

- Python 3.13 (veikia ir su 3.11+)
- Windows PowerShell (greičiausiai naudojamas dev.ps1 skriptas)

## 🚀 Greitas paleidimas (Rekomenduojama)

### Pirmą kartą arba po pakeitimų:

```powershell
cd chorepoints
./dev.ps1
```

Skriptas automatiškai:
1. Sukuria / aktyvuoja `.venv` (jei trūksta)
2. Įdiegia priklausomybes (tik jei `requirements.txt` pasikeitė)
3. Paleidžia migracijas
4. Atidaro naršyklę http://127.0.0.1:8000/
5. Startuoja Django serverį (nutraukimas `CTRL+C`)

### Kasdienis greitas paleidimas:

```powershell
cd chorepoints
./run.ps1
```

Skriptas tik:
1. Aktyvuoja esamą `.venv`
2. Atidaro naršyklę
3. Startuoja Django serverį

**Papildomos parinktys:**

```powershell
./dev.ps1 -Reset      # iš naujo kuria venv
./dev.ps1 -Port 8010  # startuoja kitu portu
./run.ps1 -Port 8010  # greitas startas kitu portu
```

## 🔧 Rankinis paleidimas (jei nenaudojate skripto)

```powershell
cd chorepoints

python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Sustabdyti serverį: `CTRL+C` PowerShell lange.

## 👤 Pirmas prisijungimas tėvams

```powershell
python manage.py createsuperuser
```

Prisijunkite prie admino: http://127.0.0.1:8000/admin/

**Pamiršote slaptažodį?**

```powershell
python manage.py changepassword <vartotojo_vardas>
```

## 👧 Vaikų prisijungimas (PIN)

- Vaikai neprisijungia per Django User – naudojamas sesijos PIN modelis.
- Prisijungimo adresas: http://127.0.0.1:8000/kid/login/
- Vaikas pasirenka kortelę (nuotrauka -> emoji -> raidės monograma) ir įveda PIN.
- PIN keičiamas admin'e `Kid` įraše (saugomas paprastu tekstu; MVP ribojimas).

## 🌱 Demo duomenų sėkla

```powershell
python manage.py seed_demo_lt --username <tevų_vartotojas>
```

Sukuria pavyzdį: vaikus (Eliją, Agotą, PIN 1234), numatytus darbus ir apdovanojimus su emoji.

## 🧭 Pagrindinis scenarijus

1. Tėvai/admin prisijungia prie `/admin/`
2. Kuria vaikus (PIN, emoji arba įkelia nuotrauką)
3. Kuria darbus ir apdovanojimus (gali parinkti emoji arba įkelti ikoną)
4. Vaikas prisijungia `kid/login`, mato balansą, progresą, pateikia darbą/atlygį
5. Tėvai admin'e patvirtina ar atmeta laukiančius įrašus
6. Patvirtinus taškai automatiškai sumuojami / nuskaitomi

### Taškų vertės gairė

- Orientacinė konversija: 5 taškai ≈ 1 €.
- Tai tik gairė tėvų biudžetavimui; realūs taškai nurodyti prie darbų ir apdovanojimų.

## ✅ Patvirtinimo darbo eiga

- Vaikas pateikia darbą / apdovanojimo prašymą → sukuriamas `PENDING` įrašas (`ChoreLog` / `Redemption`).
- Vaizduotė `kid/home.html` rodo laukiančius įrašus (draudžia dubliuoti tą patį darbą / apdovanojimą, kol laukia patvirtinimo).
- Tėvai admin'e naudoja masinio veiksmų mygtukus „Patvirtinti“ / „Atmesti“.
- Patvirtinus kviečiami modelių `approve()` metodai: balansai koreguojami atominiu būdu (`transaction.atomic`).
- Vaikas, grįžęs į puslapį, mato konfeti animaciją, jei yra naujų patvirtinimų nuo paskutinio vizito.

## 🖼️ Nuotraukos ir ikonėlės

**Vaikų avatarai**
- Laukelis „Photo“ admin'e → įkelkite kvadratinę JPG/PNG/WebP (~300x300)
- Išsaugant automatiškai sumažinama iki 400x400 (jei reikalinga)
- Jei nėra nuotraukos, naudojamas emoji; jei emoji tuščias – pirmos vardo raidės monograma

**Darbo / apdovanojimo ikonėlės**
- Emoji arba paveikslėlis (`icon_image`, automatiškai sumažinamas iki 128x128)
- Seed komanda užpildo numatytus emoji (`🗑️`, `🧸`, `🍬`, …)

Failai saugomi:
- `media/kid_avatars/`
- `media/chore_icons/`
- `media/reward_icons/`

DEBUG režime Django pats aptarnauja šiuos failus; gamybai reikalinga atskira failų tarnyba.

## 🧰 Vystymo patarimai

- Visas Django kodas vienoje aplikacijoje `core/`
- Šablonai: `core/templates/` (vaiko login/home, pagrindinis landing)
- Admin konfigūracija: `core/admin.py`
- Modelių logika (taškų skaičiavimas, ikonų apdorojimas): `core/models.py`
- Sėklos komanda: `core/management/commands/seed_demo_lt.py`

## 🧪 Testavimas

- Automatiniai testai šiuo metu neįdiegti (MVP). Rekomenduojama tikrinti per admin ir UI.
- Jei norite pridėti pytest – pridėkite į `requirements.txt` ir sukurkite testų katalogą.

## 🔐 Žinomi ribojimai

- PIN saugojami atviru tekstu (galima ateityje naudoti Django hash).
- Nėra rate-limiting (vaikas teoriškai gali spaudyti mygtukus labai greitai – nors dubliavimas užblokuotas).
- PENDING dubliavimas tik logikos lygyje (per views); DB constraint dar nepridėtas.
- SQLite – skirta tik lokaliam demonstravimui.
- Nėra REST API; viskas server-side renderinta.

## 🤝 Naudingi scenarijai

```powershell
# Keisti PIN konkrečiam vaikui
python manage.py shell
>>> from core.models import Kid
>>> kid = Kid.objects.get(name="Elija")
>>> kid.pin = "4321"
>>> kid.save()

# Masinis sėklos atnaujinimas (emocijoms):
python manage.py seed_demo_lt --username tevai

# Sustabdyti serverį (jei paleistas per dev.ps1)
CTRL+C PowerShell lange
```

## 📦 Deployment pastabos

- Numatytasis SECRET_KEY skirtas tik dev (`settings.py`).
- Į gamybą reikės atskiro WSGI/ASGI serverio (Gunicorn/uvicorn) bei statinių/media failų servisavimo.
- Susikonfigūruokite `ALLOWED_HOSTS`, `DEBUG=False`, `CSRF_TRUSTED_ORIGINS`, `SECURE_*` nustatymus.

---

Jei kyla klausimų arba norite prisidėti – drąsiai atsidarykite issues / pull requests GitHub'e! Taškų nuotykis laukia 🚀
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

### Points-to-euro rule of thumb

- Approximate conversion: 5 pts ≈ €1.
- This is only guidance for budgeting; actual point values are defined per chore/reward.

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
