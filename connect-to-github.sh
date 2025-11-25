#!/bin/bash
# Connect local git repo to GitHub and push

cd /Users/ghuman/tolls

if [ $# -lt 2 ]; then
    echo "Usage: ./connect-to-github.sh GITHUB_USERNAME REPO_NAME"
    echo ""
    echo "Example:"
    echo "  ./connect-to-github.sh myusername tolls-app"
    echo ""
    exit 1
fi

USERNAME=$1
REPO_NAME=$2
REPO_URL="https://github.com/${USERNAME}/${REPO_NAME}.git"

echo "=========================================="
echo "Connecting to GitHub"
echo "=========================================="
echo ""
echo "Repository URL: $REPO_URL"
echo ""

# Check if remote already exists
if git remote | grep -q origin; then
    echo "⚠️  Remote 'origin' already exists:"
    git remote -v
    echo ""
    read -p "Update to new URL? (y/n): " UPDATE
    if [ "$UPDATE" = "y" ]; then
        git remote set-url origin "$REPO_URL"
        echo "✓ Remote URL updated"
    else
        echo "Keeping existing remote"
    fi
else
    echo "Adding remote..."
    git remote add origin "$REPO_URL"
    echo "✓ Remote added"
fi

echo ""
echo "Pushing to GitHub..."
echo ""

# Try to push
if git push -u origin main 2>&1; then
    echo ""
    echo "=========================================="
    echo "✅ Successfully pushed to GitHub!"
    echo "=========================================="
    echo ""
    echo "Repository: https://github.com/${USERNAME}/${REPO_NAME}"
    echo ""
    echo "Next steps:"
    echo "1. Go to: https://render.com"
    echo "2. Connect your GitHub repository"
    echo "3. Deploy using app-render.py"
    echo ""
else
    echo ""
    echo "⚠️  Push failed. Common issues:"
    echo ""
    echo "1. Repository doesn't exist:"
    echo "   → Create it at: https://github.com/new"
    echo ""
    echo "2. Authentication required:"
    echo "   → Install GitHub CLI: brew install gh"
    echo "   → Login: gh auth login"
    echo "   → Try again: git push -u origin main"
    echo ""
    echo "3. Repository has existing files:"
    echo "   → Pull first: git pull origin main --allow-unrelated-histories"
    echo "   → Then push: git push -u origin main"
    echo ""
    echo "Current remote:"
    git remote -v
    echo ""
fi

