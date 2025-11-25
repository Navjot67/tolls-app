# Email Format Guide for E-ZPass Toll Dashboard

## 📧 How to Send Email Requests

Send an email to your configured email address with account/plate information in any of the following formats:

---

## ✅ Supported Formats

### 1. NY Account Format (Recommended)

```
Account: 493790720
Plate: T693884C
Email: your-email@example.com
```

**Required:**
- `Account:` - Your NY E-ZPass account number
- `Plate:` - Your license plate number

**Optional:**
- `Email:` - Email address to send results to (defaults to sender's email)

---

### 2. NJ Violation Format

```
Violation: T132556432797
Plate: T693884C
Email: your-email@example.com
```

**Required:**
- `Violation:` - Your NJ violation/invoice number
- `Plate:` - Your license plate number

**Optional:**
- `Email:` - Email address to send results to (defaults to sender's email)

---

### 3. Both NY and NJ Format

```
Account: 493790720
Plate: T693884C
Violation: T132556432797
Email: your-email@example.com
```

This will process both NY and NJ accounts and send combined results.

---

### 4. Single Line Format

```
Account: 493790720, Plate: T693884C, Email: your-email@example.com
```

Or:

```
Violation: T132556432797, Plate: T693884C, Email: your-email@example.com
```

---

### 5. Alternative Label Formats

The system recognizes various label formats:

**For Account Number:**
- `Account: 123456789`
- `Account Number: 123456789`
- `Account #: 123456789`
- `NY Account: 123456789`
- `Acc: 123456789`

**For Violation Number:**
- `Violation: T132556432797`
- `Violation Number: T132556432797`
- `Violation #: T132556432797`
- `NJ Violation: T132556432797`
- `Invoice: T132556432797`

**For Plate Number:**
- `Plate: ABC1234`
- `Plate Number: ABC1234`
- `Plate #: ABC1234`
- `License Plate: ABC1234`

**For Email:**
- `Email: user@example.com`
- `Email Address: user@example.com`

---

### 6. JSON Format

```
{"account_number": "493790720", "plate_number": "T693884C", "email": "user@example.com"}
```

---

## 📋 Examples

### Example 1: NY Account Only
```
Subject: Toll Check Request

Account: 493790720
Plate: T693884C
```

### Example 2: NJ Violation Only
```
Subject: Check NJ Violation

Violation: T132556432797
Plate: T693884C
```

### Example 3: Both NY and NJ
```
Subject: Check Both Accounts

Account: 493790720
Plate: T693884C
Violation: T132556432797
```

### Example 4: With Custom Email
```
Account: 493790720
Plate: T693884C
Email: different-email@example.com
```

---

## ⚠️ Important Notes

1. **Email Address**: If you don't specify an email, the system will use the sender's email address
2. **Case Insensitive**: Account numbers, plates, and labels can be uppercase or lowercase
3. **Spaces**: Spaces around colons are optional (`Account:123` = `Account : 123`)
4. **Auto-Save**: Accounts are automatically saved to the "saved accounts (auto-fetch)" list
5. **Merging**: If the same email is used, NY and NJ accounts will be merged into one account
6. **Processing**: Accounts are processed sequentially (NY first, then NJ)

---

## 🔄 What Happens After Sending

1. ✅ Email is read and parsed
2. ✅ Account is automatically saved to saved accounts
3. ✅ Toll data is fetched from E-ZPass websites
4. ✅ Results are emailed back to you
5. ✅ Account balance is updated in saved accounts

---

## 📧 Where to Send

Send emails to the email address configured in the system (check your `.env` file for `SMTP_USERNAME`).

---

## ❓ Troubleshooting

**Email not processed?**
- Make sure the email contains "Account:" or "Violation:" and "Plate:" labels
- Check that account/violation and plate numbers are valid
- Ensure the email is sent to the correct address

**Wrong data extracted?**
- Use clear labels: `Account:`, `Plate:`, `Violation:`
- Put each field on a separate line for best results
- Avoid special characters in account/plate numbers

---

## 📝 Quick Reference

**Minimum Required:**
- NY: `Account: [number]` + `Plate: [plate]`
- NJ: `Violation: [number]` + `Plate: [plate]`

**Optional:**
- `Email: [email]` - Custom email for results




