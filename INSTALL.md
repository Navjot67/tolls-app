# E-ZPass NY Toll Dashboard - Installation Guide for Mac

## Quick Installation

1. **Download or extract the package** to a location on your Mac

2. **Open Terminal** and navigate to the package directory

3. **Run the installer:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

4. **Start the dashboard:**
   ```bash
   cd ~/ezpass-toll-dashboard
   ./start.sh
   ```

5. **Open in your browser:**
   ```
   http://localhost:5000
   ```

## System Requirements

- **macOS** 10.13 (High Sierra) or later
- **Python 3.7** or later (included with macOS or download from [python.org](https://www.python.org/downloads/))
- **Google Chrome** browser (required for automation)
- **Internet connection**

## Detailed Installation Steps

### Step 1: Prerequisites

Check if Python 3 is installed:
```bash
python3 --version
```

If not installed, download from: https://www.python.org/downloads/

Install Google Chrome if not already installed:
https://www.google.com/chrome/

### Step 2: Install the Application

1. Extract the package or clone the repository
2. Open Terminal and navigate to the package directory
3. Make the installer executable:
   ```bash
   chmod +x install.sh
   ```
4. Run the installer:
   ```bash
   ./install.sh
   ```

The installer will:
- Create installation directory: `~/ezpass-toll-dashboard`
- Set up Python virtual environment
- Install all dependencies
- Create configuration files
- Create launcher scripts

### Step 3: Configure Email (Optional)

To enable email notifications:

1. Edit the `.env` file:
   ```bash
   cd ~/ezpass-toll-dashboard
   nano .env
   ```

2. Add your email settings:
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   FROM_EMAIL=your-email@gmail.com
   ```

3. See `EMAIL_SETUP.md` for detailed instructions

### Step 4: Start the Dashboard

**Option 1: Using the launcher script**
```bash
cd ~/ezpass-toll-dashboard
./start.sh
```

**Option 2: Manual start**
```bash
cd ~/ezpass-toll-dashboard
source venv/bin/activate
python3 app.py
```

The dashboard will be available at: **http://localhost:5000**

### Step 5: Setup Automated Fetching (Optional)

To automatically fetch toll information every 3 hours:

```bash
cd ~/ezpass-toll-dashboard
./setup_autofetch.sh
```

This will set up a background scheduler that runs automatically.

## Usage

### Web Dashboard

1. Open http://localhost:5000 in your browser
2. Enter account number and license plate
3. (Optional) Enter email address for notifications
4. Click "Fetch Toll Information"
5. View your balance and bill numbers

### Managing Saved Accounts

- Click "Refresh Accounts" to load saved accounts
- Click "Add Account" to add a new account to auto-fetch list
- Accounts in the auto-fetch list are processed every 3 hours (if automation is enabled)

### Multi-User Mode

- Click "Add User" to add multiple accounts
- Fill in account and plate numbers for each user
- Click "Fetch All" to process all accounts at once
- Results will be displayed in a grid

## Configuration Files

- **`accounts_config.json`**: Saved accounts for automated fetching
- **`.env`**: Email configuration (optional)
- **`com.toll-dashboard-autofetch.plist`**: macOS scheduler configuration

## Troubleshooting

### Dashboard Won't Start

1. Check if port 5000 is already in use:
   ```bash
   lsof -i :5000
   ```
2. Stop any existing instances:
   ```bash
   cd ~/ezpass-toll-dashboard
   ./stop.sh
   ```
3. Try starting again

### Chrome Driver Issues

Selenium automatically manages ChromeDriver via `webdriver-manager`. If you encounter issues:

1. Make sure Google Chrome is installed and up to date
2. Check Chrome version:
   ```bash
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
   ```

### Python Environment Issues

If you encounter import errors:

1. Make sure you're using the virtual environment:
   ```bash
   cd ~/ezpass-toll-dashboard
   source venv/bin/activate
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Automation Not Running

Check if the scheduler is loaded:
```bash
launchctl list | grep toll-dashboard
```

Check logs:
```bash
tail -f ~/ezpass-toll-dashboard/auto_fetch.log
```

Reload the scheduler:
```bash
cd ~/ezpass-toll-dashboard
./setup_autofetch.sh
```

## Uninstallation

To remove the application:

```bash
cd ~/ezpass-toll-dashboard
chmod +x uninstall.sh
./uninstall.sh
```

This will:
- Stop the dashboard
- Remove automated scheduler
- Backup configuration files
- Remove installation directory

## File Structure

```
~/ezpass-toll-dashboard/
├── app.py                          # Flask backend
├── automation_selenium.py          # Web automation script
├── auto_fetch.py                   # Automated fetching script
├── email_service.py                # Email service
├── requirements.txt                # Python dependencies
├── accounts_config.json            # Saved accounts
├── .env                           # Email configuration
├── start.sh                       # Start script
├── stop.sh                        # Stop script
├── setup_autofetch.sh             # Setup automation
├── templates/                     # HTML templates
│   ├── dashboard.html
│   └── email_template.html
└── static/                        # CSS/JS files
    ├── style.css
    ├── script.js
    ├── multi-user.js
    └── saved-accounts.js
```

## Support

For issues or questions:
1. Check `README.md` for general information
2. Check `EMAIL_SETUP.md` for email configuration
3. Check `AUTOMATION_SETUP.md` for automation setup
4. Review logs in `auto_fetch.log`

## License

MIT




