"""
Stealth Selenium Scraper with Advanced Anti-Detection
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class StealthScraper:
    """Stealth scraper with advanced anti-detection measures"""
    
    def __init__(self, headless=True):
        self.driver = self._setup_stealth_driver(headless)
        self.wait = WebDriverWait(self.driver, 10)
        
    def _setup_stealth_driver(self, headless=True):
        """Setup Chrome driver with maximum stealth settings"""
        options = Options()
        
        if headless:
            options.add_argument("--headless=new")  # Use new headless mode
        
        # Maximum anti-detection settings
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-prompt-on-repost")
        options.add_argument("--disable-domain-reliability")
        options.add_argument("--disable-component-extensions-with-background-pages")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-translate")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--mute-audio")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-permissions-api")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        
        # Remove automation indicators
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("detach", True)
        
        # Realistic user agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        options.add_argument(f"--user-agent={user_agent}")
        
        # Additional preferences
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "geolocation": 2,
                "media_stream": 2,
                "camera": 2,
                "microphone": 2
            },
            "profile.managed_default_content_settings": {
                "images": 1  # Allow images
            },
            "profile.default_content_settings": {
                "popups": 0
            }
        }
        options.add_experimental_option("prefs", prefs)
        
        try:
            driver = webdriver.Chrome(options=options)
            
            # Remove webdriver property and add realistic properties
            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
            """)
            
            driver.execute_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """)
            
            driver.execute_script("""
                Object.defineProperty(navigator, 'permissions', {
                    get: () => undefined,
                });
            """)
            
            # Set realistic window size
            driver.set_window_size(1920, 1080)
            
            return driver
            
        except Exception as e:
            logger.error(f"Failed to setup stealth driver: {e}")
            raise
    
    def search_google(self, query: str) -> bool:
        """Search Google with stealth measures"""
        try:
            # Use DuckDuckGo instead of Google to avoid detection
            search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
            logger.info(f"Searching DuckDuckGo for: {query}")
            
            self.driver.get(search_url)
            self._human_delay()
            
            # Check if we got blocked
            current_url = self.driver.current_url
            if 'sorry' in current_url or 'blocked' in current_url:
                logger.warning("Got blocked, trying alternative approach")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return False
    
    def find_crunchbase_links(self, company_name: str) -> List[str]:
        """Find Crunchbase links using stealth search"""
        try:
            # Try DuckDuckGo first
            if self.search_google(f"crunchbase {company_name}"):
                return self._extract_crunchbase_links()
            
            # Fallback to direct Crunchbase search
            logger.info("Trying direct Crunchbase search")
            crunchbase_url = f"https://www.crunchbase.com/search/organizations/field/organizations/num_employees_org/{company_name}"
            self.driver.get(crunchbase_url)
            self._human_delay()
            
            return self._extract_crunchbase_links()
            
        except Exception as e:
            logger.error(f"Error finding Crunchbase links: {e}")
            return []
    
    def find_linkedin_links(self, company_name: str) -> List[str]:
        """Find LinkedIn company links using stealth search"""
        try:
            # Try DuckDuckGo first
            if self.search_google(f"linkedin {company_name} company"):
                return self._extract_linkedin_links()
            
            # Fallback to direct LinkedIn search
            logger.info("Trying direct LinkedIn search")
            linkedin_url = f"https://www.linkedin.com/search/results/companies/?keywords={company_name}"
            self.driver.get(linkedin_url)
            self._human_delay()
            
            return self._extract_linkedin_links()
            
        except Exception as e:
            logger.error(f"Error finding LinkedIn links: {e}")
            return []
    
    def _extract_crunchbase_links(self) -> List[str]:
        """Extract Crunchbase links from current page"""
        links = []
        try:
            # Find all links
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in all_links:
                href = link.get_attribute('href')
                if href and 'crunchbase.com' in href and 'google.com' not in href:
                    links.append(href)
                    logger.info(f"Found Crunchbase link: {href}")
            
        except Exception as e:
            logger.error(f"Error extracting Crunchbase links: {e}")
        
        return links
    
    def _extract_linkedin_links(self) -> List[str]:
        """Extract LinkedIn company links from current page"""
        links = []
        try:
            # Find all links
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in all_links:
                href = link.get_attribute('href')
                if href and 'linkedin.com/company' in href and 'google.com' not in href:
                    links.append(href)
                    logger.info(f"Found LinkedIn company link: {href}")
            
        except Exception as e:
            logger.error(f"Error extracting LinkedIn links: {e}")
        
        return links
    
    def _human_delay(self):
        """Add human-like delays"""
        time.sleep(random.uniform(2, 5))
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()
