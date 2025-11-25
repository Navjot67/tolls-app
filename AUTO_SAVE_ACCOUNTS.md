# Auto-Save Email Accounts Feature

## ✅ Feature Enabled!

The system now automatically saves any new email account/plate/email combinations to the saved accounts (auto-fetch) list.

## How It Works

When an email is processed:
1. **Email is received** with account/plate information
2. **Account is automatically saved** to `accounts_config.json`
3. **Toll data is fetched** via automation
4. **Results are sent** back via email
5. **Email is marked as read**

## Benefits

- ✅ **No manual entry required** - accounts are automatically added
- ✅ **No duplicates** - system checks if account already exists
- ✅ **Auto-fetch enabled** - saved accounts are checked automatically every 3 hours
- ✅ **Email updates** - if email address changes, it's updated automatically

## Account Management

### View Saved Accounts

```bash
cat accounts_config.json
```

Or use the API:
```bash
curl http://localhost:5000/api/accounts
```

### Manual Account Management

You can still manually add/remove accounts through:
- The web dashboard at `http://localhost:5000`
- Directly editing `accounts_config.json`
- Using the `account_manager.py` module

### Account Format

Accounts are stored in `accounts_config.json`:

```json
{
  "accounts": [
    {
      "account_number": "123456789",
      "plate_number": "ABC1234",
      "email": "user@example.com"
    }
  ]
}
```

## Duplicate Prevention

The system prevents duplicate accounts:
- If an account/plate combination already exists, it won't be added again
- However, if a new email address is provided, it will update the existing account's email

## Integration Points

Auto-save is integrated into:
1. ✅ `check_and_process_emails.py` - Manual email checking script
2. ✅ `email_checker_worker.py` - Background worker for automatic checking
3. ✅ `/api/check-emails` - API endpoint for email processing

## Testing

Test the auto-save feature:
1. Send an email with account/plate info:
   ```
   Account: 123456789
   Plate: ABC1234
   Email: recipient@example.com
   ```

2. Check emails:
   ```bash
   python3 check_and_process_emails.py
   ```

3. Verify account was saved:
   ```bash
   cat accounts_config.json
   ```

## Logs

When an account is saved, you'll see:
```
💾 Saving account to auto-fetch list...
✅ Added account to saved accounts: 123456789 / ABC1234
   Email: recipient@example.com
```

If account already exists:
```
ℹ️  Account 123456789 / Plate ABC1234 already exists in saved accounts
```




