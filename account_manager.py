"""
Account management utility to save and load accounts from config file
"""
import json
import os
from typing import List, Dict, Optional


def load_accounts() -> List[Dict]:
    """Load accounts from config file"""
    config_file = os.path.join(os.path.dirname(__file__), 'accounts_config.json')
    
    if not os.path.exists(config_file):
        return []
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            return config.get('accounts', [])
    except Exception as e:
        print(f"Error loading accounts: {str(e)}")
        return []


def load_archived_accounts() -> List[Dict]:
    """Load archived accounts from config file"""
    config_file = os.path.join(os.path.dirname(__file__), 'accounts_config.json')
    
    if not os.path.exists(config_file):
        return []
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            return config.get('archived_accounts', [])
    except Exception as e:
        print(f"Error loading archived accounts: {str(e)}")
        return []


def save_accounts(accounts: List[Dict], archived_accounts: List[Dict] = None) -> bool:
    """Save accounts to config file"""
    config_file = os.path.join(os.path.dirname(__file__), 'accounts_config.json')
    
    try:
        # Load existing config to preserve archived accounts if not provided
        existing_config = {}
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    existing_config = json.load(f)
            except:
                pass
        
        config = {
            'accounts': accounts
        }
        
        # Include archived accounts if provided, otherwise preserve existing
        if archived_accounts is not None:
            config['archived_accounts'] = archived_accounts
        elif 'archived_accounts' in existing_config:
            config['archived_accounts'] = existing_config['archived_accounts']
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving accounts: {str(e)}")
        return False


def archive_account(account: Dict, reason: str = None) -> bool:
    """Move an account to the archived list"""
    try:
        from datetime import datetime
        archived_accounts = load_archived_accounts()
        accounts = load_accounts()
        
        # Create a copy to archive
        archived_acc = account.copy()
        archived_acc['archived_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if reason:
            archived_acc['archived_reason'] = reason
        
        archived_accounts.append(archived_acc)
        
        # Remove from active accounts
        accounts = [acc for acc in accounts if acc != account]
        
        return save_accounts(accounts, archived_accounts)
    except Exception as e:
        print(f"Error archiving account: {str(e)}")
        return False


def add_account(account_number: str = None, plate_number: str = None, email: Optional[str] = None,
                violation_number: str = None, source: str = 'NY') -> bool:
    """
    Add a new account to the saved accounts list, merging with existing accounts by email
    
    Args:
        account_number: E-ZPass account number (for NY)
        plate_number: License plate number
        email: Optional email address (used for merging accounts)
        violation_number: Violation number (for NJ)
        source: 'NY' or 'NJ'
        
    Returns:
        True if account was added/merged, False if error occurred
    """
    plate_number = plate_number.strip().upper() if plate_number else None
    email = email.strip().lower() if email else None
    source = source.upper()
    
    # Validate based on source
    if source == 'NJ':
        if not violation_number or not plate_number:
            print("⚠️  Violation number and plate number are required for NJ")
            return False
        violation_number = violation_number.strip().upper()
    else:  # NY
        if not account_number or not plate_number:
            print("⚠️  Account number and plate number are required for NY")
            return False
        account_number = account_number.strip().upper()
    
    # Load existing accounts
    accounts = load_accounts()
    
    # Check if account already exists (by source-specific fields + plate number)
    account_exists = False
    for acc in accounts:
        if source == 'NJ':
            if (acc.get('violation_number', '').strip().upper() == violation_number and
                acc.get('plate_number', '').strip().upper() == plate_number and
                acc.get('source', 'NY') == 'NJ'):
                account_exists = True
                # Update email if provided
                if email and acc.get('email') != email:
                    acc['email'] = email
                    save_accounts(accounts)
                    print(f"✅ Updated email for existing NJ account to {email}")
                break
        else:  # NY
            if (acc.get('account_number', '').strip().upper() == account_number and
                acc.get('plate_number', '').strip().upper() == plate_number and
                acc.get('source', 'NY') == 'NY'):
                account_exists = True
                # Update email if provided
                if email and acc.get('email') != email:
                    acc['email'] = email
                    save_accounts(accounts)
                    print(f"✅ Updated email for existing NY account to {email}")
                break
    
    if account_exists:
        print(f"ℹ️  {source} account already exists in saved accounts")
        return False
    
    # Check if we should merge with existing account by email
    merged = False
    if email:
        from datetime import datetime
        existing_accounts_to_archive = []
        merged_account = None
        accounts_to_remove_indices = []
        
        # Find all accounts with the same email
        for idx, acc in enumerate(accounts):
            existing_email = acc.get('email', '').strip().lower()
            if existing_email == email:
                if merged_account is None:
                    # This is the first matching account - use it as the base for merging
                    old_account = acc.copy()  # Keep copy of old account for archiving
                    merged_account = acc.copy()
                    
                    # Archive the old account
                    old_account['archived_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    old_account['archived_reason'] = f'Merged with new {source} account (same email: {email})'
                    existing_accounts_to_archive.append(old_account)
                    accounts_to_remove_indices.append(idx)
                    
                    # Merge: add new account's info to existing account
                    if source == 'NJ':
                        merged_account['nj_violation_number'] = violation_number
                        merged_account['violation_number'] = violation_number  # Set both fields
                        merged_account['nj_plate_number'] = plate_number
                        # Keep existing plate_number if it's different (might be NY plate)
                        if not merged_account.get('plate_number'):
                            merged_account['plate_number'] = plate_number
                    else:
                        merged_account['account_number'] = account_number
                        merged_account['plate_number'] = plate_number
                        # Keep existing nj_plate_number if it exists
                        if not merged_account.get('nj_plate_number'):
                            merged_account['nj_plate_number'] = plate_number
                    
                    merged_account['sources'] = merged_account.get('sources', [merged_account.get('source', 'NY')])
                    if source not in merged_account['sources']:
                        merged_account['sources'].append(source)
                    
                    # Update email if needed (normalize case)
                    merged_account['email'] = email
                    
                    merged = True
                else:
                    # Found another account with same email - archive this one too
                    old_acc = acc.copy()
                    old_acc['archived_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    old_acc['archived_reason'] = f'Merged with account (same email: {email})'
                    existing_accounts_to_archive.append(old_acc)
                    accounts_to_remove_indices.append(idx)
                    
                    # Merge data from this account too
                    if source == 'NJ':
                        # Preserve NJ data from old account
                        if old_acc.get('violation_number') and not merged_account.get('violation_number'):
                            merged_account['violation_number'] = old_acc.get('violation_number')
                            merged_account['nj_violation_number'] = old_acc.get('violation_number')
                        if old_acc.get('nj_violation_number') and not merged_account.get('nj_violation_number'):
                            merged_account['nj_violation_number'] = old_acc.get('nj_violation_number')
                            merged_account['violation_number'] = old_acc.get('nj_violation_number')
                        if old_acc.get('nj_plate_number') and not merged_account.get('nj_plate_number'):
                            merged_account['nj_plate_number'] = old_acc.get('nj_plate_number')
                        # Preserve NY data from old account if it exists
                        if old_acc.get('account_number') and not merged_account.get('account_number'):
                            merged_account['account_number'] = old_acc.get('account_number')
                        if old_acc.get('plate_number') and not merged_account.get('plate_number'):
                            merged_account['plate_number'] = old_acc.get('plate_number')
                    else:
                        # Preserve NY data from old account
                        if old_acc.get('account_number') and not merged_account.get('account_number'):
                            merged_account['account_number'] = old_acc.get('account_number')
                        if old_acc.get('plate_number') and not merged_account.get('plate_number'):
                            merged_account['plate_number'] = old_acc.get('plate_number')
                        # Preserve NJ data from old account if it exists
                        if old_acc.get('violation_number') and not merged_account.get('violation_number'):
                            merged_account['violation_number'] = old_acc.get('violation_number')
                            merged_account['nj_violation_number'] = old_acc.get('violation_number')
                        if old_acc.get('nj_violation_number') and not merged_account.get('nj_violation_number'):
                            merged_account['nj_violation_number'] = old_acc.get('nj_violation_number')
                            merged_account['violation_number'] = old_acc.get('nj_violation_number')
                        if old_acc.get('nj_plate_number') and not merged_account.get('nj_plate_number'):
                            merged_account['nj_plate_number'] = old_acc.get('nj_plate_number')
                    
                    # Merge sources
                    old_sources = old_acc.get('sources', [old_acc.get('source', 'NY')])
                    merged_account['sources'] = list(set(merged_account['sources'] + old_sources))
        
        if merged:
            # Archive old accounts
            archived_accounts = load_archived_accounts()
            archived_accounts.extend(existing_accounts_to_archive)
            
            # Remove archived accounts from active list (in reverse order to preserve indices)
            for idx in sorted(accounts_to_remove_indices, reverse=True):
                accounts.pop(idx)
            
            # Add the merged account
            accounts.append(merged_account)
            
            print(f"✅ Merged {source} account with existing account(s) and archived {len(existing_accounts_to_archive)} old account(s) (same email: {email})")
            
            # Save with archived accounts
            save_accounts(accounts, archived_accounts)
    
    if not merged:
        # Add new account
        new_account = {
            'plate_number': plate_number,
            'source': source,
            'sources': [source]
        }
        
        if source == 'NJ':
            new_account['violation_number'] = violation_number
            new_account['nj_violation_number'] = violation_number  # Set both fields
            new_account['nj_plate_number'] = plate_number
        else:
            new_account['account_number'] = account_number
        
        if email:
            new_account['email'] = email
        
        accounts.append(new_account)
        print(f"✅ Added new {source} account to saved accounts")
        if source == 'NJ':
            print(f"   Violation: {violation_number} / Plate: {plate_number}")
        else:
            print(f"   Account: {account_number} / Plate: {plate_number}")
        if email:
            print(f"   Email: {email}")
    
    # Save accounts (only if not already saved during merge)
    if not merged:
        archived_accounts = load_archived_accounts()
        if save_accounts(accounts, archived_accounts):
            return True
        else:
            print(f"❌ Failed to save account")
            return False
    else:
        # Already saved during merge
        return True


def account_exists(account_number: str, plate_number: str) -> bool:
    """Check if an account already exists in saved accounts"""
    account_number = account_number.strip().upper()
    plate_number = plate_number.strip().upper()
    
    accounts = load_accounts()
    for acc in accounts:
        if (acc.get('account_number', '').strip().upper() == account_number and
            acc.get('plate_number', '').strip().upper() == plate_number):
            return True
    return False

