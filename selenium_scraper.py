"""
Core Selenium Web Scraping Framework for Company Data Collection
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import re
import random
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class CompanyMetrics:
    """Data structure for company metrics"""
    name: str
    funding_raised: Optional[float] = None
    valuation: Optional[float] = None
    revenue: Optional[float] = None
    employees: Optional[int] = None
    founded_year: Optional[int] = None
    ceo: Optional[str] = None
    founders: List[str] = None
    investors: List[str] = None
    market_cap: Optional[float] = None
    profit_loss: Optional[float] = None
    growth_rate: Optional[float] = None
    funding_rounds: List[Dict] = None
    competitors: List[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    
    def __post_init__(self):
        if self.founders is None:
            self.founders = []
        if self.investors is None:
            self.investors = []
        if self.funding_rounds is None:
            self.funding_rounds = []
        if self.competitors is None:
            self.competitors = []

class SeleniumCompanyScraper:
    """Base class for Selenium-based company data scraping"""
    
    def __init__(self, headless=True, wait_timeout=10):
        self.driver = self._setup_driver(headless)
        self.wait = WebDriverWait(self.driver, wait_timeout)
        self.delay_range = (1, 3)
        
    def _setup_driver(self, headless=True):
        """Setup Chrome driver with optimal settings"""
        options = Options()
        if headless:
            options.add_argument("--headless")
        
        # Anti-detection settings
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Randomize viewport
            driver.set_window_size(
                random.randint(1200, 1920), 
                random.randint(800, 1080)
            )
            
            return driver
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise
    
    def human_like_scroll(self):
        """Simulate human-like scrolling"""
        for i in range(random.randint(3, 6)):
            self.driver.execute_script(f"window.scrollTo(0, {i * 200});")
            time.sleep(random.uniform(0.5, 1.5))
    
    def random_mouse_movement(self):
        """Simulate random mouse movements"""
        actions = ActionChains(self.driver)
        for _ in range(random.randint(2, 5)):
            x_offset = random.randint(-100, 100)
            y_offset = random.randint(-100, 100)
            actions.move_by_offset(x_offset, y_offset)
            actions.perform()
            time.sleep(random.uniform(0.1, 0.3))
    
    def random_delay(self):
        """Add random delay to mimic human behavior"""
        time.sleep(random.uniform(self.delay_range[0], self.delay_range[1]))
    
    def safe_click(self, element):
        """Safely click an element with error handling"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            element.click()
            return True
        except Exception as e:
            logger.warning(f"Failed to click element: {e}")
            return False
    
    def navigate_with_retry(self, url: str, max_retries: int = 3):
        """Navigate to URL with retry logic"""
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                return True
            except Exception as e:
                logger.warning(f"Navigation failed (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(random.uniform(2, 5))
        return False

    def wait_and_find(self, by, value, timeout: int = 10, retries: int = 3):
        """Wait for and find an element with retry logic"""
        for attempt in range(retries):
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
                return element
            except TimeoutException:
                logger.warning(f"Element not found (attempt {attempt + 1}/{retries}): {value}")
                time.sleep(1)
        return None

    def extract_text_safely(self, selector: str, default: str = "") -> str:
        """Safely extract text from an element with retry"""
        try:
            element = self.wait_and_find(By.CSS_SELECTOR, selector, timeout=5, retries=2)
            if element:
                return element.text.strip()
            return default
        except Exception:
            return default
    
    def extract_multiple_text(self, selector: str) -> List[str]:
        """Extract text from multiple elements"""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            return [elem.text.strip() for elem in elements if elem.text.strip()]
        except NoSuchElementException:
            return []
    
    def parse_funding_amount(self, text: str) -> Optional[float]:
        """Parse funding amount from text"""
        if not text:
            return None
        
        # Remove common prefixes/suffixes
        text = re.sub(r'[^\d.,$MBK]', '', text.upper())
        
        # Extract number and multiplier
        amount_match = re.search(r'[\d,]+\.?\d*', text)
        if not amount_match:
            return None
        
        amount = float(amount_match.group().replace(',', ''))
        
        # Apply multiplier
        if 'B' in text:
            amount *= 1_000_000_000
        elif 'M' in text:
            amount *= 1_000_000
        elif 'K' in text:
            amount *= 1_000
        
        return amount
    
    def parse_employee_count(self, text: str) -> Optional[int]:
        """Parse employee count from text"""
        if not text:
            return None
        
        # Extract numbers
        numbers = re.findall(r'\d+', text.replace(',', ''))
        if numbers:
            return int(numbers[0])
        return None
    
    def parse_year(self, text: str) -> Optional[int]:
        """Parse year from text"""
        if not text:
            return None
        
        # Look for 4-digit year
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        if year_match:
            return int(year_match.group())
        return None
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
