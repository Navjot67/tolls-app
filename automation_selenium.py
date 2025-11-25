"""
Web automation script using Selenium to extract toll balance and violations from E-ZPass NY website
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import json
from typing import Dict
import re


class EZPassAutomation:
    def __init__(self):
        self.account_number = None
        self.plate_number = None
        self.balance = None
        self.violations = []
        self.violation_count = 0
        self.driver = None

    def login_and_extract(self, account_number: str, plate_number: str, headless: bool = False) -> Dict:
        """
        Automate login and extract toll balance and violation information using Selenium
        
        Args:
            account_number: E-ZPass account number
            plate_number: License plate number
            headless: Whether to run browser in headless mode
            
        Returns:
            Dictionary containing balance, violations, and other extracted data
        """
        self.account_number = account_number
        self.plate_number = plate_number
        
        try:
            # Setup Chrome options
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            print("Launching Chrome browser...")
            # Use webdriver_manager to automatically handle ChromeDriver
            driver_path = ChromeDriverManager().install()
            # Ensure we're using the actual chromedriver executable
            import os
            if os.path.isdir(driver_path):
                # If path is a directory, find the chromedriver executable
                for root, dirs, files in os.walk(driver_path):
                    for file in files:
                        if file == 'chromedriver' and os.access(os.path.join(root, file), os.X_OK):
                            driver_path = os.path.join(root, file)
                            break
                    if driver_path != ChromeDriverManager().install():
                        break
            
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print(f"Browser launched (headless={headless})")
            
            # Step 1: Navigate to homepage first
            print("Navigating to E-ZPass NY homepage...")
            try:
                self.driver.get('https://www.e-zpassny.com')
                time.sleep(2)
                print(f"✓ Homepage loaded: {self.driver.current_url}")
            except Exception as e:
                print(f"Warning: Could not load homepage: {str(e)}")
            
            # Step 2: Navigate to pay toll page
            print("Navigating to Pay Toll page...")
            try:
                self.driver.get('https://www.e-zpassny.com/tbm/pay-toll')
                time.sleep(3)
                print(f"✓ Pay Toll page loaded: {self.driver.current_url}")
            except Exception as e:
                error_msg = str(e)
                if 'ERR_ABORTED' in error_msg or 'net::' in error_msg:
                    raise Exception(
                        "Unable to access E-ZPass NY website. The site appears to be blocking automated requests. "
                        "This is a common security measure. Error: " + error_msg
                    )
                raise Exception(f"Failed to load page: {error_msg}")
            
            # Step 3: Find and fill account number field
            print(f"Entering account number: {account_number}")
            account_input = None
            
            # Try multiple strategies to find the account number input field
            account_selectors = [
                # Try by heading text "Enter Account/Toll Bill/Violation Number"
                (By.XPATH, '//h2[contains(text(), "Enter Account") or contains(text(), "Account/Toll Bill")]/following::input[1]'),
                (By.XPATH, '//*[contains(text(), "Enter Account/Toll Bill/Violation Number")]/following::input[1]'),
                # Try by label text
                (By.XPATH, '//label[contains(text(), "Account") or contains(text(), "Toll Bill") or contains(text(), "Violation")]/following-sibling::input'),
                (By.XPATH, '//label[contains(text(), "Account") or contains(text(), "Toll Bill") or contains(text(), "Violation")]/../input'),
                (By.XPATH, '//input[preceding-sibling::label[contains(text(), "Account") or contains(text(), "Toll Bill") or contains(text(), "Violation")]]'),
                # Try by name/id attributes
                (By.NAME, "accountNumber"),
                (By.ID, "accountNumber"),
                (By.CSS_SELECTOR, 'input[name*="account" i]'),
                (By.CSS_SELECTOR, 'input[id*="account" i]'),
                (By.CSS_SELECTOR, 'input[placeholder*="account" i]'),
                (By.CSS_SELECTOR, 'input[placeholder*="Toll Bill" i]'),
                # Try by form structure - first text input
                (By.CSS_SELECTOR, 'input[type="text"]')
            ]
            
            for by, selector in account_selectors:
                try:
                    account_input = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    if account_input and account_input.is_displayed():
                        break
                except (TimeoutException, NoSuchElementException):
                    continue
            
            # Fallback: get first visible text input
            if not account_input:
                try:
                    text_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
                    for inp in text_inputs:
                        if inp.is_displayed():
                            account_input = inp
                            break
                except:
                    pass
            
            if not account_input:
                # Take screenshot for debugging
                self.driver.save_screenshot('debug_account_input.png')
                raise Exception("Could not find Account/Toll Bill/Violation Number input field")
            
            # Enter account number
            account_input.clear()
            account_input.send_keys(account_number)
            print(f"✓ Entered account number: {account_number}")
            time.sleep(0.5)
            
            # Step 4: Press Tab to move to plate number field, then enter plate number
            print(f"Pressing Tab to move to plate number field...")
            account_input.send_keys(Keys.TAB)
            time.sleep(0.5)
            
            # Get the currently focused element (should be the plate number field after Tab)
            plate_input = self.driver.switch_to.active_element
            
            # Verify it's an input field
            if plate_input.tag_name.lower() != 'input':
                # If Tab didn't work, try to find plate field explicitly
                print("Tab didn't move to input field, trying to find plate field...")
                plate_selectors = [
                    (By.XPATH, '//label[contains(text(), "License Plate") or contains(text(), "Tag")]/following-sibling::input'),
                    (By.XPATH, '//label[contains(text(), "License Plate") or contains(text(), "Tag")]/../input'),
                    (By.NAME, "plateNumber"),
                    (By.ID, "plateNumber"),
                    (By.CSS_SELECTOR, 'input[name*="plate" i]')
                ]
                
                for by, selector in plate_selectors:
                    try:
                        plate_input = WebDriverWait(self.driver, 2).until(
                            EC.presence_of_element_located((by, selector))
                        )
                        if plate_input and plate_input.is_displayed():
                            break
                    except TimeoutException:
                        continue
                
                # Fallback: get second visible text input
                if plate_input.tag_name.lower() != 'input':
                    try:
                        text_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
                        visible_inputs = [inp for inp in text_inputs if inp.is_displayed()]
                        if len(visible_inputs) >= 2:
                            plate_input = visible_inputs[1]
                    except:
                        pass
            
            if not plate_input or plate_input.tag_name.lower() != 'input':
                self.driver.save_screenshot('debug_plate_input.png')
                raise Exception("Could not find plate number input field")
            
            # Enter plate number
            plate_input.clear()
            plate_input.send_keys(plate_number)
            print(f"✓ Entered plate number: {plate_number}")
            time.sleep(0.5)
            
            # Step 5: Submit form
            # Based on the form: "SEARCH" button
            print("Submitting form...")
            submit_button = None
            submit_selectors = [
                # Try by button text (most reliable for "SEARCH" button)
                (By.XPATH, '//button[contains(text(), "SEARCH") or contains(text(), "Search")]'),
                (By.XPATH, '//input[@type="submit" and (contains(@value, "SEARCH") or contains(@value, "Search"))]'),
                (By.XPATH, '//button[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "search")]'),
                # Try by type
                (By.CSS_SELECTOR, 'button[type="submit"]'),
                (By.CSS_SELECTOR, 'input[type="submit"]'),
                # Try by common button text
                (By.XPATH, '//button[contains(text(), "Submit")]'),
                (By.XPATH, '//button[contains(text(), "Login")]'),
                (By.XPATH, '//button[contains(text(), "Continue")]'),
                # Try by CSS classes
                (By.CSS_SELECTOR, '.btn-primary'),
                (By.CSS_SELECTOR, '.btn-submit'),
                (By.CSS_SELECTOR, 'button.btn')
            ]
            
            for by, selector in submit_selectors:
                try:
                    submit_button = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    if submit_button and submit_button.is_displayed():
                        break
                except TimeoutException:
                    continue
            
            if submit_button:
                submit_button.click()
                print("✓ Form submitted (SEARCH button clicked)")
            else:
                # Try pressing Enter on plate input as fallback
                plate_input.send_keys(Keys.RETURN)
                print("✓ Pressed Enter to submit")
            
            # Wait for page to load data (give ample time for results to render)
            post_submit_wait = 15
            print(f"Waiting {post_submit_wait} seconds for results to load...")
            time.sleep(post_submit_wait)
            
            # Step 6: Extract all financial information from the page
            print("Extracting financial information...")
            
            # Get all text from the page
            page_text = ""
            all_dollar_amounts = []
            violations = []
            violation_count = 0
            toll_entries = []
            
            try:
                page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            except:
                pass
            
            # Find all dollar amounts on the page
            dollar_pattern = r'\$[\s]*([\d,]+\.?\d*)'
            all_matches = re.findall(dollar_pattern, page_text)
            for match in all_matches:
                try:
                    amount = float(match.replace(',', ''))
                    all_dollar_amounts.append(amount)
                except:
                    pass
            
            # Extract from tables - more comprehensive
            try:
                tables = self.driver.find_elements(By.TAG_NAME, 'table')
                for table in tables:
                    rows = table.find_elements(By.TAG_NAME, 'tr')
                    for row in rows:
                        row_text = row.text.strip()
                        row_lower = row_text.lower()
                        
                        if not row_text:
                            continue
                        
                        # Look for balance/total amounts
                        if '$' in row_text and ('balance' in row_lower or 'total' in row_lower or 'due' in row_lower or 'amount due' in row_lower):
                            # Extract amount
                            matches = re.findall(dollar_pattern, row_text)
                            if matches:
                                try:
                                    amount = float(matches[0].replace(',', ''))
                                    all_dollar_amounts.append(amount)
                                except:
                                    pass
                        
                        # Look for toll charges
                        if '$' in row_text and ('toll' in row_lower or 'charge' in row_lower or 'invoice' in row_lower or 'fee' in row_lower):
                            toll_entries.append(row_text)
                            matches = re.findall(dollar_pattern, row_text)
                            for match in matches:
                                try:
                                    amount = float(match.replace(',', ''))
                                    all_dollar_amounts.append(amount)
                                except:
                                    pass
                        
                        # Look for violations
                        if 'violation' in row_lower:
                            violations.append(row_text)
                            # Try to extract violation number
                            violation_num_match = re.search(r'violation[s]?\s*#?\s*:?\s*(\d+)', row_lower)
                            if violation_num_match:
                                violation_count = max(violation_count, int(violation_num_match.group(1)))
            except Exception as e:
                print(f"Error extracting from tables: {str(e)}")
            
            # Look for violation count in page text
            if 'violation' in page_text.lower():
                violation_patterns = [
                    r'violation[s]?\s*:?\s*(\d+)',
                    r'(\d+)\s*violation[s]?',
                    r'violation\s*count[:\s]*(\d+)',
                    r'total\s*violation[s]?\s*:?\s*(\d+)'
                ]
                for pattern in violation_patterns:
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        violation_count = max(violation_count, int(match.group(1)))
            
            # Calculate total balance due - look for specific "due" or "total" amounts first
            total_balance_due = 0.0
            balance_amount = 0.0
            toll_charges_total = 0.0
            
            # First, look for explicit "Total Due", "Amount Due", "Balance Due" text
            due_patterns = [
                r'total\s+(?:amount\s+)?due[:\s]*\$?\s*([\d,]+\.?\d*)',
                r'amount\s+due[:\s]*\$?\s*([\d,]+\.?\d*)',
                r'balance\s+due[:\s]*\$?\s*([\d,]+\.?\d*)',
                r'total\s+balance[:\s]*\$?\s*([\d,]+\.?\d*)',
                r'outstanding\s+balance[:\s]*\$?\s*([\d,]+\.?\d*)'
            ]
            
            for pattern in due_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    try:
                        total_balance_due = float(match.group(1).replace(',', ''))
                        print(f"Found explicit balance due: ${total_balance_due:.2f}")
                        break
                    except:
                        pass
            
            # Extract toll bill numbers and sum toll charges
            toll_bill_numbers = []
            for entry in toll_entries:
                # Extract bill numbers from toll entries
                # Look for patterns like "Bill #12345", "Invoice: ABC123", "Toll Bill: 123456", etc.
                bill_patterns = [
                    r'(?:bill|invoice|toll\s*bill)[\s#:]*([A-Z0-9-]+)',
                    r'\b([A-Z]{2,}\d{4,}|\d{6,})\b',  # Alphanumeric codes or long numbers
                    r'bill\s*(?:number|#)?\s*:?\s*([A-Z0-9-]+)',
                ]
                
                for pattern in bill_patterns:
                    bill_match = re.search(pattern, entry, re.IGNORECASE)
                    if bill_match and bill_match.group(1):
                        bill_num = bill_match.group(1).strip()
                        if bill_num not in toll_bill_numbers:
                            toll_bill_numbers.append(bill_num)
                        break
                
                # Sum toll charges
                matches = re.findall(dollar_pattern, entry)
                for match in matches:
                    try:
                        amount = float(match.replace(',', ''))
                        toll_charges_total += amount
                    except:
                        pass
            
            # If no explicit "due" found, calculate from components
            if total_balance_due == 0:
                # Look for account balance separately
                balance_patterns = [
                    r'account\s+balance[:\s]*\$?\s*([\d,]+\.?\d*)',
                    r'balance[:\s]*\$?\s*([\d,]+\.?\d*)',
                ]
                
                for pattern in balance_patterns:
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        try:
                            balance_amount = float(match.group(1).replace(',', ''))
                            print(f"Found account balance: ${balance_amount:.2f}")
                            break
                        except:
                            pass
                
                # If still no balance found, use the largest amount found
                if balance_amount == 0 and all_dollar_amounts:
                    # Filter out very small amounts (likely not the balance)
                    significant_amounts = [a for a in all_dollar_amounts if a > 1.0]
                    if significant_amounts:
                        balance_amount = max(significant_amounts)
                        print(f"Using largest amount found as balance: ${balance_amount:.2f}")
                
                # Use balance_amount as total_balance_due
                # Don't add toll_charges_total because it's likely already included in balance_amount
                # The toll_charges_total is extracted from individual entries, which may duplicate the balance
                total_balance_due = balance_amount
                if toll_charges_total > 0 and toll_charges_total != balance_amount:
                    # Only add if they're different (toll_charges might be separate pending charges)
                    # But if they're the same, it's likely the same amount being counted twice
                    print(f"⚠️  Note: balance_amount (${balance_amount:.2f}) and toll_charges_total (${toll_charges_total:.2f}) are different")
                    # Use the larger of the two, as toll_charges might be additional pending charges
                    total_balance_due = max(balance_amount, toll_charges_total)
                else:
                    print(f"ℹ️  Using balance_amount (${balance_amount:.2f}) as total_balance_due (toll_charges likely included)")
            else:
                # If we found explicit total_balance_due, check for separate account balance
                # Account balance is more reliable than "Total Balance Due" which might include pending charges
                balance_patterns = [
                    r'account\s+balance[:\s]*\$?\s*([\d,]+\.?\d*)',
                ]
                
                for pattern in balance_patterns:
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        try:
                            account_balance = float(match.group(1).replace(',', ''))
                            print(f"Found account balance: ${account_balance:.2f}")
                            # Prioritize account balance if it's reasonable (not 0 and not way larger than total_balance_due)
                            # Account balance is usually the actual balance due
                            if account_balance > 0 and account_balance <= total_balance_due * 1.5:
                                balance_amount = account_balance
                                print(f"✅ Using account balance (${account_balance:.2f}) as it's more reliable than total_balance_due (${total_balance_due:.2f})")
                            else:
                                # Account balance seems wrong, use total_balance_due
                                balance_amount = total_balance_due
                                print(f"⚠️  Account balance (${account_balance:.2f}) seems incorrect, using total_balance_due (${total_balance_due:.2f})")
                            break
                        except:
                            pass
                
                # If balance_amount not found separately, use total_balance_due
                if balance_amount == 0:
                    # If we have total_balance_due, use it as balance_amount
                    balance_amount = total_balance_due
                    print(f"Using total_balance_due as balance_amount: ${balance_amount:.2f}")
            
            # If no amounts found, try to find any text with "balance" or "due"
            if total_balance_due == 0:
                try:
                    # Look for balance/due text elements
                    balance_elements = self.driver.find_elements(By.XPATH, '//*[contains(text(), "Balance") or contains(text(), "Due") or contains(text(), "$")]')
                    for elem in balance_elements:
                        text = elem.text
                        if '$' in text:
                            matches = re.findall(dollar_pattern, text)
                            for match in matches:
                                try:
                                    amount = float(match.replace(',', ''))
                                    if amount > total_balance_due:
                                        total_balance_due = amount
                                except:
                                    pass
                except:
                    pass
            
            # Take screenshot
            self.driver.save_screenshot('debug_after_login.png')
            
            # Determine final balance
            # Priority: explicit total_balance_due > balance_amount > largest amount on page
            if total_balance_due > 0:
                # If we found explicit total_balance_due, use it
                # But if balance_amount is different and smaller, it might be the actual account balance
                # Check if they're close (within 10%) - if so, use the explicit total_balance_due
                if balance_amount > 0:
                    diff_percent = abs(total_balance_due - balance_amount) / max(total_balance_due, balance_amount) * 100
                    if diff_percent < 10:  # Within 10% of each other
                        # They're likely the same amount, use the explicit total_balance_due
                        final_balance = total_balance_due
                        print(f"ℹ️  Using explicit total_balance_due (${total_balance_due:.2f}) - balance_amount (${balance_amount:.2f}) is similar")
                    else:
                        # They're different - use the explicit total_balance_due (it's the "total due")
                        final_balance = total_balance_due
                        print(f"ℹ️  Using explicit total_balance_due (${total_balance_due:.2f}) - differs from balance_amount (${balance_amount:.2f})")
                else:
                    final_balance = total_balance_due
            elif balance_amount > 0:
                final_balance = balance_amount
            else:
                # Last resort: try to find any large amount on the page
                if all_dollar_amounts:
                    significant_amounts = [a for a in all_dollar_amounts if a > 10.0]  # Filter small amounts
                    if significant_amounts:
                        final_balance = max(significant_amounts)
                        print(f"Using largest significant amount found: ${final_balance:.2f}")
                    else:
                        final_balance = 0.0
                else:
                    final_balance = 0.0
            
            # Format results clearly
            result = {
                'success': True,
                'account_number': account_number,
                'plate_number': plate_number,
                'total_balance_due': round(total_balance_due, 2),
                'balance_amount': round(final_balance, 2),  # Use the larger of total_balance_due or balance_amount
                'ny_balance_amount': round(final_balance, 2),  # Set NY balance explicitly
                'nj_balance_amount': 0.0,  # No NJ balance for NY accounts
                'toll_charges_total': round(toll_charges_total, 2),
                'toll_bill_numbers': toll_bill_numbers,  # List of toll bill numbers
                'violation_count': violation_count,
                'violations': violations[:10] if violations else [],  # Limit to 10 most recent
                'toll_entries': toll_entries[:10] if toll_entries else [],  # Limit to 10
                'sources': ['NY'],
                'source': 'NY',
                'page_title': self.driver.title,
                'url': self.driver.current_url,
                'raw_page_text': page_text[:500] if page_text else ""  # First 500 chars for debugging
            }
            
            print(f"\n{'='*60}")
            print(f"EXTRACTION COMPLETE")
            print(f"{'='*60}")
            print(f"Total Balance Due: ${total_balance_due:.2f}")
            print(f"Account Balance: ${balance_amount:.2f}")
            print(f"Final Balance: ${final_balance:.2f}")
            print(f"Toll Charges: ${toll_charges_total:.2f}")
            print(f"Toll Bill Numbers: {', '.join(toll_bill_numbers) if toll_bill_numbers else 'None found'}")
            print(f"Violations: {violation_count}")
            print(f"{'='*60}\n")
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error during automation: {error_msg}")
            
            # Take screenshot if driver is still available
            try:
                if self.driver:
                    self.driver.save_screenshot('error_screenshot.png')
            except:
                pass
            
            return {
                'success': False,
                'error': error_msg,
                'account_number': account_number,
                'plate_number': plate_number
            }
        finally:
            # Clean up
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass


def extract_toll_info(account_number: str, plate_number: str, headless: bool = False) -> Dict:
    """
    Convenience function to extract toll information using Selenium
    
    Args:
        account_number: E-ZPass account number
        plate_number: License plate number
        headless: Whether to run browser in headless mode
        
    Returns:
        Dictionary with extracted information
    """
    automation = EZPassAutomation()
    return automation.login_and_extract(account_number, plate_number, headless)


if __name__ == '__main__':
    # Example usage
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python automation_selenium.py <account_number> <plate_number> [headless]")
        print("Example: python automation_selenium.py 123456 ABC123 false")
        sys.exit(1)
    
    account = sys.argv[1]
    plate = sys.argv[2]
    headless_mode = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else False
    
    result = extract_toll_info(account, plate, headless_mode)
    print(json.dumps(result, indent=2))

