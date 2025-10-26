# Azure DevOps Deployment Guide - ChorePoints App

Complete step-by-step guide to deploy the ChorePoints Django app to Azure using Azure DevOps CI/CD pipeline.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Azure Resources Setup](#azure-resources-setup)
3. [Azure DevOps Setup](#azure-devops-setup)
4. [Application Configuration](#application-configuration)
5. [CI/CD Pipeline Configuration](#cicd-pipeline-configuration)
6. [Database Migration](#database-migration)
7. [Post-Deployment](#post-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- ✅ Azure account with active subscription ($50 credit)
- ✅ Azure DevOps account (free tier available)
- ✅ Access to GitHub repository: `KayVee77/kid-chore-points`

### Required Tools (for local testing)
- Python 3.11+
- Azure CLI
- Git

### Knowledge Requirements
- Basic understanding of Git
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
   - Password: Create strong password (save this!)
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
   - Save this for later configuration
   ```

---

## Azure DevOps Setup

### Step 1: Create Azure DevOps Organization and Project

1. **Create Organization**
   ```
   - Go to https://dev.azure.com
   - Sign in with Microsoft account
   - Click "New organization"
   - Organization name: `chorepoints-devops` (or your choice)
   - Region: Choose closest to you
   - Click "Continue"
   ```

2. **Create Project**
   ```
   - Click "+ New project"
   - Project name: `ChorePoints`
   - Visibility: Private
   - Version control: Git
   - Work item process: Agile
   - Click "Create"
   ```

### Step 2: Connect GitHub Repository

1. **Import Repository**
   ```
   - In your project, go to "Repos" → "Files"
   - Click "Import" button at top
   - Clone URL: https://github.com/KayVee77/kid-chore-points.git
   - Requires authorization: Yes
   - Click "Import"
   ```

   OR if you want to keep syncing with GitHub:

2. **Set up GitHub Connection** (Alternative - keeps sync with GitHub)
   ```
   - Go to Project Settings (bottom left)
   - Click "Service connections" under Pipelines
   - Click "New service connection"
   - Choose "GitHub"
   - Click "Next"
   - Choose "Grant authorization" or "Personal access token"
   - Follow prompts to authorize
   - Connection name: `GitHub-KayVee77`
   - Click "Save"
   ```

### Step 3: Create Service Connection to Azure

1. **Create Azure Service Principal**
   ```
   - In Azure DevOps, go to Project Settings → Service connections
   - Click "New service connection"
   - Select "Azure Resource Manager" → "Next"
   - Authentication method: "Service principal (automatic)"
   - Scope level: Subscription
   - Subscription: Select your Azure subscription
   - Resource group: `chorepoints-rg`
   - Service connection name: `Azure-ChorePoints`
   - Grant access permission to all pipelines: ✅ Check this
   - Click "Save"
   ```

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

### Step 1: Create Azure Pipeline YAML

Create `azure-pipelines.yml` in the repository root:

```yaml
# Azure DevOps Pipeline for ChorePoints Django App
# Builds, tests, and deploys to Azure App Service

trigger:
  branches:
    include:
    - main
    - feature/*
  paths:
    exclude:
    - README.md
    - docs/*

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.11'
  azureServiceConnection: 'Azure-ChorePoints'
  webAppName: 'chorepoints-app'
  
stages:
- stage: Build
  displayName: 'Build and Test'
  jobs:
  - job: BuildJob
    displayName: 'Build Django App'
    steps:
    
    - task: UsePythonVersion@0
      displayName: 'Use Python $(pythonVersion)'
      inputs:
        versionSpec: '$(pythonVersion)'
    
    - script: |
        python -m pip install --upgrade pip
        pip install -r chorepoints/requirements.txt
      displayName: 'Install dependencies'
      workingDirectory: '$(System.DefaultWorkingDirectory)'
    
    - script: |
        pip install pytest pytest-django
        # Add your tests here when ready
        # pytest chorepoints/core/tests/
      displayName: 'Run tests'
      workingDirectory: '$(System.DefaultWorkingDirectory)'
      continueOnError: true
    
    - script: |
        cd chorepoints
        python manage.py collectstatic --noinput
      displayName: 'Collect static files'
      env:
        DJANGO_SETTINGS_MODULE: 'chorepoints.settings'
    
    - task: ArchiveFiles@2
      displayName: 'Archive application'
      inputs:
        rootFolderOrFile: '$(System.DefaultWorkingDirectory)/chorepoints'
        includeRootFolder: false
        archiveType: 'zip'
        archiveFile: '$(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip'
        replaceExistingArchive: true
    
    - task: PublishBuildArtifacts@1
      displayName: 'Publish artifacts'
      inputs:
        pathToPublish: '$(Build.ArtifactStagingDirectory)'
        artifactName: 'drop'

- stage: Deploy
  displayName: 'Deploy to Azure'
  dependsOn: Build
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployWeb
    displayName: 'Deploy to Azure App Service'
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebApp@1
            displayName: 'Deploy Azure Web App'
            inputs:
              azureSubscription: '$(azureServiceConnection)'
              appType: 'webAppLinux'
              appName: '$(webAppName)'
              package: '$(Pipeline.Workspace)/drop/$(Build.BuildId).zip'
              runtimeStack: 'PYTHON|3.11'
              startUpCommand: 'bash startup.sh'
```

### Step 2: Configure Pipeline in Azure DevOps

1. **Create Pipeline**
   ```
   - In Azure DevOps, go to "Pipelines" → "Pipelines"
   - Click "New pipeline"
   - Select "Azure Repos Git"
   - Select your repository
   - Choose "Existing Azure Pipelines YAML file"
   - Path: `/azure-pipelines.yml`
   - Click "Continue"
   ```

2. **Configure Pipeline Variables**
   ```
   - Click "Variables" button (top right)
   - Add these variables:
   
   Variable Name              | Value                                    | Secret?
   ---------------------------|------------------------------------------|--------
   DJANGO_SECRET_KEY          | (generate random 50 char string)        | ✅ Yes
   DB_NAME                    | chorepoints_db                          | No
   DB_USER                    | chorepoints_admin                       | No
   DB_PASSWORD                | (your PostgreSQL password)              | ✅ Yes
   DB_HOST                    | chorepoints-db.postgres.database.azure.com | No
   AZURE_ACCOUNT_NAME         | chorepointsstorage                      | No
   AZURE_ACCOUNT_KEY          | (your storage account key)              | ✅ Yes
   WEBSITE_HOSTNAME           | chorepoints-app.azurewebsites.net       | No
   ```

   To generate SECRET_KEY in Python:
   ```python
   import secrets
   print(secrets.token_urlsafe(50))
   ```

3. **Save and Run Pipeline**
   ```
   - Click "Save and run"
   - Add commit message: "Add Azure DevOps CI/CD pipeline"
   - Click "Save and run"
   - Monitor the pipeline execution
   ```

---

## Database Migration

### Step 1: Configure App Service Environment Variables

1. **Add Configuration Settings**
   ```
   - Go to Azure Portal → Your App Service
   - Click "Configuration" (left menu under Settings)
   - Click "New application setting" for each:
   
   Name                       | Value
   ---------------------------|------------------------------------------
   DJANGO_SECRET_KEY          | (copy from pipeline variables)
   DJANGO_SETTINGS_MODULE     | chorepoints.settings_production
   DB_NAME                    | chorepoints_db
   DB_USER                    | chorepoints_admin
   DB_PASSWORD                | (your PostgreSQL password)
   DB_HOST                    | chorepoints-db.postgres.database.azure.com
   AZURE_ACCOUNT_NAME         | chorepointsstorage
   AZURE_ACCOUNT_KEY          | (your storage account key)
   SCM_DO_BUILD_DURING_DEPLOYMENT | true
   ```

2. **Configure Startup Command**
   ```
   - Still in Configuration
   - Go to "General settings" tab
   - Startup Command: `bash startup.sh`
   - Stack: Python
   - Major version: 3
   - Minor version: 11
   - Click "Save" (top)
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
- Azure DevOps → Pipelines → Select run
- Click on any stage/job to see detailed logs
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
- App Service: https://docs.microsoft.com/azure/app-service/
- PostgreSQL: https://docs.microsoft.com/azure/postgresql/
- DevOps: https://docs.microsoft.com/azure/devops/

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
