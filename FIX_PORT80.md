# Fix: Port 80 Connection Issue

## The Problem
Port 80 requires **root/sudo** permissions. Homebrew nginx runs as a regular user and can't bind to port 80.

## Solution: Run Nginx as Root

### Step 1: Stop Homebrew Nginx
```bash
brew services stop nginx
```

### Step 2: Run Nginx with Sudo
```bash
sudo /opt/homebrew/bin/nginx
```

### Step 3: Verify It's Running
```bash
sudo lsof -i :80
# Should show nginx running
```

### Step 4: Test Domain
```bash
curl http://www.tlcezpass.com
```

## Alternative: Use Port 8080 (No Sudo Needed)

If you can't use sudo, change to port 8080:

### 1. Update nginx config:
```bash
nano /opt/homebrew/etc/nginx/servers/toll-app.conf
```

Change:
```nginx
listen 80;
```
To:
```nginx
listen 8080;
```

### 2. Reload nginx:
```bash
nginx -s reload
```

### 3. Access via:
- http://www.tlcezpass.com:8080

## Quick Fix Script

Run this to check and fix:

```bash
# Check if port 80 is in use
sudo lsof -i :80

# If nothing is using port 80, run nginx with sudo
brew services stop nginx
sudo /opt/homebrew/bin/nginx

# Test
curl http://localhost
curl http://www.tlcezpass.com
```

