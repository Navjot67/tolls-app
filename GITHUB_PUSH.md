# Push to GitHub - Quick Guide

## Simple Push

Run these commands in your terminal:

```bash
cd /Users/ghuman/tolls
git add .
git commit -m "Ready for Render deployment - User dashboard only"
git push origin main
```

## Or Use the Script

```bash
./push-to-github.sh
```

## Important Notes

### Data Files Not Included
Your `.gitignore` excludes:
- `accounts_config.json` 
- `users.json`

These files contain sensitive account data and should NOT be pushed to public repos.

### Options for Data Sync to Render

**Option 1: Private GitHub Repo** (Recommended)
- Make your repo private on GitHub
- Temporarily allow data files in git:
  ```bash
  git add -f accounts_config.json users.json
  git commit -m "Add data files for Render"
  git push
  ```
- Then remove them from .gitignore if needed

**Option 2: Manual Upload**
- Upload `accounts_config.json` and `users.json` via Render's file upload or environment variables

**Option 3: API Sync** (Future)
- Create an API endpoint on Render to receive data from your Mac

## Current Setup

Your push will include:
- ✅ `app-render.py` (Flask app)
- ✅ `requirements-render.txt` (dependencies)
- ✅ `render.yaml` (Render config)
- ✅ All templates and static files
- ✅ All Python code

Your push will NOT include:
- ❌ `.env` files (good!)
- ❌ `accounts_config.json` (excluded)
- ❌ `users.json` (excluded)

## After Push

1. Go to Render.com
2. Connect your GitHub repo
3. Deploy using `app-render.py`
4. Set up data sync separately (see options above)

