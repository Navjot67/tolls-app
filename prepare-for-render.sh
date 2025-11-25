#!/bin/bash
# Prepare and push to GitHub for Render deployment

cd /Users/ghuman/tolls

echo "=========================================="
echo "Preparing for Render Deployment"
echo "=========================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    echo "✓ Git initialized"
fi

# Check if .gitignore exists and has correct entries
if [ ! -f .gitignore ]; then
    echo "Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
venv/
env/
.venv

# Environment
.env
.env.local

# Logs
*.log
logs/

# IDE
.vscode/
.idea/

# OS
.DS_Store
EOF
    echo "✓ .gitignore created"
fi

# Stage all files
echo "Staging files..."
git add .

# Show what will be committed
echo ""
echo "Files to be committed:"
git status --short | head -30

# Check if there are changes
if git diff --staged --quiet; then
    echo ""
    echo "⚠️  No changes to commit. Everything is up to date."
    exit 0
fi

# Commit
echo ""
read -p "Commit message (or press Enter for default): " COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-"Ready for Render deployment - User dashboard only"}

git commit -m "$COMMIT_MSG"
echo "✓ Changes committed"

# Check remote
echo ""
echo "Checking git remote..."
if git remote | grep -q origin; then
    REMOTE_URL=$(git remote get-url origin)
    echo "✓ Remote configured: $REMOTE_URL"
    echo ""
    echo "Pushing to GitHub..."
    git push origin main 2>&1 || git push origin master 2>&1 || {
        echo ""
        echo "⚠️  Push failed. Check remote configuration:"
        echo "   git remote -v"
        echo ""
        echo "To set remote:"
        echo "   git remote add origin YOUR_GITHUB_REPO_URL"
        exit 1
    }
    echo "✓ Pushed to GitHub!"
else
    echo "⚠️  No remote configured."
    echo ""
    echo "To set up remote:"
    echo "1. Create a repository on GitHub"
    echo "2. Run: git remote add origin YOUR_GITHUB_REPO_URL"
    echo "3. Then run: git push -u origin main"
    echo ""
    echo "Or if you already have a repo URL:"
    read -p "Enter your GitHub repo URL: " REPO_URL
    if [ -n "$REPO_URL" ]; then
        git remote add origin "$REPO_URL"
        git branch -M main
        git push -u origin main
        echo "✓ Pushed to GitHub!"
    fi
fi

echo ""
echo "=========================================="
echo "Ready for Render Deployment!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Go to: https://render.com"
echo "2. Connect your GitHub repository"
echo "3. Deploy using app-render.py"
echo ""

