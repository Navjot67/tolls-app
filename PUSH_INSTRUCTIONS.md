# Push to GitHub - Step by Step

## Quick Push Commands

Run these in your terminal:

```bash
cd /Users/ghuman/tolls

# 1. Stage all files
git add .

# 2. Commit
git commit -m "Ready for Render deployment - User dashboard only"

# 3. Push
git push origin main
```

## If Git is Not Initialized

```bash
cd /Users/ghuman/tolls

# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit - Ready for Render"

# Add remote (replace with your GitHub repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Set main branch
git branch -M main

# Push
git push -u origin main
```

## If Remote is Not Configured

```bash
# Check current remote
git remote -v

# Add remote (if not exists)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Or update existing
git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

## Important: Data Files

Your `.gitignore` excludes:
- `accounts_config.json`
- `users.json`

These won't be pushed. This is good for security!

**To include them (only if repo is private):**
```bash
git add -f accounts_config.json users.json
git commit -m "Add data files"
git push
```

## Troubleshooting

### Authentication Error
```bash
# Use GitHub CLI
gh auth login

# Or use personal access token
git push https://YOUR_TOKEN@github.com/USERNAME/REPO.git main
```

### No Changes to Commit
```bash
# Check status
git status

# If nothing to commit, everything is already pushed
```

### Wrong Branch
```bash
# Check current branch
git branch

# Switch to main
git checkout main

# Or push to master
git push origin master
```

