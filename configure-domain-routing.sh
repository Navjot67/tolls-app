#!/bin/bash
# Configure Domain Routing for E-ZPass App
# This script sets up nginx to route domains to the appropriate app

set -e

APP_DIR="/Users/ghuman/tolls"
NGINX_PREFIX=$(brew --prefix nginx)
NGINX_CONF_DIR="$NGINX_PREFIX/etc/nginx"
NGINX_SERVERS_DIR="$NGINX_CONF_DIR/servers"

echo "=========================================="
echo "Domain Routing Configuration"
echo "=========================================="
echo ""

# Get domain name
read -p "Enter your domain name (e.g., app.yourdomain.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo "Domain name is required!"
    exit 1
fi

echo ""
echo "Configuring domain: $DOMAIN"
echo ""

# Create servers directory if it doesn't exist
mkdir -p "$NGINX_SERVERS_DIR"

# Check if nginx.conf includes servers directory
MAIN_CONF="$NGINX_CONF_DIR/nginx.conf"
if ! grep -q "include.*servers" "$MAIN_CONF" 2>/dev/null; then
    echo "⚠️  Need to add 'include servers/*.conf;' to nginx.conf"
    echo "   Adding it now..."
    
    # Create backup
    cp "$MAIN_CONF" "$MAIN_CONF.backup"
    
    # Add include statement in http block
    if grep -q "http {" "$MAIN_CONF"; then
        # Add after http { line
        sed -i.bak '/^http {/a\
    include servers/*.conf;
' "$MAIN_CONF"
        rm -f "$MAIN_CONF.bak"
        echo "✓ Added include statement to nginx.conf"
    else
        echo "✗ Could not find http block in nginx.conf"
        echo "  Please manually add: include servers/*.conf; in the http block"
    fi
fi

# Create domain configuration
echo "Creating domain configuration..."
NGINX_CONFIG="$NGINX_SERVERS_DIR/toll-app.conf"

cat > "$NGINX_CONFIG" << EOF
# Domain routing for E-ZPass Toll App
# Domain: $DOMAIN

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL Certificate paths (update after getting certificate)
    # ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    # For now, use self-signed or comment out SSL lines for HTTP only
    # Uncomment these after setting up SSL:
    # ssl_protocols TLSv1.2 TLSv1.3;
    # ssl_ciphers HIGH:!aNULL:!MD5;
    # ssl_prefer_server_ciphers on;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log $NGINX_PREFIX/var/log/nginx/toll-app-access.log;
    error_log $NGINX_PREFIX/var/log/nginx/toll-app-error.log;

    # Client max body size
    client_max_body_size 10M;

    # Proxy settings
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_set_header X-Forwarded-Host \$server_name;

    # WebSocket support
    proxy_http_version 1.1;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection "upgrade";

    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # Main application proxy (routes to Gunicorn on port 5000)
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_redirect off;
    }

    # Static files (optional - can serve directly from nginx)
    location /static/ {
        alias $APP_DIR/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

echo "✓ Domain configuration created: $NGINX_CONFIG"

# Test nginx configuration
echo ""
echo "Testing nginx configuration..."
if nginx -t 2>&1; then
    echo "✓ Nginx configuration is valid"
else
    echo "✗ Nginx configuration has errors!"
    echo "  Check: $NGINX_CONFIG"
    exit 1
fi

# Check if nginx is running
if brew services list | grep -q "nginx.*started"; then
    echo "Reloading nginx..."
    nginx -s reload
    echo "✓ Nginx reloaded"
else
    echo "Starting nginx..."
    brew services start nginx
    echo "✓ Nginx started"
fi

echo ""
echo "=========================================="
echo "Domain Routing Configured!"
echo "=========================================="
echo ""
echo "Configuration:"
echo "  Domain: $DOMAIN"
echo "  Config: $NGINX_CONFIG"
echo "  Backend: http://127.0.0.1:5000 (Gunicorn)"
echo ""
echo "Next Steps:"
echo "1. Configure DNS A record:"
echo "   $DOMAIN → Your server IP address"
echo ""
echo "2. Set up SSL certificate (optional but recommended):"
echo "   brew install certbot"
echo "   sudo certbot certonly --standalone -d $DOMAIN"
echo "   Then uncomment SSL lines in: $NGINX_CONFIG"
echo ""
echo "3. Test locally (add to /etc/hosts for testing):"
echo "   sudo nano /etc/hosts"
echo "   Add: 127.0.0.1 $DOMAIN"
echo ""
echo "4. Test domain:"
echo "   curl http://$DOMAIN"
echo "   curl http://$DOMAIN/user"
echo ""
echo "Nginx Management:"
echo "  Status:  brew services list | grep nginx"
echo "  Restart: brew services restart nginx"
echo "  Reload:  nginx -s reload"
echo "  Logs:    tail -f $NGINX_PREFIX/var/log/nginx/toll-app-access.log"
echo ""

