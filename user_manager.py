"""
User management system for user app
Handles user signup, login, and account linking
"""
import json
import os
import hashlib
import secrets
import random
from datetime import datetime, timedelta
from typing import Dict, Optional, List


class UserManager:
    def __init__(self, users_file: str = 'users.json'):
        """Initialize user manager"""
        self.users_file = os.path.join(os.path.dirname(__file__), users_file)
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        """Load users from JSON file"""
        if not os.path.exists(self.users_file):
            return {'users': []}
        
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading users: {e}")
            return {'users': []}
    
    def _save_users(self):
        """Save users to JSON file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving users: {e}")
            return False
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_token(self) -> str:
        """Generate a secure token for session management"""
        return secrets.token_urlsafe(32)
    
    def _generate_otp(self) -> str:
        """Generate a 6-digit OTP"""
        return str(random.randint(100000, 999999))
    
    def signup(self, email: str, password: str, name: str = '') -> Dict:
        """
        Sign up a new user
        
        Args:
            email: User email address
            password: User password
            name: Optional user name
            
        Returns:
            Dictionary with success status and user data or error message
        """
        email = email.strip().lower()
        
        # Validate email
        if not email or '@' not in email:
            return {
                'success': False,
                'error': 'Invalid email address'
            }
        
        # Validate password
        if not password or len(password) < 6:
            return {
                'success': False,
                'error': 'Password must be at least 6 characters'
            }
        
        # Check if user already exists
        existing_user = None
        for user in self.users.get('users', []):
            if user.get('email', '').lower() == email:
                existing_user = user
                break
        
        # If user exists and is verified, return error
        if existing_user:
            if existing_user.get('email_verified', False):
                return {
                    'success': False,
                    'error': 'Email already registered. Please sign in instead.'
                }
            else:
                # User exists but not verified - allow re-signup (update info and send new OTP)
                # Remove old unverified user
                self.users.get('users', []).remove(existing_user)
        
        # Generate OTP for email verification
        otp = self._generate_otp()
        otp_expires = (datetime.now() + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
        
        # Create new user (not verified yet)
        new_user = {
            'email': email,
            'password_hash': self._hash_password(password),
            'name': name.strip(),
            'email_verified': False,
            'otp': otp,
            'otp_expires': otp_expires,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'last_login': None,
            'token': None,  # No token until email is verified
            'accounts': []  # Will be linked by email matching
        }
        
        self.users.setdefault('users', []).append(new_user)
        
        if self._save_users():
            return {
                'success': True,
                'user': {
                    'email': new_user['email'],
                    'name': new_user['name'],
                    'email_verified': False,
                    'otp_sent': True
                },
                'otp': otp,  # Return OTP for testing (in production, don't return this)
                'resend': existing_user is not None  # Indicate if this was a re-signup
            }
        else:
            return {
                'success': False,
                'error': 'Failed to save user'
            }
    
    def login(self, email: str, password: str) -> Dict:
        """
        Login user (requires email verification)
        
        Args:
            email: User email address
            password: User password
            
        Returns:
            Dictionary with success status and user data or error message
        """
        email = email.strip().lower()
        password_hash = self._hash_password(password)
        
        # Find user
        for user in self.users.get('users', []):
            if user.get('email', '').lower() == email:
                if user.get('password_hash') == password_hash:
                    # Check if email is verified
                    if not user.get('email_verified', False):
                        return {
                            'success': False,
                            'error': 'Email not verified. Please verify your email with the OTP sent to your inbox.',
                            'requires_verification': True
                        }
                    
                    # Update last login and generate new token
                    user['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    user['token'] = self._generate_token()
                    
                    if self._save_users():
                        return {
                            'success': True,
                            'user': {
                                'email': user['email'],
                                'name': user.get('name', ''),
                                'token': user['token']
                            }
                        }
                    else:
                        return {
                            'success': False,
                            'error': 'Failed to update user data'
                        }
                else:
                    return {
                        'success': False,
                        'error': 'Invalid password'
                    }
        
        return {
            'success': False,
            'error': 'User not found'
        }
    
    def verify_otp(self, email: str, otp: str) -> Dict:
        """
        Verify OTP and mark email as verified
        
        Args:
            email: User email address
            otp: OTP code to verify
            
        Returns:
            Dictionary with success status
        """
        email = email.strip().lower()
        
        # Find user
        user = self.get_user_by_email(email)
        if not user:
            return {
                'success': False,
                'error': 'User not found'
            }
        
        # Check if already verified
        if user.get('email_verified', False):
            return {
                'success': True,
                'message': 'Email already verified',
                'user': {
                    'email': user['email'],
                    'name': user.get('name', ''),
                    'token': user.get('token')
                }
            }
        
        # Check OTP
        stored_otp = user.get('otp', '')
        otp_expires_str = user.get('otp_expires', '')
        
        if not stored_otp or not otp_expires_str:
            return {
                'success': False,
                'error': 'No OTP found. Please request a new OTP.'
            }
        
        # Check if OTP expired
        try:
            otp_expires = datetime.strptime(otp_expires_str, "%Y-%m-%d %H:%M:%S")
            if datetime.now() > otp_expires:
                return {
                    'success': False,
                    'error': 'OTP expired. Please request a new OTP.'
                }
        except:
            return {
                'success': False,
                'error': 'Invalid OTP expiration date'
            }
        
        # Verify OTP
        if stored_otp != otp.strip():
            return {
                'success': False,
                'error': 'Invalid OTP code'
            }
        
        # Mark email as verified and generate token
        user['email_verified'] = True
        user['token'] = self._generate_token()
        user['otp'] = None  # Clear OTP after verification
        user['otp_expires'] = None
        
        if self._save_users():
            return {
                'success': True,
                'message': 'Email verified successfully',
                'user': {
                    'email': user['email'],
                    'name': user.get('name', ''),
                    'token': user['token']
                }
            }
        else:
            return {
                'success': False,
                'error': 'Failed to save verification status'
            }
    
    def resend_otp(self, email: str) -> Dict:
        """
        Resend OTP to user email
        
        Args:
            email: User email address
            
        Returns:
            Dictionary with success status and OTP
        """
        email = email.strip().lower()
        
        # Find user
        user = self.get_user_by_email(email)
        if not user:
            return {
                'success': False,
                'error': 'User not found'
            }
        
        # Check if already verified
        if user.get('email_verified', False):
            return {
                'success': False,
                'error': 'Email already verified'
            }
        
        # Generate new OTP
        otp = self._generate_otp()
        otp_expires = (datetime.now() + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
        
        user['otp'] = otp
        user['otp_expires'] = otp_expires
        
        if self._save_users():
            return {
                'success': True,
                'message': 'OTP sent successfully',
                'otp': otp  # Return OTP for testing (in production, don't return this)
            }
        else:
            return {
                'success': False,
                'error': 'Failed to save OTP'
            }
    
    def get_user_by_token(self, token: str) -> Optional[Dict]:
        """
        Get user by authentication token
        
        Args:
            token: Authentication token
            
        Returns:
            User dictionary or None
        """
        for user in self.users.get('users', []):
            if user.get('token') == token:
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Get user by email address
        
        Args:
            email: User email address
            
        Returns:
            User dictionary or None
        """
        email = email.strip().lower()
        for user in self.users.get('users', []):
            if user.get('email', '').lower() == email:
                return user
        return None
    
    def link_accounts_to_user(self, email: str) -> bool:
        """
        Link accounts from accounts_config.json to user by email
        
        Args:
            email: User email address
            
        Returns:
            True if accounts were linked, False otherwise
        """
        email = email.strip().lower()
        user = self.get_user_by_email(email)
        
        if not user:
            return False
        
        # Load accounts from accounts_config.json
        accounts_file = os.path.join(os.path.dirname(__file__), 'accounts_config.json')
        if not os.path.exists(accounts_file):
            return False
        
        try:
            with open(accounts_file, 'r') as f:
                accounts_config = json.load(f)
            
            # Find accounts matching this email
            linked_accounts = []
            for account in accounts_config.get('accounts', []):
                account_email = account.get('email', '').strip().lower()
                if account_email == email:
                    # Create account summary (without sensitive data)
                    account_summary = {
                        'account_number': account.get('account_number', ''),
                        'plate_number': account.get('plate_number', ''),
                        'violation_number': account.get('violation_number') or account.get('nj_violation_number', ''),
                        'nj_plate_number': account.get('nj_plate_number', ''),
                        'balance_amount': account.get('balance_amount', 0),
                        'ny_balance_amount': account.get('ny_balance_amount', 0),
                        'nj_balance_amount': account.get('nj_balance_amount', 0),
                        'violation_count': account.get('violation_count', 0),
                        'toll_bill_numbers': account.get('toll_bill_numbers', []),
                        'last_updated': account.get('last_updated', ''),
                        'sources': account.get('sources', [])
                    }
                    linked_accounts.append(account_summary)
            
            # Update user's accounts
            user['accounts'] = linked_accounts
            
            return self._save_users()
        except Exception as e:
            print(f"Error linking accounts: {e}")
            return False
    
    def get_user_accounts(self, email: str) -> List[Dict]:
        """
        Get all accounts linked to a user
        
        Args:
            email: User email address
            
        Returns:
            List of account dictionaries
        """
        email = email.strip().lower()
        user = self.get_user_by_email(email)
        
        if not user:
            return []
        
        # Ensure accounts are up to date
        self.link_accounts_to_user(email)
        
        # Reload user to get updated accounts
        user = self.get_user_by_email(email)
        return user.get('accounts', []) if user else []

