# scrapper/element_discovery.py
"""
Dynamic element discovery for Vahan portal
Discovers and caches element selectors in database
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .browser import BrowserManager
from .element_cache import ElementCache, FieldOption

logger = logging.getLogger("app.element_discovery")


class ElementDiscoverer:
    """Discovers and caches dynamic element selectors"""
    
    def __init__(self, site_name: str = "vahan"):
        self.cache = ElementCache(site_name)
        self.discovery_results = {}
    
    def discover_all_elements(
        self, 
        url: str = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"
    ) -> Dict[str, bool]:
        """Discover all elements on the Vahan portal"""
        results = {}
        
        with BrowserManager(headless=False, use_proxy=False, stealth=False) as browser:
            logger.info("Starting element discovery...")
            
            # Navigate to page
            if not browser.navigate_with_retry(url):
                logger.error("Failed to navigate to Vahan portal")
                return results
            
            time.sleep(5)  # Wait for page to fully load
            
            # Discover each element type
            discovery_methods = [
                ("y_axis_dropdown", self._discover_y_axis),
                ("x_axis_dropdown", self._discover_x_axis),
                ("state_dropdown", self._discover_state_dropdown),
                ("rto_dropdown", self._discover_rto_dropdown),
                ("refresh_button", self._discover_refresh_buttons),
                ("filter_panel_toggle", self._discover_filter_toggle),
                ("vehicle_checkboxes", self._discover_vehicle_checkboxes),
                ("excel_export", self._discover_excel_export),
                ("data_table", self._discover_data_table),
                ("loading_indicators", self._discover_loading_indicators)
            ]
            
            for element_name, discovery_method in discovery_methods:
                try:
                    logger.info(f"Discovering {element_name}...")
                    success = discovery_method(browser.get_driver())
                    results[element_name] = success
                    
                    if success:
                        logger.info(f"✓ Successfully discovered {element_name}")
                    else:
                        logger.warning(f"✗ Failed to discover {element_name}")
                        
                except Exception as e:
                    logger.error(f"Error discovering {element_name}: {e}")
                    results[element_name] = False
        
        # Summary
        successful = sum(1 for v in results.values() if v)
        total = len(results)
        logger.info(f"Discovery complete: {successful}/{total} elements found")
        
        return results
    
    def _discover_y_axis(self, driver) -> bool:
        """Discover Y-axis dropdown"""
        try:
            element = driver.find_element(By.ID, "yaxisVar")
            if element:
                success = self.cache.store_selector(
                    field_name="y_axis",
                    selector="yaxisVar",
                    ui_type="select"
                )
                
                # Also discover Y-axis options
                if success:
                    self._discover_axis_options(driver, "y_axis", "yaxisVar")
                
                return success
        except NoSuchElementException:
            pass
        
        return False
    
    def _discover_x_axis(self, driver) -> bool:
        """Discover X-axis dropdown"""
        try:
            element = driver.find_element(By.ID, "xaxisVar")
            if element:
                success = self.cache.store_selector(
                    field_name="x_axis",
                    selector="xaxisVar",
                    ui_type="select"
                )
                
                # Also discover X-axis options
                if success:
                    self._discover_axis_options(driver, "x_axis", "xaxisVar")
                
                return success
        except NoSuchElementException:
            pass
        
        return False
    
    def _discover_axis_options(self, driver, field_name: str, selector_id: str):
        """Discover options for axis dropdowns"""
        try:
            select_element = driver.find_element(By.ID, selector_id)
            options = select_element.find_elements(By.TAG_NAME, "option")
            
            field_options = []
            for option in options:
                value = option.get_attribute("value")
                text = option.text.strip()
                
                if value and text and value != "":  # Skip empty options
                    field_options.append(FieldOption(
                        value_code=value,
                        label=text
                    ))
            
            if field_options:
                self.cache.store_field_options(field_name, field_options)
                logger.debug(f"Stored {len(field_options)} options for {field_name}")
                
        except Exception as e:
            logger.warning(f"Failed to discover options for {field_name}: {e}")
    
    def _discover_state_dropdown(self, driver) -> bool:
        """Discover dynamic state dropdown"""
        # Method 1: Look for dropdowns with state-related labels
        try:
            dropdowns = driver.find_elements(By.CSS_SELECTOR, "div.ui-selectonemenu")
            for dropdown in dropdowns:
                try:
                    label = dropdown.find_element(By.CSS_SELECTOR, "label.ui-selectonemenu-label")
                    label_text = label.text.strip().lower()
                    dropdown_id = dropdown.get_attribute("id")
                    
                    if any(keyword in label_text for keyword in ['state', 'vahan4 running states']):
                        success = self.cache.store_selector(
                            field_name="state",
                            selector=dropdown_id,
                            ui_type="select"
                        )
                        
                        if success:
                            self._discover_state_options(driver, dropdown_id)
                        
                        return success
                except:
                    continue
        except:
            pass
        
        # Method 2: Try known patterns
        known_patterns = ["j_idt37", "j_idt40", "j_idt43", "j_idt44", "j_idt45"]
        for pattern in known_patterns:
            try:
                elem = driver.find_element(By.ID, pattern)
                if elem and "ui-selectonemenu" in elem.get_attribute("class"):
                    success = self.cache.store_selector(
                        field_name="state",
                        selector=pattern,
                        ui_type="select"
                    )
                    
                    if success:
                        self._discover_state_options(driver, pattern)
                    
                    return success
            except:
                continue
        
        return False
    
    def _discover_state_options(self, driver, dropdown_id: str):
        """Discover state dropdown options"""
        try:
            # Click to open dropdown
            dropdown = driver.find_element(By.ID, dropdown_id)
            dropdown.click()
            time.sleep(1)
            
            # Find options panel
            options_panel = driver.find_element(By.CSS_SELECTOR, f"#{dropdown_id}_panel .ui-selectonemenu-items")
            options = options_panel.find_elements(By.CSS_SELECTOR, ".ui-selectonemenu-item")
            
            field_options = []
            for option in options:
                value = option.get_attribute("data-option-value") or option.get_attribute("data-label")
                text = option.text.strip()
                
                if value and text and text.lower() != "select":
                    field_options.append(FieldOption(
                        value_code=value,
                        label=text
                    ))
            
            # Close dropdown
            dropdown.click()
            
            if field_options:
                self.cache.store_field_options("state", field_options)
                logger.debug(f"Stored {len(field_options)} state options")
                
        except Exception as e:
            logger.warning(f"Failed to discover state options: {e}")
    
    def _discover_rto_dropdown(self, driver) -> bool:
        """Discover RTO dropdown"""
        try:
            element = driver.find_element(By.ID, "selectedRto")
            if element:
                return self.cache.store_selector(
                    field_name="rto",
                    selector="selectedRto",
                    ui_type="select",
                    depends_on="state"  # RTO depends on state selection
                )
        except NoSuchElementException:
            pass
        
        return False
    
    def _discover_refresh_buttons(self, driver) -> bool:
        """Discover refresh buttons"""
        refresh_buttons = []
        
        # Method 1: Find by button text
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if button.is_displayed() and "refresh" in button.text.lower():
                    button_id = button.get_attribute("id")
                    button_location = button.location
                    
                    # Determine button type by position
                    button_type = "main_refresh" if button_location.get('x', 0) > 500 else "filter_refresh"
                    
                    success = self.cache.store_selector(
                        field_name=button_type,
                        selector=button_id,
                        ui_type="button"
                    )
                    
                    if success:
                        refresh_buttons.append(button_type)
        except:
            pass
        
        # Method 2: Known refresh button IDs
        known_refresh_ids = ["j_idt68", "j_idt70", "j_idt58", "j_idt51", "j_idt52", "j_idt57", "j_idt65", "j_idt77"]
        for btn_id in known_refresh_ids:
            try:
                button = driver.find_element(By.ID, btn_id)
                if button.tag_name.lower() == "button":
                    button_location = button.location
                    button_type = "main_refresh" if button_location.get('x', 0) > 500 else "filter_refresh"
                    
                    success = self.cache.store_selector(
                        field_name=button_type,
                        selector=btn_id,
                        ui_type="button"
                    )
                    
                    if success:
                        refresh_buttons.append(button_type)
                        break  # Use first working button
            except:
                continue
        
        return len(refresh_buttons) > 0
    
    def _discover_filter_toggle(self, driver) -> bool:
        """Discover filter panel toggle"""
        toggle_selectors = [
            ("id", "filterLayout-toggler"),
            ("css", ".ui-panel-titlebar-toggler"),
            ("css", "[id$='filterLayout-toggler']")
        ]
        
        for selector_type, selector_value in toggle_selectors:
            try:
                if selector_type == "id":
                    element = driver.find_element(By.ID, selector_value)
                    selector_to_store = selector_value
                else:
                    element = driver.find_element(By.CSS_SELECTOR, selector_value)
                    selector_to_store = selector_value
                
                if element:
                    return self.cache.store_selector(
                        field_name="filter_toggle",
                        selector=selector_to_store,
                        ui_type="button"
                    )
            except:
                continue
        
        return False
    
    def _discover_vehicle_checkboxes(self, driver) -> bool:
        """Discover vehicle category checkboxes"""
        vehicle_categories = ["MOTOR CAR", "MOTOR CAB", "ELECTRIC(BOV)", "PURE EV"]
        discovered_count = 0
        
        for category in vehicle_categories:
            try:
                # Find by label text
                label_xpath = f"//label[normalize-space(.)='{category}']"
                label = driver.find_element(By.XPATH, label_xpath)
                
                # Try to find associated checkbox
                checkbox_xpath = f"//label[normalize-space(.)='{category}']/preceding-sibling::div//input[@type='checkbox']"
                
                try:
                    checkbox = driver.find_element(By.XPATH, checkbox_xpath)
                    checkbox_id = checkbox.get_attribute("id")
                    
                    success = self.cache.store_selector(
                        field_name=f"vehicle_{category.lower().replace(' ', '_').replace('(', '').replace(')', '')}",
                        selector=checkbox_id if checkbox_id else checkbox_xpath,
                        ui_type="checkbox"
                    )
                except:
                    # Fallback to clicking label
                    success = self.cache.store_selector(
                        field_name=f"vehicle_{category.lower().replace(' ', '_').replace('(', '').replace(')', '')}",
                        selector=label_xpath,
                        ui_type="checkbox"
                    )
                
                if success:
                    discovered_count += 1
                    
            except Exception as e:
                logger.warning(f"Could not find vehicle category '{category}': {e}")
        
        return discovered_count > 0
    
    def _discover_excel_export(self, driver) -> bool:
        """Discover Excel export links"""
        export_patterns = [
            ("xpath", "//a[contains(@onclick, ':xls') or contains(@onclick, 'xls:')]"),
            ("xpath", "//a[contains(@onclick, 'groupingTable:xls')]"),
            ("css", "a[onclick*='exportChartAs']")
        ]
        
        for selector_type, selector_value in export_patterns:
            try:
                if selector_type == "xpath":
                    element = driver.find_element(By.XPATH, selector_value)
                else:
                    element = driver.find_element(By.CSS_SELECTOR, selector_value)
                
                if element:
                    return self.cache.store_selector(
                        field_name="excel_export",
                        selector=selector_value,
                        ui_type="button"
                    )
            except:
                continue
        
        return False
    
    def _discover_data_table(self, driver) -> bool:
        """Discover data table selectors"""
        table_selectors = [
            "#reportTable tbody tr",
            ".ui-datatable tbody tr",
            "table tbody tr",
            "#reportTable_data tr",
            ".ui-datatable-data tr"
        ]
        
        for selector in table_selectors:
            try:
                rows = driver.find_elements(By.CSS_SELECTOR, selector)
                if rows:
                    return self.cache.store_selector(
                        field_name="data_table_rows",
                        selector=selector,
                        ui_type="other"
                    )
            except:
                continue
        
        return False
    
    def _discover_loading_indicators(self, driver) -> bool:
        """Discover loading indicators"""
        loading_selectors = [
            ".ui-blockui",
            ".ui-widget-overlay",
            "[id*='loading']",
            ".loading",
            ".spinner"
        ]
        
        discovered_count = 0
        for selector in loading_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    success = self.cache.store_selector(
                        field_name=f"loading_{selector.replace('.', '').replace('[', '').replace(']', '').replace('*=', '').replace("'", '')}",
                        selector=selector,
                        ui_type="other"
                    )
                    if success:
                        discovered_count += 1
            except:
                continue
        
        return discovered_count > 0
    
    def verify_cached_selectors(self) -> Dict[str, bool]:
        """Verify all cached selectors still work"""
        results = {}
        cached_selectors = self.cache.get_all_selectors()
        
        if not cached_selectors:
            logger.warning("No cached selectors found")
            return results
        
        with BrowserManager(headless=True) as browser:
            if not browser.navigate_with_retry("https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"):
                logger.error("Failed to navigate for verification")
                return results
            
            time.sleep(3)
            driver = browser.get_driver()
            
            for field_name, selector_info in cached_selectors.items():
                try:
                    if selector_info.selector.startswith("//"):
                        # XPath selector
                        element = driver.find_element(By.XPATH, selector_info.selector)
                    elif selector_info.selector.startswith("#") or selector_info.selector.startswith("."):
                        # CSS selector
                        element = driver.find_element(By.CSS_SELECTOR, selector_info.selector)
                    else:
                        # Assume ID
                        element = driver.find_element(By.ID, selector_info.selector)
                    
                    results[field_name] = element is not None
                    
                    # Update last seen time
                    self.cache.store_selector(
                        field_name=field_name,
                        selector=selector_info.selector,
                        ui_type=selector_info.ui_type
                    )
                    
                except Exception as e:
                    logger.warning(f"Selector verification failed for {field_name}: {e}")
                    results[field_name] = False
                    # Mark as invalid
                    self.cache.mark_selector_invalid(field_name)
        
        # Summary
        working = sum(1 for v in results.values() if v)
        total = len(results)
        logger.info(f"Selector verification: {working}/{total} selectors working")
        
        return results
    
    def auto_discover_missing(self, force_rediscover: bool = False) -> Dict[str, bool]:
        """Automatically discover missing or stale selectors"""
        required_fields = [
            "y_axis", "x_axis", "state", "rto", 
            "main_refresh", "filter_refresh", "excel_export"
        ]
        
        missing_fields = []
        
        for field in required_fields:
            if force_rediscover or self.cache.is_selector_stale(field):
                missing_fields.append(field)
        
        if not missing_fields:
            logger.info("All required selectors are cached and fresh")
            return {}
        
        logger.info(f"Auto-discovering {len(missing_fields)} missing/stale selectors...")
        return self.discover_all_elements()


def main():
    """Main discovery function for CLI usage"""
    import sys
    
    discoverer = ElementDiscoverer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        print("=== Verifying Cached Selectors ===\n")
        results = discoverer.verify_cached_selectors()
        
        print("\nVerification Results:")
        for field, working in results.items():
            status = "✓" if working else "✗"
            print(f"  {field}: {status}")
            
    elif len(sys.argv) > 1 and sys.argv[1] == "auto":
        print("=== Auto-discovering Missing Selectors ===\n")
        results = discoverer.auto_discover_missing()
        
        if results:
            print("\nDiscovery Results:")
            for field, success in results.items():
                status = "✓" if success else "✗"
                print(f"  {field}: {status}")
        else:
            print("All selectors are up to date!")
            
    else:
        print("=== Full Element Discovery ===\n")
        results = discoverer.discover_all_elements()
        
        print("\nDiscovery Results:")
        for field, success in results.items():
            status = "✓" if success else "✗"
            print(f"  {field}: {status}")


if __name__ == "__main__":
    main()


# scrapper/browser.py
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
import time
import random

logger = logging.getLogger("app.browser")


class BrowserManager:
    def __init__(self, headless: bool = True, use_proxy: bool = False, stealth: bool = False):
        """
        Manage browser sessions with optional proxy and stealth.
        Defaults are plain Chrome (safe for Vahan).
        """
        self.headless = headless
        self.use_proxy = use_proxy
        self.stealth = stealth
        self.driver = None

    def __enter__(self):
        self.driver = self._create_driver()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")

    def _create_driver(self):
        """Create Chrome WebDriver instance."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless=new")  # modern headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # Optional proxy
        if self.use_proxy:
            proxy = self._get_proxy()
            if proxy:
                chrome_options.add_argument(f"--proxy-server={proxy}")
                logger.info(f"Using proxy: {proxy}")

        # Optional stealth
        if self.stealth:
            try:
                import undetected_chromedriver as uc
                logger.info("Launching undetected_chromedriver (stealth mode enabled)")
                return uc.Chrome(options=chrome_options)
            except ImportError:
                logger.warning("undetected_chromedriver not installed, fallback to normal driver")

        # Default: plain Chrome
        logger.info("Launching plain Chrome browser")
        return webdriver.Chrome(options=chrome_options)

    def _get_proxy(self):
        """
        Placeholder for proxy pool fetch.
        Right now returns None (so Vahan runs plain).
        """
        return None

    def get_driver(self):
        return self.driver

    def navigate_with_retry(self, url: str, retries: int = 3, delay: int = 5) -> bool:
        """Try navigating to a URL with retries."""
        for attempt in range(1, retries + 1):
            try:
                self.driver.get(url)
                time.sleep(2)  # let the page start loading
                return True
            except WebDriverException as e:
                logger.warning(f"Navigation failed (attempt {attempt}/{retries}): {e}")
                time.sleep(delay)
        return False
