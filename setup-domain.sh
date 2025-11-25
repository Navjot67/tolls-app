#!/bin/bash
# Domain Setup Script for E-ZPass User App
# This script helps set up nginx and domain configuration

set -e

echo "=========================================="
echo "E-ZPass User App - Domain Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

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
    echo "Nginx is not installed. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install nginx
    else
        apt-get update
        apt-get install -y nginx
    fi
fi

# Copy nginx config
echo "Creating nginx configuration..."
NGINX_CONFIG="/etc/nginx/sites-available/toll-app"
cp "$APP_DIR/nginx-domain.conf" "$NGINX_CONFIG"

# Replace placeholders
sed -i.bak "s/YOUR_DOMAIN/$DOMAIN/g" "$NGINX_CONFIG"
sed -i.bak "s|/Users/ghuman/tolls|$APP_DIR|g" "$NGINX_CONFIG"

# Enable site
echo "Enabling nginx site..."
ln -sf "$NGINX_CONFIG" /etc/nginx/sites-enabled/toll-app

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
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install certbot
        else
            apt-get install -y certbot python3-certbot-nginx
        fi
    fi
    
    echo "Obtaining SSL certificate..."
    certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --email admin@$DOMAIN || {
        echo "SSL certificate setup failed. You can set it up manually later with:"
        echo "  certbot --nginx -d $DOMAIN"
    }
fi

# Reload nginx
echo "Reloading nginx..."
systemctl reload nginx || service nginx reload || nginx -s reload

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure DNS A record for $DOMAIN to point to this server's IP"
echo "2. Wait for DNS propagation (usually 5-60 minutes)"
echo "3. Test your domain: https://$DOMAIN/user"
echo ""
echo "If SSL certificate setup was skipped, run:"
echo "  certbot --nginx -d $DOMAIN"
echo ""
echo "Nginx config file: $NGINX_CONFIG"
echo ""

