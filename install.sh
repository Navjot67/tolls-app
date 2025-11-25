#!/bin/bash

# E-ZPass NY Toll Dashboard - Mac Installer
# This script installs the dashboard application on any Mac

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation directory
INSTALL_DIR="${HOME}/ezpass-toll-dashboard"
APP_NAME="E-ZPass NY Toll Dashboard"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     E-ZPass NY Toll Dashboard - Mac Installation          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Error: This installer is for macOS only.${NC}"
    exit 1
fi

# Get the directory where the installer script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if installation directory already exists
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Installation directory already exists: $INSTALL_DIR${NC}"
    read -p "Do you want to reinstall? This will backup existing configs. (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Backup existing configs
        if [ -f "$INSTALL_DIR/accounts_config.json" ]; then
            cp "$INSTALL_DIR/accounts_config.json" "$INSTALL_DIR/accounts_config.json.backup"
        fi
        if [ -f "$INSTALL_DIR/.env" ]; then
            cp "$INSTALL_DIR/.env" "$INSTALL_DIR/.env.backup"
        fi
        rm -rf "$INSTALL_DIR"
    else
        echo "Installation cancelled."
        exit 0
    fi
fi

# Step 1: Check for Python 3
echo -e "${BLUE}[1/8]${NC} Checking Python 3 installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"

# Step 2: Check for Chrome
echo -e "${BLUE}[2/8]${NC} Checking Google Chrome installation..."
if [ ! -d "/Applications/Google Chrome.app" ]; then
    echo -e "${YELLOW}⚠ Warning: Google Chrome not found.${NC}"
    echo "Selenium requires Chrome to run. Please install Chrome from:"
    echo "https://www.google.com/chrome/"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} Google Chrome found"
fi

# Step 3: Create installation directory
echo -e "${BLUE}[3/8]${NC} Creating installation directory..."
mkdir -p "$INSTALL_DIR"
echo -e "${GREEN}✓${NC} Directory created: $INSTALL_DIR"

# Step 4: Copy application files
echo -e "${BLUE}[4/8]${NC} Copying application files..."

# List of files to copy (excluding venv, logs, temp files)
FILES_TO_COPY=(
    "app.py"
    "automation_selenium.py"
    "auto_fetch.py"
    "email_service.py"
    "test_email.py"
    "requirements.txt"
    "README.md"
    "EMAIL_SETUP.md"
    "AUTOMATION_SETUP.md"
    "EMAIL_TROUBLESHOOTING.md"
    "setup_autofetch.sh"
    "com.toll-dashboard-autofetch.plist.template"
    ".env.example"
)

# Copy files
for file in "${FILES_TO_COPY[@]}"; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        cp "$SCRIPT_DIR/$file" "$INSTALL_DIR/"
    fi
done

# Copy directories
if [ -d "$SCRIPT_DIR/templates" ]; then
    cp -r "$SCRIPT_DIR/templates" "$INSTALL_DIR/"
fi

if [ -d "$SCRIPT_DIR/static" ]; then
    cp -r "$SCRIPT_DIR/static" "$INSTALL_DIR/"
fi

echo -e "${GREEN}✓${NC} Files copied"

# Step 5: Create virtual environment
echo -e "${BLUE}[5/8]${NC} Creating Python virtual environment..."
cd "$INSTALL_DIR"
python3 -m venv venv
echo -e "${GREEN}✓${NC} Virtual environment created"

# Step 6: Install dependencies
echo -e "${BLUE}[6/8]${NC} Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

# Step 7: Create default configuration files
echo -e "${BLUE}[7/8]${NC} Setting up configuration files..."

# Create accounts_config.json if it doesn't exist
if [ ! -f "$INSTALL_DIR/accounts_config.json" ]; then
    cat > "$INSTALL_DIR/accounts_config.json" << 'EOF'
{
  "accounts": []
}
EOF
fi

# Restore backed up configs if they exist
if [ -f "$INSTALL_DIR/accounts_config.json.backup" ]; then
    cp "$INSTALL_DIR/accounts_config.json.backup" "$INSTALL_DIR/accounts_config.json"
    rm "$INSTALL_DIR/accounts_config.json.backup"
fi

# Create .env file from example if it doesn't exist
if [ ! -f "$INSTALL_DIR/.env" ]; then
    if [ -f "$INSTALL_DIR/.env.example" ]; then
        cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
        echo -e "${YELLOW}⚠ Created .env file from template. Please configure email settings.${NC}"
    fi
else
    # Restore backed up .env if it exists
    if [ -f "$INSTALL_DIR/.env.backup" ]; then
        cp "$INSTALL_DIR/.env.backup" "$INSTALL_DIR/.env"
        rm "$INSTALL_DIR/.env.backup"
    fi
fi

# Create plist from template if template exists, otherwise update existing one
if [ -f "$INSTALL_DIR/com.toll-dashboard-autofetch.plist.template" ]; then
    cp "$INSTALL_DIR/com.toll-dashboard-autofetch.plist.template" "$INSTALL_DIR/com.toll-dashboard-autofetch.plist"
    sed -i '' "s|INSTALL_DIR_PLACEHOLDER|$INSTALL_DIR|g" "$INSTALL_DIR/com.toll-dashboard-autofetch.plist"
else
    # Update existing plist file with correct paths
    sed -i '' "s|/Users/ghuman/tolls|$INSTALL_DIR|g" "$INSTALL_DIR/com.toll-dashboard-autofetch.plist" 2>/dev/null || \
    sed -i '' "s|INSTALL_DIR_PLACEHOLDER|$INSTALL_DIR|g" "$INSTALL_DIR/com.toll-dashboard-autofetch.plist" 2>/dev/null || true
fi

# Create logs directory
mkdir -p "$INSTALL_DIR/logs"

echo -e "${GREEN}✓${NC} Configuration files created"

# Step 8: Create launcher script
echo -e "${BLUE}[8/8]${NC} Creating launcher scripts..."

# Create start script
cat > "$INSTALL_DIR/start.sh" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
source venv/bin/activate
python3 app.py
EOF
chmod +x "$INSTALL_DIR/start.sh"

# Create stop script
cat > "$INSTALL_DIR/stop.sh" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pkill -f "python3 app.py"
echo "Dashboard stopped"
EOF
chmod +x "$INSTALL_DIR/stop.sh"

echo -e "${GREEN}✓${NC} Launcher scripts created"

# Installation complete
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Installation Completed Successfully!              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Installation Directory:${NC} $INSTALL_DIR"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo -e "1. ${YELLOW}Configure Email (Optional):${NC}"
echo "   Edit: $INSTALL_DIR/.env"
echo "   See: $INSTALL_DIR/EMAIL_SETUP.md"
echo ""
echo -e "2. ${YELLOW}Start the Dashboard:${NC}"
echo "   cd $INSTALL_DIR"
echo "   ./start.sh"
echo ""
echo "   Or run directly:"
echo "   cd $INSTALL_DIR && source venv/bin/activate && python3 app.py"
echo ""
echo -e "3. ${YELLOW}Open in Browser:${NC}"
echo "   http://localhost:5000"
echo ""
echo -e "4. ${YELLOW}Setup Automated Fetching (Optional):${NC}"
echo "   cd $INSTALL_DIR"
echo "   ./setup_autofetch.sh"
echo ""
echo -e "${BLUE}Quick Commands:${NC}"
echo "  Start:   cd $INSTALL_DIR && ./start.sh"
echo "  Stop:    cd $INSTALL_DIR && ./stop.sh"
echo "  Logs:    tail -f $INSTALL_DIR/auto_fetch.log"
echo ""
echo -e "${GREEN}Installation complete!${NC}"

