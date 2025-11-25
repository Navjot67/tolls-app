#!/usr/bin/env python3
"""
Test email sending functionality
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Import email service
from email_service import send_toll_info_email

# Get SMTP username (will send test email to this address)
smtp_username = os.getenv('SMTP_USERNAME', '')

if not smtp_username:
    print("❌ SMTP_USERNAME not found in .env file")
    sys.exit(1)

print("=" * 60)
print("SENDING TEST EMAIL")
print("=" * 60)
print(f"\n📧 Sending test email to: {smtp_username}")
print("   Using SMTP settings from .env file")
print("\n⏳ Sending...\n")

# Create test toll data
test_toll_data = {
    'account_number': 'TEST123456',
    'plate_number': 'TEST123',
    'violation_number': 'T132556432797',
    'nj_plate_number': 'TEST123',
    'balance_amount': 25.50,
    'ny_balance_amount': 0.00,
    'nj_balance_amount': 25.50,
    'toll_bill_numbers': ['TEST-BILL-001'],
    'violation_count': 1,
    'sources': ['NJ']
}

# Send test email
success = send_toll_info_email(smtp_username, test_toll_data)

print("\n" + "=" * 60)
if success:
    print("✅ TEST EMAIL SENT SUCCESSFULLY!")
    print(f"   Check inbox: {smtp_username}")
    print("   Subject: E-ZPass NJ Toll Information - Balance Due: $25.50")
else:
    print("❌ TEST EMAIL FAILED")
    print("   Check error messages above for details")
print("=" * 60)
