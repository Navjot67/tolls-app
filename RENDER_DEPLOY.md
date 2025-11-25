# Deploying to Render.com

Render is a cloud platform that makes deployment much easier than managing your own server!

## ✅ Benefits of Render

- **Free tier available** for web services
- **Automatic SSL/HTTPS** (free)
- **Auto-deploy from Git**
- **No server management**
- **Automatic scaling**
- **Built-in monitoring**

## Quick Deploy (5 Steps)

### Step 1: Prepare Your Code

Your code is already ready! Just make sure you have:
- ✅ `requirements.txt`
- ✅ `app.py`
- ✅ All your files in a Git repository

### Step 2: Create render.yaml

I've created `render.yaml` for you. This tells Render how to deploy your app.

### Step 3: Push to GitHub/GitLab

```bash
# Initialize git if not already
git init
git add .
git commit -m "Initial commit for Render deployment"

# Push to GitHub/GitLab
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### Step 4: Deploy on Render

1. **Go to**: https://render.com
2. **Sign up/Login** (use GitHub account for easy integration)
3. **Click**: "New +" → "Web Service"
4. **Connect** your GitHub repository
5. **Configure**:
   - **Name**: `toll-app` (or your choice)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`
   - **Plan**: Free (or paid for more resources)

6. **Environment Variables** (add these):
   - `FLASK_ENV=production`
   - `SMTP_SERVER` (from your .env)
   - `SMTP_PORT`
   - `SMTP_USERNAME`
   - `SMTP_PASSWORD`
   - `IMAP_SERVER`
   - `IMAP_PORT`
   - `IMAP_USERNAME`
   - `IMAP_PASSWORD`

7. **Click**: "Create Web Service"

### Step 5: Configure Domain

After deployment:
1. Go to your service settings
2. Click "Custom Domains"
3. Add: `www.tlcezpass.com`
4. Render will provide DNS records to add
5. Update your DNS with Render's provided records

## Environment Variables on Render

Add these in Render dashboard → Environment:

```bash
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

## Important: Update for Render

Render uses dynamic port allocation. We need to update `app.py` to work with Render's `$PORT` environment variable.

### Update app.py

The start command in `render.yaml` already handles this, but make sure your app works with `$PORT`:

```python
# In app.py, change the last line from:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
```

## File Structure for Render

Make sure these files exist:
```
tolls/
├── app.py                 ✅
├── requirements.txt       ✅
├── render.yaml           ✅ (just created)
├── gunicorn_config.py    ✅
├── static/               ✅
├── templates/            ✅
├── *.py files            ✅
└── .env                  ❌ (don't commit - use Render env vars)
```

## .gitignore

Make sure `.gitignore` includes:
```
.env
*.log
logs/
__pycache__/
*.pyc
venv/
.DS_Store
```

## Render-Specific Considerations

### 1. Selenium/ChromeDriver

Selenium needs ChromeDriver. Render free tier might have limitations. Options:

**Option A: Use Render's Docker** (recommended):
- Create a Dockerfile with ChromeDriver installed

**Option B: Use headless Chrome**:
- Already using headless in your code
- Render may need Chrome installed in the environment

### 2. Background Workers

For the email checker worker (`email_checker_worker.py`):
- Render free tier doesn't support background workers
- You'll need a paid "Background Worker" service
- Or use a free alternative like Railway, Fly.io, or Heroku

### 3. File Storage

- Render's filesystem is ephemeral (resets on deploy)
- Store `accounts_config.json` and `users.json` in a database
- Or use Render PostgreSQL (free tier available)

## Quick Deploy Checklist

- [ ] Code is in Git repository
- [ ] Pushed to GitHub/GitLab
- [ ] Created Render account
- [ ] Created new Web Service
- [ ] Connected GitHub repo
- [ ] Added environment variables
- [ ] Started deployment
- [ ] Configured custom domain (optional)
- [ ] Updated DNS records (if using custom domain)

## Alternative: Railway.app (Free Tier Friendly)

Railway also offers free tier and is easier for Python apps:

1. **Go to**: https://railway.app
2. **Deploy from GitHub**
3. **Add environment variables**
4. **Deploy** - It auto-detects Python apps!

## What Render Gives You

- ✅ **HTTPS/SSL**: Automatic (free)
- ✅ **Custom Domain**: Easy setup
- ✅ **Auto-deploy**: Push to Git = auto deploy
- ✅ **Monitoring**: Built-in logs and metrics
- ✅ **Scaling**: Easy to scale up
- ✅ **No Server Management**: Everything handled

## Next Steps

1. **Push to GitHub** if not already
2. **Sign up at Render.com**
3. **Create Web Service**
4. **Add environment variables**
5. **Deploy!**

Your app will be live at: `https://your-app.onrender.com`

Then add custom domain: `www.tlcezpass.com`

## Need Help?

- Render Docs: https://render.com/docs
- Support: support@render.com
- Community: Render Discord/Slack

