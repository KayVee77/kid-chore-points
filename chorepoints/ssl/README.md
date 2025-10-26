# SSL Certificates for Local Development

This directory contains self-signed SSL certificates for HTTPS local development.

## Files (Auto-generated)

- `cert.pem` - Self-signed certificate
- `key.pem` - Private key

## Regenerate Certificates

If you need to regenerate the certificates (e.g., after cloning the repo or if IP address changed):

```bash
cd chorepoints
python generate_cert.py
```

## Security Note

⚠️ **These are self-signed certificates for development only!**

- Do NOT use in production
- Your browser and mobile devices will show security warnings - this is expected
- You need to manually accept/trust the certificate on each device

## Mobile Device Setup

When accessing from a mobile device:

1. Open `https://YOUR_LOCAL_IP:8000` in mobile browser
2. You'll see a security warning (e.g., "Your connection is not private")
3. Click "Advanced" or "Details"
4. Click "Proceed anyway" or "Accept risk and continue"
5. The app will load with HTTPS!

Some browsers (especially iOS Safari) may require additional steps:
- Go to Settings → General → About → Certificate Trust Settings
- Enable full trust for the certificate (after first visit)
