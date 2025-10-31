# Azure Deployment Guide (GitHub Actions) - ChorePoints App

Complete step-by-step guide to deploy the ChorePoints Django app to Azure using GitHub Actions for CI/CD.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Azure Resources Setup](#azure-resources-setup)
3. [GitHub Repository & Access](#github-repository--access)
4. [GitHub Actions Setup](#github-actions-setup)
5. [Application Configuration](#application-configuration)
6. [CI/CD Pipeline Configuration](#cicd-pipeline-configuration)
7. [Database Migration](#database-migration)
8. [Post-Deployment](#post-deployment)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- ✅ Azure account with active subscription ($50 credit)
- ✅ GitHub account with access to repository: `KayVee77/kid-chore-points`

### Required Tools (for local testing)
- Python 3.11+
- Azure CLI
- Git

### Knowledge Requirements
- Basic understanding of Git & GitHub
- Basic Azure portal navigation
- Basic command line usage

---

## Azure Resources Setup

### Step 1: Create Azure App Service

1. **Login to Azure Portal**
   - Go to https://portal.azure.com
   - Sign in with your Azure account

2. **Create Resource Group**
   ```
   - Click "Resource groups" → "+ Create"
   - Subscription: Your Azure subscription
   - Resource group name: `chorepoints-rg`
   - Region: `East US` (or closest to Lithuania)
   - Click "Review + create" → "Create"
   ```

3. **Create App Service Plan**
   ```
   - Search for "App Service plans" → "+ Create"
   - Resource Group: `chorepoints-rg`
   - Name: `chorepoints-plan`
   - Operating System: Linux
   - Region: Same as resource group
   - Pricing tier: Basic B1 ($13/month)
     * 1 core, 1.75GB RAM
     * Good for family app
   - Click "Review + create" → "Create"
   ```

4. **Create Web App**
   ```
   - Search for "App Services" → "+ Create" → "Web App"
   - Resource Group: `chorepoints-rg`
   - Name: `chorepoints-app` (must be globally unique)
     * Your URL will be: chorepoints-app.azurewebsites.net
     * If taken, try: chorepoints-app-[yourname]
   - Publish: Code
   - Runtime stack: Python 3.11
   - Operating System: Linux
   - Region: Same as resource group
   - App Service Plan: `chorepoints-plan`
   - Click "Review + create" → "Create"
   ```

### Step 2: Create Azure Database for PostgreSQL

1. **Create PostgreSQL Flexible Server**
   ```
   - Search for "Azure Database for PostgreSQL flexible servers"
   - Click "+ Create"
   - Resource Group: `chorepoints-rg`
   - Server name: `chorepoints-db`
   - Region: Same as resource group
   - PostgreSQL version: 15
   - Workload type: Development (burstable tier)
   - Compute + storage:
     * Compute tier: Burstable
     * Compute size: B1ms (1 vCore, 2 GiB RAM) - ~$12/month
     * Storage: 32 GiB
   - Authentication: PostgreSQL authentication only
   - Admin username: `chorepoints_admin`
   - Password: Create strong password (save this securely!)
   - Click "Next: Networking"
   ```

2. **Configure Database Networking**
   ```
   - Connectivity method: Public access
   - Firewall rules:
     ✅ Allow public access from any Azure service
     ✅ Add current client IP (if you want to connect from local)
   - Click "Review + create" → "Create"
   ```

3. **Create Database**
   ```
   After server is created:
   - Go to your PostgreSQL server
   - Click "Databases" (left menu)
   - Click "+ Add"
   - Database name: `chorepoints_db`
   - Click "Save"
   ```

### Step 3: Create Azure Storage Account (for Media Files)

1. **Create Storage Account**
   ```
   - Search for "Storage accounts" → "+ Create"
   - Resource Group: `chorepoints-rg`
   - Storage account name: `chorepointsstorage` (must be unique, lowercase only)
   - Region: Same as resource group
   - Performance: Standard
   - Redundancy: LRS (Locally-redundant storage) - cheapest option
   - Click "Review + create" → "Create"
   ```

2. **Create Blob Containers**
   ```
   After storage account is created:
   - Go to your storage account
   - Click "Containers" (left menu under Data storage)
   - Create three containers:
     1. Name: `media` → Public access level: Blob
     2. Name: `static` → Public access level: Blob
     3. Name: `backups` → Public access level: Private
   ```

3. **Get Storage Connection String**
   ```
   - In storage account, click "Access keys" (left menu)
   - Copy "Connection string" from key1
   - Format: DefaultEndpointsProtocol=https;AccountName=<name>;AccountKey=<key>;EndpointSuffix=core.windows.net
   - Save this for later configuration (DO NOT commit to Git)
   ```

---

## GitHub Repository & Access

### Step 1: Confirm Repository Access
1. Visit https://github.com/KayVee77/kid-chore-points and verify you have push or fork permissions.
2. If you cannot push directly:
   - Click **Fork** → personal namespace → keep branch name `main`.
   - Update remote origin locally to point to your fork.

### Step 2: Clone Locally (optional but recommended)
```bash
cd c:\Users\User\Documents\python_apps
git clone https://github.com/<your-account>/kid-chore-points.git
cd kid-chore-points
```
- Work on feature branches locally, then push to GitHub.
- Keep `main` protected so only reviewed changes land there.

### Step 3: Enable GitHub Actions
1. In the GitHub repo, go to **Settings → Actions → General**.
2. Ensure "Allow all actions and reusable workflows" is enabled.
3. If Actions were disabled for a fork, click **Enable GitHub Actions** on the Actions tab.

---

## GitHub Actions Setup

### Step 1: Create Azure Service Principal (for deployments)
We will authenticate the GitHub workflow against Azure via a service principal.

```bash
az ad sp create-for-rbac \
  --name chorepoints-gh-deploy \
  --role contributor \
  --scopes /subscriptions/7a4e0763-6e2c-4871-aa4f-488ddb0c6df9/resourceGroups/chorepoints-rg \
  --sdk-auth
```

- Replace `<SUBSCRIPTION_ID>` with the ID shown in the Azure Portal (Home → Subscriptions).
- Copy the JSON output. You will paste it into a GitHub secret in Step 2.

### Step 2: Add Required GitHub Secrets
In the GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**, create the following entries:

| Secret Name | Value |
|-------------|-------|
| `AZURE_CREDENTIALS` | Entire JSON from the service principal command above |
| `DJANGO_SECRET_KEY` | `secrets.token_urlsafe(50)` output |
| `DB_PASSWORD` | Strong PostgreSQL password you set earlier |
| `AZURE_ACCOUNT_KEY` | Storage account key (Access keys → key1) |

Also add non-secret configuration as repository variables (same screen → **Variables** tab) so they can be reused inside workflows:

| Variable Name | Example Value |
|---------------|---------------|
| `AZURE_WEBAPP_NAME` | `chorepoints-app` |
| `AZURE_RG` | `chorepoints-rg` |
| `AZURE_LOCATION` | `westeurope` |
| `DB_HOST` | `chorepoints-db.postgres.database.azure.com` |
| `DB_NAME` | `chorepoints_db` |
| `DB_USER` | `chorepoints_admin` |
| `AZURE_ACCOUNT_NAME` | `chorepointsstorage` |

> Tip: keep credentials out of version control. GitHub Actions automatically masks secrets in logs.

### Step 3: (Optional) Configure Branch Protection
- In **Settings → Branches**, add a protection rule for `main`.
- Require PR reviews and successful GitHub Action runs before merging.

---

## Application Configuration

### Step 1: Prepare Production Settings

We need to create production-ready configuration files. These will be added to the repository.

1. **Create `chorepoints/chorepoints/settings_production.py`**

```python
"""
Production settings for ChorePoints deployed on Azure App Service.
Imports from base settings.py and overrides for production.
"""
from .settings import *
import os

# Security Settings
DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = [
    os.environ.get('WEBSITE_HOSTNAME'),  # Azure provides this
    'chorepoints-app.azurewebsites.net',  # Your app URL
    '*.azurewebsites.net',
]

# Database Configuration (PostgreSQL on Azure)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Azure Storage for Static and Media Files
DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
STATICFILES_STORAGE = 'storages.backends.azure_storage.AzureStorage'

AZURE_ACCOUNT_NAME = os.environ.get('AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = os.environ.get('AZURE_ACCOUNT_KEY')
AZURE_CONTAINER = 'media'
AZURE_STATIC_CONTAINER = 'static'

# Static files (CSS, JavaScript, Images)
STATIC_URL = f'https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_STATIC_CONTAINER}/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (uploads)
MEDIA_URL = f'https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_CONTAINER}/'

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

2. **Update `chorepoints/requirements.txt`**

Add production dependencies:

```txt
Django>=5.0,<5.3
Pillow>=10.4,<11.0
django-extensions>=3.2,<4.0
werkzeug>=3.0,<4.0
pyOpenSSL>=24.0,<25.0

# Production dependencies
gunicorn>=21.0,<22.0
psycopg2-binary>=2.9,<3.0
django-storages[azure]>=1.14,<2.0
whitenoise>=6.6,<7.0
python-decouple>=3.8,<4.0
```

3. **Create `chorepoints/.env.example`**

Template for environment variables:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here-change-in-production
DJANGO_SETTINGS_MODULE=chorepoints.settings_production

# Database (Azure PostgreSQL)
DB_NAME=chorepoints_db
DB_USER=chorepoints_admin
DB_PASSWORD=your-db-password-here
DB_HOST=chorepoints-db.postgres.database.azure.com

# Azure Storage
AZURE_ACCOUNT_NAME=chorepointsstorage
AZURE_ACCOUNT_KEY=your-storage-key-here

# Azure App Service (auto-provided)
WEBSITE_HOSTNAME=chorepoints-app.azurewebsites.net
```

4. **Create `chorepoints/startup.sh`**

Startup script for Azure App Service:

```bash
#!/bin/bash

echo "Starting ChorePoints Django App..."

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate --noinput

# Create superuser if it doesn't exist (optional)
# python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'changeme')"

# Start Gunicorn
gunicorn chorepoints.wsgi:application \
    --bind=0.0.0.0:8000 \
    --workers=2 \
    --threads=4 \
    --timeout=120 \
    --access-logfile '-' \
    --error-logfile '-' \
    --log-level info
```

Make it executable:
```bash
chmod +x chorepoints/startup.sh
```

---

## CI/CD Pipeline Configuration

### Step 1: Create GitHub Actions Workflow
Create the directory `.github/workflows/` (if it does not exist) and add `deploy.yml` with the following content:

```yaml
name: Deploy ChorePoints

on:
   push:
      branches: ["main"]
   pull_request:
      branches: ["main"]
   workflow_dispatch:

env:
   PYTHON_VERSION: "3.11"
   DJANGO_SETTINGS_MODULE: "chorepoints.settings"

jobs:
   build-and-deploy:
      runs-on: ubuntu-latest

      steps:
         - name: Checkout source
            uses: actions/checkout@v4

         - name: Set up Python ${{ env.PYTHON_VERSION }}
            uses: actions/setup-python@v5
            with:
               python-version: ${{ env.PYTHON_VERSION }}

         - name: Install dependencies
            working-directory: chorepoints
            run: |
               python -m pip install --upgrade pip
               pip install -r requirements.txt

         - name: Run unit tests (placeholder)
            working-directory: chorepoints
            run: |
               pip install pytest pytest-django
               # pytest core/tests  # Enable once tests are added
            continue-on-error: true

         - name: Collect static files
            working-directory: chorepoints
            run: python manage.py collectstatic --noinput

         - name: Archive application
            run: |
               cd chorepoints
               zip -r ../chorepoints-package.zip . -x "__pycache__/*" "*.pyc" "*.pyo" "*.pytest_cache/*"

         - name: Azure login
            uses: azure/login@v2
            with:
               creds: ${{ secrets.AZURE_CREDENTIALS }}

         - name: Deploy to Azure Web App
            uses: azure/webapps-deploy@v3
            with:
               app-name: ${{ vars.AZURE_WEBAPP_NAME }}
               package: chorepoints-package.zip
               slot-name: Production
               startup-command: "bash startup.sh"

         - name: Logout
            if: always()
            run: az logout
```

> Adjust the testing step once you add formal test coverage. Fail the build by removing `continue-on-error` when ready.

### Step 2: Commit the Workflow
1. Commit `deploy.yml` to the repository (ideally via pull request).
2. Verify that GitHub automatically detects the new workflow under the **Actions** tab.

### Step 3: Run the Pipeline
1. Push to `main` or click **Run workflow** (workflow_dispatch) to trigger manually.
2. Monitor the job logs in GitHub Actions.
3. On first run, expect ~8–10 minutes (dependency install + deployment).

### Step 4: Approve & Merge Pull Requests
- Configure branch protection so PRs must pass the `Deploy ChorePoints` workflow before merging into `main`.
- For feature development, target the default branch; the workflow will run in "build only" mode on PRs and deploy only on `push` to `main`.

---

## Database Migration

### Step 1: Configure App Service Environment Variables

**Option A: Using Azure CLI** (Recommended - Fast!)

First, login to Azure and set your subscription:
```powershell
# Login to Azure
az login

# Set your subscription (replace with your subscription name or ID)
az account set --subscription "7a4e0763-6e2c-4871-aa4f-488ddb0c6df9"
```

Now configure all environment variables with one command:
```powershell
# Use your existing Django secret key
$DJANGO_SECRET="VYYuFkyTmwQgCHx_0UC3qtYB1NG_EeyJ-k3sNcooYjFZLZwGz29uY5uFg-57KF-FV8o"

# Get your storage account key
$AZURE_KEY=$(az storage account keys list --resource-group chorepoints-rg-us --account-name chorepointsstorage --query "[0].value" -o tsv)

# Configure all app settings at once
az webapp config appsettings set `
  --resource-group chorepoints-rg-us `
  --name elija-agota `
  --settings `
    DJANGO_SECRET_KEY="$DJANGO_SECRET" `
    DJANGO_SETTINGS_MODULE="chorepoints.settings_production" `
    DB_NAME="chorepoints_db" `
    DB_USER="chorepoints_admin" `
    DB_PASSWORD="<your-db-password>" `
    DB_HOST="chorepoints-db.postgres.database.azure.com" `
    AZURE_ACCOUNT_NAME="chorepointsstorage" `
    AZURE_ACCOUNT_KEY="$AZURE_KEY" `
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"
```

Configure the startup command:
```powershell
az webapp config set `
  --resource-group chorepoints-rg-us `
  --name elija-agota `
  --startup-file "bash startup.sh"
```

Verify the settings:
```powershell
# List all app settings (passwords will be masked)
az webapp config appsettings list `
  --resource-group chorepoints-rg-us `
  --name elija-agota `
  --output table
```

**Option B: Using Azure Portal** (Manual)

1. **Add Configuration Settings**
   ```
   - Go to https://portal.azure.com
   - Navigate to your App Service "elija-agota"
   - Click "Configuration" (left menu under Settings)
   - Click "New application setting" for each:
   ```
   
   | Name | Value |
   |------|-------|
   | `DJANGO_SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
   | `DJANGO_SETTINGS_MODULE` | `chorepoints.settings_production` |
   | `DB_NAME` | `chorepoints_db` |
   | `DB_USER` | `chorepoints_admin` |
   | `DB_PASSWORD` | Your PostgreSQL password |
   | `DB_HOST` | `chorepoints-db.postgres.database.azure.com` |
   | `AZURE_ACCOUNT_NAME` | `chorepointsstorage` |
   | `AZURE_ACCOUNT_KEY` | Get from: Portal → Storage account "chorepointsstorage" → Access keys → key1 → Show → Copy |
   | `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |
   
   - Click "OK" after each setting
   - Click "Save" at the top to apply all changes
   - Click "Continue" when warned about restart

2. **Configure Startup Command**
   ```
   - Still in Configuration
   - Click "General settings" tab
   - Startup Command: `bash startup.sh`
   - Stack: Python
   - Major version: 3
   - Minor version: 11
   - Click "Save" (top)
   - Click "Continue" to restart the app
   ```

### Step 2: Run Initial Migrations

**Option A: Via SSH in Azure Portal** (Recommended)

1. **Connect via SSH**
   ```
   - In App Service, click "SSH" (left menu under Development Tools)
   - Click "Go"
   - A terminal will open in browser
   ```

2. **Run Migration Commands**
   ```bash
   cd /home/site/wwwroot
   
   # Run migrations
   python manage.py migrate
   
   # Create superuser (interactive)
   python manage.py createsuperuser
   # Username: admin
   # Email: your-email@example.com
   # Password: (create strong password)
   
   # Load demo data (optional)
   python manage.py seed_demo_lt --username admin
   ```

**Option B: Via Azure CLI** (Alternative)

```bash
# Install Azure CLI first: https://docs.microsoft.com/cli/azure/install-azure-cli

# Login
az login

# Set subscription
az account set --subscription "Your Subscription Name"

# Run migration
az webapp ssh --name chorepoints-app --resource-group chorepoints-rg

# Then run migration commands as in Option A
```

---

## Post-Deployment

### Step 1: Verify Deployment

1. **Check Application URL**
   ```
   - Open browser
   - Go to: https://chorepoints-app.azurewebsites.net
   - You should see the ChorePoints landing page
   ```

2. **Test Login**
   ```
   - Go to: https://chorepoints-app.azurewebsites.net/admin/
   - Login with superuser credentials created earlier
   - Verify you can access admin panel
   ```

3. **Test Kid Login**
   ```
   - Go to: https://chorepoints-app.azurewebsites.net/kid/login/
   - Login with demo kids (if you ran seed_demo_lt)
   - Elija: PIN 1234
   - Agota: PIN 5678
   ```

### Step 2: Configure Custom Domain (Optional)

1. **Add Custom Domain**
   ```
   - In App Service, click "Custom domains" (left menu)
   - Click "Add custom domain"
   - Enter your domain (e.g., chorepoints.yourfamily.com)
   - Follow DNS verification steps
   - Click "Validate" then "Add"
   ```

2. **Add SSL Certificate**
   ```
   - Still in Custom domains
   - Click on your custom domain
   - Click "Add binding"
   - TLS/SSL type: App Service Managed Certificate (Free)
   - Click "Add binding"
   ```

### Step 3: Set Up Monitoring

1. **Enable Application Insights**
   ```
   - In App Service, click "Application Insights" (left menu)
   - Click "Turn on Application Insights"
   - Create new resource or use existing
   - Click "Apply"
   ```

2. **Configure Alerts**
   ```
   - Go to Application Insights resource
   - Click "Alerts" (left menu)
   - Click "+ Create" → "Alert rule"
   - Set up alerts for:
     * HTTP 5xx errors
     * Response time > 5 seconds
     * Failed requests > 10 in 5 minutes
   ```

### Step 4: Set Up Backups

1. **Configure Database Backup**
   ```
   - Go to PostgreSQL server
   - Click "Backup and restore" (left menu)
   - Backups are automatic (7-35 days retention)
   - Point-in-time restore available
   ```

2. **Configure App Service Backup**
   ```
   - In App Service, click "Backups" (left menu)
   - Requires Standard tier or higher (upgrade from Basic if needed)
   - Configure storage account for backups
   - Set backup schedule
   ```

### Step 5: Performance Optimization

1. **Enable Caching**
   
   Add to `settings_production.py`:
   ```python
   # Redis cache (requires Azure Redis Cache - additional cost)
   # Or use built-in file-based cache for free
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
           'LOCATION': '/tmp/django_cache',
       }
   }
   ```

2. **Configure CDN** (Optional - for static files)
   ```
   - Create Azure CDN endpoint
   - Point to your storage account
   - Update STATIC_URL in settings to CDN URL
   ```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Pipeline Fails - Build Error

**Symptoms**: Build stage fails with dependency errors

**Solution**:
```bash
# Check requirements.txt is correct
# Ensure all dependencies have version pins
# Check Python version matches (3.11)
```

#### 2. App Won't Start - 500 Error

**Symptoms**: App shows generic error page

**Solution**:
```bash
# Check logs in Azure Portal
# App Service → Monitoring → Log stream
# Common issues:
- Missing environment variables
- Database connection failure
- Static files not collected
```

#### 3. Database Connection Failed

**Symptoms**: "Could not connect to server" error

**Solution**:
```bash
# Check firewall rules in PostgreSQL
# Azure Portal → PostgreSQL → Networking
# Ensure "Allow public access from any Azure service" is enabled
# Check connection string in App Service configuration
```

#### 4. Static Files Not Loading

**Symptoms**: CSS/JS not loading, broken styling

**Solution**:
```bash
# SSH into App Service
cd /home/site/wwwroot
python manage.py collectstatic --noinput

# Check Azure Storage container permissions
# Ensure 'static' container has public blob access
```

#### 5. Media Upload Fails

**Symptoms**: Can't upload kid avatars or icons

**Solution**:
```bash
# Check Azure Storage connection string
# Verify AZURE_ACCOUNT_KEY in App Service configuration
# Ensure 'media' container exists and has blob access
```

### Viewing Logs

**Application Logs**:
```
- App Service → Monitoring → Log stream
- Or download logs:
  App Service → Monitoring → App Service logs
  Enable: Application logging (Filesystem)
  Level: Information
```

**Database Logs**:
```
- PostgreSQL → Monitoring → Logs
- Query Store for performance insights
```

**Pipeline Logs**:
```
- GitHub → Actions → Select workflow run
- Expand each job/step to inspect logs and artifacts
```

### Performance Optimization Tips

1. **Upgrade App Service Plan** if needed
   ```
   - Monitor CPU/Memory usage
   - If consistently > 80%, consider upgrading to B2 ($26/month)
   ```

2. **Database Connection Pooling**
   
   Add to `settings_production.py`:
   ```python
   DATABASES['default']['CONN_MAX_AGE'] = 60  # Keep connections for 60 seconds
   ```

3. **Enable Compression**
   
   Add to `settings_production.py`:
   ```python
   MIDDLEWARE = [
       'django.middleware.gzip.GZipMiddleware',  # Add at top
       # ... other middleware
   ]
   ```

---

## Cost Breakdown (Monthly)

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| App Service | Basic B1 (1 core, 1.75GB) | $13.14 |
| PostgreSQL | Burstable B1ms (1 core, 2GB) | $12.41 |
| Storage Account | LRS, ~10GB | $0.50 |
| Bandwidth | First 100GB | Free |
| **TOTAL** | | **~$26/month** |

**Your $50 budget**: ~2 months of hosting

### Cost Optimization Tips

1. **Use Free Tier** (first 12 months if new Azure account)
   - App Service: 10 web apps for free (F1 tier)
   - Azure Database: First month free trial
   - Storage: 5GB free

2. **Development/Production Split**
   - Use SQLite for development (free)
   - Only run production on weekends initially
   - Scale down/up as needed

3. **Auto-shutdown** (if not in use)
   - Create automation to stop App Service at night
   - Start manually when needed

---

## Security Checklist

Before going live:

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY (50+ random characters)
- [ ] Enable HTTPS only (done automatically on Azure)
- [ ] Set DEBUG = False in production
- [ ] Configure proper ALLOWED_HOSTS
- [ ] Enable Azure DDoS protection
- [ ] Set up Application Insights for monitoring
- [ ] Configure backup strategy
- [ ] Review database firewall rules
- [ ] Enable authentication for admin panel
- [ ] Set up email notifications for errors
- [ ] Review and limit CORS settings
- [ ] Enable rate limiting for APIs
- [ ] Regular security updates (keep dependencies updated)

---

## Maintenance Schedule

### Daily
- Monitor Application Insights for errors
- Check pipeline runs for failures

### Weekly
- Review performance metrics
- Check storage usage
- Review security alerts

### Monthly
- Update Python dependencies
- Review and optimize database queries
- Check backup integrity
- Review costs and optimize resources

---

## Support and Resources

### Azure Documentation
- App Service: https://learn.microsoft.com/azure/app-service/
- PostgreSQL: https://learn.microsoft.com/azure/postgresql/
- GitHub Actions: https://docs.github.com/actions

### Django Resources
- Deployment: https://docs.djangoproject.com/en/5.0/howto/deployment/
- PostgreSQL: https://docs.djangoproject.com/en/5.0/ref/databases/#postgresql-notes

### Getting Help
- Azure Support: https://azure.microsoft.com/support/
- Stack Overflow: Tag questions with `azure-app-service` and `django`
- GitHub Issues: Report app-specific issues

---

## Summary

You now have:
✅ Complete Azure infrastructure setup
✅ Automated CI/CD pipeline
✅ Production-ready Django configuration
✅ Database migration procedures
✅ Monitoring and logging
✅ Security best practices
✅ Troubleshooting guide

**Next Steps**:
1. Follow this guide step-by-step
2. Test thoroughly before giving to family
3. Monitor costs in Azure Portal
4. Set up billing alerts
5. Enjoy your deployed app! 🎉

**Estimated Setup Time**: 2-3 hours for first deployment
