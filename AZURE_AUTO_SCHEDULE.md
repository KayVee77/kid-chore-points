# Azure App Service Auto-Shutdown Schedule Guide

**Goal**: Automatically stop the app at 22:00 (10 PM) and start at 12:00 (noon) Lithuania time to save costs during nights.

**Cost Savings**: ~14 hours/day stopped = ~$6-8/month savings

---

## Option 1: Manual Start/Stop (Simplest - No Cost)

### Stop the App
```powershell
az webapp stop --name elija-agota --resource-group chorepoints-rg-us
```

### Start the App
```powershell
az webapp start --name elija-agota --resource-group chorepoints-rg-us
```

### Azure Portal UI:
1. Go to https://portal.azure.com
2. Navigate to App Service "elija-agota"
3. Click **Stop** button at the top
4. Click **Start** button when needed

**Pros**: Free, simple, immediate
**Cons**: You must remember to start/stop manually

---

## Option 2: Azure Automation (Recommended - Fully Automated)

### Prerequisites
- Azure Automation account (Free tier available - 500 minutes/month)
- System-assigned managed identity for authentication

### Step 1: Create Automation Account

1. **Go to Azure Portal** → Search for "Automation Accounts"
2. Click **+ Create**
3. Fill in details:
   - **Subscription**: Your subscription
   - **Resource Group**: `chorepoints-rg-us`
   - **Automation account name**: `chorepoints-automation`
   - **Region**: `North Central US` (same as app)
4. Click **Review + create** → **Create**

### Step 2: Enable System-Assigned Managed Identity

1. Go to your new Automation Account
2. Click **Identity** (left menu under Account Settings)
3. Under **System assigned** tab:
   - Toggle **Status** to **On**
   - Click **Save**
   - Click **Yes** to confirm
4. Click **Azure role assignments**
5. Click **+ Add role assignment**
   - **Scope**: Resource group
   - **Subscription**: Your subscription
   - **Resource group**: `chorepoints-rg-us`
   - **Role**: `Contributor`
6. Click **Save**

### Step 3: Create Stop Runbook

1. In Automation Account, click **Runbooks** (left menu under Process Automation)
2. Click **+ Create a runbook**
3. Fill in:
   - **Name**: `Stop-ChorePointsApp`
   - **Runbook type**: PowerShell
   - **Runtime version**: 7.2
   - **Description**: Stop app at 10 PM Lithuania time
4. Click **Create**
5. Paste this code:

```powershell
<#
.SYNOPSIS
    Stops the ChorePoints Azure App Service
.DESCRIPTION
    Automatically stops elija-agota app service to save costs during night hours
#>

# Ensures you do not inherit an AzContext in your runbook
Disable-AzContextAutosave -Scope Process | Out-Null

# Connect using managed identity
try {
    Write-Output "Connecting to Azure using managed identity..."
    Connect-AzAccount -Identity | Out-Null
    Write-Output "Connected successfully"
}
catch {
    Write-Error "Failed to connect to Azure: $_"
    throw $_
}

# Variables
$ResourceGroupName = "chorepoints-rg-us"
$WebAppName = "elija-agota"

# Stop the App Service
try {
    Write-Output "Stopping App Service: $WebAppName"
    Stop-AzWebApp -ResourceGroupName $ResourceGroupName -Name $WebAppName
    Write-Output "App Service stopped successfully at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') UTC"
    Write-Output "Lithuania time: $(([System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId((Get-Date), 'FLE Standard Time')).ToString('yyyy-MM-dd HH:mm:ss'))"
}
catch {
    Write-Error "Failed to stop App Service: $_"
    throw $_
}
```

6. Click **Save**
7. Click **Publish** → **Yes**

### Step 4: Create Start Runbook

1. Click **Runbooks** → **+ Create a runbook**
2. Fill in:
   - **Name**: `Start-ChorePointsApp`
   - **Runbook type**: PowerShell
   - **Runtime version**: 7.2
   - **Description**: Start app at noon Lithuania time
3. Click **Create**
4. Paste this code:

```powershell
<#
.SYNOPSIS
    Starts the ChorePoints Azure App Service
.DESCRIPTION
    Automatically starts elija-agota app service for daily usage
#>

# Ensures you do not inherit an AzContext in your runbook
Disable-AzContextAutosave -Scope Process | Out-Null

# Connect using managed identity
try {
    Write-Output "Connecting to Azure using managed identity..."
    Connect-AzAccount -Identity | Out-Null
    Write-Output "Connected successfully"
}
catch {
    Write-Error "Failed to connect to Azure: $_"
    throw $_
}

# Variables
$ResourceGroupName = "chorepoints-rg-us"
$WebAppName = "elija-agota"

# Start the App Service
try {
    Write-Output "Starting App Service: $WebAppName"
    Start-AzWebApp -ResourceGroupName $ResourceGroupName -Name $WebAppName
    Write-Output "App Service started successfully at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') UTC"
    Write-Output "Lithuania time: $(([System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId((Get-Date), 'FLE Standard Time')).ToString('yyyy-MM-dd HH:mm:ss'))"
}
catch {
    Write-Error "Failed to start App Service: $_"
    throw $_
}
```

5. Click **Save**
6. Click **Publish** → **Yes**

### Step 5: Test Runbooks (Important!)

**Test Stop Runbook:**
1. Go to **Stop-ChorePointsApp** runbook
2. Click **Start**
3. Click **OK**
4. Watch the **Output** pane - should see "App Service stopped successfully"
5. Verify app is stopped: Go to App Service → should show "Stopped" status
6. **Restart the app manually** for now: Click **Start** button

**Test Start Runbook:**
1. Go to **Start-ChorePointsApp** runbook
2. Click **Start**
3. Click **OK**
4. Watch the **Output** pane - should see "App Service started successfully"
5. Verify app is running: Go to App Service → should show "Running" status

### Step 6: Create Schedules

**Schedule 1: Stop at 10 PM Lithuania Time**

Lithuania is UTC+2 (EET) in winter, UTC+3 (EEST) in summer.
- 22:00 Lithuania time = **20:00 UTC** (winter) or **19:00 UTC** (summer)

1. In Automation Account, click **Schedules** (left menu)
2. Click **+ Add a schedule**
3. Click **Link a schedule to your runbook**
4. Click **+ Add a schedule**
5. Fill in:
   - **Name**: `Stop at 10 PM Lithuania`
   - **Description**: Stop app at 22:00 EET/EEST
   - **Starts**: Today's date, **20:00** (8:00 PM UTC)
   - **Time zone**: **(UTC) Coordinated Universal Time**
   - **Recurrence**: Recurring
   - **Recur every**: 1 Day
6. Click **Create**
7. Select **Stop-ChorePointsApp** runbook
8. Click **OK**

**Schedule 2: Start at Noon Lithuania Time**

- 12:00 Lithuania time = **10:00 UTC** (winter) or **09:00 UTC** (summer)

1. Click **Schedules** → **+ Add a schedule**
2. Click **Link a schedule to your runbook**
3. Click **+ Add a schedule**
4. Fill in:
   - **Name**: `Start at Noon Lithuania`
   - **Description**: Start app at 12:00 EET/EEST
   - **Starts**: Today's date, **10:00** (10:00 AM UTC)
   - **Time zone**: **(UTC) Coordinated Universal Time**
   - **Recurrence**: Recurring
   - **Recur every**: 1 Day
5. Click **Create**
6. Select **Start-ChorePointsApp** runbook
7. Click **OK**

### Step 7: Adjust for Daylight Saving Time

**Important**: Lithuania observes DST (last Sunday in March & October)

When DST changes:
1. Go to **Schedules**
2. Edit both schedules
3. Adjust times:
   - **Winter (UTC+2)**: Stop at 20:00 UTC, Start at 10:00 UTC
   - **Summer (UTC+3)**: Stop at 19:00 UTC, Start at 09:00 UTC

---

## Option 3: Azure Logic Apps (Alternative - Visual Designer)

### Step 1: Create Logic App

1. Search for "Logic Apps" in Azure Portal
2. Click **+ Add**
3. Fill in:
   - **Resource Group**: `chorepoints-rg-us`
   - **Logic app name**: `chorepoints-scheduler`
   - **Region**: `North Central US`
   - **Plan type**: Consumption (pay per execution)
4. Click **Review + create** → **Create**

### Step 2: Create Stop Workflow

1. Go to Logic App → Click **Logic app designer**
2. Select trigger: **Recurrence**
3. Configure:
   - **Interval**: 1
   - **Frequency**: Day
   - **Time zone**: (UTC+02:00) Helsinki, Kyiv, Riga, Sofia, Tallinn, Vilnius
   - **At these hours**: 22 (10 PM)
   - **At these minutes**: 0
4. Click **+ New step**
5. Search for "Azure App Service" → Select **Stop web app**
6. Sign in with your Azure account
7. Select:
   - **Subscription**: Your subscription
   - **Resource Group**: `chorepoints-rg-us`
   - **Web App Name**: `elija-agota`
8. Click **Save**

### Step 3: Create Start Workflow

1. Click **+ New** → **Logic App**
2. Name: `chorepoints-starter`
3. Same region and resource group
4. In designer, select **Recurrence** trigger
5. Configure:
   - **Interval**: 1
   - **Frequency**: Day
   - **Time zone**: (UTC+02:00) Helsinki, Kyiv, Riga, Sofia, Tallinn, Vilnius
   - **At these hours**: 12 (noon)
   - **At these minutes**: 0
6. Click **+ New step**
7. Search for "Azure App Service" → Select **Start web app**
8. Select your app: `elija-agota`
9. Click **Save**

**Pros**: Visual designer, easier to modify, handles DST automatically
**Cons**: Slightly more expensive (~$0.50/month)

---

## Option 4: Using Azure CLI (For Quick Testing)

Create a simple script you can run manually or via Task Scheduler on your PC:

**stop-app.ps1:**
```powershell
# Stop the app
az webapp stop --name elija-agota --resource-group chorepoints-rg-us
Write-Host "App stopped at $(Get-Date)" -ForegroundColor Green
```

**start-app.ps1:**
```powershell
# Start the app
az webapp start --name elija-agota --resource-group chorepoints-rg-us
Write-Host "App started at $(Get-Date)" -ForegroundColor Green
```

**Windows Task Scheduler Setup:**
1. Open Task Scheduler
2. Create Basic Task:
   - **Name**: Stop ChorePoints App
   - **Trigger**: Daily at 10:00 PM
   - **Action**: Start a program
   - **Program**: `powershell.exe`
   - **Arguments**: `-File "C:\path\to\stop-app.ps1"`
3. Repeat for start task at noon

**Cons**: Your PC must be on at those times

---

## Verification & Monitoring

### Check Current Status
```powershell
az webapp show --name elija-agota --resource-group chorepoints-rg-us --query "state" -o tsv
```

### View Automation Job History
1. Go to Automation Account
2. Click **Jobs** (left menu)
3. See all recent runs, success/failure status
4. Click any job to see detailed logs

### Set Up Email Alerts
1. In Automation Account, click **Alerts** (left menu)
2. Click **+ New alert rule**
3. Condition: Job failed
4. Action group: Send email
5. Your email address

---

## Cost Breakdown

| Solution | Monthly Cost | Complexity | Reliability |
|----------|--------------|------------|-------------|
| Manual | Free | Very Low | Depends on you |
| Automation | ~$0 (free tier) | Medium | High |
| Logic Apps | ~$0.50 | Low | High |
| Task Scheduler | Free | Low | Medium (PC must be on) |

**Recommended**: Azure Automation (Option 2) - free and fully automated

---

## Expected Savings

**Current Cost**: ~$26/month running 24/7

**With Schedule** (14 hours off per day):
- App Service: $13.14 × (10/24) = ~$5.50/month
- Database: $12.41 (always on - keeps data)
- Storage: $0.50
- **Total**: ~$18.50/month
- **Savings**: ~$7.50/month (~30%)

**Note**: Database must stay running to keep data. Only App Service stops.

---

## Troubleshooting

### Runbook Fails with "Access Denied"
- Verify managed identity has Contributor role on resource group
- Wait 5-10 minutes after assigning role for permissions to propagate

### Schedule Doesn't Run
- Check runbook is **Published** (not draft)
- Verify schedule is **Enabled**
- Check time zone is correct (UTC)

### App Doesn't Respond After Start
- Check Azure Portal → App Service should show "Running"
- Wait 2-3 minutes for app to fully start
- Check Application Insights for startup errors

### Wrong Time Execution
- Remember Lithuania uses DST
- Schedules use UTC time
- Adjust schedules twice a year for DST changes

---

## Quick Reference Commands

```powershell
# Check app status
az webapp show -n elija-agota -g chorepoints-rg-us --query state -o tsv

# Stop manually
az webapp stop -n elija-agota -g chorepoints-rg-us

# Start manually
az webapp start -n elija-agota -g chorepoints-rg-us

# Restart (if app is acting weird)
az webapp restart -n elija-agota -g chorepoints-rg-us

# Check last 5 automation jobs
az automation job list --automation-account-name chorepoints-automation -g chorepoints-rg-us --output table
```

---

**Need Help?** Check Azure Portal → Automation Account → Jobs for error logs
