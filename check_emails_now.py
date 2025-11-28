#!/usr/bin/env python3
"""
Manually check for new emails and process toll requests
"""
import sys
import os
sys.path.insert(0, '/Users/ghuman/tolls')
os.chdir('/Users/ghuman/tolls')

from email_checker_worker import process_email_request
from email_reader import check_emails_and_extract
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

print("=" * 60)
print("📧 CHECKING FOR NEW EMAILS AND PROCESSING REQUESTS")
print("=" * 60)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

try:
    print("🔍 Checking for new email requests...")
    print()
    
    # Check emails and extract requests
    email_requests = check_emails_and_extract()
    
    if email_requests:
        print(f"✅ Found {len(email_requests)} email request(s)!")
        print()
        
        for i, email_data in enumerate(email_requests, 1):
            print(f"📨 Processing Request #{i}:")
            print(f"   Source: {email_data.get('source', 'N/A')}")
            if email_data.get('source') == 'NY':
                print(f"   Account: {email_data.get('account_number', 'N/A')}")
            elif email_data.get('source') == 'NJ':
                print(f"   Violation: {email_data.get('violation_number', 'N/A')}")
            print(f"   Plate: {email_data.get('plate_number', 'N/A')}")
            print(f"   From: {email_data.get('sender_email', 'N/A')}")
            print(f"   Send to: {email_data.get('email', 'N/A')}")
            print()
            
            # Process the request
            print(f"🚀 Running automation for Request #{i}...")
            process_email_request(email_data)
            print(f"✅ Completed Request #{i}")
            print()
    else:
        print("✅ No new email requests found")
        print("   (All emails have been processed or no valid requests)")
        print()
        print("💡 To check email status:")
        print("   tail -f logs/email_checker_stdout.log")
    
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)



