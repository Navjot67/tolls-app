#!/bin/bash

# E-ZPass NY Toll Dashboard - Uninstaller
# This script removes the dashboard application from your Mac

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

INSTALL_DIR="${HOME}/ezpass-toll-dashboard"
PLIST_FILE="${HOME}/Library/LaunchAgents/com.toll-dashboard-autofetch.plist"

echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║     E-ZPass NY Toll Dashboard - Uninstaller                ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if installation directory exists
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Installation directory not found: $INSTALL_DIR${NC}"
    echo "Nothing to uninstall."
    exit 0
fi

# Stop dashboard if running
echo -e "${BLUE}[1/4]${NC} Stopping dashboard..."
pkill -f "python3 app.py" 2>/dev/null || true
echo -e "${GREEN}✓${NC} Dashboard stopped"

# Unload launchd service if it exists
echo -e "${BLUE}[2/4]${NC} Removing automated scheduler..."
if [ -f "$PLIST_FILE" ]; then
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
    rm -f "$PLIST_FILE"
    echo -e "${GREEN}✓${NC} Automated scheduler removed"
else
    echo -e "${YELLOW}⚠${NC} Scheduler not found (may not have been set up)"
fi

# Ask about removing configuration files
echo -e "${BLUE}[3/4]${NC} Backup configuration files..."
BACKUP_DIR="${HOME}/ezpass-toll-dashboard-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f "$INSTALL_DIR/accounts_config.json" ]; then
    cp "$INSTALL_DIR/accounts_config.json" "$BACKUP_DIR/"
    echo -e "${GREEN}✓${NC} Backed up accounts_config.json"
fi

if [ -f "$INSTALL_DIR/.env" ]; then
    cp "$INSTALL_DIR/.env" "$BACKUP_DIR/"
    echo -e "${GREEN}✓${NC} Backed up .env file"
fi

echo -e "${YELLOW}Configuration files backed up to: $BACKUP_DIR${NC}"

# Remove installation directory
echo -e "${BLUE}[4/4]${NC} Removing installation directory..."
read -p "Are you sure you want to remove $INSTALL_DIR? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$INSTALL_DIR"
    echo -e "${GREEN}✓${NC} Installation directory removed"
else
    echo "Uninstall cancelled. Files remain in $INSTALL_DIR"
    exit 0
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Uninstallation Completed!                     ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Configuration files backed up to:${NC} $BACKUP_DIR"
echo ""
echo -e "${GREEN}Uninstallation complete!${NC}"




