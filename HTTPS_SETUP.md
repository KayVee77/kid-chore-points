# HTTPS Local Development Setup

This branch adds HTTPS support for local development to resolve "insecure connection" warnings on mobile devices.

## Quick Start

### For HTTPS (Recommended for mobile testing):
```powershell
.\chorepoints\run_https.ps1
```

### For HTTP (Basic local testing):
```powershell
.\chorepoints\run.ps1
```

## What Changed

### New Files
- `chorepoints/run_https.ps1` - HTTPS server launcher with auto-SSL setup
- `chorepoints/generate_cert.py` - Self-signed certificate generator
- `chorepoints/ssl/` - Directory for SSL certificates (auto-generated)
- `chorepoints/ssl/README.md` - SSL certificate documentation

### Modified Files
- `chorepoints/requirements.txt` - Added django-extensions, werkzeug, pyOpenSSL
- `chorepoints/settings.py` - Added django_extensions app, updated ALLOWED_HOSTS
- `chorepoints/run.ps1` - Now binds to 0.0.0.0 for network access
- `.gitignore` - Excludes SSL certificate files

## Mobile Access

### HTTP (shows security warnings):
```
http://192.168.0.35:8000
```

### HTTPS (no warnings after accepting cert once):
```
https://192.168.0.35:8000
```

## Mobile Setup Instructions

1. Start the HTTPS server: `.\chorepoints\run_https.ps1`
2. On your phone, open `https://192.168.0.35:8000`
3. You'll see a security warning (expected for self-signed cert)
4. Click "Advanced" → "Proceed anyway" or similar
5. The app will load securely with HTTPS!

### iOS Safari Additional Steps
If you continue to see warnings:
1. Settings → General → About → Certificate Trust Settings
2. Enable full trust for the "ChorePoints Local Dev" certificate

## How It Works

1. **Self-Signed Certificate**: `generate_cert.py` creates a local SSL certificate
2. **Django Extensions**: Uses `runserver_plus` command which supports HTTPS
3. **Werkzeug**: Provides the WSGI server with SSL support
4. **Auto-Detection**: Script detects your Wi-Fi IP for easy mobile access

## Security Notes

⚠️ **For development only!**
- Self-signed certificates are NOT secure for production
- Browsers will show warnings - this is expected
- Each device needs to manually accept the certificate once
- Certificates valid for 1 year from generation date

## Troubleshooting

### Certificate not working after IP change?
Regenerate the certificate:
```powershell
cd chorepoints
python generate_cert.py
```

### Firewall blocking connections?
Add Windows Firewall rule (run as Administrator):
```powershell
netsh advfirewall firewall add rule name="Django Dev Server" dir=in action=allow protocol=TCP localport=8000
```

### Can't find your IP?
```powershell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -like '*Wi-Fi*'}
```

## Technical Details

### Dependencies
- **django-extensions**: Provides `runserver_plus` with SSL support
- **werkzeug**: WSGI utilities and development server
- **pyOpenSSL**: SSL certificate generation

### Certificate Details
- Algorithm: RSA 2048-bit
- Validity: 1 year
- Subject Alternative Names: localhost, *.local, 127.0.0.1, your local IP
- Issuer: ChorePoints Local Dev (self-signed)

## Merging to Main

Once tested and approved:
```bash
git checkout main
git merge feature/https-local-dev
git push origin main
```
