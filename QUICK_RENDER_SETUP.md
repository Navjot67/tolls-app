# Quick Render.com Setup Guide

## Why Render?

- ✅ **Free HTTPS/SSL** - Automatic
- ✅ **Free tier** - Perfect for testing
- ✅ **Auto-deploy** - Push to Git = Deploy
- ✅ **No server management**
- ✅ **Custom domains** - Easy setup

## 5-Minute Setup

### 1. Push to GitHub

```bash
cd /Users/ghuman/tolls

# Initialize git if needed
git init
git add .
git commit -m "Ready for Render deployment"

# Push to GitHub (create repo first on github.com)
git remote add origin https://github.com/YOUR_USERNAME/tolls.git
git branch -M main
git push -u origin main
```

### 2. Sign Up on Render

1. Go to: https://render.com
2. Sign up (use GitHub for easy connection)
3. Click "New +" → "Web Service"

### 3. Connect Repository

- Select your GitHub repository
- Or paste your repo URL

### 4. Configure Service

**Settings:**
- **Name**: `toll-app` (or your choice)
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: `/` (leave empty)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`

**Plan:** Free (or Starter for better performance)

### 5. Add Environment Variables

Click "Advanced" → "Environment Variables" → Add:

```
FLASK_ENV=production
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=your-email@gmail.com
IMAP_PASSWORD=your-app-password
EMAIL_CHECK_INTERVAL=60
```

### 6. Deploy!

Click "Create Web Service" and wait ~5 minutes for deployment.

### 7. Add Custom Domain

After deployment:

1. Go to your service → "Settings" → "Custom Domains"
2. Add: `www.tlcezpass.com`
3. Render shows DNS records to add
4. Update your DNS with those records
5. Wait for DNS propagation

## Your App Will Be Live At:

- **Render URL**: `https://toll-app.onrender.com`
- **Custom Domain**: `https://www.tlcezpass.com` (after DNS setup)

## Important Notes

### Selenium on Render

Render free tier may have limitations with Selenium. Options:

1. **Use Render Dockerfile** (I created one)
2. **Or** switch to headless Chrome setup
3. **Or** use a different service for Selenium tasks

### Background Workers

Email checker worker needs a separate Background Worker service:
- Render free tier: ❌ No background workers
- Render paid: ✅ Available
- Alternative: Use Railway.app or Fly.io for workers

### File Storage

Render's filesystem is **ephemeral** (clears on deploy):
- Use **PostgreSQL** for `accounts_config.json` and `users.json`
- Render offers free PostgreSQL database
- Or use external storage (S3, etc.)

## Quick Deploy Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Web service created
- [ ] Environment variables added
- [ ] Deployed successfully
- [ ] Custom domain added (optional)
- [ ] DNS records updated (if custom domain)

## That's It!

Your app will automatically:
- ✅ Deploy when you push to GitHub
- ✅ Get free HTTPS/SSL
- ✅ Scale as needed
- ✅ Monitor and log automatically

## Support

- Render Docs: https://render.com/docs
- Render Status: https://status.render.com

