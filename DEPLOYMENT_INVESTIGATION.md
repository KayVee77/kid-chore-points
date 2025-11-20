# Deployment Issue Analysis & Resolution

## Problem Identified
Code changes pushed to GitHub Actions are not reflecting on Azure App Service despite workflow completing successfully.

## Root Cause
**Azure App Service Build Settings are DISABLED:**
- `SCM_DO_BUILD_DURING_DEPLOYMENT = false`
- `ENABLE_ORYX_BUILD = false`

This means:
1. The zip file is being uploaded to Azure
2. Azure extracts the zip to `/home/site/wwwroot`
3. BUT the `startup.sh` script may not be running properly
4. OR the files are being extracted to the wrong location
5. The app continues running old code from a previous deployment

## Deployment Workflow Analysis

Current workflow (`.github/workflows/deploy.yml`):
1. ✓ Checks out code
2. ✓ Installs dependencies locally (for testing)
3. ✓ Creates zip file of `chorepoints/` directory
4. ✓ Logs into Azure with service principal
5. ? Uses `azure/webapps-deploy@v3` to upload zip
6. ? Sets startup command to `bash startup.sh`

**Potential Issues:**
- The `clean: true` parameter might be causing problems
- The startup command might not be persisted correctly
- Azure might not be extracting the zip to the correct location
- The app might need a restart BEFORE the new startup script runs

## Solution Approaches

### Option 1: Use Kudu ZIP Deploy API (RECOMMENDED)
Instead of using `azure/webapps-deploy@v3`, use direct Kudu API:

```yaml
- name: Deploy via Kudu ZIP API
  run: |
    # Get publishing credentials
    PUBLISH_PROFILE=$(az webapp deployment list-publishing-profiles \
      --name elija-agota \
      --resource-group chorepoints-rg-us \
      --query "[?publishMethod=='MSDeploy']|[0].{user:userName,pass:userPWD}" \
      -o json)
    
    USERNAME=$(echo $PUBLISH_PROFILE | jq -r '.user')
    PASSWORD=$(echo $PUBLISH_PROFILE | jq -r '.pass')
    
    # Deploy using Kudu ZIP API
    curl -X POST \
      -u "$USERNAME:$PASSWORD" \
      --data-binary @"./chorepoints.zip" \
      https://elija-agota.scm.azurewebsites.net/api/zipdeploy
    
    # Restart app
    az webapp restart --name elija-agota --resource-group chorepoints-rg-us
```

### Option 2: Enable Oryx Build
Enable build during deployment:

```bash
az webapp config appsettings set \
  --name elija-agota \
  --resource-group chorepoints-rg-us \
  --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true ENABLE_ORYX_BUILD=true
```

### Option 3: Use Run From Package
Deploy as a package instead of extracting:

```bash
az webapp config appsettings set \
  --name elija-agota \
  --resource-group chorepoints-rg-us \
  --settings WEBSITE_RUN_FROM_PACKAGE=1
```

## Recommended Fix (Combination Approach)

1. **Update workflow to use Kudu ZIP Deploy**
2. **Add explicit restart after deployment**
3. **Add deployment verification**
4. **Keep build disabled** (we pre-install deps in GitHub Actions)

## Test Plan

1. Deploy changes with new workflow
2. Verify health check endpoint returns new version
3. Verify CSV file contains test marker
4. Verify DEPLOYMENT_VERSION.txt is accessible
5. Test actual app functionality

## Current Test Artifacts

- `/kid/health-check/` endpoint with version `2025.11.20-deployment-test`
- `chores.csv` with marker `[CSV Updated 2025-11-20]`
- `DEPLOYMENT_VERSION.txt` with timestamp

These will confirm when deployment actually works.
