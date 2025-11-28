#!/usr/bin/env python3
"""
Automated script to fetch toll information for all configured accounts
Runs every 3 hours via launchd scheduler
Processes accounts sequentially (one by one) with 15-second wait between each
"""
import os
import sys
import json
import time
from datetime import datetime
from automation_selenium import extract_toll_info
from automation_selenium_nj import extract_toll_info_nj
from email_service import send_toll_info_email
from account_manager import load_accounts, save_accounts
import threading

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration file path
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'accounts_config.json')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'auto_fetch.log')

def log_message(message):
    """Log message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    # Print to console (for launchd logs)
    print(log_entry.strip())
    
    # Write to log file
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing to log file: {e}")

def load_accounts():
    """Load account configurations from JSON file"""
    if not os.path.exists(CONFIG_FILE):
        log_message(f"⚠️  Config file not found: {CONFIG_FILE}")
        log_message("Creating example config file...")
        create_example_config()
        return []
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            accounts = config.get('accounts', [])
            log_message(f"✅ Loaded {len(accounts)} account(s) from config")
            return accounts
    except json.JSONDecodeError as e:
        log_message(f"❌ Error parsing config file: {e}")
        return []
    except Exception as e:
        log_message(f"❌ Error loading config file: {e}")
        return []

def create_example_config():
    """Create an example configuration file"""
    example_config = {
        "accounts": [
            {
                "account_number": "YOUR_ACCOUNT_NUMBER",
                "plate_number": "YOUR_PLATE_NUMBER",
                "email": "your-email@example.com"
            }
        ]
    }
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(example_config, f, indent=2)
        log_message(f"✅ Created example config at {CONFIG_FILE}")
        log_message("Please edit the file and add your account details")
    except Exception as e:
        log_message(f"❌ Error creating config file: {e}")

def process_account(account_data, results_list, results_lock):
    """
    Process a single account - handles both NY and NJ accounts sequentially
    Merges results if account has both NY and NJ
    """
    sources = account_data.get('sources', [account_data.get('source', 'NY')])
    email = account_data.get('email', '').strip()
    
    # Determine what accounts to process
    has_ny = 'NY' in sources and account_data.get('account_number', '').strip()
    has_nj = 'NJ' in sources and (account_data.get('violation_number') or account_data.get('nj_violation_number'))
    
    if not has_ny and not has_nj:
        log_message(f"⚠️  Skipping account - no valid NY or NJ data")
        return
    
    # Combined results
    combined_balance = 0.0
    ny_balance = 0.0
    nj_balance = 0.0
    combined_bill_numbers = []
    combined_violations = 0
    combined_results = []
    has_success = False
    
    # Process NY account first (if exists)
    if has_ny:
        account_number = account_data.get('account_number', '').strip()
        plate_number = account_data.get('plate_number', '').strip()
        
        log_message(f"🔄 Processing NY Account: {account_number}, Plate: {plate_number}")
        
        try:
            result = extract_toll_info(account_number, plate_number, headless=False)
            result['source'] = 'NY'
            
            if result.get('success'):
                ny_balance = result.get('balance_amount', 0)
                combined_balance += ny_balance
                combined_bill_numbers.extend(result.get('toll_bill_numbers', []))
                combined_violations += result.get('violation_count', 0)
                has_success = True
                combined_results.append(result)
                # Store NY balance separately
                account_data['ny_balance_amount'] = ny_balance
                log_message(f"✅ NY Success - Balance: ${ny_balance:.2f}")
            else:
                log_message(f"❌ NY Failed: {result.get('error', 'Unknown error')}")
                combined_results.append(result)
        except Exception as e:
            log_message(f"❌ NY Exception: {str(e)}")
            combined_results.append({'success': False, 'source': 'NY', 'error': str(e)})
    
    # Process NJ account second (if exists) - sequentially after NY
    if has_nj:
        violation_number = account_data.get('violation_number') or account_data.get('nj_violation_number', '').strip()
        nj_plate = account_data.get('nj_plate_number') or account_data.get('plate_number', '').strip()
        
        log_message(f"🔄 Processing NJ Violation: {violation_number}, Plate: {nj_plate}")
        
        try:
            result = extract_toll_info_nj(
                violation_number=violation_number,
                plate_number=nj_plate,
                headless=False
            )
            result['source'] = 'NJ'
            
            if result.get('success'):
                nj_balance = result.get('balance_amount', 0)
                combined_balance += nj_balance
                combined_bill_numbers.extend(result.get('toll_bill_numbers', []))
                combined_violations += result.get('violation_count', 0)
                has_success = True
                combined_results.append(result)
                # Store NJ balance separately
                account_data['nj_balance_amount'] = nj_balance
                log_message(f"✅ NJ Success - Balance: ${nj_balance:.2f}")
            else:
                log_message(f"❌ NJ Failed: {result.get('error', 'Unknown error')}")
                combined_results.append(result)
        except Exception as e:
            log_message(f"❌ NJ Exception: {str(e)}")
            combined_results.append({'success': False, 'source': 'NJ', 'error': str(e)})
    
    # Create combined result
    combined_result = {
        'success': has_success,
        'account_number': account_data.get('account_number', ''),
        'plate_number': account_data.get('plate_number', ''),
        'violation_number': account_data.get('violation_number') or account_data.get('nj_violation_number', ''),
        'balance_amount': combined_balance,
        'ny_balance_amount': ny_balance,
        'nj_balance_amount': nj_balance,
        'toll_bill_numbers': list(set(combined_bill_numbers)),  # Remove duplicates
        'violation_count': combined_violations,
        'sources': sources,
        'ny_result': next((r for r in combined_results if r.get('source') == 'NY'), None),
        'nj_result': next((r for r in combined_results if r.get('source') == 'NJ'), None),
        'combined_results': combined_results
    }
    
    # Update account data in accounts_config.json if automation was successful
    if has_success:
        try:
            accounts = load_accounts()
            account_updated = False
            
            # Find and update the account that was processed
            account_number = account_data.get('account_number', '').strip().upper() if account_data.get('account_number') else ''
            violation_number = (account_data.get('violation_number') or account_data.get('nj_violation_number', '')).strip().upper()
            plate_number = account_data.get('plate_number', '').strip().upper() if account_data.get('plate_number') else ''
            nj_plate = (account_data.get('nj_plate_number') or account_data.get('plate_number', '')).strip().upper()
            
            for acc in accounts:
                # Match by NY account details
                acc_account = acc.get('account_number', '').strip().upper()
                acc_plate = acc.get('plate_number', '').strip().upper()
                match_by_ny = (account_number and acc_account == account_number and acc_plate == plate_number)
                
                # Match by NJ violation details
                acc_violation = (acc.get('violation_number') or acc.get('nj_violation_number', '')).strip().upper()
                acc_nj_plate = (acc.get('nj_plate_number') or acc.get('plate_number', '')).strip().upper()
                match_by_nj = (violation_number and acc_violation == violation_number and acc_nj_plate == nj_plate)
                
                # Match by email (fallback)
                acc_email = acc.get('email', '').strip().lower()
                match_by_email = (email and acc_email == email.lower())
                
                # Update if matched
                if match_by_ny or match_by_nj or (match_by_email and (has_ny or has_nj)):
                    # Update balances (always set, even if 0)
                    acc['balance_amount'] = combined_balance
                    acc['ny_balance_amount'] = ny_balance
                    acc['nj_balance_amount'] = nj_balance
                    acc['violation_count'] = combined_violations
                    acc['toll_bill_numbers'] = list(set(combined_bill_numbers))
                    acc['last_updated'] = datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")
                    account_updated = True
                    log_message(f"💾 Updated account data - NY: ${ny_balance:.2f}, NJ: ${nj_balance:.2f}, Total: ${combined_balance:.2f}")
                    break
            
            if account_updated:
                # Save updated accounts
                save_accounts(accounts)
            else:
                log_message(f"⚠️  Could not find matching account to update (Account: {account_number}, Violation: {violation_number}, Email: {email})")
        except Exception as e:
            log_message(f"⚠️  Warning: Could not update account data: {str(e)}")
            import traceback
            log_message(f"   Traceback: {traceback.format_exc()}")
    
    # Send email if provided
    if email:
        if has_success:
            try:
                log_message(f"📤 Attempting to send email to {email}...")
                # Pass logger function to email_service
                email_success = send_toll_info_email(email, combined_result, logger=log_message)
                
                if email_success:
                    log_message(f"✅ Email sent successfully to {email} (Combined: {' + '.join(sources)})")
                else:
                    log_message(f"❌ Email sending failed for {email} - check error messages above")
                    
            except Exception as e:
                log_message(f"❌ Error sending email to {email}: {str(e)}")
                import traceback
                log_message(f"   Traceback: {traceback.format_exc()}")
        else:
            log_message(f"⚠️  Email not sent to {email} - automation did not complete successfully (no data to send)")
    
    with results_lock:
        results_list.append(combined_result)

def main():
    """Main function to process all accounts"""
    log_message("=" * 60)
    log_message("🚀 Starting automated toll information fetch")
    log_message("=" * 60)
    
    # Load accounts
    accounts = load_accounts()
    
    if not accounts:
        log_message("⚠️  No accounts configured. Exiting.")
        return
    
    # Filter out accounts with missing required fields (either NY or NJ must be present)
    valid_accounts = []
    for acc in accounts:
        has_ny = acc.get('account_number', '').strip() and acc.get('plate_number', '').strip()
        has_nj = (acc.get('violation_number') or acc.get('nj_violation_number')) and (acc.get('plate_number') or acc.get('nj_plate_number'))
        if has_ny or has_nj:
            valid_accounts.append(acc)
    
    if not valid_accounts:
        log_message("⚠️  No valid accounts found (need either NY account+plate or NJ violation+plate). Exiting.")
        return
    
    log_message(f"📋 Found {len(valid_accounts)} account(s) to process")
    log_message("📌 Processing accounts sequentially (one at a time, not in parallel)")
    log_message("⏱️  Wait time between accounts: 15 seconds")
    log_message("=" * 60)
    
    # Process accounts sequentially (one by one, not in parallel)
    results = []
    results_lock = threading.Lock()
    
    for i, account in enumerate(valid_accounts, 1):
        log_message(f"\n[{i}/{len(valid_accounts)}] Processing account...")
        process_account(account, results, results_lock)
        log_message(f"✓ Completed account {i}/{len(valid_accounts)}")
        
        # Wait 15 seconds before processing next account (except for the last one)
        if i < len(valid_accounts):
            log_message("⏳ Waiting 15 seconds before processing next account...")
            time.sleep(15)
            log_message("✅ Wait complete, proceeding to next account\n")
    
    # Summary
    successful = sum(1 for r in results if r.get('success'))
    failed = len(results) - successful
    
    log_message("=" * 60)
    log_message(f"✅ Completed: {successful} successful, {failed} failed out of {len(results)} total")
    log_message("=" * 60)
    log_message("")  # Empty line for readability

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log_message("⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        log_message(f"❌ Fatal error: {str(e)}")
        import traceback
        log_message(traceback.format_exc())
        sys.exit(1)

