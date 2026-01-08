"""
Crunchbase Web Scraper for Company Data Collection
"""

from selenium_scraper import SeleniumCompanyScraper, CompanyMetrics
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import time
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class CrunchbaseScraper(SeleniumCompanyScraper):
    """Crunchbase-specific scraper for company data"""
    
    def __init__(self, headless=True):
        super().__init__(headless)
        self.base_url = "https://www.crunchbase.com"
        
    def scrape_company_data(self, company_name: str) -> Dict:
        """Scrape comprehensive company data from Crunchbase"""
        logger.info(f"Starting Crunchbase scraping for: {company_name}")
        
        try:
            # Search for company
            search_url = f"{self.base_url}/discover/organization.companies"
            if not self.navigate_with_retry(search_url):
                return {"error": "Failed to navigate to Crunchbase search"}
            self.random_delay()
            
            # Try multiple approaches to find search functionality
            search_box = None
            
            # Method 1: Look for search input fields
            search_selectors = [
                "input[data-test='search-input']",
                "input[placeholder*='Search']",
                "input[type='search']",
                ".search-input",
                "#search-input",
                "input[name='q']",
                "input[class*='search']",
                "input[placeholder*='company']",
                "input[placeholder*='organization']"
            ]
            
            for selector in search_selectors:
                try:
                    search_box = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Found search box with selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            # Method 2: Try direct URL search
            if not search_box:
                logger.info("Trying direct URL search approach")
                search_urls = [
                    f"{self.base_url}/discover/organization.companies?q={company_name}",
                    f"{self.base_url}/search?q={company_name}",
                    f"{self.base_url}/organization/{company_name.lower().replace(' ', '-')}",
                    f"{self.base_url}/organization/{company_name.lower().replace(' ', '')}"
                ]
                
                for search_url in search_urls:
                    try:
                        logger.info(f"Trying Crunchbase URL: {search_url}")
                        if not self.navigate_with_retry(search_url):
                            continue
                        self.random_delay()
                        
                        # Look for results on the search results page
                        result_selectors = [
                            ".search-results", ".results", ".entity-result", 
                            ".search-result", ".company-card", ".organization-card",
                            "[data-test='search-result']", ".result-item"
                        ]
                        
                        for selector in result_selectors:
                            try:
                                results = self.wait.until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                                )
                                if results:
                                    logger.info(f"Found search results via direct URL with selector: {selector}")
                                    # Extract data from search results page
                                    return self._extract_from_search_results(company_name)
                            except TimeoutException:
                                continue
                                
                    except Exception as e:
                        logger.warning(f"Failed with URL {search_url}: {e}")
                        continue
            
            if not search_box:
                logger.warning("Could not find search box or search results")
                return {"error": "Search functionality not accessible"}
            
            # Perform search
            search_box.clear()
            search_box.send_keys(company_name)
            search_box.submit()
            self.random_delay()
            
            # Look for company results
            company_selectors = [
                "a[data-test='company-name']",
                ".search-result-name a",
                ".company-name a",
                "a[href*='/organization/']"
            ]
            
            company_link = None
            for selector in company_selectors:
                try:
                    company_link = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not company_link:
                logger.warning(f"No company found for: {company_name}")
                return {"error": f"Company '{company_name}' not found on Crunchbase"}
            
            # Click on first result
            company_url = company_link.get_attribute('href')
            if not self.navigate_with_retry(company_url):
                return {"error": "Failed to navigate to company page"}
            self.random_delay()
            
            # Extract comprehensive data
            company_data = self._extract_company_metrics(company_name)
            logger.info(f"Successfully scraped data for: {company_name}")
            
            return company_data
            
        except Exception as e:
            logger.error(f"Error scraping Crunchbase for {company_name}: {e}")
            return {"error": str(e)}
    
    def _extract_company_metrics(self, company_name: str) -> Dict:
        """Extract specific metrics from Crunchbase company page"""
        metrics = {"name": company_name}
        
        # Company description
        description_selectors = [
            ".description",
            ".company-description",
            "[data-test='company-description']",
            ".overview-section p"
        ]
        metrics['description'] = self._try_multiple_selectors(description_selectors)
        
        # Website
        website_selectors = [
            "a[data-test='company-website']",
            ".website a",
            "a[href*='http']"
        ]
        website_element = self._find_element_safe(website_selectors)
        if website_element:
            metrics['website'] = website_element.get_attribute('href')
        
        # Total funding
        funding_selectors = [
            "[data-test='funding-total']",
            ".funding-total",
            ".total-funding",
            "span:contains('Total Funding')"
        ]
        funding_text = self._try_multiple_selectors(funding_selectors)
        metrics['funding_raised'] = self.parse_funding_amount(funding_text)
        
        # Valuation
        valuation_selectors = [
            "[data-test='valuation']",
            ".valuation",
            ".company-valuation"
        ]
        valuation_text = self._try_multiple_selectors(valuation_selectors)
        metrics['valuation'] = self.parse_funding_amount(valuation_text)
        
        # Employee count
        employee_selectors = [
            "[data-test='employee-count']",
            ".employee-count",
            ".num-employees"
        ]
        employee_text = self._try_multiple_selectors(employee_selectors)
        metrics['employees'] = self.parse_employee_count(employee_text)
        
        # Founded year
        founded_selectors = [
            "[data-test='founded-year']",
            ".founded",
            ".founded-year"
        ]
        founded_text = self._try_multiple_selectors(founded_selectors)
        metrics['founded_year'] = self.parse_year(founded_text)
        
        # Location
        location_selectors = [
            "[data-test='location']",
            ".location",
            ".headquarters"
        ]
        metrics['location'] = self._try_multiple_selectors(location_selectors)
        
        # Founders
        founders = self._extract_founders()
        metrics['founders'] = founders
        
        # Investors
        investors = self._extract_investors()
        metrics['investors'] = investors
        
        # Funding rounds
        funding_rounds = self._extract_funding_rounds()
        metrics['funding_rounds'] = funding_rounds
        
        return metrics
    
    def _try_multiple_selectors(self, selectors: List[str]) -> str:
        """Try multiple CSS selectors to find text"""
        for selector in selectors:
            try:
                text = self.extract_text_safely(selector)
                if text:
                    return text
            except:
                continue
        return ""
    
    def _find_element_safe(self, selectors: List[str]):
        """Safely find element using multiple selectors"""
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element:
                    return element
            except:
                continue
        return None
    
    def _extract_founders(self) -> List[str]:
        """Extract founder information"""
        founders = []
        
        founder_selectors = [
            "[data-test='founder-name']",
            ".founder-name",
            ".founder .name",
            ".founders .person-name"
        ]
        
        for selector in founder_selectors:
            try:
                founder_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in founder_elements:
                    if elem.text.strip():
                        founders.append(elem.text.strip())
                if founders:
                    break
            except:
                continue
        
        return list(set(founders))  # Remove duplicates
    
    def _extract_investors(self) -> List[str]:
        """Extract investor information"""
        investors = []
        
        investor_selectors = [
            "[data-test='investor-name']",
            ".investor-name",
            ".investor .name",
            ".investors .investor-name"
        ]
        
        for selector in investor_selectors:
            try:
                investor_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in investor_elements:
                    if elem.text.strip():
                        investors.append(elem.text.strip())
                if investors:
                    break
            except:
                continue
        
        return list(set(investors))  # Remove duplicates
    
    def _extract_funding_rounds(self) -> List[Dict]:
        """Extract funding round information"""
        rounds = []
        
        try:
            # Look for funding rounds section
            rounds_section = self.driver.find_element(By.CSS_SELECTOR, ".funding-rounds, .rounds-section")
            
            # Extract individual rounds
            round_elements = rounds_section.find_elements(By.CSS_SELECTOR, ".round, .funding-round")
            
            for round_elem in round_elements:
                round_data = {}
                
                # Round date
                date_elem = round_elem.find_element(By.CSS_SELECTOR, ".date, .round-date")
                round_data['date'] = date_elem.text if date_elem else None
                
                # Round amount
                amount_elem = round_elem.find_element(By.CSS_SELECTOR, ".amount, .round-amount")
                round_data['amount'] = self.parse_funding_amount(amount_elem.text) if amount_elem else None
                
                # Round type
                type_elem = round_elem.find_element(By.CSS_SELECTOR, ".type, .round-type")
                round_data['type'] = type_elem.text if type_elem else None
                
                if round_data['amount'] or round_data['type']:
                    rounds.append(round_data)
        
        except NoSuchElementException:
            logger.info("No funding rounds section found")
        
        return rounds
    
    def _extract_from_search_results(self, company_name: str) -> Dict:
        """Extract company data from search results page"""
        try:
            # Look for company cards or results
            result_selectors = [
                ".entity-result",
                ".search-result",
                ".company-card",
                ".organization-card",
                "[data-test='company-card']"
            ]
            
            company_card = None
            for selector in result_selectors:
                try:
                    cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for card in cards:
                        # Check if this card matches our company
                        card_text = card.text.lower()
                        if company_name.lower() in card_text:
                            company_card = card
                            break
                    if company_card:
                        break
                except:
                    continue
            
            if not company_card:
                logger.warning(f"No company card found for {company_name}")
                return {"error": f"No results found for {company_name}"}
            
            # Extract basic info from the card
            metrics = {"name": company_name}
            
            # Try to extract description from card
            desc_selectors = [".description", ".summary", ".about", ".overview"]
            for selector in desc_selectors:
                try:
                    desc_elem = company_card.find_element(By.CSS_SELECTOR, selector)
                    if desc_elem.text.strip():
                        metrics['description'] = desc_elem.text.strip()
                        break
                except:
                    continue
            
            # Try to extract location
            location_selectors = [".location", ".headquarters", ".address"]
            for selector in location_selectors:
                try:
                    loc_elem = company_card.find_element(By.CSS_SELECTOR, selector)
                    if loc_elem.text.strip():
                        metrics['location'] = loc_elem.text.strip()
                        break
                except:
                    continue
            
            # Try to extract funding info
            funding_selectors = [".funding", ".investment", ".raised"]
            for selector in funding_selectors:
                try:
                    funding_elem = company_card.find_element(By.CSS_SELECTOR, selector)
                    if funding_elem.text.strip():
                        metrics['funding_raised'] = self.parse_funding_amount(funding_elem.text)
                        break
                except:
                    continue
            
            logger.info(f"Successfully extracted basic data from search results for {company_name}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error extracting from search results: {e}")
            return {"error": str(e)}
