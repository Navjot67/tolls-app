#!/bin/bash
# Production Setup Script for E-ZPass Toll App (macOS)
# Sets up Gunicorn + LaunchAgent

set -e

echo "=========================================="
echo "E-ZPass Toll App - Production Setup (macOS)"
echo "=========================================="
echo ""

# Get app directory
read -p "Enter full path to app directory (default: /Users/ghuman/tolls): " APP_DIR
APP_DIR=${APP_DIR:-/Users/ghuman/tolls}

if [ ! -d "$APP_DIR" ]; then
    echo "App directory not found: $APP_DIR"
    exit 1
fi

echo ""
echo "Configuration:"
echo "  App Directory: $APP_DIR"
echo ""

# Create logs directory
echo "Creating logs directory..."
mkdir -p "$APP_DIR/logs"

# Check if virtual environment exists
if [ ! -d "$APP_DIR/venv" ]; then
    echo "Virtual environment not found. Creating..."
    cd "$APP_DIR"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Check if gunicorn is installed
echo "Checking Gunicorn installation..."
if [ ! -f "$APP_DIR/venv/bin/gunicorn" ]; then
    echo "Installing Gunicorn..."
    cd "$APP_DIR"
    source venv/bin/activate
    pip install gunicorn
fi

# Find gunicorn path
GUNICORN_PATH="$APP_DIR/venv/bin/gunicorn"
if [ ! -f "$GUNICORN_PATH" ]; then
    # Try system gunicorn
    if command -v gunicorn &> /dev/null; then
        GUNICORN_PATH=$(which gunicorn)
        echo "Using system Gunicorn: $GUNICORN_PATH"
    else
        echo "Error: Gunicorn not found!"
        exit 1
    fi
else
    echo "Using venv Gunicorn: $GUNICORN_PATH"
fi

# Test Gunicorn config
echo "Testing Gunicorn configuration..."
cd "$APP_DIR"
if "$GUNICORN_PATH" --check-config gunicorn_config.py app:app 2>&1 | head -5; then
    echo "✓ Gunicorn configuration is valid"
else
    echo "⚠️  Gunicorn config test completed (may show warnings)"
fi

# Create LaunchAgent plist
echo "Creating LaunchAgent configuration..."
PLIST_FILE="$HOME/Library/LaunchAgents/com.toll-app.plist"
cp "$APP_DIR/com.toll-app.plist" "$PLIST_FILE"

# Replace placeholders
sed -i.bak "s|GUNICORN_PATH_PLACEHOLDER|$GUNICORN_PATH|g" "$PLIST_FILE"
sed -i.bak "s|WORKING_DIR_PLACEHOLDER|$APP_DIR|g" "$PLIST_FILE"
sed -i.bak "s|LOGS_DIR_PLACEHOLDER|$APP_DIR/logs|g" "$PLIST_FILE"

# Remove backup file
rm -f "$PLIST_FILE.bak"

echo "✓ LaunchAgent plist created: $PLIST_FILE"

# Stop existing service if running
if launchctl list com.toll-app &>/dev/null; then
    echo "Stopping existing service..."
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
fi

# Load service
echo "Loading LaunchAgent service..."
launchctl load "$PLIST_FILE"

# Wait a moment
sleep 2

# Check status
echo ""
echo "Checking service status..."
if launchctl list com.toll-app &>/dev/null; then
    echo "✓ Service loaded successfully"
    launchctl list com.toll-app
else
    echo "⚠️  Service may not have started. Check logs:"
    echo "   tail -f $APP_DIR/logs/gunicorn-stderr.log"
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
echo "Service Management (macOS):"
echo "  Status:  launchctl list com.toll-app"
echo "  Start:   launchctl load $PLIST_FILE"
echo "  Stop:    launchctl unload $PLIST_FILE"
echo "  Restart: launchctl unload $PLIST_FILE && launchctl load $PLIST_FILE"
echo ""
echo "Logs:"
echo "  Stdout:  tail -f $APP_DIR/logs/gunicorn-stdout.log"
echo "  Stderr:  tail -f $APP_DIR/logs/gunicorn-stderr.log"
echo ""
echo "Test the app:"
echo "  curl http://localhost:5000"
echo ""
echo "To view service details:"
echo "  launchctl list com.toll-app"
echo ""

