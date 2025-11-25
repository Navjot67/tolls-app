# Email Reader Setup Guide

This feature allows the system to automatically read emails, extract account/plate information, and trigger toll data fetching.

## How It Works

1. **Email Reading**: The system connects to your email via IMAP and checks for unread emails
2. **Data Extraction**: It parses emails to find account numbers and plate numbers
3. **Automation**: Automatically triggers the toll data fetching process
4. **Email Response**: Sends back the toll information to the email address found in the message

## Email Format

The system can extract information from emails in multiple formats:

### Format 1: Structured Text
```
Account: 123456789
Plate: ABC1234
Email: user@example.com
```

### Format 2: Single Line
```
Account: 123456789, Plate: ABC1234, Email: user@example.com
```

### Format 3: Label-Value Pairs
```
account_number: 123456789
plate_number: ABC1234
```

### Format 4: JSON Format
```json
{
  "account_number": "123456789",
  "plate_number": "ABC1234",
  "email": "user@example.com"
}
```

**Note**: If no email address is found in the email, the system will use the sender's email address as the recipient.

## Setup

### 1. Configure IMAP Settings

Add the following to your `.env` file:

```bash
# IMAP Configuration (reuses SMTP credentials)
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 2. IMAP Server Settings by Provider

#### Gmail
```
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
```

#### Outlook
```
IMAP_SERVER=outlook.office365.com
IMAP_PORT=993
```

#### Yahoo
```
IMAP_SERVER=imap.mail.yahoo.com
IMAP_PORT=993
```

## API Endpoints

### 1. Check and Process Emails

**POST** `/api/check-emails`

This endpoint checks for unread emails, extracts account/plate information, and automatically processes them.

**Request Body** (optional):
```json
{
  "auto_process": true,  // Automatically trigger automation (default: true)
  "mark_read": true      // Mark emails as read after processing (default: true)
}
```

**Response**:
```json
{
  "success": true,
  "message": "Processed 2 email(s)",
  "emails_processed": 2,
  "results": [
    {
      "email_id": "123",
      "sender": "user@example.com",
      "subject": "Check toll info",
      "account_number": "123456789",
      "plate_number": "ABC1234",
      "email": "user@example.com",
      "processed": true,
      "toll_data": { ... },
      "email_sent": true
    }
  ]
}
```

### 2. Simple Email Check (No Processing)

**GET** `/api/check-emails-simple`

This endpoint only checks for emails and returns parsed data without triggering automation.

**Response**:
```json
{
  "success": true,
  "emails_found": 1,
  "emails": [
    {
      "account_number": "123456789",
      "plate_number": "ABC1234",
      "email": "user@example.com",
      "sender": "user@example.com",
      "subject": "Check toll info"
    }
  ]
}
```

## Usage Examples

### Using curl

**Check emails and process automatically:**
```bash
curl -X POST http://localhost:5000/api/check-emails \
  -H "Content-Type: application/json" \
  -d '{"auto_process": true, "mark_read": true}'
```

**Just check emails (don't process):**
```bash
curl http://localhost:5000/api/check-emails-simple
```

### Using JavaScript/Fetch

```javascript
// Check and process emails
fetch('http://localhost:5000/api/check-emails', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    auto_process: true,
    mark_read: true
  })
})
.then(response => response.json())
.then(data => {
  console.log('Processed emails:', data);
});
```

## Automated Email Checking

To automatically check emails periodically, you can:

### Option 1: Use the Auto-Fetch Script

Modify `auto_fetch.py` to also check emails before processing saved accounts.

### Option 2: Create a Scheduled Task

Add a cron job or scheduled task to call the API endpoint periodically:

```bash
# Check emails every hour
0 * * * * curl -X POST http://localhost:5000/api/check-emails
```

### Option 3: Background Worker

Create a simple background script that runs continuously:

```python
import time
import requests

while True:
    try:
        response = requests.post('http://localhost:5000/api/check-emails', 
                                json={'auto_process': True, 'mark_read': True})
        print(f"Checked emails: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(3600)  # Check every hour
```

## Troubleshooting

### Email connection fails

- Check that IMAP is enabled in your email account settings
- Verify IMAP credentials in `.env` file
- For Gmail: Make sure you're using an App Password, not your regular password
- Check that IMAP_PORT is correct for your email provider

### Emails not being parsed

- Make sure the email contains clear labels like "Account:" and "Plate:"
- Check that account numbers and plate numbers are formatted correctly
- Try using the structured format shown above

### Automation not triggering

- Verify that `auto_process` is set to `true`
- Check server logs for error messages
- Make sure account number and plate number are both found in the email

## Security Notes

- Store email credentials securely in `.env` file (not in code)
- Use App Passwords instead of regular passwords for Gmail
- Consider using environment variables in production
- Mark emails as read to avoid reprocessing them




