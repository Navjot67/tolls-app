# Domain Setup Guide for E-ZPass User App

This guide will help you connect your user login app to a custom domain.

## Prerequisites

1. A domain name (e.g., `yourdomain.com`)
2. DNS access to configure domain records
3. Server with nginx installed
4. SSL certificate (Let's Encrypt recommended)

## Step 1: Choose Your Domain Structure

You have two options:

### Option A: Subdomain (Recommended)
- User App: `app.yourdomain.com` or `users.yourdomain.com`
- Main Dashboard: `yourdomain.com` or `admin.yourdomain.com`

### Option B: Main Domain
- User App: `yourdomain.com`
- Main Dashboard: `admin.yourdomain.com`

## Step 2: Configure DNS

### For Subdomain (Option A):
1. Log into your domain registrar/DNS provider
2. Add an A record:
   - **Type**: A
   - **Name**: `app` (or `users`)
   - **Value**: Your server's IP address
   - **TTL**: 3600 (or default)

### For Main Domain (Option B):
1. Add an A record:
   - **Type**: A
   - **Name**: `@` (or leave blank)
   - **Value**: Your server's IP address
   - **TTL**: 3600

**Note**: DNS changes can take 24-48 hours to propagate, but usually happen within minutes.

## Step 3: Install SSL Certificate

### Using Let's Encrypt (Free):

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Get certificate (replace YOUR_DOMAIN with your actual domain)
sudo certbot --nginx -d YOUR_DOMAIN -d www.YOUR_DOMAIN

# Auto-renewal (certbot sets this up automatically)
sudo certbot renew --dry-run
```

## Step 4: Configure Nginx

1. **Copy the nginx configuration**:
   ```bash
   sudo cp nginx-domain.conf /etc/nginx/sites-available/toll-app
   ```

2. **Edit the configuration**:
   ```bash
   sudo nano /etc/nginx/sites-available/toll-app
   ```
   
   Replace:
   - `YOUR_DOMAIN` with your actual domain (e.g., `app.yourdomain.com`)
   - Update SSL certificate paths if using custom certificates
   - Update the static files path if different

3. **Enable the site**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/toll-app /etc/nginx/sites-enabled/
   ```

4. **Test nginx configuration**:
   ```bash
   sudo nginx -t
   ```

5. **Reload nginx**:
   ```bash
   sudo systemctl reload nginx
   ```

## Step 5: Update Flask App Configuration

The Flask app should already be configured to work with domains. However, you may want to update CORS settings:

```python
# In app.py, update CORS if needed:
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://YOUR_DOMAIN", "https://www.YOUR_DOMAIN"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

## Step 6: Update Environment Variables (Optional)

If you need domain-specific settings, add to `.env`:

```bash
APP_DOMAIN=https://app.yourdomain.com
ALLOWED_ORIGINS=https://app.yourdomain.com,https://www.app.yourdomain.com
```

## Step 7: Test the Setup

1. **Check DNS propagation**:
   ```bash
   nslookup YOUR_DOMAIN
   ```

2. **Test SSL**:
   ```bash
   curl -I https://YOUR_DOMAIN
   ```

3. **Access in browser**:
   - User App: `https://YOUR_DOMAIN/user`
   - Main Dashboard: `https://YOUR_DOMAIN/`

## Step 8: Keep Flask App Running

Make sure your Flask app is running and will restart automatically:

### Using systemd (Recommended):

Create `/etc/systemd/system/toll-app.service`:

```ini
[Unit]
Description=E-ZPass Toll App
After=network.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/Users/ghuman/tolls
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /Users/ghuman/tolls/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable toll-app
sudo systemctl start toll-app
```

### Using screen/tmux (Alternative):

```bash
screen -S toll-app
cd /Users/ghuman/tolls
python3 app.py
# Press Ctrl+A then D to detach
```

## Troubleshooting

### Domain not resolving:
- Check DNS records are correct
- Wait for DNS propagation (can take up to 48 hours)
- Use `dig YOUR_DOMAIN` to check DNS

### SSL certificate errors:
- Ensure certificate paths are correct in nginx config
- Check certificate hasn't expired: `sudo certbot certificates`
- Renew if needed: `sudo certbot renew`

### 502 Bad Gateway:
- Check Flask app is running: `ps aux | grep app.py`
- Check Flask app logs
- Verify nginx proxy_pass points to correct port (5000)

### CORS errors:
- Update CORS settings in `app.py`
- Check browser console for specific error
- Verify domain is in allowed origins list

## Security Recommendations

1. **Enable firewall**:
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **Keep SSL certificates updated**:
   - Let's Encrypt certificates auto-renew
   - Monitor renewal logs

3. **Regular updates**:
   ```bash
   sudo apt-get update && sudo apt-get upgrade
   ```

4. **Monitor logs**:
   ```bash
   tail -f /var/log/nginx/toll-app-access.log
   tail -f /var/log/nginx/toll-app-error.log
   ```

## Multiple Domains

If you want to serve both admin dashboard and user app on different domains:

1. Create separate nginx configs for each domain
2. Use Flask blueprints or route based on `request.host`
3. Configure CORS for both domains

Example Flask routing:
```python
@app.route('/')
def index():
    host = request.host
    if 'app' in host or 'user' in host:
        return render_template('user_dashboard.html')
    else:
        return render_template('dashboard.html')
```

## Support

For issues, check:
- Nginx error logs: `/var/log/nginx/toll-app-error.log`
- Flask app logs
- System logs: `journalctl -u toll-app -f`

