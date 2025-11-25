# Automated Toll Information Fetching

This guide explains how to set up automatic toll information fetching that runs every 3 hours without any user interaction.

## Quick Setup

1. **Configure your accounts:**
   Edit `accounts_config.json` and add your account details:
   ```json
   {
     "accounts": [
       {
         "account_number": "YOUR_ACCOUNT_NUMBER",
         "plate_number": "YOUR_PLATE_NUMBER",
         "email": "your-email@example.com"
       },
       {
         "account_number": "ANOTHER_ACCOUNT",
         "plate_number": "ANOTHER_PLATE",
         "email": "another-email@example.com"
       }
     ]
   }
   ```

2. **Run the setup script:**
   ```bash
   ./setup_autofetch.sh
   ```

That's it! The script will now run automatically every 3 hours.

## How It Works

- **Schedule**: Runs every 3 hours (10,800 seconds)
- **Mode**: Runs in headless mode (no browser window)
- **Processing**: All accounts are processed in parallel
- **Emails**: Each account receives an email if configured
- **Logging**: All activity is logged to `auto_fetch.log`

## Files

- `auto_fetch.py` - Main automation script
- `accounts_config.json` - Account configurations
- `com.toll-dashboard-autofetch.plist` - macOS launchd configuration
- `auto_fetch.log` - Execution logs
- `launchd_stdout.log` - Standard output from launchd
- `launchd_stderr.log` - Standard error from launchd

## Management Commands

### Check if service is running:
```bash
launchctl list | grep com.toll-dashboard-autofetch
```

### View recent logs:
```bash
tail -f auto_fetch.log
```

### Stop automatic fetching:
```bash
launchctl unload ~/Library/LaunchAgents/com.toll-dashboard-autofetch.plist
```

### Start automatic fetching:
```bash
launchctl load ~/Library/LaunchAgents/com.toll-dashboard-autofetch.plist
```

### Run manually (test):
```bash
./venv/bin/python3 auto_fetch.py
```

### Uninstall:
```bash
launchctl unload ~/Library/LaunchAgents/com.toll-dashboard-autofetch.plist
rm ~/Library/LaunchAgents/com.toll-dashboard-autofetch.plist
```

## Schedule Details

- **Interval**: 3 hours (10,800 seconds)
- **First Run**: Starts 3 hours after setup
- **Runs**: Continuously every 3 hours
- **Timezone**: Uses system timezone

## Troubleshooting

### Service not running:
1. Check if it's loaded: `launchctl list | grep com.toll-dashboard-autofetch`
2. Check logs: `tail -f auto_fetch.log`
3. Check launchd logs: `tail -f launchd_stdout.log launchd_stderr.log`

### No emails received:
1. Verify email credentials in `.env` file
2. Check that email addresses are correct in `accounts_config.json`
3. Check email logs in `auto_fetch.log`

### Accounts not processing:
1. Verify `accounts_config.json` format is valid JSON
2. Ensure account_number and plate_number are filled in
3. Check `auto_fetch.log` for specific errors

### Permission errors:
- Make sure `auto_fetch.py` is executable: `chmod +x auto_fetch.py`
- Check that Python path in plist is correct

## Notes

- The script runs in **headless mode** (no visible browser) for automation
- Each account runs in parallel for faster processing
- Emails are sent automatically after successful fetch
- All activity is logged for debugging


