"""
Flask backend for E-ZPass NY Toll Dashboard
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from automation_selenium import extract_toll_info
from automation_selenium_nj import extract_toll_info_nj
from email_service import send_toll_info_email, send_otp_email
from email_reader import EmailReader, check_emails_and_extract
from account_manager import add_account
from user_manager import UserManager
import time
import json
import threading

app = Flask(__name__)
# CORS configuration - update with your domain
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Update to specific domains in production: ["https://yourdomain.com"]
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Store last fetched data
last_data = None

# Initialize user manager
user_manager = UserManager()


@app.route('/')
def index():
    """Serve the dashboard page or user dashboard based on domain"""
    # Check if this is a user app domain (optional - for domain-based routing)
    host = request.host.lower()
    if 'app' in host or 'user' in host or 'users' in host:
        return render_template('user_dashboard.html')
    return render_template('dashboard.html')


@app.route('/user')
def user_dashboard():
    """Serve the user dashboard page"""
    return render_template('user_dashboard.html')


@app.route('/api/fetch-toll-info', methods=['POST'])
def fetch_toll_info():
    """API endpoint to trigger automation and fetch toll information"""
    try:
        data = request.json
        account_number = data.get('account_number', '').strip()
        plate_number = data.get('plate_number', '').strip()
        
        if not account_number or not plate_number:
            return jsonify({
                'success': False,
                'error': 'Account number and plate number are required'
            }), 400
        
        # Get headless option from request (default False - always show browser)
        headless = data.get('headless', False)
        
        # Get email address if provided
        email = data.get('email', '').strip()
        
        # Run the automation (Selenium is synchronous)
        result = extract_toll_info(account_number, plate_number, headless=headless)
        
        # Store the result
        global last_data
        last_data = result
        
        # Send email if provided and data was successfully fetched
        if email and result.get('success'):
            # Send email in background thread to not block response
            email_sent_success = [False]  # Use list to allow modification in nested function
            email_error = [None]
            
            def send_email_async():
                try:
                    # Ensure we're in the right directory and load env
                    import os
                    os.chdir('/Users/ghuman/tolls')
                    from dotenv import load_dotenv
                    load_dotenv()
                    
                    success = send_toll_info_email(email, result)
                    email_sent_success[0] = success
                    if success:
                        print(f"✅ Email sent successfully to {email}")
                    else:
                        print(f"❌ Email failed to send to {email}")
                except Exception as e:
                    error_msg = str(e)
                    email_error[0] = error_msg
                    print(f"❌ Exception sending email: {error_msg}")
                    email_sent_success[0] = False
            
            email_thread = threading.Thread(target=send_email_async)
            email_thread.daemon = True
            email_thread.start()
            
            # Give the thread more time to complete (email can take a few seconds)
            email_thread.join(timeout=10)  # Wait up to 10 seconds
            
            result['email_sent'] = email_sent_success[0]
            if email_error[0]:
                result['email_error'] = email_error[0]
        else:
            result['email_sent'] = False
            if not email:
                print("⚠️  No email address provided")
            elif not result.get('success'):
                print("⚠️  Data fetch failed, email not sent")
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/fetch-batch-toll-info', methods=['POST'])
def fetch_batch_toll_info():
    """API endpoint to fetch toll information for multiple accounts in parallel"""
    try:
        data = request.json
        accounts = data.get('accounts', [])
        
        if not accounts or len(accounts) == 0:
            return jsonify({
                'success': False,
                'error': 'At least one account is required'
            }), 400
        
        # Validate accounts
        for acc in accounts:
            if not acc.get('account_number', '').strip() or not acc.get('plate_number', '').strip():
                return jsonify({
                    'success': False,
                    'error': 'All accounts must have account number and plate number'
                }), 400
        
        # Process accounts in parallel using threads
        results = []
        threads = []
        results_lock = threading.Lock()
        
        def process_account(account_data):
            """Process a single account"""
            account_number = account_data['account_number'].strip()
            plate_number = account_data['plate_number'].strip()
            email = account_data.get('email', '').strip()
            
            try:
                # Run automation
                result = extract_toll_info(account_number, plate_number, headless=False)
                
                # Send email if provided
                if email and result.get('success'):
                    try:
                        import os
                        os.chdir('/Users/ghuman/tolls')
                        from dotenv import load_dotenv
                        load_dotenv()
                        
                        email_success = send_toll_info_email(email, result)
                        result['email_sent'] = email_success
                        if email_success:
                            print(f"✅ Email sent to {email} for account {account_number}")
                    except Exception as e:
                        print(f"❌ Error sending email to {email}: {str(e)}")
                        result['email_sent'] = False
                else:
                    result['email_sent'] = False
                
                with results_lock:
                    results.append(result)
                    
            except Exception as e:
                error_result = {
                    'success': False,
                    'account_number': account_number,
                    'plate_number': plate_number,
                    'error': str(e),
                    'email_sent': False
                }
                with results_lock:
                    results.append(error_result)
        
        # Start threads for each account
        for account in accounts:
            thread = threading.Thread(target=process_account, args=(account,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete (with timeout)
        for thread in threads:
            thread.join(timeout=300)  # 5 minutes per account
        
        # Check if any threads are still running
        still_running = [t for t in threads if t.is_alive()]
        if still_running:
            print(f"⚠️  {len(still_running)} account(s) still processing (timeout)")
        
        return jsonify({
            'success': True,
            'total_accounts': len(accounts),
            'processed': len(results),
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """Get saved accounts from config file"""
    try:
        import os
        config_file = os.path.join(os.path.dirname(__file__), 'accounts_config.json')
        
        if not os.path.exists(config_file):
            return jsonify({
                'success': True,
                'accounts': []
            })
        
        with open(config_file, 'r') as f:
            config = json.load(f)
            return jsonify({
                'success': True,
                'accounts': config.get('accounts', [])
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error reading accounts: {str(e)}'
        }), 500


@app.route('/api/accounts', methods=['POST'])
def save_accounts():
    """Save accounts to config file"""
    try:
        import os
        data = request.json
        accounts = data.get('accounts', [])
        
        # Validate accounts - must have either NY account+plate or NJ violation+plate
        for acc in accounts:
            # Check for NY account
            account_number = acc.get('account_number', '') or ''
            plate_number = acc.get('plate_number', '') or ''
            has_ny = bool(str(account_number).strip()) and bool(str(plate_number).strip())
            
            # Check for NJ violation
            violation_number = acc.get('violation_number') or acc.get('nj_violation_number') or ''
            nj_plate = acc.get('nj_plate_number') or acc.get('plate_number') or ''
            has_nj = bool(str(violation_number).strip()) and bool(str(nj_plate).strip())
            
            if not has_ny and not has_nj:
                return jsonify({
                    'success': False,
                    'error': f'Each account must have either NY (account number + plate) or NJ (violation number + plate). Account data: {acc}'
                }), 400
        
        config_file = os.path.join(os.path.dirname(__file__), 'accounts_config.json')
        
        # Preserve balance data if it exists
        existing_config = {}
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    existing_config = json.load(f)
            except:
                pass
        
        # Preserve balance data from existing accounts when saving updates (don't merge/archive on save)
        existing_accounts = existing_config.get('accounts', [])
        archived_accounts = existing_config.get('archived_accounts', [])
        
        # When saving from UI, just preserve balance data for matching accounts
        # Don't merge/archive - that should only happen when explicitly adding accounts via add_account()
        for new_acc in accounts:
            new_email = new_acc.get('email', '').strip().lower()
            
            # Try to match with existing account to preserve balance data
            for existing_acc in existing_accounts:
                existing_email = existing_acc.get('email', '').strip().lower()
                
                # Match by email first
                if new_email and existing_email == new_email:
                    # Preserve balance data if not provided in new account
                    if 'balance_amount' not in new_acc and 'balance_amount' in existing_acc:
                        new_acc['balance_amount'] = existing_acc.get('balance_amount')
                    if 'ny_balance_amount' not in new_acc and 'ny_balance_amount' in existing_acc:
                        new_acc['ny_balance_amount'] = existing_acc.get('ny_balance_amount')
                    if 'nj_balance_amount' not in new_acc and 'nj_balance_amount' in existing_acc:
                        new_acc['nj_balance_amount'] = existing_acc.get('nj_balance_amount')
                    if 'violation_count' not in new_acc and 'violation_count' in existing_acc:
                        new_acc['violation_count'] = existing_acc.get('violation_count')
                    if 'toll_bill_numbers' not in new_acc and 'toll_bill_numbers' in existing_acc:
                        new_acc['toll_bill_numbers'] = existing_acc.get('toll_bill_numbers')
                    if 'last_updated' not in new_acc and 'last_updated' in existing_acc:
                        new_acc['last_updated'] = existing_acc.get('last_updated')
                    break
                else:
                    # Match by account details (NY)
                    match_by_ny = (existing_acc.get('account_number', '').strip().upper() == new_acc.get('account_number', '').strip().upper() and
                                  existing_acc.get('plate_number', '').strip().upper() == new_acc.get('plate_number', '').strip().upper() and
                                  new_acc.get('account_number', '').strip())
                    # Match by account details (NJ)
                    existing_violation = (existing_acc.get('violation_number') or existing_acc.get('nj_violation_number') or '').strip().upper()
                    new_violation = (new_acc.get('violation_number') or new_acc.get('nj_violation_number') or '').strip().upper()
                    match_by_nj = existing_violation and new_violation and existing_violation == new_violation
                    
                    if match_by_ny or match_by_nj:
                        # Preserve balance data if not provided in new account
                        if 'balance_amount' not in new_acc and 'balance_amount' in existing_acc:
                            new_acc['balance_amount'] = existing_acc.get('balance_amount')
                        if 'ny_balance_amount' not in new_acc and 'ny_balance_amount' in existing_acc:
                            new_acc['ny_balance_amount'] = existing_acc.get('ny_balance_amount')
                        if 'nj_balance_amount' not in new_acc and 'nj_balance_amount' in existing_acc:
                            new_acc['nj_balance_amount'] = existing_acc.get('nj_balance_amount')
                        if 'violation_count' not in new_acc and 'violation_count' in existing_acc:
                            new_acc['violation_count'] = existing_acc.get('violation_count')
                        if 'toll_bill_numbers' not in new_acc and 'toll_bill_numbers' in existing_acc:
                            new_acc['toll_bill_numbers'] = existing_acc.get('toll_bill_numbers')
                        if 'last_updated' not in new_acc and 'last_updated' in existing_acc:
                            new_acc['last_updated'] = existing_acc.get('last_updated')
                        break
        
        config = {
            'accounts': accounts,
            'archived_accounts': archived_accounts if 'archived_accounts' in locals() else existing_config.get('archived_accounts', [])
        }
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Saved {len(accounts)} account(s) successfully',
            'accounts': accounts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error saving accounts: {str(e)}'
        }), 500


@app.route('/api/last-data', methods=['GET'])
def get_last_data():
    """Get the last fetched data"""
    global last_data
    if last_data:
        return jsonify(last_data)
    return jsonify({
        'success': False,
        'error': 'No data available. Please fetch toll information first.'
    }), 404


@app.route('/api/check-emails', methods=['POST'])
def check_emails():
    """Check for new emails and extract account/plate information, then trigger automation"""
    try:
        # Get configuration from request
        data = request.json or {}
        auto_process = data.get('auto_process', True)  # Automatically process emails by default
        mark_read = data.get('mark_read', True)  # Mark emails as read after processing
        
        # Check for emails
        reader = EmailReader()
        try:
            if not reader.connect():
                return jsonify({
                    'success': False,
                    'error': 'Failed to connect to email server. Check IMAP credentials in EMAIL_CHECK_INTERVAL=60.env file.'
                }), 500
            
            emails = reader.get_unread_emails()
            
            if not emails:
                return jsonify({
                    'success': True,
                    'message': 'No emails with account/plate information found',
                    'emails_processed': 0,
                    'results': []
                })
            
            results = []
            
            # Process each email sequentially (one by one)
            for email_data in emails:
                account_number = email_data.get('account_number')
                violation_number = email_data.get('violation_number')
                plate_number = email_data.get('plate_number')
                nj_plate_number = email_data.get('nj_plate_number') or plate_number
                email_address = email_data.get('email')
                email_id = email_data.get('email_id')
                source = email_data.get('source', 'NY')
                
                result = {
                    'email_id': email_id,
                    'sender': email_data.get('sender_email'),
                    'subject': email_data.get('subject'),
                    'account_number': account_number,
                    'violation_number': violation_number,
                    'plate_number': plate_number,
                    'email': email_address,
                    'source': source,
                    'processed': False
                }
                
                has_data = (account_number and plate_number) or (violation_number and nj_plate_number)
                
                if auto_process and has_data:
                    combined_balance = 0.0
                    combined_bill_numbers = []
                    combined_violations = 0
                    combined_result = None
                    sources_processed = []
                    
                    # Process NY account first (if exists)
                    if account_number and plate_number:
                        # Automatically save account to saved accounts
                        add_account(account_number=account_number, plate_number=plate_number, email=email_address, source='NY')
                        result['account_saved'] = True
                        
                        try:
                            # Run NY automation
                            ny_result = extract_toll_info(account_number, plate_number, headless=False)
                            if ny_result.get('success'):
                                combined_balance += ny_result.get('balance_amount', 0)
                                combined_bill_numbers.extend(ny_result.get('toll_bill_numbers', []))
                                combined_violations += ny_result.get('violation_count', 0)
                                combined_result = ny_result
                                sources_processed.append('NY')
                        except Exception as e:
                            result['ny_error'] = str(e)
                    
                    # Process NJ violation second (if exists) - sequentially after NY
                    if violation_number and nj_plate_number:
                        # Automatically save NJ account to saved accounts
                        add_account(violation_number=violation_number, plate_number=nj_plate_number, email=email_address, source='NJ')
                        
                        try:
                            # Run NJ automation
                            nj_result = extract_toll_info_nj(violation_number, nj_plate_number, headless=False)
                            if nj_result.get('success'):
                                combined_balance += nj_result.get('balance_amount', 0)
                                combined_bill_numbers.extend(nj_result.get('toll_bill_numbers', []))
                                combined_violations += nj_result.get('violation_count', 0)
                                if combined_result:
                                    combined_result['balance_amount'] = combined_balance
                                    combined_result['toll_bill_numbers'] = list(set(combined_bill_numbers))
                                    combined_result['violation_count'] = combined_violations
                                    combined_result['nj_result'] = nj_result
                                    combined_result['sources'] = sources_processed + ['NJ']
                                else:
                                    combined_result = nj_result
                                sources_processed.append('NJ')
                        except Exception as e:
                            result['nj_error'] = str(e)
                    
                    if combined_result:
                        result['toll_data'] = combined_result
                        result['processed'] = True
                        result['sources'] = sources_processed
                        
                        # Send email back with results if email address is provided
                        if email_address and combined_result.get('success'):
                            send_toll_info_email(email_address, combined_result)
                            result['email_sent'] = True
                    
                    # Mark email as read if requested
                    if mark_read and email_id:
                        reader.mark_as_read(email_id)
                
                results.append(result)
            
            return jsonify({
                'success': True,
                'message': f'Processed {len(emails)} email(s)',
                'emails_processed': len(emails),
                'results': results
            })
        
        finally:
            reader.disconnect()
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error checking emails: {str(e)}'
        }), 500


@app.route('/api/check-emails-simple', methods=['GET'])
def check_emails_simple():
    """Simple endpoint to check emails and return parsed data without processing"""
    try:
        emails = check_emails_and_extract()
        
        return jsonify({
            'success': True,
            'emails_found': len(emails),
            'emails': [
                {
                    'account_number': e.get('account_number'),
                    'plate_number': e.get('plate_number'),
                    'email': e.get('email'),
                    'sender': e.get('sender_email'),
                    'subject': e.get('subject')
                }
                for e in emails
            ]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error checking emails: {str(e)}'
        }), 500


@app.route('/api/fetch-single-account', methods=['POST'])
def fetch_single_account():
    """API endpoint to fetch toll information for a single account by account/plate"""
    try:
        data = request.json
        account_number = data.get('account_number', '').strip()
        plate_number = data.get('plate_number', '').strip()
        source = data.get('source', 'NY').upper()  # Default to NY
        
        if not plate_number:
            return jsonify({
                'success': False,
                'error': 'Plate number is required'
            }), 400
        
        # Choose automation based on source
        if source == 'NJ':
            violation_number = data.get('violation_number', '').strip()
            if not violation_number:
                return jsonify({
                    'success': False,
                    'error': 'Violation number is required for NJ E-ZPass'
                }), 400
            result = extract_toll_info_nj(
                violation_number=violation_number,
                plate_number=plate_number,
                account_number=account_number,
                headless=False
            )
        else:
            # NY E-ZPass
            if not account_number:
                return jsonify({
                    'success': False,
                    'error': 'Account number is required for NY E-ZPass'
                }), 400
            result = extract_toll_info(account_number, plate_number, headless=False)
            
            # For NY accounts, set ny_balance_amount from balance_amount
            if result.get('success') and 'balance_amount' in result:
                result['ny_balance_amount'] = result.get('balance_amount', 0)
                result['nj_balance_amount'] = 0  # No NJ balance for NY-only accounts
                result['sources'] = ['NY']
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/fetch-nj-violation', methods=['POST'])
def fetch_nj_violation():
    """API endpoint to fetch violation information from E-ZPass NJ"""
    try:
        data = request.json
        violation_number = data.get('violation_number', '').strip()
        plate_number = data.get('plate_number', '').strip()
        
        if not violation_number or not plate_number:
            return jsonify({
                'success': False,
                'error': 'Violation number and plate number are required'
            }), 400
        
        # Run the NJ automation
        result = extract_toll_info_nj(
            violation_number=violation_number,
            plate_number=plate_number,
            headless=False
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/send-account-email', methods=['POST'])
def send_account_email():
    """API endpoint to send email with toll information"""
    try:
        data = request.json
        recipient_email = data.get('email', '').strip()
        toll_data = data.get('toll_data', {})
        
        if not recipient_email:
            return jsonify({
                'success': False,
                'error': 'Email address is required'
            }), 400
        
        if not toll_data:
            return jsonify({
                'success': False,
                'error': 'Toll data is required'
            }), 400
        
        # Send email
        email_success = send_toll_info_email(recipient_email, toll_data)
        
        if email_success:
            return jsonify({
                'success': True,
                'message': f'Email sent successfully to {recipient_email}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send email. Check SMTP configuration and logs.'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


# ==================== USER AUTHENTICATION ENDPOINTS ====================

@app.route('/api/user/signup', methods=['POST'])
def user_signup():
    """User signup endpoint"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        name = data.get('name', '').strip()
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        result = user_manager.signup(email, password, name)
        
        if result['success']:
            # Send OTP email
            otp = result.get('otp', '')
            if otp:
                email_sent = send_otp_email(email, otp, name)
                if not email_sent:
                    return jsonify({
                        'success': False,
                        'error': 'Account created but failed to send verification email. Please try again later.'
                    }), 500
            
            # Check if this was a re-signup (unverified email)
            message = 'Account created successfully. Please check your email for verification code.'
            if result.get('resend', False):
                message = 'New verification code sent to your email. Please check your inbox.'
            
            return jsonify({
                'success': True,
                'user': result['user'],
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Signup failed')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/user/login', methods=['POST'])
def user_login():
    """User login endpoint"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        result = user_manager.login(email, password)
        
        if result['success']:
            # Link accounts to user by email
            user_manager.link_accounts_to_user(email)
            
            return jsonify({
                'success': True,
                'user': result['user'],
                'message': 'Login successful'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Login failed')
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/user/data', methods=['GET'])
def get_user_data():
    """Get user data and linked accounts"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Authentication token required'
            }), 401
        
        user = user_manager.get_user_by_token(token)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 401
        
        # Link accounts to user (refresh)
        user_manager.link_accounts_to_user(user['email'])
        
        # Get updated user data
        user = user_manager.get_user_by_token(token)
        accounts = user_manager.get_user_accounts(user['email'])
        
        return jsonify({
            'success': True,
            'user': {
                'email': user['email'],
                'name': user.get('name', ''),
                'created_at': user.get('created_at', ''),
                'last_login': user.get('last_login', '')
            },
            'accounts': accounts
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/user/refresh', methods=['POST'])
def refresh_user_data():
    """Refresh user data by re-linking accounts"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Authentication token required'
            }), 401
        
        user = user_manager.get_user_by_token(token)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 401
        
        # Link accounts to user
        user_manager.link_accounts_to_user(user['email'])
        
        # Get updated accounts
        accounts = user_manager.get_user_accounts(user['email'])
        
        return jsonify({
            'success': True,
            'accounts': accounts,
            'message': 'Data refreshed successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/user/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and activate user account"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        otp = data.get('otp', '').strip()
        
        if not email or not otp:
            return jsonify({
                'success': False,
                'error': 'Email and OTP are required'
            }), 400
        
        result = user_manager.verify_otp(email, otp)
        
        if result['success']:
            # Link accounts to user by email
            user_manager.link_accounts_to_user(email)
            
            return jsonify({
                'success': True,
                'user': result.get('user'),
                'message': result.get('message', 'Email verified successfully')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'OTP verification failed')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/user/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP to user email"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        result = user_manager.resend_otp(email)
        
        if result['success']:
            # Get user name for email
            user = user_manager.get_user_by_email(email)
            name = user.get('name', '') if user else ''
            
            # Send OTP email
            otp = result.get('otp', '')
            if otp:
                email_sent = send_otp_email(email, otp, name)
                if not email_sent:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to send verification email. Please try again later.'
                    }), 500
            
            return jsonify({
                'success': True,
                'message': 'OTP sent successfully. Please check your email.'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to resend OTP')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


if __name__ == '__main__':
    # Development server - use Gunicorn in production
    import os
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    
    # Use PORT from environment (for Render/Heroku) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    print("Starting E-ZPass NY Toll Dashboard...")
    print("⚠️  Development server - Use Gunicorn in production!")
    print("   Production: gunicorn --config gunicorn_config.py app:app")
    print(f"   Open http://localhost:{port} in your browser")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)

