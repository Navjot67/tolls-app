#!/bin/bash
# Automated Domain Routing Configuration
# Usage: ./configure-domain-auto.sh YOUR_DOMAIN
# Example: ./configure-domain-auto.sh app.yourdomain.com

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 YOUR_DOMAIN"
    echo "Example: $0 app.yourdomain.com"
    exit 1
fi

DOMAIN="$1"
APP_DIR="/Users/ghuman/tolls"
NGINX_PREFIX=$(brew --prefix nginx)
NGINX_CONF_DIR="$NGINX_PREFIX/etc/nginx"
NGINX_SERVERS_DIR="$NGINX_CONF_DIR/servers"

echo "=========================================="
echo "Configuring Domain Routing"
echo "=========================================="
echo "Domain: $DOMAIN"
echo ""

# Create servers directory
mkdir -p "$NGINX_SERVERS_DIR"

# Update nginx.conf to include servers directory
MAIN_CONF="$NGINX_CONF_DIR/nginx.conf"
if ! grep -q "include.*servers" "$MAIN_CONF" 2>/dev/null; then
    echo "Adding servers/*.conf to nginx.conf..."
    cp "$MAIN_CONF" "$MAIN_CONF.backup"
    
    # Add include after http {
    if grep -q "^http {" "$MAIN_CONF"; then
        sed -i.bak '/^http {/a\
    include servers/*.conf;
' "$MAIN_CONF"
        rm -f "$MAIN_CONF.bak"
        echo "✓ Updated nginx.conf"
    fi
fi

# Create domain configuration
echo "Creating domain configuration..."
NGINX_CONFIG="$NGINX_SERVERS_DIR/toll-app.conf"

cat > "$NGINX_CONFIG" << 'EOF'
# Domain routing for E-ZPass Toll App
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER www.DOMAIN_PLACEHOLDER;

    # Redirect HTTP to HTTPS (comment out if no SSL yet)
    # return 301 https://$server_name$request_uri;
    
    # For now, allow HTTP (uncomment above after SSL setup)
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

# HTTPS server (uncomment after SSL certificate setup)
# server {
#     listen 443 ssl http2;
#     server_name DOMAIN_PLACEHOLDER www.DOMAIN_PLACEHOLDER;
#
#     ssl_certificate /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/fullchain.pem;
#     ssl_certificate_key /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/privkey.pem;
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers HIGH:!aNULL:!MD5;
#     ssl_prefer_server_ciphers on;
#
#     proxy_set_header Host $host;
#     proxy_set_header X-Real-IP $remote_addr;
#     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#     proxy_set_header X-Forwarded-Proto $scheme;
#
#     location / {
#         proxy_pass http://127.0.0.1:5000;
#         proxy_redirect off;
#     }
#
#     location /static/ {
#         alias APP_DIR_PLACEHOLDER/static/;
#         expires 30d;
#     }
# }
EOF

# Replace placeholders
sed -i.bak "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" "$NGINX_CONFIG"
sed -i.bak "s|APP_DIR_PLACEHOLDER|$APP_DIR|g" "$NGINX_CONFIG"
rm -f "$NGINX_CONFIG.bak"

echo "✓ Configuration created: $NGINX_CONFIG"

# Test nginx config
echo "Testing nginx configuration..."
if nginx -t 2>&1; then
    echo "✓ Nginx configuration is valid"
else
    echo "✗ Configuration has errors!"
    exit 1
fi

# Reload nginx
if brew services list | grep -q "nginx.*started"; then
    echo "Reloading nginx..."
    nginx -s reload
else
    echo "Starting nginx..."
    brew services start nginx
fi

echo ""
echo "=========================================="
echo "Domain Routing Configured!"
echo "=========================================="
echo ""
echo "Domain: $DOMAIN"
echo "Backend: http://127.0.0.1:5000"
echo ""
echo "Next steps:"
echo "1. Add to /etc/hosts for local testing:"
echo "   sudo sh -c 'echo \"127.0.0.1 $DOMAIN\" >> /etc/hosts'"
echo ""
echo "2. Test: curl http://$DOMAIN"
echo ""
echo "3. Configure DNS A record: $DOMAIN → Your server IP"
echo ""

