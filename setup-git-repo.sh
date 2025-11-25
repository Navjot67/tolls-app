#!/bin/bash
# Setup git repository and prepare for first push

cd /Users/ghuman/tolls

echo "=========================================="
echo "Setting up Git Repository"
echo "=========================================="
echo ""

# Check if already a git repo
if [ -d .git ]; then
    echo "✓ Git repository already exists"
else
    echo "Initializing git repository..."
    git init
    echo "✓ Git initialized"
fi

# Stage all files
echo ""
echo "Staging files..."
git add .

# Show what will be committed
echo ""
echo "Files to be committed:"
git status --short | head -30

# First commit
echo ""
echo "Creating initial commit..."
git commit -m "Initial commit - Ready for Render deployment"
echo "✓ Committed"

# Set branch to main
echo ""
echo "Setting branch to main..."
git branch -M main
echo "✓ Branch set to main"

echo ""
echo "=========================================="
echo "✅ Git repository ready!"
echo "=========================================="
echo ""
echo "Next step: Connect to GitHub"
echo ""
echo "1. Create a repository on GitHub (if you haven't):"
echo "   https://github.com/new"
echo ""
echo "2. Then run one of these:"
echo ""
echo "   If repo is EMPTY (no README):"
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
echo "   git push -u origin main"
echo ""
echo "   If repo has files (README, etc):"
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
echo "   git pull origin main --allow-unrelated-histories"
echo "   git push -u origin main"
echo ""
echo "Or run: ./connect-to-github.sh YOUR_USERNAME YOUR_REPO_NAME"
echo ""

