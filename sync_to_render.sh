#!/bin/bash
# Auto-sync data files to Render via Git
# This script commits and pushes accounts_config.json and users.json to GitHub
# Render will auto-deploy when it detects the push

cd /Users/ghuman/tolls

# Check if git repo exists
if [ ! -d .git ]; then
    echo "⚠️  Not a git repository. Initializing..."
    git init
    git remote add origin YOUR_GITHUB_REPO_URL 2>/dev/null || true
    echo "⚠️  Please set git remote: git remote add origin YOUR_REPO_URL"
fi

# Stage data files
git add accounts_config.json users.json 2>/dev/null

# Check if there are changes
if git diff --staged --quiet; then
    echo "ℹ️  No changes to sync"
    exit 0
fi

# Commit
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
git commit -m "Auto-sync account data: $TIMESTAMP" 2>/dev/null || {
    echo "⚠️  Git commit failed"
    exit 1
}

# Push to GitHub (Render will auto-deploy)
git push origin main 2>/dev/null || {
    echo "⚠️  Git push failed. Check your git remote configuration."
    echo "   To set remote: git remote set-url origin YOUR_GITHUB_REPO_URL"
    exit 1
}

echo "✅ Data synced to Render (auto-deploying...)"
echo "   Render will update in 2-5 minutes"

