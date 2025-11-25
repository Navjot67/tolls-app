#!/bin/bash
# Fix nginx to listen on port 80 properly

echo "Fixing nginx configuration for port 80..."

# Check if nginx is running as root or user
if lsof -i :80 2>/dev/null | grep -q nginx; then
    echo "✓ Nginx is listening on port 80"
else
    echo "⚠ Nginx may need to bind to port 80"
    echo "Port 80 requires root/sudo access"
fi

# Update nginx config to ensure it listens on all interfaces
cat > /opt/homebrew/etc/nginx/servers/toll-app.conf << 'EOF'
# Domain routing for www.tlcezpass.com
server {
    listen 80;
    listen [::]:80;
    server_name www.tlcezpass.com tlcezpass.com;

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
    }

    # Static files
    location /static/ {
        alias /Users/ghuman/tolls/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

echo "✓ Updated nginx configuration"
nginx -t && echo "✓ Configuration is valid" || echo "✗ Configuration error"

echo ""
echo "To run nginx on port 80, you may need to:"
echo "1. Stop nginx: brew services stop nginx"
echo "2. Run with sudo: sudo nginx"
echo "Or configure nginx to run as root in launchd"

