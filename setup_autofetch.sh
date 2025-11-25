#!/bin/bash
# Setup script for automated toll information fetching

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_NAME="com.toll-dashboard-autofetch"
PLIST_FILE="$SCRIPT_DIR/$PLIST_NAME.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_NAME.plist"

# Update plist with current paths if not already updated
if grep -q "/Users/ghuman/tolls" "$PLIST_FILE" 2>/dev/null; then
    INSTALL_DIR="$SCRIPT_DIR"
    sed -i '' "s|/Users/ghuman/tolls|$INSTALL_DIR|g" "$PLIST_FILE" 2>/dev/null || \
    sed -i "s|/Users/ghuman/tolls|$INSTALL_DIR|g" "$PLIST_FILE" 2>/dev/null || true
fi

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Automated Toll Fetch Setup (Every 3 Hours)             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if plist file exists
if [ ! -f "$PLIST_FILE" ]; then
    echo "❌ Error: Plist file not found at $PLIST_FILE"
    exit 1
fi

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

# Check if already loaded
if launchctl list | grep -q "$PLIST_NAME"; then
    echo "⚠️  Service is already loaded. Unloading first..."
    launchctl unload "$TARGET_PLIST" 2>/dev/null || true
fi

# Copy plist to LaunchAgents
echo "📋 Copying plist file to LaunchAgents..."
cp "$PLIST_FILE" "$TARGET_PLIST"

# Load the service
echo "🚀 Loading launchd service..."
launchctl load "$TARGET_PLIST"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Automated fetching is now set up!"
    echo ""
    echo "📋 Configuration:"
    echo "   • Runs every 3 hours automatically"
    echo "   • Accounts configured in: $SCRIPT_DIR/accounts_config.json"
    echo "   • Logs saved to: $SCRIPT_DIR/auto_fetch.log"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Edit $SCRIPT_DIR/accounts_config.json"
    echo "   2. Add your account numbers, plate numbers, and emails"
    echo "   3. The script will run automatically every 3 hours"
    echo ""
    echo "🔧 Management commands:"
    echo "   • Check status: launchctl list | grep $PLIST_NAME"
    echo "   • View logs: tail -f $SCRIPT_DIR/auto_fetch.log"
    echo "   • Stop: launchctl unload $TARGET_PLIST"
    echo "   • Start: launchctl load $TARGET_PLIST"
    echo "   • Run now: $SCRIPT_DIR/venv/bin/python3 $SCRIPT_DIR/auto_fetch.py"
    echo ""
else
    echo "❌ Failed to load service. Check the plist file for errors."
    exit 1
fi


