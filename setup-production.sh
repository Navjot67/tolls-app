#!/bin/bash
# Production Setup Script for E-ZPass Toll App
# Sets up Gunicorn + Systemd + Nginx

set -e

echo "=========================================="
echo "E-ZPass Toll App - Production Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Get app directory
read -p "Enter full path to app directory (default: /Users/ghuman/tolls): " APP_DIR
APP_DIR=${APP_DIR:-/Users/ghuman/tolls}

if [ ! -d "$APP_DIR" ]; then
    echo "App directory not found: $APP_DIR"
    exit 1
fi

# Get user and group
read -p "Enter system user to run app (default: $(whoami)): " APP_USER
APP_USER=${APP_USER:-$(whoami)}

read -p "Enter system group (default: $APP_USER): " APP_GROUP
APP_GROUP=${APP_GROUP:-$APP_USER}

# Check if user exists
if ! id "$APP_USER" &>/dev/null; then
    echo "User $APP_USER does not exist!"
    exit 1
fi

echo ""
echo "Configuration:"
echo "  App Directory: $APP_DIR"
echo "  User: $APP_USER"
echo "  Group: $APP_GROUP"
echo ""

# Create logs directory
echo "Creating logs directory..."
mkdir -p "$APP_DIR/logs"
chown "$APP_USER:$APP_GROUP" "$APP_DIR/logs"

# Check if virtual environment exists
if [ ! -d "$APP_DIR/venv" ]; then
    echo "Virtual environment not found. Creating..."
    cd "$APP_DIR"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Update service file
echo "Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/toll-app.service"
cp "$APP_DIR/toll-app.service" "$SERVICE_FILE"

# Replace placeholders
sed -i.bak "s|YOUR_USER|$APP_USER|g" "$SERVICE_FILE"
sed -i.bak "s|YOUR_GROUP|$APP_GROUP|g" "$SERVICE_FILE"
sed -i.bak "s|/Users/ghuman/tolls|$APP_DIR|g" "$SERVICE_FILE"

# Check if gunicorn is installed
echo "Checking Gunicorn installation..."
if [ ! -f "$APP_DIR/venv/bin/gunicorn" ]; then
    echo "Installing Gunicorn..."
    cd "$APP_DIR"
    source venv/bin/activate
    pip install gunicorn
fi

# Test Gunicorn config
echo "Testing Gunicorn configuration..."
cd "$APP_DIR"
if "$APP_DIR/venv/bin/gunicorn" --check-config gunicorn_config.py app:app 2>&1 | head -5; then
    echo "✓ Gunicorn configuration is valid"
else
    echo "⚠️  Gunicorn config test completed (may show warnings)"
fi

# Enable and start service
echo "Enabling systemd service..."
systemctl daemon-reload
systemctl enable toll-app

echo ""
read -p "Do you want to start the service now? (y/n): " START_SERVICE
if [ "$START_SERVICE" = "y" ] || [ "$START_SERVICE" = "Y" ]; then
    systemctl start toll-app
    sleep 2
    systemctl status toll-app --no-pager
fi

# Setup domain (optional)
echo ""
read -p "Do you want to set up domain/nginx now? (y/n): " SETUP_DOMAIN
if [ "$SETUP_DOMAIN" = "y" ] || [ "$SETUP_DOMAIN" = "Y" ]; then
    if [ -f "$APP_DIR/setup-domain.sh" ]; then
        bash "$APP_DIR/setup-domain.sh"
    else
        echo "Domain setup script not found. Run manually: sudo ./setup-domain.sh"
    fi
fi

echo ""
echo "=========================================="
echo "Production Setup Complete!"
echo "=========================================="
echo ""
echo "Service Management:"
echo "  Status:  sudo systemctl status toll-app"
echo "  Start:   sudo systemctl start toll-app"
echo "  Stop:    sudo systemctl stop toll-app"
echo "  Restart: sudo systemctl restart toll-app"
echo "  Logs:    sudo journalctl -u toll-app -f"
echo ""
echo "Gunicorn Logs:"
echo "  Access:  tail -f $APP_DIR/logs/gunicorn-access.log"
echo "  Error:   tail -f $APP_DIR/logs/gunicorn-error.log"
echo ""
echo "Test the app:"
echo "  curl http://localhost:5000"
echo ""

