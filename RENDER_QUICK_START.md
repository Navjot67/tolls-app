# Render Quick Start Guide

## Setup Summary

**Mac**: Handles Selenium/automation  
**Render**: User dashboard only (no Selenium)

## 3-Step Deploy

### 1. Push to GitHub
```bash
cd /Users/ghuman/tolls
git add .
git commit -m "Ready for Render"
git push origin main
```

### 2. Create Render Service

1. Go to: https://render.com
2. Sign up (use GitHub)
3. "New +" → "Web Service"
4. Connect GitHub repo
5. Use these settings:
   - **Build Command**: `pip install -r requirements-render.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app-render:app`
6. Add environment variables (SMTP, IMAP)
7. Deploy!

### 3. Data Sync

Data syncs automatically via Git:
- Mac updates data → Auto-commits → Pushes to GitHub
- Render auto-deploys → Users see updated data

## Your App URLs

- **Render URL**: `https://your-app.onrender.com`
- **Custom Domain**: `https://www.tlcezpass.com` (after setup)

## That's It! 🚀

Users can now:
- Sign up with email
- Verify with OTP
- Login and view their toll data
- See updates automatically (synced from Mac)

