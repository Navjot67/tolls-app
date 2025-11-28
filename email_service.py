"""
Email service for sending toll information to users
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from jinja2 import Template
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def send_toll_info_email(recipient_email, toll_data, logger=None):
    """
    Send toll information via email with beautiful HTML template
    
    Args:
        recipient_email: Email address to send to
        toll_data: Dictionary containing toll information
        logger: Optional logger function to use instead of print()
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Use logger if provided, otherwise use print
    log = logger if logger else print
    
    try:
        # Email configuration (using Gmail SMTP as default)
        # You can change these or use environment variables
        SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
        SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
        SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
        
        # If credentials not set, return False
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            log("⚠️  Email credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD environment variables.")
            return False
        
        # Read email template
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'email_template.html')
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Create template and render
        template = Template(template_content)
        
        # Prepare data for template
        # Get balance amounts
        balance_due_raw = toll_data.get('balance_amount', 0)
        ny_balance_raw = toll_data.get('ny_balance_amount', 0)
        nj_balance_raw = toll_data.get('nj_balance_amount', 0)
        bill_numbers = toll_data.get('toll_bill_numbers', [])
        violation_count = toll_data.get('violation_count', 0)
        sources = toll_data.get('sources', [])
        has_ny = 'NY' in sources or toll_data.get('account_number')
        has_nj = 'NJ' in sources or toll_data.get('violation_number') or toll_data.get('nj_violation_number')
        
        # Format balances (handle None values)
        try:
            balance_due_raw = float(balance_due_raw) if balance_due_raw is not None else 0.0
        except (ValueError, TypeError):
            balance_due_raw = 0.0
        
        try:
            ny_balance_raw = float(ny_balance_raw) if ny_balance_raw is not None else 0.0
        except (ValueError, TypeError):
            ny_balance_raw = 0.0
        
        try:
            nj_balance_raw = float(nj_balance_raw) if nj_balance_raw is not None else 0.0
        except (ValueError, TypeError):
            nj_balance_raw = 0.0
        
        # If NY balance is 0 but balance_amount has value and it's a NY-only account, use balance_amount
        if ny_balance_raw == 0 and balance_due_raw > 0:
            if has_ny and not has_nj:
                # NY-only account, use balance_amount as ny_balance
                ny_balance_raw = balance_due_raw
                log(f"Using balance_amount (${balance_due_raw:.2f}) as ny_balance_amount for NY-only account")
        
        balance_due = f"{balance_due_raw:.2f}"
        ny_balance = ny_balance_raw
        nj_balance = nj_balance_raw
        
        ny_balance_due = f"{ny_balance:.2f}"
        nj_balance_due = f"{nj_balance:.2f}"
        
        html_content = template.render(
            account_number=toll_data.get('account_number', 'N/A'),
            plate_number=toll_data.get('plate_number', 'N/A'),
            violation_number=toll_data.get('violation_number') or toll_data.get('nj_violation_number', 'N/A'),
            nj_plate_number=toll_data.get('nj_plate_number', toll_data.get('plate_number', 'N/A')),
            date=datetime.now().strftime('%B %d, %Y at %I:%M %p'),
            balance_due=balance_due,
            ny_balance_due=ny_balance_due,
            nj_balance_due=nj_balance_due,
            bill_numbers=bill_numbers,
            violation_count=violation_count,
            has_ny=has_ny,
            has_nj=has_nj,
            sources=sources
        )
        
        # Create message with updated subject
        subject_balance = f"${balance_due}"
        if has_ny and has_nj:
            subject = f"E-ZPass Toll Information - NY: ${ny_balance_due} | NJ: ${nj_balance_due} | Total: {subject_balance}"
        elif has_nj:
            subject = f"E-ZPass NJ Toll Information - Balance Due: {subject_balance}"
        else:
            subject = f"E-ZPass NY Toll Information - Balance Due: {subject_balance}"
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_USERNAME
        msg['To'] = recipient_email
        
        # Create plain text version
        text_parts = ["E-ZPass Toll Information\n"]
        
        if has_ny:
            text_parts.append(f"NY Account Number: {toll_data.get('account_number', 'N/A')}")
            text_parts.append(f"NY Plate Number: {toll_data.get('plate_number', 'N/A')}")
            text_parts.append(f"NY Balance: ${ny_balance_due}\n")
        
        if has_nj:
            text_parts.append(f"NJ Violation Number: {toll_data.get('violation_number') or toll_data.get('nj_violation_number', 'N/A')}")
            text_parts.append(f"NJ Plate Number: {toll_data.get('nj_plate_number', toll_data.get('plate_number', 'N/A'))}")
            text_parts.append(f"NJ Balance: ${nj_balance_due}\n")
        
        text_parts.extend([
            f"Total Balance Due: ${balance_due}",
            f"Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            f"\nBill Numbers: {', '.join(bill_numbers) if bill_numbers else 'None'}",
            f"Violations: {violation_count}"
        ])
        
        text_content = "\n".join(text_parts)
        
        # Attach both versions
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        try:
            # Use SSL for port 465, STARTTLS for port 587
            if SMTP_PORT == 465:
                # Use SMTP_SSL for port 465
                server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30)
            else:
                # Use regular SMTP with STARTTLS for port 587
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
                server.starttls()
            
            try:
                try:
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                except smtplib.SMTPAuthenticationError as auth_error:
                    error_msg = str(auth_error)
                    log(f"❌ Authentication failed: {error_msg}")
                    if "BadCredentials" in error_msg or "Username and Password not accepted" in error_msg:
                        log("\n💡 Common fixes for Gmail:")
                        log("   1. Make sure you're using an App Password (not your regular password)")
                        log("   2. Generate App Password at: https://myaccount.google.com/apppasswords")
                        log("   3. Enable 2-Step Verification first if you haven't")
                        log("   4. Make sure SMTP_USERNAME is your full email address")
                    return False
                except Exception as login_error:
                    log(f"❌ Login error: {str(login_error)}")
                    import traceback
                    error_trace = traceback.format_exc()
                    log(error_trace)
                    return False
                
                server.send_message(msg)
                log(f"✅ Email sent successfully to {recipient_email}")
                
                # Close connection
                if SMTP_PORT != 465:
                    server.quit()
                else:
                    server.close()
                return True
            except Exception as inner_error:
                if server:
                    if SMTP_PORT != 465:
                        server.quit()
                    else:
                        server.close()
                raise inner_error
        except smtplib.SMTPException as smtp_error:
            error_msg = f"❌ SMTP error sending email: {str(smtp_error)}"
            log(error_msg)
            import traceback
            error_trace = traceback.format_exc()
            log(error_trace)
            return False
    except Exception as e:
        error_msg = f"❌ Error sending email: {str(e)}\n   Error type: {type(e).__name__}"
        log(error_msg)
        import traceback
        error_trace = traceback.format_exc()
        log(error_trace)
        return False

