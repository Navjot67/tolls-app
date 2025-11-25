#!/bin/bash
# Setup script to enable automatic email checking

echo "Setting up automatic email checking..."
echo ""

# Get the absolute path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_FILE="$SCRIPT_DIR/com.toll-email-checker.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$LAUNCH_AGENTS_DIR/com.toll.email-checker.plist"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Get Python path
PYTHON_PATH=$(which python3)

# Update plist with correct paths
sed -e "s|EMAIL_CHECKER_PATH_PLACEHOLDER|$SCRIPT_DIR/email_checker_worker.py|g" \
    -e "s|WORKING_DIR_PLACEHOLDER|$SCRIPT_DIR|g" \
    -e "s|LOGS_DIR_PLACEHOLDER|$SCRIPT_DIR/logs|g" \
    "$PLIST_FILE" > "$TARGET_PLIST"

# Load the service
echo "Loading email checker service..."
launchctl unload "$TARGET_PLIST" 2>/dev/null
launchctl load "$TARGET_PLIST"

if [ $? -eq 0 ]; then
    echo "✅ Email checker service installed and started!"
    echo ""
    echo "The service will:"
    echo "  - Start automatically on login"
    echo "  - Restart automatically if it crashes"
    echo "  - Check emails every hour (configurable via EMAIL_CHECK_INTERVAL in .env)"
    echo ""
    echo "To check status:"
    echo "  launchctl list | grep email-checker"
    echo ""
    echo "To stop:"
    echo "  launchctl unload ~/Library/LaunchAgents/com.toll.email-checker.plist"
    echo ""
    echo "To start:"
    echo "  launchctl load ~/Library/LaunchAgents/com.toll.email-checker.plist"
    echo ""
    echo "Logs are in: $SCRIPT_DIR/logs/"
else
    echo "❌ Failed to load service"
    exit 1
fi

