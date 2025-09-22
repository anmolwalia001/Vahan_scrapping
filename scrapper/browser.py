# # scrapper/browser.py
# """
# Browser management for Vahan RTO scraping
# Handles Chrome driver setup, proxy rotation, and session management
# """

# import logging
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import TimeoutException, WebDriverException
# import random
# import time
# from typing import Optional, Dict, List
# from datetime import datetime, timedelta

# from db.session import SessionLocal
# from db.models import ProxyPool, ProxyEndpoint, UserAgentPool, UserAgent
# from configs.setting import PROXY_CONFIG

# logger = logging.getLogger("app.browser")


# class BrowserManager:
#     """Manages Chrome browser instances with proxy and user agent rotation"""
    
#     def __init__(self, headless: bool = True, use_proxy: bool = True):
#         self.headless = headless
#         self.use_proxy = use_proxy
#         self.driver: Optional[webdriver.Chrome] = None
#         self.current_proxy = None
#         self.current_user_agent = None
#         self.session_start_time = None
        
#     def _get_random_user_agent(self) -> Optional[str]:
#         """Get a random user agent from database"""
#         with SessionLocal() as db:
#             # Get active user agent pools
#             pools = db.query(UserAgentPool).all()
#             if not pools:
#                 logger.warning("No user agent pools found in database")
#                 return None
            
#             # Pick random pool
#             pool = random.choice(pools)
            
#             # Get random user agent from pool
#             user_agents = db.query(UserAgent).filter(
#                 UserAgent.pool_id == pool.id
#             ).all()
            
#             if not user_agents:
#                 logger.warning(f"No user agents found in pool {pool.name}")
#                 return None
            
#             # Weighted random selection
#             weights = [ua.weight for ua in user_agents]
#             selected_ua = random.choices(user_agents, weights=weights)[0]
            
#             logger.debug(f"Selected user agent from pool '{pool.name}': {selected_ua.ua_string[:50]}...")
#             return selected_ua.ua_string
    
#     def _get_random_proxy(self) -> Optional[str]:
#         """Get a random proxy from database"""
#         if not self.use_proxy:
#             return None
            
#         with SessionLocal() as db:
#             # Get active proxy pools
#             pools = db.query(ProxyPool).all()
#             if not pools:
#                 logger.warning("No proxy pools found in database")
#                 return None
            
#             # Pick random pool
#             pool = random.choice(pools)
            
#             # Get active proxies from pool (not used recently)
#             cutoff_time = datetime.now() - timedelta(minutes=PROXY_CONFIG.get("rotate_interval", 10))
            
#             proxies = db.query(ProxyEndpoint).filter(
#                 ProxyEndpoint.pool_id == pool.id,
#                 ProxyEndpoint.is_active == True,
#                 (ProxyEndpoint.last_used_at.is_(None) | (ProxyEndpoint.last_used_at < cutoff_time))
#             ).all()
            
#             if not proxies:
#                 logger.warning(f"No available proxies in pool {pool.name}")
#                 return None
            
#             # Weighted random selection
#             weights = [proxy.weight for proxy in proxies]
#             selected_proxy = random.choices(proxies, weights=weights)[0]
            
#             # Update last used time
#             selected_proxy.last_used_at = datetime.now()
#             db.commit()
            
#             logger.debug(f"Selected proxy from pool '{pool.name}': {selected_proxy.endpoint}")
#             return selected_proxy.endpoint
    
#     def create_driver(self) -> webdriver.Chrome:
#         """Create a new Chrome driver with random proxy and user agent"""
#         chrome_options = Options()
        
#         # Basic Chrome options
#         chrome_options.add_argument('--no-sandbox')
#         chrome_options.add_argument('--disable-dev-shm-usage')
#         chrome_options.add_argument('--disable-blink-features=AutomationControlled')
#         chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         chrome_options.add_experimental_option('useAutomationExtension', False)
        
#         if self.headless:
#             chrome_options.add_argument('--headless')
        
#         # Set random user agent
#         user_agent = self._get_random_user_agent()
#         if user_agent:
#             chrome_options.add_argument(f'--user-agent={user_agent}')
#             self.current_user_agent = user_agent
        
#         # Set random proxy
#         proxy = self._get_random_proxy()
#         if proxy:
#             chrome_options.add_argument(f'--proxy-server={proxy}')
#             self.current_proxy = proxy
        
#         # Additional stealth options
#         chrome_options.add_argument('--disable-extensions')
#         chrome_options.add_argument('--disable-plugins-discovery')
#         chrome_options.add_argument('--disable-web-security')
#         chrome_options.add_argument('--allow-running-insecure-content')
        
#         try:
#             driver = webdriver.Chrome(options=chrome_options)
            
#             # Execute script to remove webdriver property
#             driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
#             self.driver = driver
#             self.session_start_time = datetime.now()
            
#             logger.info(f"Browser session started with proxy: {proxy or 'None'}")
#             return driver
            
#         except Exception as e:
#             logger.error(f"Failed to create Chrome driver: {e}")
#             raise
    
#     def get_driver(self) -> webdriver.Chrome:
#         """Get current driver or create new one"""
#         if self.driver is None:
#             return self.create_driver()
#         return self.driver
    
#     def refresh_session(self) -> webdriver.Chrome:
#         """Close current session and create new one with different proxy/UA"""
#         logger.info("Refreshing browser session...")
        
#         if self.driver:
#             try:
#                 self.driver.quit()
#             except:
#                 pass
        
#         self.driver = None
#         self.current_proxy = None
#         self.current_user_agent = None
        
#         return self.create_driver()
    
#     def should_refresh_session(self) -> bool:
#         """Check if session should be refreshed based on time or other criteria"""
#         if not self.session_start_time:
#             return True
        
#         # Refresh every 30 minutes to avoid detection
#         session_duration = datetime.now() - self.session_start_time
#         if session_duration > timedelta(minutes=30):
#             return True
        
#         return False
    
#     def navigate_with_retry(self, url: str, max_retries: int = 3) -> bool:
#         """Navigate to URL with retry logic"""
#         driver = self.get_driver()
        
#         for attempt in range(max_retries):
#             try:
#                 logger.info(f"Navigating to {url} (attempt {attempt + 1})")
#                 driver.get(url)
                
#                 # Wait for page to load
#                 WebDriverWait(driver, 10).until(
#                     lambda d: d.execute_script("return document.readyState") == "complete"
#                 )
                
#                 # Check for CAPTCHA or blocking
#                 if self._detect_blocking():
#                     logger.warning("Blocking detected, refreshing session...")
#                     self.refresh_session()
#                     driver = self.get_driver()
#                     continue
                
#                 return True
                
#             except TimeoutException:
#                 logger.warning(f"Navigation timeout (attempt {attempt + 1})")
#                 if attempt == max_retries - 1:
#                     return False
#                 time.sleep(2 ** attempt)  # Exponential backoff
                
#             except WebDriverException as e:
#                 logger.error(f"WebDriver error: {e}")
#                 self.refresh_session()
#                 driver = self.get_driver()
        
#         return False
    
#     def _detect_blocking(self) -> bool:
#         """Detect if we're being blocked (CAPTCHA, rate limiting, etc.)"""
#         driver = self.get_driver()
        
#         # Check for common blocking indicators
#         blocking_indicators = [
#             "captcha",
#             "blocked",
#             "access denied",
#             "rate limit",
#             "too many requests",
#             "cloudflare"
#         ]
        
#         try:
#             page_text = driver.page_source.lower()
#             for indicator in blocking_indicators:
#                 if indicator in page_text:
#                     logger.warning(f"Blocking detected: {indicator}")
#                     return True
#         except:
#             pass
        
#         return False
    
#     def wait_for_element(self, by: By, value: str, timeout: int = 10):
#         """Wait for element to be present and visible"""
#         driver = self.get_driver()
#         wait = WebDriverWait(driver, timeout)
        
#         try:
#             element = wait.until(EC.element_to_be_clickable((by, value)))
#             return element
#         except TimeoutException:
#             logger.warning(f"Element not found: {by}='{value}'")
#             return None
    
#     def safe_click(self, element, max_attempts: int = 3) -> bool:
#         """Safely click an element with retry logic"""
#         driver = self.get_driver()
        
#         for attempt in range(max_attempts):
#             try:
#                 # Scroll element into view
#                 driver.execute_script("arguments[0].scrollIntoView(true);", element)
#                 time.sleep(0.5)
                
#                 # Try regular click first
#                 element.click()
#                 return True
                
#             except Exception as e:
#                 logger.debug(f"Click attempt {attempt + 1} failed: {e}")
                
#                 if attempt == max_attempts - 1:
#                     # Last attempt - try JavaScript click
#                     try:
#                         driver.execute_script("arguments[0].click();", element)
#                         return True
#                     except:
#                         logger.error("JavaScript click also failed")
#                         return False
                
#                 time.sleep(0.5)
        
#         return False
    
#     def close(self):
#         """Close the browser session"""
#         if self.driver:
#             try:
#                 self.driver.quit()
#                 logger.info("Browser session closed")
#             except Exception as e:
#                 logger.error(f"Error closing browser: {e}")
#             finally:
#                 self.driver = None
    
#     def __enter__(self):
#         """Context manager entry"""
#         return self
    
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         """Context manager exit"""
#         self.close()

"""
Browser management for Vahan scraping
Supports plain Chrome, optional proxy, and stealth mode
"""

import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

logger = logging.getLogger("app.browser")


class BrowserManager:
    def __init__(self, headless: bool = True, use_proxy: bool = False, stealth: bool = False):
        """
        Manage browser sessions with optional proxy and stealth.
        Defaults: plain Chrome (safe for Vahan).
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
                logger.info("Browser closed")
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")

    def _create_driver(self):
        """Create Chrome WebDriver instance."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless=new")  # modern headless
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # Optional proxy (dummy example)
        if self.use_proxy:
            proxy = "http://127.0.0.1:8080"
            chrome_options.add_argument(f"--proxy-server={proxy}")
            logger.info(f"Using proxy: {proxy}")

        # Optional stealth
        if self.stealth:
            try:
                import undetected_chromedriver as uc
                logger.info("Launching undetected_chromedriver (stealth mode)")
                return uc.Chrome(options=chrome_options)
            except ImportError:
                logger.warning("undetected_chromedriver not installed, fallback to normal driver")

        # Default plain Chrome
        logger.info("Launching plain Chrome browser")
        return webdriver.Chrome(options=chrome_options)

    def get_driver(self):
        return self.driver

    def navigate_with_retry(self, url: str, retries: int = 3, delay: int = 5) -> bool:
        """Try navigating to a URL with retries."""
        for attempt in range(1, retries + 1):
            try:
                logger.info(f"Navigating to {url} (attempt {attempt}/{retries})")
                self.driver.get(url)
                time.sleep(2)  # let page load
                return True
            except WebDriverException as e:
                logger.warning(f"Navigation failed (attempt {attempt}/{retries}): {e}")
                time.sleep(delay)
        return False
