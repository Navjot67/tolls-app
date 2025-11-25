#!/bin/bash
# Automated Production Setup for macOS (Non-interactive)
# Run: ./setup-production-auto.sh

set -e

APP_DIR="/Users/ghuman/tolls"
LOGS_DIR="$APP_DIR/logs"

echo "=========================================="
echo "E-ZPass Toll App - Automated Setup (macOS)"
echo "=========================================="
echo ""

# Create logs directory
echo "✓ Creating logs directory..."
mkdir -p "$LOGS_DIR"

# Check if virtual environment exists
if [ ! -d "$APP_DIR/venv" ]; then
    echo "⚠️  Virtual environment not found. Please create it first:"
    echo "   cd $APP_DIR && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Find gunicorn path
GUNICORN_PATH="$APP_DIR/venv/bin/gunicorn"
if [ ! -f "$GUNICORN_PATH" ]; then
    echo "Installing Gunicorn..."
    cd "$APP_DIR"
    source venv/bin/activate
    pip install gunicorn
fi

echo "✓ Gunicorn found: $GUNICORN_PATH"

# Test Gunicorn config
echo "Testing Gunicorn configuration..."
cd "$APP_DIR"
if "$GUNICORN_PATH" --check-config gunicorn_config.py app:app 2>&1 | head -5; then
    echo "✓ Gunicorn configuration is valid"
fi

# Create LaunchAgent plist
echo "Creating LaunchAgent configuration..."
PLIST_FILE="$HOME/Library/LaunchAgents/com.toll-app.plist"

# Create plist with actual paths
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.toll-app</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$GUNICORN_PATH</string>
        <string>--config</string>
        <string>$APP_DIR/gunicorn_config.py</string>
        <string>app:app</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>$APP_DIR</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>$LOGS_DIR/gunicorn-stdout.log</string>
    
    <key>StandardErrorPath</key>
    <string>$LOGS_DIR/gunicorn-stderr.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>PYTHONPATH</key>
        <string>$APP_DIR</string>
    </dict>
</dict>
</plist>
EOF

echo "✓ LaunchAgent plist created: $PLIST_FILE"

# Stop existing service if running
if launchctl list com.toll-app &>/dev/null; then
    echo "Stopping existing service..."
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
    sleep 1
fi

# Load service
echo "Loading LaunchAgent service..."
launchctl load "$PLIST_FILE"

# Wait a moment
sleep 3

# Check status
echo ""
echo "Checking service status..."
if launchctl list com.toll-app &>/dev/null; then
    echo "✓ Service loaded successfully!"
    echo ""
    launchctl list com.toll-app
else
    echo "⚠️  Service may not have started. Check logs:"
    echo "   tail -f $LOGS_DIR/gunicorn-stderr.log"
fi

# Test endpoint
echo ""
echo "Testing application..."
sleep 2
if curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo "✓ Application is responding!"
else
    echo "⚠️  Application not responding yet. Check logs:"
    echo "   tail -f $LOGS_DIR/gunicorn-stderr.log"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Service Management:"
echo "  Status:  launchctl list com.toll-app"
echo "  Stop:    launchctl unload $PLIST_FILE"
echo "  Start:   launchctl load $PLIST_FILE"
echo "  Restart: launchctl unload $PLIST_FILE && launchctl load $PLIST_FILE"
echo ""
echo "Logs:"
echo "  Stdout:  tail -f $LOGS_DIR/gunicorn-stdout.log"
echo "  Stderr:  tail -f $LOGS_DIR/gunicorn-stderr.log"
echo ""
echo "Test: curl http://localhost:5000"
echo ""

