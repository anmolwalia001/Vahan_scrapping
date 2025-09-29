# scrapper/browser.py
"""
Enhanced browser management for Vahan scraping with service integration
Supports plain Chrome, optional proxy, stealth mode, and service layer integration
"""

import logging
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from pathlib import Path
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

from scrapper.element_cache import ElementCache

logger = logging.getLogger("app.scrapper.browser")


class VahanBrowser:
    """
    Enhanced browser manager for Vahan portal scraping
    Integrates with services layer and element caching
    """
    
    def __init__(self, headless: bool = False, use_proxy: bool = False, stealth: bool = False, user_agent=None):
        """
        Initialize Vahan browser manager
        
        Args:
            headless: Run browser in headless mode
            use_proxy: Enable proxy support (placeholder)
            stealth: Use stealth mode to avoid detection
        """
        self.headless = headless
        self.use_proxy = use_proxy
        self.stealth = stealth
        self.driver = None
        self.wait = None
        self.element_cache = ElementCache()
        
        self.temp_download_dir = None

        if user_agent:
            self.chrome_options.add_argument(f'--user-agent={user_agent}')
        
        logger.info(f"VahanBrowser initialized - headless: {headless}, stealth: {stealth}")

    def setup(self, temp_download_dir: str = None):
        """Setup browser and configure download directory"""
        self.temp_download_dir = temp_download_dir or os.path.join(os.getcwd(), "temp_downloads")
        os.makedirs(self.temp_download_dir, exist_ok=True)
        
        self.driver = self._create_driver()
        self.wait = WebDriverWait(self.driver, 20)
        
        # Set download behavior
        self.driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": self.temp_download_dir
        })
        
        logger.info("Browser setup completed")

    def _create_driver(self):
        """Create Chrome WebDriver instance with optimized settings"""
        chrome_options = Options()
        
        # Basic settings
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # SSL/Certificate handling for Vahan portal
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--allow-insecure-localhost")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.set_capability("acceptInsecureCerts", True)
        
        # Download preferences
        prefs = {
            "download.default_directory": self.temp_download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Optional proxy
        if self.use_proxy:
            proxy = "http://127.0.0.1:8080"  # Placeholder
            chrome_options.add_argument(f"--proxy-server={proxy}")
            logger.info(f"Using proxy: {proxy}")

        # Optional stealth mode
        if self.stealth:
            try:
                import undetected_chromedriver as uc
                logger.info("Using undetected_chromedriver for stealth mode")
                driver = uc.Chrome(options=chrome_options)
            except ImportError:
                logger.warning("undetected_chromedriver not available, using regular Chrome")
                driver = webdriver.Chrome(options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        
        # Maximize window and set user agent
        driver.maximize_window()
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver

    def navigate_to_portal(self) -> bool:
        """Navigate to Vahan portal with retry logic"""
        url = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"
        
        for attempt in range(3):
            try:
                logger.info(f"Navigating to Vahan portal (attempt {attempt + 1}/3)")
                self.driver.get(url)
                time.sleep(5)
                
                # Refresh page to ensure proper loading
                self.driver.refresh()
                time.sleep(3)
                
                # Verify page loaded
                if "reportview" in self.driver.current_url.lower():
                    logger.info("Successfully navigated to Vahan portal")
                    return True
                    
            except WebDriverException as e:
                logger.warning(f"Navigation attempt {attempt + 1} failed: {e}")
                time.sleep(5)
        
        logger.error("Failed to navigate to Vahan portal after 3 attempts")
        return False

    def set_axis(self, y_axis: str, x_axis: str) -> bool:
        """Set Y-axis and X-axis dropdown values"""
        try:
            logger.info(f"Setting axis - Y: {y_axis}, X: {x_axis}")
            
            # Set Y-axis
            if not self._select_primefaces_dropdown("yaxisVar", y_axis):
                logger.error(f"Failed to set Y-axis to {y_axis}")
                return False
            
            # Set X-axis
            if not self._select_primefaces_dropdown("xaxisVar", x_axis):
                logger.error(f"Failed to set X-axis to {x_axis}")
                return False
            
            logger.info("Axis values set successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error setting axis values: {e}")
            return False

    def select_state(self, state_name: str) -> bool:
        """Select state from dropdown using cached element"""
        try:
            logger.info(f"Selecting state: {state_name}")
            
            # Get state dropdown ID from cache
            state_dropdown_id = self.element_cache.get_state_dropdown_id()
            
            if not state_dropdown_id:
                logger.error("Could not find state dropdown")
                return False
        
            self._log_step(f"select_state start 👌👌👌: {state_name}")
            # Select state
            success = self._select_primefaces_dropdown(state_dropdown_id, state_name)
            
            if success:
                logger.info(f"Successfully selected state: {state_name}")
                self._wait_for_ajax()
                time.sleep(2)
                self.ensure_axes()
                self._log_step(f"select_state done 👌👌👌: {state_name}")
                return True
            else:
                logger.error(f"Failed to select state: {state_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error selecting state {state_name}: {e}")
            return False

    def select_rto(self, rto_text: str) -> bool:
        """Select RTO from dropdown"""
        try:
            logger.info(f"Selecting RTO: {rto_text}")

            self._log_step(f"select_rto start 🌲🌲🌲:  {rto_text}")
            
            success = self._select_primefaces_dropdown("selectedRto", rto_text)
            
            if success:
                logger.info(f"Successfully selected RTO: {rto_text}")
                self._wait_for_ajax()
                self.ensure_axes()
                self._log_step(f"select_rto done 🌲🌲🌲:  {rto_text}")
                return True
            else:
                logger.error(f"Failed to select RTO: {rto_text}")
                return False
                
        except Exception as e:
            logger.error(f"Error selecting RTO {rto_text}: {e}")
            return False

    def click_refresh(self) -> bool:
        """Click refresh button to load data - FIXED VERSION"""

        selectors = [
        "//span[normalize-space()='Refresh']",
        "//button[.//span[text()='Refresh']]"
        ]

        for sel in selectors:
            try:
                btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, sel)))
                self._log_step("refresh click start 🔄🔄🔄")
                self.driver.execute_script("arguments[0].click();", btn)
                self._wait_for_ajax()
                self.ensure_axes()
                self._log_step("refresh done 🔄🔄🔄")
                return True
            except:
                continue
        logger.error("Could not find refresh button with any selector")
        return False
        try:
            logger.debug("Clicking refresh button")
            
            # Try multiple possible refresh button selectors
            refresh_selectors = [
                "input[value='Refresh']",
                "input[type='submit'][value='Refresh']", 
                "button:contains('Refresh')",
                ".ui-button:contains('Refresh')",
                "[id*='refresh']",
                "[id*='Refresh']"
            ]
            
            for selector in refresh_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            time.sleep(0.5)
                            self.driver.execute_script("arguments[0].click();", element)
                            
                            # Wait for data to load
                            self._wait_for_ajax(timeout=15)
                            time.sleep(2)
                            
                            logger.debug("Refresh completed")
                            return True
                except Exception as e:
                    logger.debug(f"Refresh selector {selector} failed: {e}")
                    continue
            
            logger.error("Could not find refresh button with any selector")
            return False
            
        except Exception as e:
            logger.error(f"Error clicking refresh: {e}")
            return False

    # def apply_vehicle_filter(self, vehicle_categories: List[str]) -> bool:
    #     """Apply vehicle category filter"""
    #     try:
    #         logger.info(f"Applying vehicle filter: {vehicle_categories}")
            
    #         from scrapper.element_cache import apply_vehicle_filter_cached
            
    #         success = apply_vehicle_filter_cached(
    #             self.driver, 
    #             self.wait, 
    #             self.element_cache, 
    #             vehicle_categories
    #         )
            
    #         if success:
    #             logger.info("Vehicle filter applied successfully")
    #             return True
    #         else:
    #             logger.error("Failed to apply vehicle filter")
    #             return False
                
    #     except Exception as e:
    #         logger.error(f"Error applying vehicle filter: {e}")
    #         return False

    def apply_vehicle_filter(self, vehicle_categories: List[str]) -> bool:
        """Apply vehicle category filter with improved checkbox handling - FIXED VERSION"""
        try:
            logger.info(f"Applying vehicle filter: {vehicle_categories}")
            
            # First try to find and open the filter panel
            filter_toggle_selectors = [
                "[id*='filterToggle']",
                ".filter-toggle",
                "button:contains('Filter')",
                ".ui-button:contains('Filter')"
            ]
            
            for selector in filter_toggle_selectors:
                try:
                    if ":contains(" in selector:
                        # Handle contains with XPath
                        toggle = self.driver.find_element(By.XPATH, f"//*[contains(text(), 'Filter')]")
                    else:
                        toggle = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if toggle.is_displayed():
                        self.driver.execute_script("arguments[0].click();", toggle)
                        self._wait_for_ajax()
                        time.sleep(0.5)
                        break
                except:
                    continue
            
            # Now find and select checkboxes
            success_count = 0
            for category in vehicle_categories:
                try:
                    checkbox_found = False
                    
                    # Approach 1: Find by label text and associated checkbox
                    label_xpath = f"//label[normalize-space(text())='{category}']"
                    try:
                        label = self.driver.find_element(By.XPATH, label_xpath)
                        # Try to find associated checkbox
                        checkbox_id = label.get_attribute('for')
                        if checkbox_id:
                            checkbox = self.driver.find_element(By.ID, checkbox_id)
                        else:
                            # Look for checkbox in same container
                            parent = label.find_element(By.XPATH, './..')
                            checkbox = parent.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                        
                        if not checkbox.is_selected():
                            self.driver.execute_script("arguments[0].click();", checkbox)
                            self._wait_for_ajax()
                            time.sleep(0.5)
                            checkbox_found = True
                            success_count += 1
                            
                    except Exception as e:
                        logger.debug(f"Label approach failed for {category}: {e}")
                    
                    # Approach 2: Find checkbox by value attribute
                    if not checkbox_found:
                        try:
                            checkbox = self.driver.find_element(By.CSS_SELECTOR, f'input[type="checkbox"][value="{category}"]')
                            if not checkbox.is_selected():
                                self.driver.execute_script("arguments[0].click();", checkbox)
                                checkbox_found = True
                                success_count += 1
                        except Exception as e:
                            logger.debug(f"Value approach failed for {category}: {e}")
                    
                    # Approach 3: Click on the label itself
                    if not checkbox_found:
                        try:
                            label = self.driver.find_element(By.XPATH, f"//label[contains(text(), '{category}')]")
                            self.driver.execute_script("arguments[0].click();", label)
                            checkbox_found = True
                            success_count += 1
                        except Exception as e:
                            logger.debug(f"Label click approach failed for {category}: {e}")
                    
                    if not checkbox_found:
                        logger.warning(f"Could not find checkbox for category: {category}")
                        
                except Exception as e:
                    logger.error(f"Error selecting category {category}: {e}")
            
            if success_count > 0:
                logger.info(f"Successfully applied {success_count}/{len(vehicle_categories)} vehicle filters")
                time.sleep(1)  # Wait for filter to apply
                return True
            else:
                logger.error("No vehicle filters were successfully applied")
                return False
                
        except Exception as e:
            logger.error(f"Error applying vehicle filter: {e}")
            return False


    def check_data_exists(self) -> bool:
        """Check if data exists in the report table"""
        try:
            logger.debug("Checking if data exists")

            time.sleep(2)  # small wait for table to render

        # First check: "No records found" message
            if self.driver.find_elements(By.XPATH, "//*[contains(text(), 'No records found')]"):
                logger.debug("Found 'No records found' message")
                return False

        # Candidate selectors for data rows
            table_selectors = [
            "#reportTable_data tr",
            ".ui-datatable-data tr",
            "#reportTable tbody tr",
            ".ui-datatable tbody tr",
            "table tbody tr"
            ]

            for selector in table_selectors:
                try:
                    rows = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if not rows:
                        continue

                    logger.debug(f"Found {len(rows)} rows using selector: {selector}")

                # Inspect first couple of rows for actual text
                    for row in rows[:2]:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if cells and any(cell.text.strip() for cell in cells):
                            logger.debug("Valid data row found")
                            return True
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            logger.debug("No valid data rows found")
            return False

        except Exception as e:
            logger.error(f"Error checking data existence: {e}")
            return False


    def download_excel(self, output_dir: str, filename: str) -> bool:
        """Download Excel file from the portal"""
        try:
            logger.info(f"Downloading Excel file: {filename}")

        # Clear temp directory first
            self._clear_temp_downloads()

        # Try multiple selectors for Excel export button
            export_selectors = [
                "//a[contains(@onclick, ':xls')]",
                "//a[contains(@onclick, 'groupingTable:xls')]",
                "//a[contains(@onclick, 'xls:')]",
            ]

            excel_element = None
            for xpath in export_selectors:
                try:
                    export_element = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                    break
                except:
                    continue

            if not export_element:
                logger.error("Excel export button not found")
                return False

        # Click via JS to avoid hidden/overlay issues
            self.driver.execute_script("arguments[0].click();", export_element)
            logger.debug("Clicked Excel export link")

        # Wait for download to complete (reportTable.xlsx is default name)
            expected_file = "reportTable.xlsx"
            if not self._wait_for_download_complete(expected_file, timeout=30):
                logger.error("Excel download did not complete in time")
                return False

        # Move file from temp to output_dir
            temp_file = os.path.join(self.temp_download_dir, expected_file)
            final_file = os.path.join(output_dir, filename)

            os.makedirs(output_dir, exist_ok=True)
            import shutil
            shutil.move(temp_file, final_file)

            logger.info(f"Excel file saved: {final_file}")
            return True

        except Exception as e:
            logger.error(f"Error downloading Excel: {e}")
            return False


    def refresh_page(self):
        """Refresh the current page"""
        try:
            logger.info("Refreshing page")
            self.driver.refresh()
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error refreshing page: {e}")

    def quit(self):
        """Close browser and cleanup"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            finally:
                self.driver = None
                self.wait = None

    def _select_primefaces_dropdown(self, dropdown_id: str, option_text: str) -> bool:
        """
        Select an option from a PrimeFaces dropdown with retries.
        Handles stale element reference issues caused by DOM refresh.
        """
        panel_id = f"{dropdown_id}_panel"

        for attempt in range(3):  # retry up to 3 times
            try:
            # open dropdown
                dropdown = self.wait.until(EC.element_to_be_clickable((By.ID, dropdown_id)))
                self.driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
                dropdown.click()
                time.sleep(1)

            # locate the option
                option_xpath = f"//div[@id='{panel_id}']//li[contains(normalize-space(.), '{option_text}')]"
                option = self.wait.until(EC.presence_of_element_located((By.XPATH, option_xpath)))

            # click it via JS (avoids stale issues)
                self.driver.execute_script("arguments[0].click();", option)

            # wait for PrimeFaces AJAX
                self._wait_for_ajax()
                logger.info(f"Selected '{option_text}' from {dropdown_id}")
                return True

            except Exception as e:
                logger.warning(f"Attempt {attempt+1}/3 failed selecting '{option_text}' from {dropdown_id}: {e}")
                time.sleep(1)
                continue

        logger.error(f"Failed to select '{option_text}' from {dropdown_id} after retries")
        return False

        
    
    def _wait_for_ajax(self, timeout: int = 10):
        """Wait for AJAX requests to complete"""
        try:
            # Wait for jQuery if available
            self.wait.until(
                lambda driver: driver.execute_script("return jQuery.active == 0") if 
                driver.execute_script("return typeof jQuery !== 'undefined'") else True,
                timeout
            )
        except:
            # Fallback: just wait
            time.sleep(2)

    def _wait_for_download_complete(self, expected_filename: str, timeout: int = 30) -> bool:
        """Wait for download to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            files = os.listdir(self.temp_download_dir)
            
            if expected_filename in files:
                filepath = os.path.join(self.temp_download_dir, expected_filename)
                initial_size = os.path.getsize(filepath)
                time.sleep(1)
                
                try:
                    current_size = os.path.getsize(filepath)
                    if current_size == initial_size and current_size > 0:
                        time.sleep(1)  # Extra wait to ensure file is complete
                        return True
                except:
                    pass
            
            # Check for partial downloads
            temp_files = [f for f in files if f.endswith('.crdownload') or f.endswith('.tmp')]
            if temp_files:
                time.sleep(1)
                continue
            
            time.sleep(0.5)
        
        return False
    
    def _read_selected_from_dropdown(self, dropdown_id: str) -> Optional[str]:
        """
        Read the visible label of a PrimeFaces dropdown after selection.
        Works for <div id="..."> based PF dropdowns where the label is in a child span.
        """
        try:
            root = self.driver.find_element(By.ID, dropdown_id)
            # Typical PF markup: <label/span> inside the root; fallback to textContent
            try:
                label_el = root.find_element(By.CSS_SELECTOR, ".ui-selectonemenu-label")
                return label_el.text.strip()
            except:
                return root.text.strip()
        except Exception:
            return None

    def set_axis_and_verify(self, y_axis: str, x_axis: str) -> bool:
        """
        Set Y and X axis and verify the UI actually reflects those values.
        """
        if not self.set_axis(y_axis, x_axis):
            return False

        self._wait_for_ajax()
        time.sleep(0.5)

        y_selected = self._read_selected_from_dropdown("yaxisVar")
        x_selected = self._read_selected_from_dropdown("xaxisVar")

        if (y_selected or "").strip().lower() != y_axis.strip().lower():
            logger.error(f"Y-axis mismatch. Expected '{y_axis}', got '{y_selected}'")
            return False

        if (x_selected or "").strip().lower() != x_axis.strip().lower():
            logger.error(f"X-axis mismatch. Expected '{x_axis}', got '{x_selected}'")
            return False
        
        self._desired_y_axis = y_axis
        self._desired_x_axis = x_axis

        logger.info(f"Axis verified: Y='{y_selected}', X='{x_selected}'")
        return True

    def _clear_temp_downloads(self):
        """Clear temporary download directory"""
        try:
            if os.path.exists(self.temp_download_dir):
                for file in os.listdir(self.temp_download_dir):
                    file_path = os.path.join(self.temp_download_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        except Exception as e:
            logger.warning(f"Error clearing temp downloads: {e}")

    def ensure_axes(self) -> bool:
        """If desired axes are known, verify the UI still shows them; if not, set again."""
        if not (self._desired_y_axis and self._desired_x_axis):
            return True  # nothing to enforce yet

        self._wait_for_ajax()
        time.sleep(0.3)

        y_selected = self._read_selected_from_dropdown("yaxisVar")
        x_selected = self._read_selected_from_dropdown("xaxisVar")

        if (y_selected or "").strip().lower() == self._desired_y_axis.strip().lower() and \
            (x_selected or "").strip().lower() == self._desired_x_axis.strip().lower():
            return True

        logger.warning(
            f"Axes drifted. Re-applying... "
            f"(have: Y='{y_selected}', X='{x_selected}'; want: Y='{self._desired_y_axis}', X='{self._desired_x_axis}')"
        )
        return self.set_axis_and_verify(self._desired_y_axis, self._desired_x_axis)


    def _log_step(self, label: str):
        """Tiny helper to log a timestamped step for throttle diagnostics."""
        print(f"[THROTTLE] {label} @ {datetime.now().isoformat(timespec='seconds')}")


    def get_driver(self):
        """Get the WebDriver instance"""
        return self.driver

    def __enter__(self):
        """Context manager entry"""
        if not self.driver:
            self.setup()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit"""
        self.quit()


class BrowserManager:
    """
    Legacy compatibility class - use VahanBrowser instead
    """
    
    def __init__(self, headless: bool = True, use_proxy: bool = False, stealth: bool = False):
        """
        Legacy browser manager for backward compatibility
        """
        logger.warning("BrowserManager is deprecated, use VahanBrowser instead")
        self.headless = headless
        self.use_proxy = use_proxy
        self.stealth = stealth
        self.driver = None
        self._vahan_browser = None
        self._desired_y_axis = None
        self._desired_x_axis = None

    def __enter__(self):
        self._vahan_browser = VahanBrowser(self.headless, self.use_proxy, self.stealth)
        self._vahan_browser.setup()
        self.driver = self._vahan_browser.get_driver()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._vahan_browser:
            self._vahan_browser.quit()

    def get_driver(self):
        return self.driver

    def navigate_with_retry(self, url: str, retries: int = 3, delay: int = 5) -> bool:
        """Navigate with retry logic"""
        if self._vahan_browser:
            return self._vahan_browser.navigate_to_portal()
        return False
    
    def download_excel(self, state_code: str, rto_code: str, file_path: Path):
        """
        Legacy Excel download method - creates dummy file
        Use VahanBrowser.download_excel() for real functionality
        """
        logger.warning("Using legacy dummy Excel download - use VahanBrowser for real downloads")
        
        data = {
            "State": [state_code],
            "RTO": [rto_code],
            "GeneratedAt": [datetime.utcnow().isoformat()],
            "Note": ["This is a dummy file generated by legacy BrowserManager"]
        }
        
        df = pd.DataFrame(data)
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(file_path, index=False)

        logger.info(f"Generated dummy Excel file: {file_path}")
        return file_path


# Utility functions for service integration
def create_browser_for_extraction(headless: bool = False) -> VahanBrowser:
    """
    Create a browser instance optimized for extraction service
    
    Args:
        headless: Whether to run in headless mode
    
    Returns:
        Configured VahanBrowser instance
    """
    browser = VahanBrowser(
        headless=headless,
        use_proxy=False,  # Disabled for now
        stealth=False     # Can be enabled if needed
    )
    
    return browser


def test_browser_connection() -> bool:
    """
    Test browser connection to Vahan portal
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        with VahanBrowser(headless=True) as browser:
            browser.setup()
            success = browser.navigate_to_portal()
            
            if success:
                logger.info("Browser connection test: SUCCESS")
                return True
            else:
                logger.error("Browser connection test: FAILED - Could not navigate to portal")
                return False
                
    except Exception as e:
        logger.error(f"Browser connection test: FAILED - {e}")
        return False


# Example usage for testing
def main():
    """Test browser functionality"""
    print("Testing Vahan Browser...")
    
    # Test connection
    if test_browser_connection():
        print("✓ Browser connection test passed")
    else:
        print("✗ Browser connection test failed")
        return
    
    # Test full workflow (dummy)
    try:
        with VahanBrowser(headless=False) as browser:
            browser.setup()
            
            if browser.navigate_to_portal():
                print("✓ Navigation successful")
                
                if browser.set_axis("Maker", "Month Wise"):
                    print("✓ Axis setting successful")
                    
                    if browser.select_state("Delhi"):
                        print("✓ State selection successful")
                    else:
                        print("✗ State selection failed")
                else:
                    print("✗ Axis setting failed")
            else:
                print("✗ Navigation failed")
                
    except Exception as e:
        print(f"✗ Test failed: {e}")


if __name__ == "__main__":
    main()