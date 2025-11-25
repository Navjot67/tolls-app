# 🔧 Email Troubleshooting Guide

## Current Issue: Authentication Failed

**Error:** `Username and Password not accepted`

This means Gmail is rejecting your credentials.

## ✅ Quick Fixes

### For Gmail Users:

1. **Use App Password (REQUIRED)**
   - Gmail no longer accepts regular passwords
   - You MUST use an App Password
   - Generate at: https://myaccount.google.com/apppasswords

2. **Enable 2-Step Verification First**
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification
   - Then generate App Password

3. **Update .env File**
   ```bash
   nano .env
   ```
   
   Set:
   ```env
   SMTP_USERNAME=your-actual-email@gmail.com
   SMTP_PASSWORD=your-16-character-app-password
   ```

4. **Restart Server**
   ```bash
   # Stop server (Ctrl+C)
   python3 app.py
   ```

## 🧪 Test Email Function

Run the test script:
```bash
python3 test_email.py
```

This will:
- Test email configuration
- Show detailed error messages
- Help identify the issue

## 📋 Step-by-Step Gmail Setup

1. **Enable 2-Step Verification:**
   - https://myaccount.google.com/security
   - Click "2-Step Verification"
   - Follow setup process

2. **Generate App Password:**
   - https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter "E-ZPass Dashboard"
   - Copy the 16-character password

3. **Update .env:**
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx
   ```
   (Remove spaces from app password)

4. **Restart and Test**

## 🔍 Common Errors

### "Username and Password not accepted"
- ❌ Using regular password → ✅ Use App Password
- ❌ 2-Step Verification not enabled → ✅ Enable it first
- ❌ Wrong email address → ✅ Use full email

### "Connection refused"
- Check SMTP_SERVER and SMTP_PORT
- Try port 465 with SSL instead

### "Email not in inbox"
- Check spam/junk folder
- Verify recipient email is correct
- Check server logs for errors

## 🆘 Still Not Working?

1. **Verify credentials:**
   ```bash
   python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('User:', os.getenv('SMTP_USERNAME')); print('Pass set:', bool(os.getenv('SMTP_PASSWORD')))"
   ```

2. **Test manually:**
   ```bash
   python3 test_email.py
   ```

3. **Check server console** for error messages

4. **Try different email provider** (Outlook, Yahoo, etc.)


