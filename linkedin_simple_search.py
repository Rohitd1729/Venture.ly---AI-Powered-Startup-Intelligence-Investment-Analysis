"""
Simple LinkedIn Scraper using Google Search Approach
"""

from selenium_scraper import SeleniumCompanyScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import time
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class LinkedInSimpleScraper(SeleniumCompanyScraper):
    """Simple LinkedIn scraper using Google search approach"""
    
    def __init__(self, headless=True):
        super().__init__(headless)
        
    def scrape_company_data(self, company_name: str) -> Dict:
        """Scrape company data from LinkedIn using Google search"""
        logger.info(f"Starting simple LinkedIn scraping for: {company_name}")
        
        try:
            # Use DuckDuckGo search to avoid Google's anti-bot measures
            search_url = f"https://duckduckgo.com/?q=linkedin+{company_name.replace(' ', '+')}+company"
            logger.info(f"Searching DuckDuckGo for: linkedin {company_name} company")
            
            self.driver.get(search_url)
            self.random_delay()
            
            # Look for LinkedIn company links in Google results
            linkedin_links = []
            
            # Wait for DuckDuckGo results to load
            try:
                self.wait.until(EC.presence_of_element_located((By.ID, "links_wrapper")))
            except TimeoutException:
                logger.warning("DuckDuckGo search results did not load")
            
            # Try multiple approaches to find LinkedIn company links
            link_selectors = [
                "a[href*='linkedin.com/company']",
                "a[href*='linkedin.com/company/']",
                "a[href*='linkedin.com/company/']"
            ]
            
            for selector in link_selectors:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for link in links:
                        href = link.get_attribute('href')
                        if href and 'linkedin.com/company' in href and 'google.com' not in href:
                            linkedin_links.append(href)
                            logger.info(f"Found LinkedIn company link: {href}")
                except Exception as e:
                    logger.warning(f"Error with selector {selector}: {e}")
                    continue
            
            # If no links found with selectors, try a broader approach
            if not linkedin_links:
                logger.info("Trying broader search for LinkedIn company links")
                try:
                    all_links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in all_links:
                        href = link.get_attribute('href')
                        if href and 'linkedin.com/company' in href and 'google.com' not in href:
                            linkedin_links.append(href)
                            logger.info(f"Found LinkedIn company link via broad search: {href}")
                except Exception as e:
                    logger.warning(f"Error in broad search: {e}")
            
            if not linkedin_links:
                logger.warning("No LinkedIn company links found in DuckDuckGo search")
                return {"error": "No LinkedIn company page found for this company"}
            
            # Click on the first LinkedIn company link
            first_linkedin_link = linkedin_links[0]
            logger.info(f"Found LinkedIn company link: {first_linkedin_link}")
            
            # Navigate to the LinkedIn company page
            self.driver.get(first_linkedin_link)
            self.random_delay()
            
            # Wait for page to load
            try:
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            except TimeoutException:
                logger.warning("LinkedIn page did not load properly")
            
            # Extract data from the LinkedIn company page
            company_data = self._extract_company_metrics()
            logger.info(f"Successfully scraped LinkedIn data for: {company_name}")
            
            return company_data
                
        except Exception as e:
            logger.error(f"Error scraping LinkedIn for {company_name}: {e}")
            return {"error": str(e)}
    
    def _extract_company_metrics(self) -> Dict:
        """Extract company metrics from LinkedIn page"""
        metrics = {}
        
        try:
            # Extract company name
            name_selectors = [
                "h1", ".org-top-card-summary__title", ".company-name", 
                "[data-test='company-name']", ".profile-name"
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
                ".org-about-us-organization-description", ".description", 
                ".summary", ".about", "[data-test='description']"
            ]
            
            for selector in desc_selectors:
                try:
                    desc_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if desc_elem.text.strip():
                        metrics['description'] = desc_elem.text.strip()
                        break
                except:
                    continue
            
            # Extract employee count
            employee_selectors = [
                ".org-top-card-summary__info-item", ".employee-count", 
                ".employees", ".team-size", "[data-test='employee-count']"
            ]
            
            for selector in employee_selectors:
                try:
                    emp_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if emp_elem.text.strip() and any(word in emp_elem.text.lower() for word in ['employee', 'people', 'staff']):
                        metrics['employees'] = self._parse_employee_count(emp_elem.text)
                        break
                except:
                    continue
            
            # Extract location
            location_selectors = [
                ".org-top-card-summary__info-item", ".location", 
                ".headquarters", ".address", "[data-test='location']"
            ]
            
            for selector in location_selectors:
                try:
                    loc_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if loc_elem.text.strip() and any(word in loc_elem.text.lower() for word in ['location', 'headquarters', 'based']):
                        metrics['location'] = loc_elem.text.strip()
                        break
                except:
                    continue
            
            # Extract industry
            industry_selectors = [
                ".org-top-card-summary__info-item", ".industry", 
                ".sector", "[data-test='industry']"
            ]
            
            for selector in industry_selectors:
                try:
                    industry_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if industry_elem.text.strip() and any(word in industry_elem.text.lower() for word in ['industry', 'sector', 'technology']):
                        metrics['industry'] = industry_elem.text.strip()
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
                    if href and href.startswith('http') and 'linkedin.com' not in href:
                        metrics['website'] = href
                        break
                except:
                    continue
            
            logger.info(f"Extracted {len(metrics)} metrics from LinkedIn page")
            return metrics
            
        except Exception as e:
            logger.error(f"Error extracting metrics: {e}")
            return {"error": str(e)}
    
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
