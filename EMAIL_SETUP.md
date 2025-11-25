# Email Setup Guide

## Quick Setup

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your email credentials:**
   ```bash
   nano .env
   ```

3. **For Gmail users:**
   - Use your Gmail address as `SMTP_USERNAME`
   - Generate an "App Password" at: https://myaccount.google.com/apppasswords
   - Use the app password as `SMTP_PASSWORD` (not your regular password)

4. **For other email providers:**
   - Update `SMTP_SERVER` and `SMTP_PORT` accordingly
   - Use your email and password

## Supported Email Providers

### Gmail (Default)
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Outlook
```
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

### Yahoo
```
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
```

## How It Works

1. User enters account number, plate number, and optional email
2. System fetches toll information
3. If email provided, a beautiful HTML email is sent automatically
4. Email includes:
   - Account information
   - Balance due (prominently displayed)
   - Bill numbers
   - Violation count
   - Professional formatting

## Testing

After setting up `.env`, restart the server and test by:
1. Entering your account/plate information
2. Adding your email address
3. Clicking "Fetch Toll Information"
4. Check your inbox for the email!

## Troubleshooting

**Email not sending?**
- Check `.env` file exists and has correct credentials
- For Gmail: Make sure you're using an App Password, not your regular password
- Check server logs for error messages
- Verify SMTP server and port are correct

**Email goes to spam?**
- This is normal for automated emails
- Check your spam/junk folder
- Mark as "Not Spam" to improve deliverability


