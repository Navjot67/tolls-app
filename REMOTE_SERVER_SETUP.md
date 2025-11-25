# Remote Server Setup Guide

## Current Situation

✅ **Local nginx is working**: `curl http://localhost` returns HTML  
✅ **Nginx is listening on port 80**  
❌ **Domain can't connect**: www.tlcezpass.com (74.68.113.248)

## The Problem

The DNS points to `74.68.113.248`, which appears to be a **remote server IP**, not your local Mac. This means:

1. **This is a remote server setup** - You're configuring nginx locally, but the domain points to a remote server
2. **Or** - The IP is your router's public IP, and you need port forwarding

## Solutions

### Option 1: This IS a Remote Server

If 74.68.113.248 is a remote server (VPS, cloud server), you need to:

1. **SSH into that server**
2. **Set up the application there**
3. **Configure nginx on that server**

**Steps:**
```bash
# SSH to remote server
ssh user@74.68.113.248

# Then on remote server:
# - Install nginx
# - Copy your application
# - Configure domain routing
# - Run Gunicorn + nginx
```

### Option 2: This is Your Router's Public IP

If 74.68.113.248 is your router's public IP (home/office network):

1. **Check your local IP:**
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. **Set up Port Forwarding on Router:**
   - Login to router admin panel
   - Forward port 80 → Your Mac's local IP
   - Forward port 5000 → Your Mac's local IP (optional)

3. **Configure Firewall:**
   ```bash
   # macOS firewall settings
   System Preferences → Security → Firewall
   ```

### Option 3: Test Locally First

To test your setup locally before deploying:

1. **Add to /etc/hosts:**
   ```bash
   sudo sh -c 'echo "127.0.0.1 www.tlcezpass.com" >> /etc/hosts'
   ```

2. **Test:**
   ```bash
   curl http://www.tlcezpass.com
   ```

3. **Remove when done:**
   ```bash
   sudo nano /etc/hosts
   # Remove the line: 127.0.0.1 www.tlcezpass.com
   ```

## Quick Check

Run this to identify the situation:

```bash
# Check if 74.68.113.248 is your public IP
curl ifconfig.me

# Check your local IPs
ifconfig | grep "inet " | grep -v 127.0.0.1

# Test domain resolution
nslookup www.tlcezpass.com
```

## What You Need

1. **If remote server**: Deploy application to that server
2. **If local behind router**: Configure port forwarding
3. **If testing**: Use /etc/hosts method above

## Next Steps

Based on your situation:

- **Remote Server?** → Set up on that server
- **Local Network?** → Configure port forwarding  
- **Testing?** → Use /etc/hosts method

