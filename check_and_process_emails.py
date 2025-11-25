#!/usr/bin/env python3
"""
Quick script to check emails and process toll requests
"""
from email_reader import EmailReader
from automation_selenium import extract_toll_info
from automation_selenium_nj import extract_toll_info_nj
from email_service import send_toll_info_email
from account_manager import add_account
import os
from dotenv import load_dotenv

load_dotenv()

print('=' * 60)
print('Checking emails and processing toll requests...')
print('=' * 60)

reader = EmailReader()
try:
    if not reader.connect():
        print('❌ Failed to connect to email server')
        print('   Check your IMAP settings in .env file')
        exit(1)
    
    emails = reader.get_unread_emails()
    
    if not emails:
        print('📭 No unread emails with account/plate information found')
    else:
        print(f'📬 Found {len(emails)} email(s) with toll requests\n')
        
        for i, email_data in enumerate(emails, 1):
            account_number = email_data.get('account_number')
            violation_number = email_data.get('violation_number')
            plate_number = email_data.get('plate_number')
            nj_plate_number = email_data.get('nj_plate_number') or plate_number
            email_address = email_data.get('email')
            sender = email_data.get('sender_email')
            subject = email_data.get('subject')
            email_id = email_data.get('email_id')
            source = email_data.get('source', 'NY')
            
            print(f'[{i}/{len(emails)}] Processing email from {sender}')
            print(f'   Subject: {subject}')
            if source == 'BOTH':
                print(f'   NY Account: {account_number}')
                print(f'   NJ Violation: {violation_number}')
                print(f'   Plate: {plate_number}')
            elif source == 'NJ':
                print(f'   NJ Violation: {violation_number}')
                print(f'   Plate: {plate_number}')
            else:
                print(f'   Account: {account_number}')
                print(f'   Plate: {plate_number}')
            print(f'   Send results to: {email_address}\n')
            
            has_data = False
            combined_balance = 0.0
            combined_bill_numbers = []
            combined_violations = 0
            combined_result = None
            
            # Process NY account if present
            if account_number and plate_number:
                has_data = True
                # Automatically save NY account to saved accounts (will merge if same email)
                print('   💾 Saving NY account to auto-fetch list...')
                add_account(account_number=account_number, plate_number=plate_number, email=email_address, source='NY')
                
                try:
                    print('   🔄 Fetching NY toll data...')
                    ny_result = extract_toll_info(account_number, plate_number, headless=False)
                    
                    if ny_result.get('success'):
                        print('   ✅ Successfully fetched NY toll data')
                        balance = ny_result.get('balance_amount', 0)
                        violations = ny_result.get('violation_count', 0)
                        print(f'   💰 NY Balance: ${balance:.2f}')
                        print(f'   ⚠️  NY Violations: {violations}')
                        
                        combined_balance += balance
                        combined_bill_numbers.extend(ny_result.get('toll_bill_numbers', []))
                        combined_violations += violations
                        combined_result = ny_result
                    else:
                        error_msg = ny_result.get('error', 'Unknown error')
                        print(f'   ❌ NY failed: {error_msg}')
                except Exception as e:
                    print(f'   ❌ Error processing NY request: {str(e)}')
                    import traceback
                    traceback.print_exc()
            
            # Process NJ violation if present (sequentially after NY)
            if violation_number and nj_plate_number:
                has_data = True
                # Automatically save NJ account to saved accounts (will merge if same email)
                print('   💾 Saving NJ account to auto-fetch list...')
                add_account(violation_number=violation_number, plate_number=nj_plate_number, email=email_address, source='NJ')
                
                try:
                    print('   🔄 Fetching NJ violation data...')
                    nj_result = extract_toll_info_nj(violation_number, nj_plate_number, headless=False)
                    
                    if nj_result.get('success'):
                        print('   ✅ Successfully fetched NJ violation data')
                        balance = nj_result.get('balance_amount', 0)
                        violations = nj_result.get('violation_count', 0)
                        print(f'   💰 NJ Balance: ${balance:.2f}')
                        print(f'   ⚠️  NJ Violations: {violations}')
                        
                        combined_balance += balance
                        combined_bill_numbers.extend(nj_result.get('toll_bill_numbers', []))
                        combined_violations += violations
                        
                        # Merge results
                        if combined_result:
                            combined_result['balance_amount'] = combined_balance
                            combined_result['toll_bill_numbers'] = list(set(combined_bill_numbers))
                            combined_result['violation_count'] = combined_violations
                            combined_result['nj_result'] = nj_result
                            combined_result['sources'] = ['NY', 'NJ']
                        else:
                            combined_result = nj_result
                    else:
                        error_msg = nj_result.get('error', 'Unknown error')
                        print(f'   ❌ NJ failed: {error_msg}')
                except Exception as e:
                    print(f'   ❌ Error processing NJ request: {str(e)}')
                    import traceback
                    traceback.print_exc()
            
            if has_data and combined_result and combined_result.get('success'):
                print(f'   💰 Total Balance: ${combined_balance:.2f}')
                print(f'   ⚠️  Total Violations: {combined_violations}')
                
                if email_address:
                    print(f'   📤 Sending results to {email_address}...')
                    email_sent = send_toll_info_email(email_address, combined_result)
                    if email_sent:
                        print('   ✅ Email sent successfully')
                    else:
                        print('   ❌ Failed to send email')
            
            # Mark email as read
            if email_id:
                reader.mark_as_read(email_id)
                print('   ✓ Marked email as read\n')
    
    print('=' * 60)
    print('✅ Email check complete')
    print('=' * 60)
    
finally:
    reader.disconnect()

