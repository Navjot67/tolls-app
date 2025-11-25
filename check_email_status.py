#!/usr/bin/env python3
"""
Diagnostic script to check email sending status and configuration
"""
import os
import json
from dotenv import load_dotenv
from email_service import send_toll_info_email

load_dotenv()

print("=" * 60)
print("EMAIL SENDING DIAGNOSTICS")
print("=" * 60)

# Check email configuration
smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
smtp_port = int(os.getenv('SMTP_PORT', '587'))
smtp_username = os.getenv('SMTP_USERNAME', '')
smtp_password = os.getenv('SMTP_PASSWORD', '')

print("\n1. SMTP Configuration:")
print(f"   Server: {smtp_server}:{smtp_port}")
print(f"   Username: {'✓ Set' if smtp_username else '✗ NOT SET'}")
print(f"   Password: {'✓ Set' if smtp_password else '✗ NOT SET'}")

if not smtp_username or not smtp_password:
    print("\n   ⚠️  WARNING: Email credentials not configured!")
    print("   Please set SMTP_USERNAME and SMTP_PASSWORD in .env file")
    exit(1)

# Check accounts
print("\n2. Account Email Configuration:")
config_file = os.path.join(os.path.dirname(__file__), 'accounts_config.json')
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
        accounts = config.get('accounts', [])
        
        accounts_with_email = 0
        accounts_without_email = 0
        
        for i, acc in enumerate(accounts, 1):
            email = acc.get('email', '')
            sources = acc.get('sources', [])
            has_ny = 'NY' in sources or acc.get('account_number')
            has_nj = 'NJ' in sources or acc.get('violation_number') or acc.get('nj_violation_number')
            
            print(f"\n   Account #{i}:")
            print(f"     Email: {email if email else '✗ NOT SET'}")
            print(f"     Sources: {', '.join(sources) if sources else 'None'}")
            
            if email:
                accounts_with_email += 1
            else:
                accounts_without_email += 1
        
        print(f"\n   Summary: {accounts_with_email} with email, {accounts_without_email} without email")
else:
    print("   ✗ accounts_config.json not found")

# Test email sending
print("\n3. Test Email Sending:")
test_email = input("   Enter email address to test (or press Enter to skip): ").strip()

if test_email:
    test_data = {
        'account_number': 'TEST123',
        'plate_number': 'TEST123',
        'violation_number': 'T123456789',
        'nj_violation_number': 'T123456789',
        'nj_plate_number': 'TEST123',
        'balance_amount': 25.50,
        'ny_balance_amount': 10.00,
        'nj_balance_amount': 15.50,
        'sources': ['NY', 'NJ'],
        'toll_bill_numbers': ['T123456789'],
        'violation_count': 1
    }
    
    print(f"\n   Sending test email to {test_email}...")
    try:
        result = send_toll_info_email(test_email, test_data)
        if result:
            print(f"   ✅ Test email sent successfully!")
            print(f"   Check your inbox and spam folder")
        else:
            print(f"   ❌ Test email failed - check errors above")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print("   Skipped")

print("\n" + "=" * 60)
print("Diagnostics complete")
print("=" * 60)




