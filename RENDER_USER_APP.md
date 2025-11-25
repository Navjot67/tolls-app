# Render Deployment: User Dashboard Only

## Architecture

```
┌─────────────────────┐
│   Your Mac          │
│                     │
│  • Selenium         │
│  • Auto-fetch       │
│  • Email checker    │
│  • accounts_config  │
│  • users.json       │
└─────────────────────┘
         │
         │ (Data sync)
         ▼
┌─────────────────────┐
│   Render.com        │
│                     │
│  • User Dashboard   │
│  • Authentication   │
│  • View Data Only   │
│  • No Selenium      │
└─────────────────────┘
```

## Setup

### 1. Create Render App (User Dashboard Only)

**Files needed for Render:**
- ✅ `app-render.py` - User dashboard app (no Selenium)
- ✅ `requirements-render.txt` - Lightweight dependencies
- ✅ `user_manager.py` - User management
- ✅ `email_service.py` - For OTP emails
- ✅ `templates/user_dashboard.html` - User interface
- ✅ `static/user_dashboard.*` - CSS/JS
- ✅ `accounts_config.json` - Account data (synced from Mac)
- ✅ `users.json` - User data (synced from Mac)

### 2. Data Sync Strategy

**Option A: Git Sync (Simplest)**
- Mac commits updated `accounts_config.json` and `users.json`
- Push to GitHub
- Render auto-deploys and picks up new data
- **Downside**: Not real-time, requires git push

**Option B: Shared Database (Best)**
- Use Render PostgreSQL (free tier)
- Mac writes to database
- Render reads from database
- **Benefit**: Real-time updates

**Option C: API Sync (Advanced)**
- Render calls Mac server API to get latest data
- Mac exposes API endpoint
- **Benefit**: Real-time, no database needed

### 3. Quick Setup

#### Step 1: Update render.yaml

Use `app-render.py` instead of `app.py`:

```yaml
services:
  - type: web
    name: toll-user-app
    env: python
    plan: free
    buildCommand: pip install -r requirements-render.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app-render:app
    envVars:
      - key: FLASK_ENV
        value: production
```

#### Step 2: Deploy

1. Push to GitHub
2. Create Render service
3. Use `app-render.py` as entry point
4. Use `requirements-render.txt` for dependencies

#### Step 3: Set Environment Variables

Same as before (SMTP, IMAP settings)

## Data Sync: Recommended Approach

### Use Shared PostgreSQL Database

1. **Create PostgreSQL on Render** (free tier)
2. **Mac writes data to database**
3. **Render reads from database**

This gives you real-time sync without git pushes.

## What Runs Where

### Mac Server:
- ✅ Selenium automation
- ✅ Email checker worker
- ✅ Auto-fetch every 3 hours
- ✅ Updates `accounts_config.json`
- ✅ Updates `users.json`

### Render (User App):
- ✅ User signup/login
- ✅ OTP verification
- ✅ Display account data
- ✅ User dashboard UI
- ❌ NO Selenium
- ❌ NO automation

## Files Structure

```
tolls/
├── app.py                    # Full app (Mac only)
├── app-render.py            # User dashboard (Render)
├── requirements.txt         # Full (Mac)
├── requirements-render.txt  # Lightweight (Render)
├── accounts_config.json     # Synced from Mac
├── users.json               # Synced from Mac
└── ... (other files)
```

## Deployment Checklist

- [ ] Create `app-render.py` ✅
- [ ] Create `requirements-render.txt` ✅
- [ ] Update `render.yaml` to use `app-render.py`
- [ ] Set up data sync (Git or Database)
- [ ] Deploy to Render
- [ ] Configure custom domain
- [ ] Test user signup/login
- [ ] Verify data sync works

## Next: Set Up Database Sync (Optional but Recommended)

See `DATABASE_SYNC.md` for PostgreSQL setup.

