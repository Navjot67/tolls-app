#!/bin/bash
# Simple Domain Setup - Works with current nginx installation
# Usage: ./setup-domain-simple.sh YOUR_DOMAIN

set -e

if [ -z "$1" ]; then
    DOMAIN="tollapp.local"
    echo "Using default domain: $DOMAIN"
    echo "To use custom domain: ./setup-domain-simple.sh yourdomain.com"
else
    DOMAIN="$1"
fi

APP_DIR="/Users/ghuman/tolls"

# Find nginx config directory
NGINX_CONF=$(nginx -T 2>&1 | grep "configuration file" | awk '{print $NF}' | head -1)
NGINX_DIR=$(dirname "$NGINX_CONF")
NGINX_SERVERS_DIR="$NGINX_DIR/servers"

echo "=========================================="
echo "Setting up domain: $DOMAIN"
echo "=========================================="
echo "Nginx config: $NGINX_CONF"
echo "Servers dir: $NGINX_SERVERS_DIR"
echo ""

# Create servers directory
mkdir -p "$NGINX_SERVERS_DIR"

# Check if include exists in nginx.conf
if ! grep -q "include.*servers" "$NGINX_CONF" 2>/dev/null; then
    echo "⚠️  Need to add 'include servers/*.conf;' to nginx.conf"
    echo "   Please add this line in the http block of: $NGINX_CONF"
    echo "   Or run: echo '    include servers/*.conf;' >> $NGINX_CONF"
    echo ""
    read -p "Press Enter after adding the include line, or Ctrl+C to cancel..."
fi

# Create domain config
echo "Creating domain configuration..."
cat > "$NGINX_SERVERS_DIR/toll-app.conf" << EOF
# Domain routing for $DOMAIN
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files
    location /static/ {
        alias $APP_DIR/static/;
        expires 30d;
    }
}
EOF

echo "✓ Configuration created: $NGINX_SERVERS_DIR/toll-app.conf"

# Test config
echo "Testing nginx configuration..."
if nginx -t; then
    echo "✓ Configuration is valid"
else
    echo "✗ Configuration has errors!"
    exit 1
fi

# Reload nginx
echo "Reloading nginx..."
nginx -s reload 2>/dev/null || brew services restart nginx

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Domain: $DOMAIN"
echo ""
echo "To test locally, add to /etc/hosts:"
echo "  sudo sh -c 'echo \"127.0.0.1 $DOMAIN\" >> /etc/hosts'"
echo ""
echo "Then test:"
echo "  curl http://$DOMAIN"
echo "  curl http://$DOMAIN/user"
echo ""
echo "Or open in browser:"
echo "  http://$DOMAIN"
echo "  http://$DOMAIN/user"
echo ""

