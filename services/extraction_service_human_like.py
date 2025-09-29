# services/extraction_service_human_like.py
"""
Human-like extraction service with intelligent delays and retry mechanisms
"""

import logging
import time
import random
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from selenium.common.exceptions import WebDriverException, TimeoutException
from extractor.extract_states import StateExtractor, StateData
from extractor.extract_all_rto import RTOExtractor, RTOData
from scrapper.browser import VahanBrowser
from extractor.extract_axis import AxisExtractor
from utils.helpers import sanitize_filename

logger = logging.getLogger("app.services.extraction")


import requests
from selenium.common.exceptions import WebDriverException


def _enhanced_connection_recovery(self, error_message: str) -> bool:
    """Enhanced connection recovery with network change handling"""
    logger.warning(f"Handling error: {error_message}")
    
    # Network-specific errors
    network_errors = [
        "err_network_changed", "network changed", "connection was interrupted",
        "connectionreseterror", "connection was reset", "connection timed out",
        "remote host", "connection broken", "connection refused"
    ]
    
    # Element-specific errors  
    element_errors = [
        "stale element reference", "no such element", "element not found",
        "element not interactable", "element click intercepted"
    ]
    
    # Timeout errors
    timeout_errors = [
        "timeout", "timeoutexception", "page load timeout",
        "script timeout", "element not clickable"
    ]
    
    # Detection-related errors (add these patterns)
    detection_errors = [
        "navigation blocked", "access denied", "forbidden", 
        "too many requests", "rate limit", "blocked"
    ]
    
    error_lower = error_message.lower()
    
    # Handle network changes with special care
    if any(err in error_lower for err in network_errors):
        logger.warning("Network error detected - full recovery protocol")
        return self._handle_network_change_error()
        
    elif any(err in error_lower for err in detection_errors):
        logger.warning("Possible detection - implementing stealth recovery")
        return self._handle_detection_recovery()
        
    elif any(err in error_lower for err in element_errors):
        logger.warning("Element error detected - page refresh and retry")
        return self._page_level_recovery()
        
    elif any(err in error_lower for err in timeout_errors):
        logger.warning("Timeout error detected - wait and retry")
        time.sleep(10)  # Longer wait for timeouts
        return self._page_level_recovery()
    
    else:
        logger.warning("Unknown error - attempting gentle recovery")
        return self._page_level_recovery()

def _handle_detection_recovery(self) -> bool:
    """Handle suspected bot detection"""
    logger.warning("Implementing detection recovery protocol")
    
    try:
        # Step 1: Long delay to cool down
        cooldown = random.uniform(120, 300)  # 2-5 minutes
        logger.info(f"Detection cooldown: {cooldown/60:.1f} minutes")
        time.sleep(cooldown)
        
        # Step 2: Complete browser reset
        self._complete_browser_reset()
        
        # Step 3: Change browser fingerprint
        self._rotate_browser_profile()
        
        # Step 4: Reinitialize with stealth mode
        return self._initialize_browser_with_retry()
        
    except Exception as e:
        logger.error(f"Detection recovery failed: {e}")
        return False

def _enhanced_browser_initialization(self) -> bool:
    """Enhanced browser initialization with better stealth"""
    try:
        # Use rotated user agent if available
        user_agent = getattr(self, 'current_user_agent', None)
        
        # Initialize with enhanced stealth
        self.browser = VahanBrowser(
            headless=False, 
            use_proxy=False, 
            stealth=True,
            user_agent=user_agent  # You'll need to add this parameter to VahanBrowser
        )
        
        # Add extra stealth measures
        if hasattr(self.browser, 'driver'):
            # Disable webdriver detection
            self.browser.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            # Add realistic viewport size
            self.browser.driver.set_window_size(1920, 1080)
            
            # Add human-like mouse movements (if your browser supports it)
            try:
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(self.browser.driver)
                # Move mouse to random position
                actions.move_by_offset(random.randint(100, 500), random.randint(100, 300))
                actions.perform()
            except:
                pass
        
        return True
        
    except Exception as e:
        logger.error(f"Enhanced browser initialization failed: {e}")
        return False

# Update your existing methods to use the enhanced error handling

def _initialize_browser_with_retry(self) -> bool:
    """Initialize browser with enhanced retry logic"""
    axis_extractor = AxisExtractor()
    labels = axis_extractor.get_current_axis_labels()
    y_axis_from_db = labels["Y"]
    x_axis_from_db = labels["X"]

    for attempt in range(self.config.delay_config.max_retries):
        try:
            logger.info(f"Initializing browser (attempt {attempt+1})")

            if self.browser:
                self.browser.quit()

            # Use enhanced initialization
            if not self._enhanced_browser_initialization():
                raise Exception("Enhanced browser initialization failed")
            
            self.browser.setup()

            if not self.browser.navigate_to_portal():
                raise Exception("Navigation failed")

            # Longer delay after navigation
            self.behavior_sim.human_delay("between_actions", "after portal navigation")

            if not self.browser.set_axis_and_verify(y_axis_from_db, x_axis_from_db):
                raise Exception(f"Failed to set axes from DB. Y='{y_axis_from_db}', X='{x_axis_from_db}'")

            self.behavior_sim.human_delay("after_dropdown_select", "after setting axis")
            logger.info("Browser initialized successfully")
            
            self.config.y_axis = y_axis_from_db
            self.config.x_axis = x_axis_from_db
            return True

        except Exception as e:
            logger.error(f"Browser initialization attempt {attempt+1} failed: {e}")
            
            # Use enhanced connection recovery
            if not self._enhanced_connection_recovery(str(e)):
                logger.error("Enhanced recovery failed")
                if not self.recovery_manager.should_retry():
                    break

    return False


@dataclass
class HumanLikeDelayConfig:
    """Configuration for human-like delays"""
    # Base delays (in seconds)
    between_actions: tuple = (2, 5)          # Between small actions
    after_dropdown_select: tuple = (1, 3)    # After selecting dropdowns
    after_filter_apply: tuple = (3, 6)       # After applying filters
    after_download: tuple = (2, 4)           # After downloading files
    between_rtos: tuple = (6, 10)            # Between RTO processing
    between_states: tuple = (45, 90)         # Between states (in seconds)
    
    # Retry delays (exponential backoff)
    retry_delays: tuple = (10, 20)        # 5s, 10s, 20s for retries
    max_retries: int = 2
    
    # Random behavior simulation
    random_pause_chance: float = 0.25         # 10% chance of random pause
    random_pause_duration: tuple = (3, 8)    # Random pause duration

    consecutive_failure_threshold: int = 3


class ConnectionRecoveryManager:
    """Manages connection recovery and retry logic"""
    
    def __init__(self, delay_config: HumanLikeDelayConfig):
        self.config = delay_config
        self.retry_count = 0
        self.last_error_time = None
        self.consecutive_errors = 0
        
    def should_retry(self) -> bool:
        """Check if we should retry after an error"""
        return self.retry_count < self.config.max_retries
    
    def get_retry_delay(self) -> float:
        """Get delay for current retry attempt"""
        if self.retry_count < len(self.config.retry_delays):
            return self.config.retry_delays[self.retry_count]
        else:
            # If we've exhausted predefined delays, use exponential backoff
            return self.config.retry_delays[-1] * (2 ** (self.retry_count - len(self.config.retry_delays) + 1))
    
    def record_error(self):
        """Record an error occurrence"""
        self.retry_count += 1
        self.consecutive_errors += 1
        self.last_error_time = datetime.now()
        
        delay = self.get_retry_delay()
        logger.warning(f"Connection error #{self.retry_count}. Waiting {delay}s before retry...")
        time.sleep(delay)
    
    def record_success(self):
        """Record a successful operation"""
        self.retry_count = 0
        self.consecutive_errors = 0
    
    def is_blocked(self) -> bool:
        """Check if we might be blocked"""
        return self.consecutive_errors >= self.config.max_retries


class HumanLikeBehaviorSimulator:
    """Simulates human-like behavior patterns"""
    
    def __init__(self, delay_config: HumanLikeDelayConfig):
        self.config = delay_config
        self.action_count = 0
    
    def human_delay(self, delay_type: str, context: str = ""):
        """Apply human-like delay with variation"""
        delay_range = getattr(self.config, delay_type, self.config.between_actions)
        
        # Add slight variation to make delays less predictable
        base_delay = random.uniform(*delay_range)
        
        # Add micro-variations (human hesitation)
        micro_variation = random.uniform(-0.5, 0.5)
        actual_delay = max(0.5, base_delay + micro_variation)
        
        logger.info(f"Human delay ({delay_type}): {actual_delay:.1f}s {context}")
        time.sleep(actual_delay)
        
        self.action_count += 1
        
        # Random pauses to simulate human behavior
        if random.random() < self.config.random_pause_chance:
            self._random_pause()
    
    def _random_pause(self):
        """Simulate random human pause (checking phone, thinking, etc.)"""
        pause_duration = random.uniform(*self.config.random_pause_duration)
        logger.info(f"Random human pause: {pause_duration:.1f}s (simulating human behavior)")
        time.sleep(pause_duration)
    
    def between_states_delay(self, current_state: str, next_state: str):
        """Longer delay between states"""
        delay = random.uniform(*self.config.between_states)
        minutes = delay / 60
        logger.info(f"Between states delay: {minutes:.1f} minutes (from {current_state} to {next_state})")
        time.sleep(delay)


@dataclass
class ExtractionConfig:
    """Enhanced configuration for human-like extraction"""
    y_axis: str = "Maker"
    x_axis: str = "Month Wise"
    apply_vehicle_filter: bool = True
    vehicle_filter_categories: List[List[str]] = None  # Changed to list of lists
    output_directory: str = None
    delay_config: HumanLikeDelayConfig = None
    
    def __post_init__(self):
        if self.vehicle_filter_categories is None:
            # Separate filters to apply sequentially
            self.vehicle_filter_categories = [
                ["MOTOR CAR", "MOTOR CAB"],      # First filter set
                ["ELECTRIC(BOV)", "PURE EV"]     # Second filter set
            ]
        
        if self.output_directory is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_directory = f"vahan_extraction_human_{timestamp}"
        
        if self.delay_config is None:
            self.delay_config = HumanLikeDelayConfig()


class HumanLikeExtractionService:
    """Extraction service with human-like behavior simulation"""
    
    def __init__(self, config: ExtractionConfig = None):
        self.config = config or ExtractionConfig()
        self.behavior_sim = HumanLikeBehaviorSimulator(self.config.delay_config)
        self.recovery_manager = ConnectionRecoveryManager(self.config.delay_config)
        
        # Extractors
        self.state_extractor = StateExtractor()
        self.rto_extractor = RTOExtractor()
        
        # Browser
        self.browser = None
        self.browser_restarts = 0
        
        logger.info("HumanLikeExtractionService initialized")
        logger.info(f"Vehicle filter sets: {len(self.config.vehicle_filter_categories)}")
    
    def start_extraction(self, specific_states: List[str] = None) -> Dict:
        """Start human-like extraction"""
        start_time = datetime.now()
        logger.info(f"Starting human-like extraction at {start_time}")
        
        try:
            # Get states to process
            active_states = self.state_extractor.extract_active_states()
            if specific_states:
                active_states = [s for s in active_states if s.code in specific_states]
            
            if not active_states:
                raise ValueError("No states to process")
            
            logger.info(f"Will process {len(active_states)} states with human-like behavior")
            
            # Setup
            output_dir = self._setup_output_directory()
            
            # Initialize browser with retry
            if not self._initialize_browser_with_retry():
                raise Exception("Failed to initialize browser after retries")
            
            # Process states
            state_results = []
            
            for idx, state in enumerate(active_states):
                print(f"\n{'='*70}")
                print(f"PROCESSING STATE {idx+1}/{len(active_states)}: {state.name}")
                print(f"{'='*70}")
                
                try:
                    # Between states delay (except first)
                    if idx > 0:
                        prev_state = active_states[idx-1].name
                        self.behavior_sim.between_states_delay(prev_state, state.name)
                    
                    # Process state
                    state_result = self._process_state_with_human_behavior(state, output_dir)
                    state_results.append(state_result)
                    
                    # Record success
                    self.recovery_manager.record_success()
                    
                    print(f"State {state.name} completed: {state_result['successful_downloads']} files")
                    
                except Exception as e:
                    logger.error(f"Error processing state {state.name}: {e}")
                    
                    # Try to recover
                    if self._handle_error_and_recover(str(e)):
                        logger.info("Recovered from error, continuing...")
                        continue
                    else:
                        logger.error("Could not recover from error, stopping extraction")
                        break
            
            # Generate summary
            end_time = datetime.now()
            summary = self._generate_summary(state_results, start_time, end_time)
            
            logger.info("Extraction completed")
            return summary
            
        finally:
            self._cleanup_browser()
    
    def _process_state_with_human_behavior(self, state: StateData, output_dir: str) -> Dict:
        """Process state with human-like behavior"""
        start_time = datetime.now()
        
        # Setup browser for state
        if not self._setup_browser_for_state_with_retry(state):
            raise Exception(f"Failed to setup browser for state: {state.name}")
        
        # Get RTOs
        rtos = self.rto_extractor.extract_rtos_by_state_id(state.id)
        logger.info(f"Found {len(rtos)} RTOs for {state.name}")
        
        if not rtos:
            return self._create_empty_state_result(state, start_time)
        
        # Create output directory
        state_dir = os.path.join(output_dir, sanitize_filename(f"{state.code}_{state.name}"))
        os.makedirs(state_dir, exist_ok=True)
        
        # Process RTOs with human behavior
        excel_files = []
        errors = []
        successful_downloads = 0
        failed_downloads = 0
        
        for idx, rto in enumerate(rtos):
            print(f"Processing RTO {idx+1}/{len(rtos)}: {rto.name}")
            
            try:
                # Delay between RTOs (human reading/thinking time)
                if idx > 0:
                    self.behavior_sim.human_delay("between_rtos", f"before processing {rto.name}")
                
                # Process RTO with human behavior
                rto_files = self._process_rto_with_human_behavior(rto, state_dir)
                
                if rto_files:
                    excel_files.extend(rto_files)
                    successful_downloads += len(rto_files)
                    logger.info(f"Downloaded {len(rto_files)} files for {rto.name}")
                    
                    # Record success
                    self.recovery_manager.record_success()
                else:
                    failed_downloads += 1
                    errors.append(f"No data for {rto.name}")
                    print(f"No data found for {rto.name}")
                
            except Exception as e:
                failed_downloads += 1
                error_msg = f"Error processing {rto.name}: {str(e)[:200]}"
                errors.append(error_msg)
                logger.error(error_msg)
                
                # Try to recover for next RTO
                if not self._handle_error_and_recover(str(e)):
                    logger.warning("Could not recover, skipping remaining RTOs in this state")
                    break
        
        end_time = datetime.now()
        
        return {
            'state': state,
            'total_rtos': len(rtos),
            'successful_downloads': successful_downloads,
            'failed_downloads': failed_downloads,
            'excel_files': excel_files,
            'errors': errors,
            'start_time': start_time,
            'end_time': end_time,
            'duration_minutes': (end_time - start_time).total_seconds() / 60
        }
    
    def _process_rto_with_human_behavior(self, rto: RTOData, state_dir: str) -> List[str]:
        """Process single RTO with human-like behavior"""
        excel_files = []
        
        # Select RTO
        if not self._select_rto_with_retry(rto):
            raise Exception(f"Failed to select RTO: {rto.name} after 2 attempts, skipping...")
        
        # Human delay after selection
        self.behavior_sim.human_delay("after_dropdown_select", f"after selecting {rto.name}")
        
        # Refresh data
        if not self._refresh_with_retry():
            logger.warning(f"Refresh failed for {rto.name}")
            return excel_files
        
        # Human delay after refresh
        self.behavior_sim.human_delay("between_actions", "after refresh")
        
       # Continue with rest of the processing...
        try:
            if not self._refresh_with_retry():
                logger.warning(f"Refresh failed for {rto.name}")
                return excel_files
            
            self.behavior_sim.human_delay("between_actions", "after refresh")

            if self.config.apply_vehicle_filter:
                for filter_idx, filter_set in enumerate(self.config.vehicle_filter_categories):
                    filter_name = f"filter_{filter_idx+1}"
                    
                    try:
                        logger.info(f"Applying filter set {filter_idx+1}: {filter_set}")

                        if not self._apply_filter_with_retry(filter_set):
                            logger.warning(f"Failed to apply filter {filter_set}")
                            continue
                        
                        # Human delay after applying filter (reading results)
                        self.behavior_sim.human_delay("after_filter_apply", f"after applying {filter_set}")
                        
                        # Check if data exists
                        if not self.browser.check_data_exists():
                            logger.info(f"No data for {rto.name} with filter {filter_set}")
                            continue
                        
                        self.behavior_sim.human_delay("between_actions", "before download")
                        
                        # Download with retry
                        filename = self._generate_filename(rto, filter_name)
                        if self._download_with_retry(state_dir, filename):
                            excel_files.append(filename)
                            logger.info(f"Downloaded: {filename}")
                            
                            # Human delay after download
                            self.behavior_sim.human_delay("after_download", f"after downloading {filename}")
                        
                    except Exception as e:
                        logger.error(f"Error with filter {filter_set}: {e}")
                        continue
            else:
                # No filter - just download
                if self.browser.check_data_exists():
                    filename = self._generate_filename(rto)
                    if self._download_with_retry(state_dir, filename):
                        excel_files.append(filename)
                        logger.info(f"Downloaded: {filename}")
            
            return excel_files
            
        except Exception as e:
            logger.error(f"Error processing RTO {rto.name}: {e}")
            return excel_files

    
    def _initialize_browser_with_retry(self) -> bool:
        """Initialize browser with retry logic"""
        # Pull DB axis labels once outside the retry loop
        axis_extractor = AxisExtractor()
        labels = axis_extractor.get_current_axis_labels()
        y_axis_from_db = labels["Y"]
        x_axis_from_db = labels["X"]

        for attempt in range(self.config.delay_config.max_retries):
            try:
                logger.info(f"Initializing browser (attempt {attempt+1})")

                if self.browser:
                    self.browser.quit()

                self.browser = VahanBrowser(headless=False, use_proxy=False, stealth=True)
                self.browser.setup()

                if not self.browser.navigate_to_portal():
                    raise Exception("Navigation failed")

                self.behavior_sim.human_delay("between_actions", "after portal navigation")

                # Use DB values + verify
                if not self.browser.set_axis_and_verify(y_axis_from_db, x_axis_from_db):
                    raise Exception(
                        f"Failed to set axes from DB. Y='{y_axis_from_db}', X='{x_axis_from_db}'"
                    )

                self.behavior_sim.human_delay("after_dropdown_select", "after setting axis")
                logger.info("Browser initialized successfully")
                # Update config for visibility/logging
                self.config.y_axis = y_axis_from_db
                self.config.x_axis = x_axis_from_db
                return True

            except Exception as e:
                logger.error(f"Browser initialization attempt {attempt+1} failed: {e}")
                self.recovery_manager.record_error()
                if not self.recovery_manager.should_retry():
                    break

        return False
    
    def _setup_browser_for_state_with_retry(self, state: StateData) -> bool:
        """Setup browser for state with retry logic"""
        for attempt in range(self.config.delay_config.max_retries):
            try:
                state_name = getattr(state, "display_name", state.name)
                logger.info(f"Selecting state: {state_name} (attempt {attempt+1})")
                
                if not self.browser.select_state(state_name):
                    raise Exception(f"Failed to select state: {state_name}")
                
                # Human delay after state selection
                self.behavior_sim.human_delay("after_dropdown_select", f"after selecting {state_name}")

                self.browser.ensure_axes()
                
                logger.info(f"State {state_name} selected successfully")
                return True
                
            except Exception as e:
                logger.error(f"State selection attempt {attempt+1} failed: {e}")
                self.recovery_manager.record_error()
                
                if not self.recovery_manager.should_retry():
                    break
                    
                # Try to recover browser
                if not self._initialize_browser_with_retry():
                    break
        
        return False
    
    def _select_rto_with_retry(self, rto: RTOData) -> bool:
        """Select RTO with retry logic"""
        for attempt in range(self.config.delay_config.max_retries):
            try:
                rto_text = rto.full_text or rto.name
                
                if self.browser.select_rto(rto_text):
                    self.browser.ensure_axes()
                    return True
                else:
                    raise Exception("RTO selection failed")
                    
            except Exception as e:
                logger.warning(f"RTO selection attempt {attempt+1} failed: {e}")
                if attempt < self.config.delay_config.max_retries - 1:
                    time.sleep(2)  # Short delay before retry
        
        return False
    
    def _refresh_with_retry(self) -> bool:
        """Refresh with retry logic"""
        for attempt in range(self.config.delay_config.max_retries):
            try:
                if self.browser.click_refresh():
                    self.browser.ensure_axes()
                    return True
                else:
                    raise Exception("Refresh failed")
                    
            except Exception as e:
                logger.warning(f"Refresh attempt {attempt+1} failed: {e}")
                if attempt < self.config.delay_config.max_retries - 1:
                    time.sleep(2)
        
        return False
    
    def _apply_filter_with_retry(self, filter_categories: List[str]) -> bool:
        """Apply filter with retry logic"""
        for attempt in range(self.config.delay_config.max_retries):
            try:
                if self.browser.apply_vehicle_filter(filter_categories):
                    return True
                else:
                    raise Exception("Filter application failed")
                    
            except Exception as e:
                logger.warning(f"Filter application attempt {attempt+1} failed: {e}")
                if attempt < self.config.delay_config.max_retries - 1:
                    time.sleep(2)
        
        return False
    
    def _download_with_retry(self, output_dir: str, filename: str) -> bool:
        """Download with retry logic"""
        for attempt in range(self.config.delay_config.max_retries):
            try:
                if self.browser.download_excel(output_dir, filename):
                    return True
                else:
                    raise Exception("Download failed")
                    
            except Exception as e:
                logger.warning(f"Download attempt {attempt+1} failed: {e}")
                if attempt < self.config.delay_config.max_retries - 1:
                    time.sleep(3)  # Longer delay for download retries
        
        return False
    
    def _handle_error_and_recover(self, error_message: str) -> bool:
        """Handle errors and attempt recovery"""
        logger.warning(f"Handling error: {error_message}")

        error_lower = error_message.lower()

        if "err_network_changed" in error_lower or "network changed" in error_lower:
            logger.warning("Network change error - implementing full recovery")
            return self._handle_network_change_error()
        
        # Check for connection issues
        connection_errors = [
            "connectionreseterror",
            "connection was reset", 
            "connection timed out",
            "stale element reference",
            "no such element",
            "failed to slect rto"
        ]
        
        is_connection_error = any(err in error_message.lower() for err in connection_errors)
        
        if is_connection_error:
            logger.warning("Connection error detected, attempting browser restart")
            self.recovery_manager.record_error()
            
            if not self.recovery_manager.should_retry():
                logger.error("Max retries exceeded, cannot recover")
                return False
            
            # Try to restart browser
            return self._initialize_browser_with_retry()
        else:
            # Other errors - just record and continue
            logger.warning("Non-connection error, continuing...")
            return True
        
    def _handle_network_change_error(self) -> bool:
        """Handle ERR_NETWORK_CHANGED and similar network errors"""
        logger.warning("Network change detected - implementing recovery strategy")
    
        try:
        # Step 1: Wait for network to stabilize
            self._wait_for_network_stability()
        
        # Step 2: Clear browser state completely
            self._complete_browser_reset()
        
        # Step 3: Change user agent and clear cache
            self._rotate_browser_profile()
        
        # Step 4: Wait longer before reconnecting
            backoff_delay = random.uniform(30, 60)  # 30-60 seconds
            logger.info(f"Network recovery delay: {backoff_delay:.1f} seconds")
            time.sleep(backoff_delay)
        
        # Step 5: Reinitialize with new session
            return self._initialize_browser_with_retry()
        
        except Exception as e:
            logger.error(f"Network change recovery failed: {e}")
            return False

    def _wait_for_network_stability(self, max_attempts: int = 5):
        """Wait for network connection to stabilize"""
        vahan_url = "https://vahan.parivahan.gov.in"
    
        for attempt in range(max_attempts):
            try:
                response = requests.get(vahan_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
            
                if response.status_code == 200:
                    logger.info(f"Network stability confirmed (attempt {attempt + 1})")
                    return True
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Network stability check failed (attempt {attempt + 1}): {e}")
                if attempt < max_attempts - 1:
                    time.sleep(5)
    
        logger.warning("Network stability could not be confirmed")
        return False

    def _complete_browser_reset(self):
        """Complete browser reset including cache and cookies"""
        try:
            if self.browser and hasattr(self.browser, 'driver'):
            # Clear all cookies
                self.browser.driver.delete_all_cookies()
            
            # Clear local storage
                self.browser.driver.execute_script("window.localStorage.clear();")
            
            # Clear session storage
                self.browser.driver.execute_script("window.sessionStorage.clear();")
            
            # Clear browser cache (if supported)
                try:
                    self.browser.driver.execute_cdp_cmd('Network.clearBrowserCache', {})
                except:
                    pass
            
        # Close browser completely
            if self.browser:
                self.browser.quit()
                self.browser = None
            
            logger.info("Complete browser reset performed")
        
        except Exception as e:
            logger.warning(f"Browser reset had issues: {e}")
    
    def _rotate_browser_profile(self):
        """Rotate browser profile to appear as different user"""
    # This will be used in the next browser initialization
        self.current_user_agent = self._get_random_user_agent()
        logger.info("Browser profile rotation prepared")

    def _get_random_user_agent(self) -> str:
        """Get a random user agent string"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebFor/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]
        return random.choice(user_agents)
    
    def _generate_filename(self, rto: RTOData, filter_suffix: str = None) -> str:
        """Generate filename for download"""
        safe_name = sanitize_filename(rto.name)[:30]
        axis_part = f"{self.config.y_axis.lower()}_{self.config.x_axis.lower().replace(' ', '_')}"
        
        if filter_suffix:
            axis_part += f"_{filter_suffix}"
        
        return f"{rto.code}_{safe_name}_{axis_part}.xlsx"
    
    def _setup_output_directory(self) -> str:
        """Setup output directory"""
        output_dir = os.path.join("result", self.config.output_directory)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def _cleanup_browser(self):
        """Cleanup browser resources"""
        if self.browser:
            try:
                self.browser.quit()
            except:
                pass
            self.browser = None
    
    def _create_empty_state_result(self, state: StateData, start_time: datetime) -> Dict:
        """Create empty result for states with no RTOs"""
        return {
            'state': state,
            'total_rtos': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'excel_files': [],
            'errors': ["No RTOs found"],
            'start_time': start_time,
            'end_time': datetime.now(),
            'duration_minutes': 0
        }
    
    def _generate_summary(self, results: List[Dict], start_time: datetime, end_time: datetime) -> Dict:
        """Generate extraction summary"""
        total_files = sum(r['successful_downloads'] for r in results)
        total_rtos = sum(r['total_rtos'] for r in results)
        duration = (end_time - start_time).total_seconds() / 60
        
        return {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_minutes': round(duration, 2),
            'states_processed': len(results),
            'total_rtos': total_rtos,
            'files_downloaded': total_files,
            'success_rate': round((total_files / total_rtos * 100) if total_rtos > 0 else 0, 2),
            'browser_restarts': self.browser_restarts,
            'state_results': [
                {
                    'state_name': r['state'].name,
                    'state_code': r['state'].code,
                    'files_downloaded': r['successful_downloads'],
                    'total_rtos': r['total_rtos']
                }
                for r in results
            ]
        }


# Main function to start human-like extraction
def start_human_like_extraction(states: List[str] = None) -> Dict:
    """
    Start extraction with human-like behavior
    
    Args:
        states: List of state codes to process (None = all states)
    
    Returns:
        Extraction summary
    """
    config = ExtractionConfig()
    service = HumanLikeExtractionService(config)
    return service.start_extraction(states)


if __name__ == "__main__":
    print("Starting human-like extraction...")
    print("This will simulate human behavior with realistic delays and retry logic")
    
    # Test with just one state first
    summary = start_human_like_extraction(['DL'])  # Just Delhi for testing
    
    print(f"\nExtraction completed!")
    print(f"Files downloaded: {summary['files_downloaded']}")
    print(f"Duration: {summary['duration_minutes']:.1f} minutes")
    print(f"Success rate: {summary['success_rate']}%")