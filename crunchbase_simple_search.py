"""
Simple Crunchbase Scraper using Google Search Approach
"""

from selenium_scraper import SeleniumCompanyScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import time
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class CrunchbaseSimpleScraper(SeleniumCompanyScraper):
    """Simple Crunchbase scraper using Google search approach"""
    
    def __init__(self, headless=True):
        super().__init__(headless)
        
    def scrape_company_data(self, company_name: str) -> Dict:
        """Scrape company data from Crunchbase using Google search"""
        logger.info(f"Starting simple Crunchbase scraping for: {company_name}")
        
        try:
            # Use DuckDuckGo search to avoid Google's anti-bot measures
            search_url = f"https://duckduckgo.com/?q=crunchbase+{company_name.replace(' ', '+')}"
            logger.info(f"Searching DuckDuckGo for: crunchbase {company_name}")
            logger.info(f"Search URL: {search_url}")
            
            self.driver.get(search_url)
            self.random_delay()
            
            # Add some debugging
            page_title = self.driver.title
            logger.info(f"Page title: {page_title}")
            
            # Check if we got blocked or redirected
            current_url = self.driver.current_url
            logger.info(f"Current URL: {current_url}")
            
            if 'duckduckgo.com' not in current_url:
                logger.warning(f"Redirected away from DuckDuckGo to: {current_url}")
                return {"error": "DuckDuckGo search redirected or blocked"}
            
            # Look for Crunchbase links in Google results
            crunchbase_links = []
            
            # Wait for DuckDuckGo results to load
            try:
                self.wait.until(EC.presence_of_element_located((By.ID, "links_wrapper")))
            except TimeoutException:
                logger.warning("DuckDuckGo search results did not load")
            
            # Try multiple approaches to find Crunchbase links
            link_selectors = [
                "a[href*='crunchbase.com']",
                "a[href*='crunchbase.com/organization']", 
                "a[href*='crunchbase.com/company']",
                "a[href*='crunchbase.com/discover']",
                "a[href*='crunchbase.com/search']"
            ]
            
            for selector in link_selectors:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for link in links:
                        href = link.get_attribute('href')
                        if href and 'crunchbase.com' in href and 'google.com' not in href:
                            crunchbase_links.append(href)
                            logger.info(f"Found Crunchbase link: {href}")
                except Exception as e:
                    logger.warning(f"Error with selector {selector}: {e}")
                    continue
            
            # If no links found with selectors, try a broader approach
            if not crunchbase_links:
                logger.info("Trying broader search for Crunchbase links")
                try:
                    all_links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in all_links:
                        href = link.get_attribute('href')
                        if href and 'crunchbase.com' in href and 'google.com' not in href:
                            crunchbase_links.append(href)
                            logger.info(f"Found Crunchbase link via broad search: {href}")
                except Exception as e:
                    logger.warning(f"Error in broad search: {e}")
            
            if not crunchbase_links:
                logger.warning("No Crunchbase links found in DuckDuckGo search")
                return {"error": "No Crunchbase page found for this company"}
            
            # Click on the first Crunchbase link
            first_crunchbase_link = crunchbase_links[0]
            logger.info(f"Found Crunchbase link: {first_crunchbase_link}")
            
            # Navigate to the Crunchbase page
            self.driver.get(first_crunchbase_link)
            self.random_delay()
            
            # Wait for page to load
            try:
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            except TimeoutException:
                logger.warning("Crunchbase page did not load properly")
            
            # Extract data from the Crunchbase company page
            company_data = self._extract_company_metrics()
            logger.info(f"Successfully scraped Crunchbase data for: {company_name}")
            
            return company_data
                
        except Exception as e:
            logger.error(f"Error scraping Crunchbase for {company_name}: {e}")
            return {"error": str(e)}
    
    def _extract_company_metrics(self) -> Dict:
        """Extract company metrics from Crunchbase page"""
        metrics = {}
        
        try:
            # Extract company name
            name_selectors = [
                "h1", ".profile-name", ".entity-name", 
                "[data-test='profile-name']", ".company-name"
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if name_elem.text.strip():
                        metrics['name'] = name_elem.text.strip()
                        break
                except:
                    continue
            
            # Extract description
            desc_selectors = [
                ".description", ".summary", ".about", 
                "[data-test='description']", ".company-description"
            ]
            
            for selector in desc_selectors:
                try:
                    desc_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if desc_elem.text.strip():
                        metrics['description'] = desc_elem.text.strip()
                        break
                except:
                    continue
            
            # Extract funding information
            funding_selectors = [
                "[data-test='funding-total']", ".funding-total", 
                ".total-funding", ".funding-amount"
            ]
            
            for selector in funding_selectors:
                try:
                    funding_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if funding_elem.text.strip():
                        metrics['total_funding'] = self._parse_funding_amount(funding_elem.text)
                        break
                except:
                    continue
            
            # Extract employee count
            employee_selectors = [
                "[data-test='employee-count']", ".employee-count", 
                ".employees", ".team-size"
            ]
            
            for selector in employee_selectors:
                try:
                    emp_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if emp_elem.text.strip():
                        metrics['employees'] = self._parse_employee_count(emp_elem.text)
                        break
                except:
                    continue
            
            # Extract location
            location_selectors = [
                ".location", ".headquarters", ".address", 
                "[data-test='location']", ".company-location"
            ]
            
            for selector in location_selectors:
                try:
                    loc_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if loc_elem.text.strip():
                        metrics['location'] = loc_elem.text.strip()
                        break
                except:
                    continue
            
            # Extract website
            website_selectors = [
                "a[href*='http']", ".website-link", 
                "[data-test='website']", ".company-website"
            ]
            
            for selector in website_selectors:
                try:
                    website_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    href = website_elem.get_attribute('href')
                    if href and href.startswith('http') and 'crunchbase.com' not in href:
                        metrics['website'] = href
                        break
                except:
                    continue
            
            logger.info(f"Extracted {len(metrics)} metrics from Crunchbase page")
            return metrics
            
        except Exception as e:
            logger.error(f"Error extracting metrics: {e}")
            return {"error": str(e)}
    
    def _parse_funding_amount(self, text: str) -> Optional[float]:
        """Parse funding amount from text"""
        if not text:
            return None
        
        # Remove common prefixes/suffixes
        text = text.replace('$', '').replace(',', '').strip()
        
        # Extract number and multiplier
        import re
        amount_match = re.search(r'[\d.]+', text)
        if not amount_match:
            return None
        
        amount = float(amount_match.group())
        
        # Apply multiplier based on text
        if 'B' in text.upper():
            amount *= 1_000_000_000
        elif 'M' in text.upper():
            amount *= 1_000_000
        elif 'K' in text.upper():
            amount *= 1_000
        
        return amount
    
    def _parse_employee_count(self, text: str) -> Optional[int]:
        """Parse employee count from text"""
        if not text:
            return None
        
        import re
        # Extract number from text
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        return None
