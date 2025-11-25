# Quick Domain Setup Guide

## Quick Start (3 Steps)

### 1. Configure DNS
Add an A record pointing to your server IP:
- **Type**: A
- **Name**: `app` (for app.yourdomain.com) or `@` (for yourdomain.com)
- **Value**: Your server's IP address

### 2. Run Setup Script
```bash
sudo ./setup-domain.sh
```
Follow the prompts to enter your domain name.

### 3. Test
Visit: `https://YOUR_DOMAIN/user`

## Manual Setup

### Step 1: Install SSL Certificate
```bash
sudo certbot --nginx -d YOUR_DOMAIN
```

### Step 2: Configure Nginx
```bash
# Copy config
sudo cp nginx-domain.conf /etc/nginx/sites-available/toll-app

# Edit and replace YOUR_DOMAIN
sudo nano /etc/nginx/sites-available/toll-app

# Enable site
sudo ln -s /etc/nginx/sites-available/toll-app /etc/nginx/sites-enabled/

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### Step 3: Update CORS (if needed)
Edit `app.py` and update the CORS origins list with your domain.

## Common Issues

**Domain not working?**
- Check DNS: `nslookup YOUR_DOMAIN`
- Check nginx: `sudo nginx -t`
- Check Flask: `ps aux | grep app.py`

**SSL errors?**
- Renew certificate: `sudo certbot renew`
- Check certificate: `sudo certbot certificates`

**502 Bad Gateway?**
- Flask app not running: `python3 app.py`
- Check port 5000 is not blocked

## Domain Examples

- User App: `app.yourdomain.com` or `users.yourdomain.com`
- Main Dashboard: `admin.yourdomain.com` or `yourdomain.com`

## Need Help?

See full guide: `DOMAIN_SETUP.md`

