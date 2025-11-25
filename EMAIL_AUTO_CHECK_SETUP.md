# Automatic Email Checking Setup

## ✅ Setup Complete!

The automatic email checking service has been installed and is running.

## How It Works

The system will:
1. **Automatically check emails** every hour (configurable)
2. **Extract account/plate information** from emails
3. **Run automation** to fetch toll data
4. **Send results** back via email
5. **Mark emails as read** after processing

## Configuration

### Check Interval

Edit your `.env` file to change how often emails are checked:

```bash
EMAIL_CHECK_INTERVAL=3600  # Check every hour (in seconds)
EMAIL_CHECK_INTERVAL=1800   # Check every 30 minutes
EMAIL_CHECK_INTERVAL=600    # Check every 10 minutes
```

### Email Folder

To check a different email folder (default is INBOX):

```bash
IMAP_FOLDER=INBOX  # or "Sent", "Drafts", etc.
```

## Service Management

### Check Status
```bash
launchctl list | grep email-checker
```

### View Logs
```bash
# Standard output
tail -f ~/tolls/logs/email_checker_stdout.log

# Errors
tail -f ~/tolls/logs/email_checker_stderr.log
```

### Stop Service
```bash
launchctl unload ~/Library/LaunchAgents/com.toll.email-checker.plist
```

### Start Service
```bash
launchctl load ~/Library/LaunchAgents/com.toll.email-checker.plist
```

### Restart Service
```bash
launchctl unload ~/Library/LaunchAgents/com.toll.email-checker.plist
launchctl load ~/Library/LaunchAgents/com.toll.email-checker.plist
```

## Email Format

Send emails with this format:

```
Account: 123456789
Plate: ABC1234
Email: recipient@example.com
```

Or in a single line:
```
Account: 123456789, Plate: ABC1234, Email: recipient@example.com
```

## Manual Check

You can also manually check emails anytime:

```bash
python3 check_and_process_emails.py
```

Or via API:
```bash
curl -X POST http://localhost:5000/api/check-emails \
  -H "Content-Type: application/json" \
  -d '{"auto_process": true, "mark_read": true}'
```

## Troubleshooting

### Service Not Running

1. Check if it's loaded:
   ```bash
   launchctl list | grep email-checker
   ```

2. Check logs for errors:
   ```bash
   cat ~/tolls/logs/email_checker_stderr.log
   ```

3. Reload the service:
   ```bash
   ./setup_email_auto_check.sh
   ```

### Emails Not Being Processed

1. Verify IMAP settings in `.env`:
   ```bash
   IMAP_SERVER=imap.gmail.com
   IMAP_PORT=993
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

2. Check that emails are in the correct format (see Email Format above)

3. Verify emails are unread (the service only processes unread emails)

### Service Crashes

The service is configured with `KeepAlive=true`, so it will automatically restart if it crashes. Check the error logs to see what caused the crash.

## Features

- ✅ Automatic email checking
- ✅ Automatic processing
- ✅ Automatic email responses
- ✅ Runs in background
- ✅ Auto-starts on login
- ✅ Auto-restarts on crash
- ✅ Configurable check interval
- ✅ Detailed logging




