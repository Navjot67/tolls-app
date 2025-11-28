"""
Web automation script using Selenium to extract toll balance and violations from E-ZPass NJ website
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


class EZPassNJAutomation:
    def __init__(self):
        self.account_number = None
        self.plate_number = None
        self.violation_number = None
        self.balance = None
        self.violations = []
        self.violation_count = 0
        self.driver = None

    def login_and_extract(self, account_number: str = None, plate_number: str = None, 
                         violation_number: str = None, headless: bool = False) -> Dict:
        """
        Automate login and extract toll balance and violation information using Selenium
        
        Args:
            account_number: E-ZPass account number (optional)
            plate_number: License plate number (required)
            violation_number: Violation/Invoice number (optional, for violation lookup)
            headless: Whether to run browser in headless mode
            
        Returns:
            Dictionary containing balance, violations, and other extracted data
        """
        self.account_number = account_number
        self.plate_number = plate_number
        self.violation_number = violation_number
        
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
            import os
            driver_path = ChromeDriverManager().install()
            
            # ChromeDriverManager sometimes returns the wrong file (e.g., THIRD_PARTY_NOTICES.chromedriver)
            # We need to find the actual chromedriver executable
            original_path = driver_path
            valid_driver_found = False
            
            # Check if the returned path is actually the chromedriver executable
            if os.path.isfile(driver_path):
                file_size = os.path.getsize(driver_path)
                # Real chromedriver binary should be > 10MB (typically ~15MB)
                # Text files like THIRD_PARTY_NOTICES.chromedriver are < 1MB
                if file_size >= 10000000:  # >= 10MB - this looks like the real executable
                    valid_driver_found = True
                    print(f"✅ ChromeDriverManager returned valid executable: {driver_path} ({file_size / 1024 / 1024:.1f}MB)")
                else:
                    # Too small - likely wrong file
                    print(f"⚠️  ChromeDriverManager returned suspicious file: {driver_path} ({file_size / 1024 / 1024:.1f}MB)")
            
            # If we don't have a valid driver_path yet, search for it
            if not valid_driver_found:
                # Search directory (either the directory itself or parent of the wrong file)
                if os.path.isdir(original_path):
                    search_dir = original_path
                elif os.path.isfile(original_path):
                    search_dir = os.path.dirname(original_path)
                else:
                    # Fallback: search common locations
                    search_dir = os.path.dirname(os.path.dirname(original_path)) if os.path.dirname(original_path) else "/Users/ghuman/.wdm/drivers/chromedriver"
                
                print(f"🔍 Searching for chromedriver executable in: {search_dir}")
                chromedriver_found = False
                
                for root, dirs, files in os.walk(search_dir):
                    for file in files:
                        # Match EXACT filename 'chromedriver' (case-sensitive)
                        # Ignore files like 'THIRD_PARTY_NOTICES.chromedriver'
                        if file == 'chromedriver':
                            candidate_path = os.path.join(root, file)
                            # Verify it's executable and has reasonable size
                            if os.path.isfile(candidate_path) and os.access(candidate_path, os.X_OK):
                                file_size = os.path.getsize(candidate_path)
                                # Real chromedriver binary should be > 10MB (typically ~15MB)
                                if file_size >= 10000000:  # >= 10MB
                                    driver_path = candidate_path
                                    chromedriver_found = True
                                    valid_driver_found = True
                                    print(f"✅ Found chromedriver executable: {driver_path} ({file_size / 1024 / 1024:.1f}MB)")
                                    break
                    if chromedriver_found:
                        break
                
                if not chromedriver_found:
                    raise Exception(f"Could not find valid chromedriver executable in: {search_dir}")
            
            # Final validation
            if not os.path.isfile(driver_path):
                raise Exception(f"ChromeDriver executable not found at: {driver_path}")
            
            if not os.access(driver_path, os.X_OK):
                raise Exception(f"ChromeDriver is not executable: {driver_path}")
            
            # Verify it's a real binary (should be > 10MB)
            file_size = os.path.getsize(driver_path)
            if file_size < 10000000:  # Less than 10MB is suspicious
                raise Exception(f"ChromeDriver file seems too small ({file_size} bytes) - might be a text file, not binary: {driver_path}")
            
            print(f"🚀 Using ChromeDriver: {driver_path} ({file_size / 1024 / 1024:.1f}MB)")
            
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print(f"Browser launched (headless={headless})")
            
            # Navigate to E-ZPass NJ homepage
            print("Navigating to E-ZPass NJ homepage...")
            try:
                self.driver.get('https://www.ezpassnj.com/en/home/index.shtml')
                time.sleep(2)
                print("✓ Homepage loaded: https://www.ezpassnj.com/en/home/index.shtml")
            except Exception as e:
                print(f"⚠️  Error loading homepage: {str(e)}")
                return self._create_error_result("Failed to load E-ZPass NJ website")
            
            # Check if we have violation number or account number
            if violation_number and plate_number:
                return self._fetch_violation_info(violation_number, plate_number)
            elif account_number and plate_number:
                return self._fetch_account_info(account_number, plate_number)
            else:
                return self._create_error_result("Either violation number + plate OR account number + plate is required")
        
        except Exception as e:
            print(f"Error during automation: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._create_error_result(str(e))
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass

    def _fetch_violation_info(self, violation_number: str, plate_number: str) -> Dict:
        """Fetch violation/invoice information"""
        try:
            print("Looking for Invoice/Violation payment section...")
            
            # Look for the violation/invoice payment link or modal
            print("Searching for Invoice/Violation payment option...")
            try:
                # Try to find and click "Invoice / Violations / Toll-by-Plate" link
                violation_link = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "Invoice / Violations / Toll-by-Plate"))
                )
                self.driver.execute_script("arguments[0].click();", violation_link)
                print("✓ Clicked Invoice/Violation link")
                time.sleep(3)
            except:
                # Try alternative selectors
                try:
                    violation_link = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Invoice"))
                    )
                    self.driver.execute_script("arguments[0].click();", violation_link)
                    print("✓ Clicked Invoice link (alternative)")
                    time.sleep(3)
                except:
                    # Try finding by text content
                    try:
                        all_links = self.driver.find_elements(By.TAG_NAME, 'a')
                        for link in all_links:
                            link_text = link.text.lower()
                            if 'invoice' in link_text or 'violation' in link_text:
                                self.driver.execute_script("arguments[0].click();", link)
                                print("✓ Clicked Invoice link (by text)")
                                time.sleep(3)
                                break
                    except Exception as e:
                        print(f"⚠️  Could not find violation link: {str(e)}")
            
            # Wait for modal/form to appear
            print("Waiting for violation form to appear...")
            time.sleep(8)  # Give more time for modal to load
            
            # Check for iframes
            try:
                iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
                if iframes:
                    print(f"Found {len(iframes)} iframe(s), switching to first one...")
                    self.driver.switch_to.frame(iframes[0])
                    time.sleep(2)
            except Exception as e:
                print(f"No iframe found or error switching: {str(e)}")
            
            # Find the violation/invoice input fields
            print("Entering violation number and plate number...")
            
            # Look for violation/invoice number input
            violation_input = None
            plate_input = None
            
            # Try multiple selectors for the inputs
            print("Trying to find input fields...")
            input_selectors = [
                ('input[name="notice_number"]', 'input[name="tag_number"]'),
                ('input[name*="notice"]', 'input[name*="tag"]'),
                ('input[id*="notice"]', 'input[id*="tag"]'),
                ('input[id*="invoice"]', 'input[id*="plate"]'),
                ('input[placeholder*="Invoice"]', 'input[placeholder*="Plate"]'),
                ('input[type="text"]', None),  # Will find both by position
            ]
            
            for notice_sel, tag_sel in input_selectors:
                try:
                    if tag_sel:
                        violation_input = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, notice_sel))
                        )
                        plate_input = self.driver.find_element(By.CSS_SELECTOR, tag_sel)
                        if violation_input and plate_input:
                            print(f"✓ Found inputs using selector: {notice_sel}")
                            break
                    else:
                        # Find all text inputs and use by position
                        all_text_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
                        if len(all_text_inputs) >= 2:
                            violation_input = all_text_inputs[0]
                            plate_input = all_text_inputs[1]
                            print("✓ Found inputs by position (first two text inputs)")
                            break
                except Exception as e:
                    continue
            
            # Alternative: find by scanning all visible inputs
            if not violation_input or not plate_input:
                print("Scanning all inputs to find fields...")
                try:
                    # Wait a bit more for modal to fully load
                    time.sleep(2)
                    # Find all input fields
                    all_inputs = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.TAG_NAME, 'input'))
                    )
                    print(f"Found {len(all_inputs)} input fields total")
                    
                    text_inputs = []
                    for inp in all_inputs:
                        try:
                            if not inp.is_displayed():
                                continue
                            inp_type = inp.get_attribute('type')
                            if inp_type not in ['text', 'tel', None, '']:
                                continue
                            inp_id = (inp.get_attribute('id') or '').lower()
                            inp_name = (inp.get_attribute('name') or '').lower()
                            inp_placeholder = (inp.get_attribute('placeholder') or '').lower()
                            inp_class = (inp.get_attribute('class') or '').lower()
                            
                            combined = inp_id + ' ' + inp_name + ' ' + inp_placeholder + ' ' + inp_class
                            
                            print(f"  Input found: id='{inp_id}', name='{inp_name}', type='{inp_type}'")
                            
                            if 'notice' in combined or 'invoice' in combined or 'violation' in combined or 'number' in combined:
                                if not violation_input:
                                    violation_input = inp
                                    print(f"  → Selected as violation input: {combined}")
                            if 'tag' in combined or 'plate' in combined or 'license' in combined:
                                if not plate_input:
                                    plate_input = inp
                                    print(f"  → Selected as plate input: {combined}")
                            
                            text_inputs.append(inp)
                        except Exception as e:
                            continue
                    
                    # If we still don't have both, use first two text inputs
                    if not violation_input or not plate_input:
                        if len(text_inputs) >= 2:
                            if not violation_input:
                                violation_input = text_inputs[0]
                                print(f"  → Using first text input as violation field")
                            if not plate_input:
                                plate_input = text_inputs[1]
                                print(f"  → Using second text input as plate field")
                except Exception as e:
                    print(f"Error finding inputs: {str(e)}")
            
            if violation_input and plate_input:
                # Make inputs visible and interactable
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", violation_input)
                    time.sleep(1)
                    # Make sure inputs are enabled
                    self.driver.execute_script("arguments[0].removeAttribute('readonly');", violation_input)
                    self.driver.execute_script("arguments[0].removeAttribute('disabled');", violation_input)
                except:
                    pass
                
                # Enter violation number using JavaScript first (more reliable)
                try:
                    print(f"Attempting to enter violation number: {violation_number}")
                    # Click to focus
                    violation_input.click()
                    time.sleep(0.5)
                    # Clear using JavaScript
                    self.driver.execute_script("arguments[0].value = '';", violation_input)
                    time.sleep(0.3)
                    # Set value using JavaScript
                    self.driver.execute_script(f"arguments[0].value = '{violation_number}';", violation_input)
                    time.sleep(0.3)
                    # Also try typing (in case there are event handlers)
                    violation_input.clear()
                    violation_input.send_keys(violation_number)
                    time.sleep(0.5)
                    
                    # Verify it was entered
                    entered_value = violation_input.get_attribute('value')
                    if entered_value:
                        print(f"✓ Entered violation number: {entered_value}")
                    else:
                        print(f"⚠️  Violation number may not have been entered. Trying alternative method...")
                        # Try alternative: select all and type
                        violation_input.send_keys(Keys.CONTROL + 'a')
                        violation_input.send_keys(violation_number)
                        time.sleep(0.5)
                        entered_value = violation_input.get_attribute('value')
                        print(f"✓ Entered violation number (retry): {entered_value or 'unknown'}")
                except Exception as e:
                    print(f"Error entering violation number: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
                # Enter plate number
                try:
                    print(f"Attempting to enter plate number: {plate_number}")
                    # Click to focus
                    plate_input.click()
                    time.sleep(0.5)
                    # Clear using JavaScript
                    self.driver.execute_script("arguments[0].value = '';", plate_input)
                    time.sleep(0.3)
                    # Set value using JavaScript
                    self.driver.execute_script(f"arguments[0].value = '{plate_number}';", plate_input)
                    time.sleep(0.3)
                    # Also try typing
                    plate_input.clear()
                    plate_input.send_keys(plate_number)
                    time.sleep(0.5)
                    
                    # Verify it was entered
                    entered_value = plate_input.get_attribute('value')
                    if entered_value:
                        print(f"✓ Entered plate number: {entered_value}")
                    else:
                        print(f"⚠️  Plate number may not have been entered. Trying alternative method...")
                        plate_input.send_keys(Keys.CONTROL + 'a')
                        plate_input.send_keys(plate_number)
                        time.sleep(0.5)
                        entered_value = plate_input.get_attribute('value')
                        print(f"✓ Entered plate number (retry): {entered_value or 'unknown'}")
                except Exception as e:
                    print(f"Error entering plate number: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
                time.sleep(2)
                
                # Find and click the "View Invoice / Violation / Toll Bill" button
                print("Looking for 'View Invoice / Violation / Toll Bill' button...")
                view_button = None
                
                # Try multiple methods to find the button
                button_selectors = [
                    # By button text
                    (By.XPATH, '//button[contains(text(), "View Invoice")]'),
                    (By.XPATH, '//button[contains(text(), "View")]'),
                    (By.XPATH, '//input[@value="View Invoice / Violation / Toll Bill"]'),
                    (By.XPATH, '//input[contains(@value, "View Invoice")]'),
                    (By.XPATH, '//input[contains(@value, "View")]'),
                    # By button type
                    (By.CSS_SELECTOR, 'button[type="submit"]'),
                    (By.CSS_SELECTOR, 'input[type="submit"]'),
                    # By class or id containing "view" or "invoice"
                    (By.CSS_SELECTOR, 'button[id*="view"]'),
                    (By.CSS_SELECTOR, 'button[class*="view"]'),
                    (By.CSS_SELECTOR, 'input[id*="view"]'),
                    (By.CSS_SELECTOR, 'input[class*="view"]'),
                    # Generic button
                    (By.CSS_SELECTOR, 'button'),
                ]
                
                for by_method, selector in button_selectors:
                    try:
                        buttons = self.driver.find_elements(by_method, selector)
                        for btn in buttons:
                            try:
                                btn_text = btn.text or btn.get_attribute('value') or ''
                                btn_text_lower = btn_text.lower()
                                if btn.is_displayed() and ('view' in btn_text_lower or 'invoice' in btn_text_lower):
                                    view_button = btn
                                    print(f"✓ Found button: '{btn_text}'")
                                    break
                            except:
                                continue
                        if view_button:
                            break
                    except:
                        continue
                
                if view_button:
                    try:
                        # Scroll to button
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", view_button)
                        time.sleep(1)
                        # Try JavaScript click first (more reliable)
                        self.driver.execute_script("arguments[0].click();", view_button)
                        print("✓ Clicked 'View Invoice / Violation / Toll Bill' button (JavaScript click)")
                    except Exception as e:
                        try:
                            view_button.click()
                            print("✓ Clicked 'View Invoice / Violation / Toll Bill' button")
                        except Exception as e2:
                            print(f"⚠️  Could not click button: {str(e2)}")
                            # Try pressing Enter on plate input as fallback
                            plate_input.send_keys(Keys.RETURN)
                            print("✓ Form submitted (Enter key - fallback)")
                else:
                    print("⚠️  Could not find 'View Invoice / Violation / Toll Bill' button")
                    # Try pressing Enter as fallback
                    plate_input.send_keys(Keys.RETURN)
                    print("✓ Form submitted (Enter key - fallback)")
                
                # Wait for results
                print("Waiting 10 seconds for results to load...")
                time.sleep(10)
                
                return self._extract_violation_data()
            else:
                # Debug: print page source snippet
                print("Could not find input fields. Page title:", self.driver.title)
                return self._create_error_result("Could not find violation input fields on the page")
        
        except Exception as e:
            print(f"Error fetching violation info: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._create_error_result(f"Error fetching violation info: {str(e)}")

    def _fetch_account_info(self, account_number: str, plate_number: str) -> Dict:
        """Fetch account information (requires login)"""
        # For now, return error as account login requires credentials
        return self._create_error_result("Account login not yet implemented. Please use violation number lookup.")

    def _extract_violation_data(self) -> Dict:
        """Extract violation/invoice data from the page"""
        try:
            print("Extracting violation information...")
            
            page_source = self.driver.page_source
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            
            # Extract ONLY total amount due (not individual amounts)
            balance_amount = 0.0
            violation_count = 0
            toll_bill_numbers = []
            
            # Look specifically for "total amount due" patterns (priority order)
            total_amount_due_patterns = [
                r'total\s+amount\s+due[:\s]*\$?\s*([\d,]+\.?\d*)',
                r'amount\s+due[:\s]*\$?\s*([\d,]+\.?\d*)',
                r'total\s+due[:\s]*\$?\s*([\d,]+\.?\d*)',
                r'balance\s+due[:\s]*\$?\s*([\d,]+\.?\d*)',
                r'total\s+balance\s+due[:\s]*\$?\s*([\d,]+\.?\d*)',
                r'outstanding\s+balance[:\s]*\$?\s*([\d,]+\.?\d*)',
            ]
            
            # Try to find "total amount due" first
            for pattern in total_amount_due_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    try:
                        amount = float(match.replace(',', ''))
                        if amount > 0:
                            balance_amount = amount
                            print(f"✓ Found total amount due: ${balance_amount:.2f}")
                            break
                    except:
                        pass
                if balance_amount > 0:
                    break
            
            # Only extract violation number if there's an amount due
            if balance_amount > 0:
                # Extract violation/invoice number
                if self.violation_number:
                    toll_bill_numbers.append(self.violation_number)
                    violation_count = 1  # Set to 1 if amount due exists
                    print(f"✓ Extracted violation number: {self.violation_number}")
                
                # Also try to find additional violation numbers on the page if amount due exists
                violation_patterns = [
                    r'violation\s*(?:number|#)?\s*[:\s]*([A-Z0-9-]+)',
                    r'invoice\s*(?:number|#)?\s*[:\s]*([A-Z0-9-]+)',
                    r'toll\s*bill\s*(?:number|#)?\s*[:\s]*([A-Z0-9-]+)',
                    r'bill\s*(?:number|#)?\s*[:\s]*([A-Z0-9-]+)',
                ]
                
                for pattern in violation_patterns:
                    matches = re.findall(pattern, page_text, re.IGNORECASE)
                    for match in matches:
                        violation_num = match.strip().upper()
                        if violation_num and violation_num not in toll_bill_numbers:
                            toll_bill_numbers.append(violation_num)
                            print(f"✓ Found additional violation/invoice number: {violation_num}")
            else:
                print("ℹ️  No total amount due found (balance = $0.00)")
                violation_count = 0
                toll_bill_numbers = []
            
            print("\n" + "=" * 60)
            print("EXTRACTION COMPLETE")
            print("=" * 60)
            print(f"Total Amount Due: ${balance_amount:.2f}")
            if balance_amount > 0:
                print(f"Violation/Invoice Numbers: {', '.join(toll_bill_numbers) if toll_bill_numbers else 'None found'}")
                print(f"Has Violations: {'Yes' if violation_count > 0 else 'No'}")
            else:
                print("No amount due - no violations extracted")
            print("=" * 60 + "\n")
            
            return {
                'success': True,
                'account_number': self.account_number or '',
                'plate_number': self.plate_number,
                'violation_number': self.violation_number,
                'balance_amount': balance_amount,
                'violation_count': violation_count,
                'toll_bill_numbers': toll_bill_numbers,
                'violations': [],
                'source': 'NJ E-ZPass'
            }
        
        except Exception as e:
            print(f"Error extracting violation data: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._create_error_result(f"Error extracting data: {str(e)}")

    def _create_error_result(self, error_message: str) -> Dict:
        """Create an error result dictionary"""
        return {
            'success': False,
            'error': error_message,
            'account_number': self.account_number or '',
            'plate_number': self.plate_number or '',
            'violation_number': self.violation_number or '',
            'balance_amount': 0,
            'violation_count': 0,
            'toll_bill_numbers': [],
            'violations': [],
            'source': 'NJ E-ZPass'
        }


def extract_toll_info_nj(violation_number: str = None, plate_number: str = None, 
                         account_number: str = None, headless: bool = False) -> Dict:
    """
    Convenience function to extract toll information from E-ZPass NJ
    
    Args:
        violation_number: Violation/Invoice number (optional)
        plate_number: License plate number (required)
        account_number: E-ZPass account number (optional)
        headless: Whether to run browser in headless mode
        
    Returns:
        Dictionary with extracted information
    """
    automation = EZPassNJAutomation()
    return automation.login_and_extract(
        account_number=account_number,
        plate_number=plate_number,
        violation_number=violation_number,
        headless=headless
    )


if __name__ == '__main__':
    # Example usage
    import sys
    
    if len(sys.argv) >= 3:
        violation_num = sys.argv[1]
        plate_num = sys.argv[2]
        result = extract_toll_info_nj(violation_number=violation_num, plate_number=plate_num)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python automation_selenium_nj.py <violation_number> <plate_number>")
        print("Example: python automation_selenium_nj.py T13255735180201 T127211C")

