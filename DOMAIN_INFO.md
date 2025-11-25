# Domain Configuration: www.tlcezpass.com

## ✅ Configured

Your domain routing is set up and ready!

### Domain Details:
- **Primary Domain**: www.tlcezpass.com
- **Alternative**: tlcezpass.com
- **Backend**: Gunicorn running on port 5000
- **Nginx Config**: `/opt/homebrew/etc/nginx/servers/toll-app.conf`

## Next Steps

### 1. Configure DNS Records

Add these DNS A records in your domain registrar:

```
Type: A
Name: www
Value: YOUR_SERVER_IP
TTL: 3600

Type: A  
Name: @
Value: YOUR_SERVER_IP
TTL: 3600
```

**How to find your server IP:**
```bash
# If server has public IP
curl ifconfig.me

# Or check your server's network interface
ifconfig | grep "inet "
```

### 2. Wait for DNS Propagation

- Usually takes 5-60 minutes
- Can take up to 24-48 hours
- Test with: `nslookup www.tlcezpass.com`

### 3. Test Domain

```bash
# After DNS propagates
curl http://www.tlcezpass.com
curl http://www.tlcezpass.com/user

# Open in browser
open http://www.tlcezpass.com
```

### 4. Set Up SSL Certificate (Recommended)

**Install Certbot:**
```bash
brew install certbot
```

**Get Certificate:**
```bash
# Stop nginx temporarily
brew services stop nginx

# Get certificate
sudo certbot certonly --standalone \
  -d www.tlcezpass.com \
  -d tlcezpass.com \
  --email your-email@example.com \
  --agree-tos

# Start nginx
brew services start nginx
```

**Update nginx config for HTTPS:**
Edit `/opt/homebrew/etc/nginx/servers/toll-app.conf` and add HTTPS section:

```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name www.tlcezpass.com tlcezpass.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name www.tlcezpass.com tlcezpass.com;

    ssl_certificate /etc/letsencrypt/live/www.tlcezpass.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.tlcezpass.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... rest of config ...
}
```

Then reload: `nginx -s reload`

## Current Configuration

### Routes:
- `/` → Main dashboard
- `/user` → User login/app
- `/api/*` → API endpoints
- `/static/*` → Static files (CSS, JS, images)

### Services Running:
- ✅ Gunicorn: http://127.0.0.1:5000
- ✅ Nginx: Listening on port 80
- ✅ Email Checker: Running in background
- ✅ Auto-fetch: Scheduled (every 3 hours)

## Troubleshooting

### Domain not resolving?
1. Check DNS: `nslookup www.tlcezpass.com`
2. Wait for DNS propagation
3. Clear DNS cache: `sudo dscacheutil -flushcache` (macOS)

### Can't connect?
1. Check nginx: `brew services list | grep nginx`
2. Check Gunicorn: `launchctl list com.toll-app`
3. Check logs: `tail -f /Users/ghuman/tolls/logs/gunicorn-stderr.log`

### Nginx errors?
```bash
# Test config
nginx -t

# View logs
tail -f /opt/homebrew/var/log/nginx/error.log
```

## Access URLs

- **Main Dashboard**: http://www.tlcezpass.com
- **User App**: http://www.tlcezpass.com/user
- **API**: http://www.tlcezpass.com/api/*

After SSL setup:
- **Main Dashboard**: https://www.tlcezpass.com
- **User App**: https://www.tlcezpass.com/user

