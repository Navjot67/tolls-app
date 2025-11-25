#!/bin/bash
# Domain Setup Script for macOS (Homebrew Nginx)
# This script helps set up nginx and domain configuration

set -e

echo "=========================================="
echo "E-ZPass User App - Domain Setup (macOS)"
echo "=========================================="
echo ""

# Get domain name
read -p "Enter your domain name (e.g., app.yourdomain.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo "Domain name is required!"
    exit 1
fi

# Get app directory
read -p "Enter full path to app directory (default: /Users/ghuman/tolls): " APP_DIR
APP_DIR=${APP_DIR:-/Users/ghuman/tolls}

if [ ! -d "$APP_DIR" ]; then
    echo "App directory not found: $APP_DIR"
    exit 1
fi

echo ""
echo "Configuration:"
echo "  Domain: $DOMAIN"
echo "  App Directory: $APP_DIR"
echo ""

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "Nginx is not installed. Installing via Homebrew..."
    brew install nginx
fi

NGINX_PREFIX=$(brew --prefix nginx)
NGINX_CONF_DIR="$NGINX_PREFIX/etc/nginx"
NGINX_SERVERS_DIR="$NGINX_CONF_DIR/servers"

# Create servers directory if it doesn't exist
mkdir -p "$NGINX_SERVERS_DIR"

echo "✓ Nginx found at: $NGINX_PREFIX"
echo "✓ Config directory: $NGINX_CONF_DIR"
echo ""

# Copy nginx config
echo "Creating nginx configuration..."
NGINX_CONFIG="$NGINX_SERVERS_DIR/toll-app.conf"
cp "$APP_DIR/nginx-domain.conf" "$NGINX_CONFIG"

# Replace placeholders
sed -i.bak "s/YOUR_DOMAIN/$DOMAIN/g" "$NGINX_CONFIG"
sed -i.bak "s|/Users/ghuman/tolls|$APP_DIR|g" "$NGINX_CONFIG"

# Remove backup file
rm -f "$NGINX_CONFIG.bak"

echo "✓ Nginx configuration created: $NGINX_CONFIG"

# Update main nginx.conf to include servers directory if not already
MAIN_CONF="$NGINX_CONF_DIR/nginx.conf"
if ! grep -q "include.*servers" "$MAIN_CONF" 2>/dev/null; then
    echo ""
    echo "⚠️  Need to add 'include servers/*.conf;' to nginx.conf"
    echo "   Edit: $MAIN_CONF"
    echo "   Add this line in the http block:"
    echo "   include servers/*.conf;"
    echo ""
    read -p "Press Enter to continue after updating nginx.conf..."
fi

# Test nginx config
echo "Testing nginx configuration..."
if nginx -t; then
    echo "✓ Nginx configuration is valid"
else
    echo "✗ Nginx configuration has errors. Please check: $NGINX_CONFIG"
    exit 1
fi

# SSL Certificate setup
echo ""
read -p "Do you want to set up SSL certificate with Let's Encrypt? (y/n): " SETUP_SSL
if [ "$SETUP_SSL" = "y" ] || [ "$SETUP_SSL" = "Y" ]; then
    # Check if certbot is installed
    if ! command -v certbot &> /dev/null; then
        echo "Installing certbot..."
        brew install certbot
    fi
    
    echo "Obtaining SSL certificate..."
    echo "Note: You'll need to temporarily stop nginx for certbot to work"
    echo ""
    read -p "Press Enter when ready to continue with SSL setup..."
    
    # Stop nginx temporarily
    brew services stop nginx 2>/dev/null || true
    
    certbot certonly --standalone -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --email admin@$DOMAIN || {
        echo ""
        echo "SSL certificate setup failed or needs manual configuration."
        echo "You can set it up manually later with:"
        echo "  certbot certonly --standalone -d $DOMAIN"
        echo ""
        echo "Or use nginx mode after starting nginx:"
        echo "  certbot --nginx -d $DOMAIN"
    }
    
    # Update nginx config with SSL paths
    if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
        sed -i.bak "s|/etc/letsencrypt/live/YOUR_DOMAIN|/etc/letsencrypt/live/$DOMAIN|g" "$NGINX_CONFIG"
        rm -f "$NGINX_CONFIG.bak"
        echo "✓ SSL certificate paths updated in nginx config"
    fi
    
    # Restart nginx
    brew services start nginx
fi

# Reload nginx
echo "Reloading nginx..."
brew services restart nginx || nginx -s reload

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure DNS A record for $DOMAIN to point to this server's IP"
echo "2. Wait for DNS propagation (usually 5-60 minutes)"
echo "3. Test your domain: http://$DOMAIN/user"
echo ""
echo "If SSL certificate setup was skipped, run:"
echo "  certbot --nginx -d $DOMAIN"
echo ""
echo "Nginx config file: $NGINX_CONFIG"
echo ""
echo "Nginx Management:"
echo "  Start:   brew services start nginx"
echo "  Stop:    brew services stop nginx"
echo "  Restart: brew services restart nginx"
echo "  Status:  brew services list | grep nginx"
echo "  Test:    nginx -t"
echo "  Reload:  nginx -s reload"
echo ""

