"""
Flask app for Render deployment - USER DASHBOARD ONLY
Selenium/automation stays on Mac server
This app only handles user authentication and displaying data
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from user_manager import UserManager
import os
import json
from datetime import datetime

app = Flask(__name__)
# CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Update to specific domains in production
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize user manager
user_manager = UserManager()


@app.route('/')
def index():
    """Serve the user dashboard page"""
    return render_template('user_dashboard.html')


@app.route('/user')
def user_dashboard():
    """Serve the user dashboard page"""
    return render_template('user_dashboard.html')


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
            # Send OTP email (from Mac server's email service)
            # Note: Email sending might need to call Mac server API
            from email_service import send_otp_email
            otp = result.get('otp', '')
            if otp:
                email_sent = send_otp_email(email, otp, name)
                if not email_sent:
                    return jsonify({
                        'success': False,
                        'error': 'Account created but failed to send verification email. Please try again later.'
                    }), 500
            
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
            if result.get('requires_verification'):
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Email not verified'),
                    'requires_verification': True
                }), 401
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
        
        # Link accounts to user (refresh from accounts_config.json)
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
        
        # Link accounts to user (reads from accounts_config.json)
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
            from email_service import send_otp_email
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


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'user-dashboard',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    # Use PORT from environment (for Render) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    
    print("Starting User Dashboard (Render)...")
    print(f"⚠️  This is the user-facing app only")
    print(f"   Selenium/automation runs on Mac server")
    print(f"   Open http://localhost:{port}/user in your browser")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
