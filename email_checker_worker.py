#!/usr/bin/env python3
"""
Background worker to periodically check emails and process toll requests
Run this script to automatically check for new emails and trigger toll data fetching
"""
import time
import os
import sys
from datetime import datetime
from email_reader import EmailReader
from automation_selenium import extract_toll_info
from automation_selenium_nj import extract_toll_info_nj
from email_service import send_toll_info_email
from account_manager import add_account
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CHECK_INTERVAL = int(os.getenv('EMAIL_CHECK_INTERVAL', '3600'))  # Default: 1 hour
IMAP_FOLDER = os.getenv('IMAP_FOLDER', 'INBOX')


def process_email_request(email_data):
    """Process a single email request - handles both NY and NJ accounts sequentially"""
    account_number = email_data.get('account_number')
    violation_number = email_data.get('violation_number')
    plate_number = email_data.get('plate_number')
    nj_plate_number = email_data.get('nj_plate_number') or plate_number
    email_address = email_data.get('email')
    sender = email_data.get('sender_email')
    source = email_data.get('source', 'NY')
    
    print(f"\n📧 Processing request from {sender}")
    if source == 'BOTH':
        print(f"   NY Account: {account_number}, Plate: {plate_number}")
        print(f"   NJ Violation: {violation_number}, Plate: {nj_plate_number}")
    elif source == 'NJ':
        print(f"   NJ Violation: {violation_number}, Plate: {plate_number}")
    else:
        print(f"   Account: {account_number}, Plate: {plate_number}")
    print(f"   Send results to: {email_address}")
    
    combined_balance = 0.0
    combined_bill_numbers = []
    combined_violations = 0
    combined_result = None
    sources_processed = []
    
    # Process NY account first (if exists)
    if account_number and plate_number:
        # Automatically save NY account to saved accounts (will merge if same email)
        print("   💾 Saving NY account to auto-fetch list...")
        add_account(account_number=account_number, plate_number=plate_number, email=email_address, source='NY')
        
        try:
            # Fetch NY toll information
            print("   🔄 Fetching NY toll data...")
            ny_result = extract_toll_info(account_number, plate_number, headless=False)
            
            if ny_result.get('success'):
                print("   ✅ Successfully fetched NY toll data")
                balance = ny_result.get('balance_amount', 0)
                violations = ny_result.get('violation_count', 0)
                print(f"   💰 NY Balance: ${balance:.2f}")
                print(f"   ⚠️  NY Violations: {violations}")
                
                combined_balance += balance
                combined_bill_numbers.extend(ny_result.get('toll_bill_numbers', []))
                combined_violations += violations
                combined_result = ny_result
                sources_processed.append('NY')
            else:
                error_msg = ny_result.get('error', 'Unknown error')
                print(f"   ❌ NY failed: {error_msg}")
        except Exception as e:
            print(f"   ❌ Error processing NY request: {str(e)}")
    
    # Process NJ violation second (if exists) - sequentially after NY
    if violation_number and (nj_plate_number or plate_number):
        # Use nj_plate_number if available, otherwise use plate_number
        nj_plate = nj_plate_number or plate_number
        # Automatically save NJ account to saved accounts (will merge if same email)
        print("   💾 Saving NJ account to auto-fetch list...")
        print(f"      Violation: {violation_number}, Plate: {nj_plate}")
        add_account(violation_number=violation_number, plate_number=nj_plate, email=email_address, source='NJ')
        
        try:
            # Fetch NJ violation information
            print("   🔄 Fetching NJ violation data...")
            nj_result = extract_toll_info_nj(violation_number, nj_plate_number, headless=False)
            
            if nj_result.get('success'):
                print("   ✅ Successfully fetched NJ violation data")
                balance = nj_result.get('balance_amount', 0)
                violations = nj_result.get('violation_count', 0)
                print(f"   💰 NJ Balance: ${balance:.2f}")
                print(f"   ⚠️  NJ Violations: {violations}")
                
                combined_balance += balance
                combined_bill_numbers.extend(nj_result.get('toll_bill_numbers', []))
                combined_violations += violations
                
                # Merge results
                if combined_result:
                    combined_result['balance_amount'] = combined_balance
                    combined_result['toll_bill_numbers'] = list(set(combined_bill_numbers))
                    combined_result['violation_count'] = combined_violations
                    combined_result['nj_result'] = nj_result
                    combined_result['sources'] = sources_processed + ['NJ']
                else:
                    combined_result = nj_result
                sources_processed.append('NJ')
            else:
                error_msg = nj_result.get('error', 'Unknown error')
                print(f"   ❌ NJ failed: {error_msg}")
        except Exception as e:
            print(f"   ❌ Error processing NJ request: {str(e)}")
    
    # Send combined email if we have results
    if combined_result and combined_result.get('success'):
        print(f"   💰 Total Balance: ${combined_balance:.2f} ({' + '.join(sources_processed)})")
        print(f"   ⚠️  Total Violations: {combined_violations}")
        
        if email_address:
            print(f"   📤 Sending results to {email_address}...")
            email_sent = send_toll_info_email(email_address, combined_result)
            if email_sent:
                print(f"   ✅ Email sent successfully")
            else:
                print(f"   ❌ Failed to send email")


def main():
    """Main worker loop"""
    print("=" * 60)
    print("E-ZPass Email Checker Worker")
    print("=" * 60)
    print(f"Checking emails every {CHECK_INTERVAL} seconds ({CHECK_INTERVAL/60:.1f} minutes)")
    print(f"Email folder: {IMAP_FOLDER}")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    reader = EmailReader()
    
    try:
        # Connect once
        if not reader.connect():
            print("❌ Failed to connect to email server")
            print("   Check your IMAP settings in .env file")
            sys.exit(1)
        
        while True:
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{timestamp}] Checking for new emails...")
                
                # Get unread emails
                emails = reader.get_unread_emails(folder=IMAP_FOLDER)
                
                if not emails:
                    print("   ℹ️  No emails with account/plate information found")
                else:
                    print(f"   📬 Found {len(emails)} email(s) with toll requests")
                    
                    # Process each email
                    for email_data in emails:
                        email_id = email_data.get('email_id')
                        process_email_request(email_data)
                        
                        # Mark email as read
                        if email_id:
                            reader.mark_as_read(email_id)
                            print(f"   ✓ Marked email as read")
            
            except KeyboardInterrupt:
                print("\n\n⚠️  Stopping email checker...")
                break
            
            except Exception as e:
                print(f"\n❌ Error in check loop: {str(e)}")
                import traceback
                traceback.print_exc()
            
            # Wait before next check
            print(f"\n⏳ Waiting {CHECK_INTERVAL} seconds until next check...")
            time.sleep(CHECK_INTERVAL)
    
    finally:
        reader.disconnect()
        print("\n✅ Email checker stopped")


if __name__ == '__main__':
    main()

