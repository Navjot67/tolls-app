# Domain Setup Guide for macOS (Homebrew Nginx)

## Quick Setup

### Option 1: Interactive Setup
```bash
./setup-domain-macos.sh
```

### Option 2: Manual Setup

#### Step 1: Update nginx.conf
Edit `/opt/homebrew/etc/nginx/nginx.conf` and add this line in the `http` block:

```nginx
http {
    # ... existing config ...
    
    include servers/*.conf;  # Add this line
    
    # ... rest of config ...
}
```

#### Step 2: Create Domain Config
```bash
# Copy template
cp nginx-domain.conf /opt/homebrew/etc/nginx/servers/toll-app.conf

# Edit and replace YOUR_DOMAIN
nano /opt/homebrew/etc/nginx/servers/toll-app.conf
# Replace:
#   YOUR_DOMAIN → your actual domain (e.g., app.yourdomain.com)
#   /Users/ghuman/tolls → your app directory path
```

#### Step 3: Test Configuration
```bash
nginx -t
```

#### Step 4: Start/Reload Nginx
```bash
# Start nginx (if not running)
brew services start nginx

# Or reload if already running
nginx -s reload
```

## SSL Certificate Setup

### Using Let's Encrypt (Certbot)

1. **Install Certbot**:
   ```bash
   brew install certbot
   ```

2. **Get Certificate**:
   ```bash
   # Stop nginx temporarily
   brew services stop nginx
   
   # Get certificate
   sudo certbot certonly --standalone -d YOUR_DOMAIN -d www.YOUR_DOMAIN
   
   # Start nginx
   brew services start nginx
   ```

3. **Update nginx config** with certificate paths:
   ```nginx
   ssl_certificate /etc/letsencrypt/live/YOUR_DOMAIN/fullchain.pem;
   ssl_certificate_key /etc/letsencrypt/live/YOUR_DOMAIN/privkey.pem;
   ```

4. **Reload nginx**:
   ```bash
   nginx -s reload
   ```

## DNS Configuration

1. **Add A Record** in your domain registrar:
   - **Type**: A
   - **Name**: `app` (for app.yourdomain.com) or `@` (for yourdomain.com)
   - **Value**: Your server's public IP address
   - **TTL**: 3600

2. **Wait for DNS propagation** (5-60 minutes)

3. **Test DNS**:
   ```bash
   nslookup YOUR_DOMAIN
   dig YOUR_DOMAIN
   ```

## Nginx Management (macOS)

```bash
# Start nginx
brew services start nginx

# Stop nginx
brew services stop nginx

# Restart nginx
brew services restart nginx

# Check status
brew services list | grep nginx

# Test configuration
nginx -t

# Reload configuration (without downtime)
nginx -s reload

# View nginx processes
ps aux | grep nginx
```

## Troubleshooting

### Nginx won't start
```bash
# Check error logs
tail -f /opt/homebrew/var/log/nginx/error.log

# Check if port 80/443 is in use
lsof -i :80
lsof -i :443
```

### Configuration errors
```bash
# Test config
nginx -t

# View full error
nginx -T 2>&1 | grep error
```

### Permission issues
```bash
# Check nginx user
ps aux | grep nginx

# Ensure nginx can read config files
ls -la /opt/homebrew/etc/nginx/servers/
```

### Can't connect to domain
1. Check DNS: `nslookup YOUR_DOMAIN`
2. Check firewall: `sudo ufw status` (if using)
3. Check nginx is running: `brew services list | grep nginx`
4. Check logs: `tail -f /opt/homebrew/var/log/nginx/access.log`

## Testing

### Local test (before DNS)
```bash
# Add to /etc/hosts for local testing
sudo nano /etc/hosts
# Add: 127.0.0.1 YOUR_DOMAIN
```

### Test endpoints
```bash
# HTTP
curl http://YOUR_DOMAIN
curl http://YOUR_DOMAIN/user

# HTTPS (after SSL setup)
curl https://YOUR_DOMAIN
curl https://YOUR_DOMAIN/user
```

## File Locations (macOS Homebrew)

- **Nginx config**: `/opt/homebrew/etc/nginx/nginx.conf`
- **Server configs**: `/opt/homebrew/etc/nginx/servers/`
- **Logs**: `/opt/homebrew/var/log/nginx/`
- **PID file**: `/opt/homebrew/var/run/nginx.pid`

## Next Steps

1. ✅ Configure DNS A record
2. ✅ Set up SSL certificate
3. ✅ Test domain access
4. ✅ Monitor logs
5. ✅ Set up auto-renewal for SSL (certbot handles this)

## Auto-renewal SSL

Certbot sets up auto-renewal automatically. Test it:
```bash
sudo certbot renew --dry-run
```

