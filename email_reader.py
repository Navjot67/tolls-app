"""
Email reader service to fetch emails and extract account/plate information
"""
import imaplib
from email import message_from_bytes
from email.message import Message
from email.header import decode_header
import os
import re
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()


class EmailReader:
    def __init__(self):
        """Initialize email reader with IMAP configuration"""
        # IMAP configuration
        self.imap_server = os.getenv('IMAP_SERVER', 'imap.gmail.com')
        self.imap_port = int(os.getenv('IMAP_PORT', '993'))
        self.imap_username = os.getenv('SMTP_USERNAME', '')  # Reuse SMTP username
        self.imap_password = os.getenv('SMTP_PASSWORD', '')  # Reuse SMTP password
        
        self.connection = None
    
    def connect(self) -> bool:
        """Connect to IMAP server"""
        try:
            print(f"Connecting to {self.imap_server}...")
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.connection.login(self.imap_username, self.imap_password)
            print(f"✅ Connected to {self.imap_server}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to IMAP server: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from IMAP server"""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
            except:
                pass
            self.connection = None
    
    def decode_mime_words(self, s):
        """Decode MIME encoded words in email headers"""
        decoded = decode_header(s)
        return ''.join(
            word.decode(encoding or 'utf-8') if isinstance(word, bytes) else word
            for word, encoding in decoded
        )
    
    def get_email_body(self, msg: Message) -> str:
        """Extract email body text"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                # Get text/plain or text/html
                if content_type == "text/plain" or content_type == "text/html":
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode()
            except:
                body = str(msg.get_payload())
        
        return body
    
    def parse_email_content(self, email_body: str, subject: str, from_email: str) -> Optional[Dict]:
        """
        Parse email content to extract account number, plate number, and email
        
        Supports multiple formats:
        1. Structured format:
           Account: 123456789
           Plate: ABC1234
           Email: user@example.com
        
        2. Single line format:
           Account: 123456789, Plate: ABC1234, Email: user@example.com
        
        3. Label-value pairs:
           account_number: 123456789
           plate_number: ABC1234
        
        4. JSON format:
           {"account_number": "123456789", "plate_number": "ABC1234"}
        
        Args:
            email_body: Email body text
            subject: Email subject
            from_email: Sender email address
            
        Returns:
            Dictionary with account_number, plate_number, and email, or None if not found
        """
        # Combine subject and body for parsing
        full_text = f"{subject}\n{email_body}".lower()
        
        # Extract email from sender (default to sender email)
        recipient_email = from_email
        
        # Filter out automated/noreply emails (common false positives)
        if from_email and ('noreply' in from_email.lower() or 
                          'no-reply' in from_email.lower() or
                          'automated' in from_email.lower() or
                          'donotreply' in from_email.lower()):
            # Still allow if explicitly contains valid account data, but be more strict
            pass  # Will validate more strictly below
        
        # Patterns to match account number (typically digits, minimum 3 characters)
        # Support formats like:
        # - "NY Toll Bill Account Number: 752918782"
        # - "Account Number: 752918782"
        # - "Account: 752918782"
        account_patterns = [
            r'ny\s*toll\s*bill\s*account\s*number\s*[:\-]?\s*([a-z0-9]{3,}(?:[\-]?[a-z0-9]+)*)',
            r'account\s*(?:number|#|num)?\s*[:\-]?\s*([a-z0-9]{3,}(?:[\-]?[a-z0-9]+)*)',
            r'account\s*[:]\s*([a-z0-9]{3,}(?:[\-]?[a-z0-9]+)*)',
            r'account[:]\s*([a-z0-9]{3,}(?:[\-]?[a-z0-9]+)*)',
            r'acc\s*[:]\s*([a-z0-9]{3,}(?:[\-]?[a-z0-9]+)*)',
            r'ny\s*account\s*[:\-]?\s*([a-z0-9]{3,}(?:[\-]?[a-z0-9]+)*)',
        ]
        
        # Patterns to match violation number (for NJ, typically starts with T or similar)
        violation_patterns = [
            r'violation\s*(?:number|#|num)?\s*[:\-]?\s*([a-z0-9]{8,}(?:[\-]?[a-z0-9]+)*)',
            r'violation\s*[:]\s*([a-z0-9]{8,}(?:[\-]?[a-z0-9]+)*)',
            r'nj\s*violation\s*[:\-]?\s*([a-z0-9]{8,}(?:[\-]?[a-z0-9]+)*)',
            r'invoice\s*(?:number|#)?\s*[:\-]?\s*([a-z0-9]{8,}(?:[\-]?[a-z0-9]+)*)',
        ]
        
        # Patterns to match plate number (typically alphanumeric, minimum 2 characters)
        # Support formats like:
        # - "Plate Number: AULAKH13"
        # - "Plate: AULAKH13"
        plate_patterns = [
            r'plate\s*(?:number|#|num)?\s*[:\-]?\s*([a-z0-9]{2,}(?:[\-]?[a-z0-9]+)*)',
            r'plate\s*[:]\s*([a-z0-9]{2,}(?:[\-]?[a-z0-9]+)*)',
            r'license\s*plate\s*[:\-]?\s*([a-z0-9]{2,}(?:[\-]?[a-z0-9]+)*)',
            r'plate[:]\s*([a-z0-9]{2,}(?:[\-]?[a-z0-9]+)*)',
        ]
        
        # Pattern to match email address
        email_pattern = r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
        
        account_number = None
        violation_number = None
        plate_number = None
        email_address = None
        source = 'NY'  # Default to NY
        
        # Try to extract account number (NY)
        for pattern in account_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                account_number = match.group(1).strip().upper()
                # Clean up common separators
                account_number = account_number.replace('-', '').replace(' ', '')
                break
        
        # Try to extract violation number (NJ)
        for pattern in violation_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                violation_number = match.group(1).strip().upper()
                # Clean up common separators
                violation_number = violation_number.replace('-', '').replace(' ', '')
                source = 'NJ'
                break
        
        # Try to extract plate number
        for pattern in plate_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                plate_number = match.group(1).strip().upper()
                # Clean up common separators but keep hyphens
                plate_number = plate_number.replace(' ', '')
                break
        
        # Try to extract email (look for explicit email field first)
        # Support multiple formats:
        # - "Email: user@example.com"
        # - "Email Address: user@example.com"
        # - "Email Address (for toll bill notifications): user@example.com"
        email_patterns = [
            r'email\s*address\s*\([^)]+\)\s*[:\-]?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # "Email Address (for toll bill notifications): ..."
            r'email\s*address\s*[:\-]?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # "Email Address: ..."
            r'email\s*[:\-]?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # "Email: ..."
        ]
        
        email_address = None
        for pattern in email_patterns:
            email_field_match = re.search(pattern, full_text, re.IGNORECASE)
            if email_field_match:
                email_address = email_field_match.group(1).strip().lower()
                break
        
        # If no email found, don't default to sender email - this causes all accounts to get the monitoring email
        # Only use sender email if it's NOT the monitoring email (myezpassdata@gmail.com)
        # This way accounts without explicit email won't get incorrectly merged
        if not email_address:
            if recipient_email and 'myezpassdata@gmail.com' not in recipient_email.lower():
                email_address = recipient_email.lower()
            else:
                # No email provided - leave as None to prevent incorrect merging
                email_address = None
        
        # If we found account/violation and plate, return the data
        # But validate they're not too short (likely false matches)
        has_account_data = False
        
        # Common false positive words to reject
        false_positives = {'AND', 'OR', 'THE', 'UUID', 'ID', 'NUMBER', 'ACCOUNT', 'PLATE', 'VIOLATION', 'EMAIL'}
        
        if account_number and plate_number:
            # Clean account number (remove non-alphanumeric except hyphens)
            account_number = re.sub(r'[^a-zA-Z0-9\-]', '', account_number).upper()
            # Clean plate number (remove non-alphanumeric except hyphens)
            plate_number = re.sub(r'[^a-zA-Z0-9\-]', '', plate_number).upper()
            
            # Reject common false positives
            if account_number in false_positives or plate_number in false_positives:
                return None
            
            # Validate minimum length and format
            account_clean = account_number.replace('-', '')
            plate_clean = plate_number.replace('-', '')
            
            # Account should be at least 6 characters (numeric or alphanumeric)
            # Plate should be at least 4 characters (alphanumeric)
            if (len(account_clean) >= 6 and len(plate_clean) >= 4 and
                not account_number.isalpha() and  # Account shouldn't be all letters
                plate_clean.isalnum()):  # Plate should be alphanumeric
                has_account_data = True
                source = 'NY'
        
        if violation_number and plate_number:
            # Clean violation number
            violation_number = re.sub(r'[^a-zA-Z0-9\-]', '', violation_number).upper()
            # Clean plate number
            plate_number = re.sub(r'[^a-zA-Z0-9\-]', '', plate_number).upper()
            
            # Reject common false positives
            if violation_number in false_positives or plate_number in false_positives:
                return None
            
            # Validate minimum length and format
            violation_clean = violation_number.replace('-', '')
            plate_clean = plate_number.replace('-', '')
            
            # Violation should be at least 8 characters, plate at least 4
            if len(violation_clean) >= 8 and len(plate_clean) >= 4 and plate_clean.isalnum():
                if has_account_data:
                    # Both NY and NJ found - return combined
                    return {
                        'account_number': account_number,
                        'violation_number': violation_number,
                        'nj_violation_number': violation_number,  # Also set nj_violation_number
                        'plate_number': plate_number,
                        'nj_plate_number': plate_number,
                        'email': email_address,
                        'sender_email': from_email,
                        'source': 'BOTH'
                    }
                else:
                    # Only NJ
                    return {
                        'violation_number': violation_number,
                        'nj_violation_number': violation_number,  # Also set nj_violation_number
                        'plate_number': plate_number,
                        'nj_plate_number': plate_number,
                        'email': email_address,
                        'sender_email': from_email,
                        'source': 'NJ'
                    }
        
        if has_account_data:
            return {
                'account_number': account_number,
                'plate_number': plate_number,
                'email': email_address,
                'sender_email': from_email,
                'source': 'NY'
            }
        
        # Try JSON format
        try:
            json_match = re.search(r'\{[^}]+\}', email_body, re.DOTALL)
            if json_match:
                import json
                json_data = json.loads(json_match.group(0))
                if 'account_number' in json_data and 'plate_number' in json_data:
                    return {
                        'account_number': str(json_data['account_number']).strip().upper(),
                        'plate_number': str(json_data['plate_number']).strip().upper(),
                        'email': json_data.get('email', from_email),
                        'sender_email': from_email
                    }
        except:
            pass
        
        return None
    
    def get_unread_emails(self, folder: str = 'INBOX', limit: int = 10) -> List[Dict]:
        """
        Get unread emails from specified folder
        
        Args:
            folder: IMAP folder name (default: INBOX)
            limit: Maximum number of emails to retrieve
            
        Returns:
            List of email dictionaries with parsed data
        """
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            # Select folder
            status, messages = self.connection.select(folder)
            if status != 'OK':
                print(f"❌ Failed to select folder {folder}")
                return []
            
            # Search for unread emails
            status, message_ids = self.connection.search(None, 'UNSEEN')
            if status != 'OK':
                print("❌ Failed to search for unread emails")
                return []
            
            email_ids = message_ids[0].split()
            
            # Limit the number of emails
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            emails = []
            
            for email_id in email_ids:
                try:
                    # Fetch email
                    status, msg_data = self.connection.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    # Parse email
                    email_body_bytes = msg_data[0][1]
                    msg = message_from_bytes(email_body_bytes)
                    
                    # Get email details
                    subject = self.decode_mime_words(msg["Subject"] or "")
                    from_email = self.decode_mime_words(msg["From"] or "")
                    
                    # Extract email address from "Name <email@example.com>" format
                    from_match = re.search(r'<([^>]+)>', from_email)
                    if from_match:
                        from_email = from_match.group(1)
                    else:
                        # If no brackets, extract email pattern
                        email_match = re.search(r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b', from_email)
                        if email_match:
                            from_email = email_match.group(1)
                    
                    # Get email body
                    body = self.get_email_body(msg)
                    
                    # Parse content
                    parsed_data = self.parse_email_content(body, subject, from_email)
                    
                    if parsed_data:
                        parsed_data['email_id'] = email_id.decode() if isinstance(email_id, bytes) else str(email_id)
                        parsed_data['subject'] = subject
                        parsed_data['body'] = body
                        emails.append(parsed_data)
                
                except Exception as e:
                    print(f"⚠️  Error processing email {email_id}: {str(e)}")
                    continue
            
            return emails
        
        except Exception as e:
            print(f"❌ Error fetching emails: {str(e)}")
            return []
    
    def mark_as_read(self, email_id: str, folder: str = 'INBOX'):
        """Mark email as read"""
        if not self.connection:
            return False
        
        try:
            self.connection.select(folder)
            self.connection.store(email_id, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            print(f"❌ Error marking email as read: {str(e)}")
            return False


def check_emails_and_extract() -> List[Dict]:
    """
    Convenience function to check emails and extract account/plate information
    
    Returns:
        List of parsed email data
    """
    reader = EmailReader()
    try:
        emails = reader.get_unread_emails()
        return emails
    finally:
        reader.disconnect()

