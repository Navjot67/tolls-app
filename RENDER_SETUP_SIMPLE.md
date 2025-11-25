# Simple Render Setup Guide

## Overview

**Mac Server:**
- Runs Selenium automation
- Fetches toll data
- Updates account data
- Syncs to Render via Git

**Render:**
- User dashboard only
- Users login and view their data
- No Selenium needed

## Quick Deploy to Render

### Step 1: Push Code to GitHub

```bash
cd /Users/ghuman/tolls

# Initialize git if needed
git init
git add .
git commit -m "Initial commit"

# Push to GitHub
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to: https://render.com
2. Sign up / Login
3. Click "New +" → "Web Service"
4. Connect your GitHub repository

### Step 3: Configure Render Service

**Settings:**
- **Name**: `toll-user-app`
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements-render.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app-render:app`

### Step 4: Add Environment Variables

In Render dashboard → Environment:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=your-email@gmail.com
IMAP_PASSWORD=your-app-password
FLASK_ENV=production
```

### Step 5: Deploy!

Click "Create Web Service" and wait ~5 minutes.

## Data Sync

### Automatic Sync

I've added automatic sync to `auto_fetch.py`. After it updates account data, it will:
1. Commit `accounts_config.json` and `users.json`
2. Push to GitHub
3. Render auto-deploys with new data

### Manual Sync

To manually sync data:

```bash
./sync_to_render.sh
```

Or:
```bash
git add accounts_config.json users.json
git commit -m "Update account data"
git push origin main
```

## How It Works

1. **Mac runs automation** → Updates `accounts_config.json`
2. **Auto-sync script runs** → Commits and pushes to GitHub
3. **Render detects push** → Auto-deploys new version
4. **Users see updated data** → When they refresh in browser

## Testing

1. **Test Mac server**: `curl http://localhost:5000`
2. **Test Render**: `curl https://your-app.onrender.com`
3. **Test data sync**: Update account data on Mac, check Render updates

## Custom Domain

After Render deployment:
1. Go to Render dashboard → Your Service → Settings
2. Click "Custom Domains"
3. Add: `www.tlcezpass.com`
4. Update DNS records as shown by Render

## Files on Render

**Required:**
- `app-render.py` ✅
- `requirements-render.txt` ✅
- `user_manager.py` ✅
- `email_service.py` ✅
- `templates/user_dashboard.html` ✅
- `static/user_dashboard.*` ✅
- `accounts_config.json` (synced from Mac)
- `users.json` (synced from Mac)

**Not needed:**
- `automation_selenium.py` ❌
- `automation_selenium_nj.py` ❌
- Selenium dependencies ❌

