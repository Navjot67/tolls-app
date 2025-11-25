# First Time Git Setup - Run These Commands

You're seeing "fatal: not a git repository" because git isn't initialized yet.

## Step 1: Initialize Git (Run This Now)

```bash
cd /Users/ghuman/tolls
git init
git add .
git commit -m "Initial commit - Ready for Render deployment"
git branch -M main
```

## Step 2: Create GitHub Repository

1. Go to: https://github.com/new
2. Create a new repository (e.g., `tolls-app`)
3. **DON'T** initialize with README or .gitignore
4. Copy the repository URL

## Step 3: Connect and Push

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual values:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

## Example

If your GitHub username is `ghuman` and repo name is `tolls-app`:

```bash
git remote add origin https://github.com/ghuman/tolls-app.git
git push -u origin main
```

## If Authentication Fails

Install GitHub CLI and login:

```bash
brew install gh
gh auth login
```

Then try pushing again:

```bash
git push -u origin main
```

## Quick Script Option

Or use the automated script:

```bash
./setup-git-repo.sh
./connect-to-github.sh YOUR_USERNAME YOUR_REPO_NAME
```

---

**After successful push, proceed to Render deployment!**

