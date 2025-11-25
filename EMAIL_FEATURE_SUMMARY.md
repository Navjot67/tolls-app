# Email Reading & Automation Feature

## Overview

The system can now read emails, extract account/plate information, and automatically trigger toll data fetching.

## Quick Start

### 1. Configure Email Settings

Add IMAP settings to your `.env` file:
```bash
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 2. Send an Email

Send an email to your configured email address with this format:

```
Account: 123456789
Plate: ABC1234
Email: recipient@example.com
```

### 3. Process Emails

**Option A: Via API (Manual)**
```bash
curl -X POST http://localhost:5000/api/check-emails
```

**Option B: Background Worker (Automatic)**
```bash
python3 email_checker_worker.py
```

The worker will check emails every hour (configurable via `EMAIL_CHECK_INTERVAL` in `.env`).

## API Endpoints

1. **POST /api/check-emails** - Check emails and automatically process them
2. **GET /api/check-emails-simple** - Check emails without processing

## Features

- ✅ Reads emails via IMAP
- ✅ Extracts account number, plate number, and email
- ✅ Automatically triggers toll data fetching
- ✅ Sends results back via email
- ✅ Supports multiple email formats
- ✅ Marks emails as read after processing
- ✅ Background worker for automatic checking

## Files Created

- `email_reader.py` - Email reading and parsing service
- `email_checker_worker.py` - Background worker for automatic email checking
- `EMAIL_READER_SETUP.md` - Detailed setup guide

## Next Steps

See `EMAIL_READER_SETUP.md` for detailed documentation and examples.




