# Data Sync Strategy: Mac ↔ Render

## Architecture

**Mac Server** (Local):
- ✅ Selenium automation
- ✅ Auto-fetch every 3 hours  
- ✅ Email checker worker
- ✅ Updates `accounts_config.json`
- ✅ Updates `users.json`

**Render** (Cloud):
- ✅ User dashboard only
- ✅ Authentication
- ✅ Display data from shared storage
- ❌ NO Selenium
- ❌ NO automation

## Data Sync Options

### Option 1: Git Sync (Simplest - Recommended to Start)

**How it works:**
1. Mac updates `accounts_config.json` and `users.json`
2. Mac commits and pushes to GitHub
3. Render auto-deploys and gets updated files
4. Users see latest data

**Pros:**
- Simple setup
- Free
- Automatic (Render auto-deploys)

**Cons:**
- Not real-time (requires git push)
- Small delay (5-10 minutes)

**Setup:**
```bash
# On Mac, after data updates:
cd /Users/ghuman/tolls
git add accounts_config.json users.json
git commit -m "Update account data"
git push origin main

# Render auto-deploys (takes 2-5 minutes)
```

### Option 2: Shared PostgreSQL Database (Best for Production)

**How it works:**
1. Create PostgreSQL on Render (free tier)
2. Mac writes data to database
3. Render reads from database
4. Real-time sync

**Pros:**
- Real-time updates
- More reliable
- Better for production

**Cons:**
- Requires database setup
- Need to update code to use database

**Setup:**
1. Create PostgreSQL on Render
2. Update Mac code to write to database
3. Update Render code to read from database

### Option 3: API Sync (Advanced)

**How it works:**
1. Mac exposes API endpoint with latest data
2. Render calls Mac API to get data
3. Real-time sync

**Pros:**
- Real-time
- No database needed
- Mac stays in control

**Cons:**
- Mac must be accessible from internet
- Need to expose API endpoint

## Recommended: Start with Git Sync

For now, use Git sync. It's simple and works well for this use case.

## Automatic Git Sync Script

Create a script to auto-sync data:

```bash
#!/bin/bash
# auto-sync-data.sh - Run this after data updates

cd /Users/ghuman/tolls

# Commit and push data files
git add accounts_config.json users.json
git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

echo "✓ Data synced to Render (will deploy automatically)"
```

Then call this from `auto_fetch.py` after updating accounts.

