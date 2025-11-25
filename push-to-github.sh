#!/bin/bash
# Simple script to push to GitHub

cd /Users/ghuman/tolls

echo "📦 Staging files..."
git add .

echo "📝 Committing..."
git commit -m "Ready for Render deployment - User dashboard only"

echo "🚀 Pushing to GitHub..."
git push origin main || git push origin master || {
    echo ""
    echo "❌ Push failed. Possible reasons:"
    echo "  1. No remote configured"
    echo "  2. Authentication required"
    echo "  3. Wrong branch name"
    echo ""
    echo "Check remote:"
    git remote -v
    echo ""
    echo "Check branch:"
    git branch
}

