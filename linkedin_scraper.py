"""
LinkedIn Web Scraper for Company Data Collection
"""

from selenium_scraper import SeleniumCompanyScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import time
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class LinkedInScraper(SeleniumCompanyScraper):
    """LinkedIn-specific scraper for company data"""
    
    def __init__(self, headless=True):
        super().__init__(headless)
        self.base_url = "https://www.linkedin.com"
        # Add more realistic user agent and headers
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
    def scrape_company_data(self, company_name: str) -> Dict:
        """Scrape company data from LinkedIn"""
        logger.info(f"Starting LinkedIn scraping for: {company_name}")
        
        try:
            # Try multiple LinkedIn search approaches
            search_urls = [
                f"{self.base_url}/search/results/companies/?keywords={company_name}",
                f"{self.base_url}/search/results/companies/?keywords={company_name.replace(' ', '%20')}",
                f"{self.base_url}/company/{company_name.lower().replace(' ', '-')}",
                f"{self.base_url}/company/{company_name.lower().replace(' ', '')}"
            ]
            
            results_container = None
            for search_url in search_urls:
                try:
                    logger.info(f"Trying LinkedIn URL: {search_url}")
                    if not self.navigate_with_retry(search_url):
                        continue
                    self.random_delay()
                    
                    # Try multiple selectors for results
                    result_selectors = [
                        ".search-results-container",
                        ".search-results",
                        ".results-container",
                        ".entity-result",
                        ".search-result",
                        ".company-card"
                    ]
                    
                    for selector in result_selectors:
                        try:
                            results_container = self.wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            logger.info(f"Found results with selector: {selector}")
                            break
                        except TimeoutException:
                            continue
                    
                    if results_container:
                        break
                        
                except Exception as e:
                    logger.warning(f"Failed with URL {search_url}: {e}")
                    continue
            
            if not results_container:
                logger.warning("LinkedIn search results not loaded with any approach")
                # Try to extract basic company info from the page anyway
                try:
                    page_title = self.driver.title
                    if company_name.lower() in page_title.lower():
                        logger.info("Found company name in page title, attempting basic extraction")
                        return self._extract_basic_company_info(company_name)
                except Exception as e:
                    logger.warning(f"Could not extract basic info: {e}")
                
                return {"error": "LinkedIn search not accessible - may require login or has anti-bot measures"}
            
            # Find company link
            company_selectors = [
                ".search-result__title a",
                ".entity-result__title-text a",
                "a[href*='/company/']",
                ".search-result a"
            ]
            
            company_link = None
            for selector in company_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.text.lower().strip() == company_name.lower().strip():
                            company_link = elem
                            break
                    if company_link:
                        break
                except:
                    continue
            
            if not company_link:
                logger.warning(f"No LinkedIn company page found for: {company_name}")
                return {"error": f"LinkedIn company page not found for '{company_name}'"}
            
            # Navigate to company page
            company_url = company_link.get_attribute('href')
            if not self.navigate_with_retry(company_url):
                return {"error": "Failed to navigate to LinkedIn company page"}
            self.random_delay()
            
            # Extract company data
            company_data = self._extract_company_metrics(company_name)
            logger.info(f"Successfully scraped LinkedIn data for: {company_name}")
            
            return company_data
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn for {company_name}: {e}")
            return {"error": str(e)}
    
    def _extract_basic_company_info(self, company_name: str) -> Dict:
        """Extract basic company information from LinkedIn page"""
        try:
            metrics = {"name": company_name}
            
            # Try to extract description from page content
            try:
                desc_elements = self.driver.find_elements(By.CSS_SELECTOR, ".description, .summary, .about")
                for elem in desc_elements:
                    if elem.text.strip():
                        metrics['description'] = elem.text.strip()
                        break
            except:
                pass
            
            # Try to extract location
            try:
                loc_elements = self.driver.find_elements(By.CSS_SELECTOR, ".location, .headquarters, .address")
                for elem in loc_elements:
                    if elem.text.strip():
                        metrics['location'] = elem.text.strip()
                        break
            except:
                pass
            
            logger.info(f"Extracted basic LinkedIn info for {company_name}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error extracting basic LinkedIn info: {e}")
            return {"error": str(e)}
    
    def _extract_company_metrics(self, company_name: str) -> Dict:
        """Extract specific metrics from LinkedIn company page"""
        metrics = {"name": company_name}
        
        # Company description
        description_selectors = [
            ".about-us-description",
            ".company-description",
            ".about-section",
            ".overview-section"
        ]
        metrics['description'] = self._try_multiple_selectors(description_selectors)
        
        # Website
        website_selectors = [
            "a[href*='http']:not([href*='linkedin'])",
            ".company-website a",
            ".website-link a"
        ]
        website_element = self._find_element_safe(website_selectors)
        if website_element:
            metrics['website'] = website_element.get_attribute('href')
        
        # Employee count
        employee_selectors = [
            ".company-size",
            ".employee-count",
            ".num-employees"
        ]
        employee_text = self._try_multiple_selectors(employee_selectors)
        metrics['employees'] = self.parse_employee_count(employee_text)
        
        # Industry
        industry_selectors = [
            ".industry",
            ".company-industry"
        ]
        metrics['industry'] = self._try_multiple_selectors(industry_selectors)
        
        # Location
        location_selectors = [
            ".company-location",
            ".headquarters",
            ".location"
        ]
        metrics['location'] = self._try_multiple_selectors(location_selectors)
        
        # Leadership team
        leadership = self._extract_leadership_info()
        metrics.update(leadership)
        
        # Recent updates/posts
        recent_updates = self._extract_recent_updates()
        metrics['recent_updates'] = recent_updates
        
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
    
    def _extract_leadership_info(self) -> Dict:
        """Extract leadership team information"""
        leadership = {"ceo": None, "leadership_team": []}
        
        try:
            # Look for people section or leadership section
            people_section = self.driver.find_element(
                By.CSS_SELECTOR, 
                ".people-section, .leadership-section, .team-section"
            )
            
            # Extract CEO/leadership names
            leader_selectors = [
                ".person-name",
                ".leader-name",
                ".executive-name",
                ".team-member-name"
            ]
            
            for selector in leader_selectors:
                try:
                    leader_elements = people_section.find_elements(By.CSS_SELECTOR, selector)
                    for elem in leader_elements:
                        if elem.text.strip():
                            leadership['leadership_team'].append(elem.text.strip())
                    if leadership['leadership_team']:
                        break
                except:
                    continue
            
            # Try to identify CEO (usually first or has CEO title)
            if leadership['leadership_team']:
                # Look for CEO title
                ceo_selectors = [
                    ".ceo",
                    "[data-test='ceo']",
                    ".chief-executive-officer"
                ]
                
                for selector in ceo_selectors:
                    try:
                        ceo_elem = people_section.find_element(By.CSS_SELECTOR, selector)
                        leadership['ceo'] = ceo_elem.text.strip()
                        break
                    except:
                        continue
                
                # If no specific CEO found, take first leader
                if not leadership['ceo'] and leadership['leadership_team']:
                    leadership['ceo'] = leadership['leadership_team'][0]
        
        except NoSuchElementException:
            logger.info("No leadership section found on LinkedIn")
        
        return leadership
    
    def _extract_recent_updates(self) -> List[str]:
        """Extract recent company updates/posts"""
        updates = []
        
        try:
            # Look for posts or updates section
            posts_section = self.driver.find_element(
                By.CSS_SELECTOR,
                ".posts-section, .updates-section, .activity-section"
            )
            
            # Extract post content
            post_selectors = [
                ".post-content",
                ".update-content",
                ".activity-content"
            ]
            
            for selector in post_selectors:
                try:
                    post_elements = posts_section.find_elements(By.CSS_SELECTOR, selector)
                    for elem in post_elements:
                        if elem.text.strip():
                            updates.append(elem.text.strip())
                    if updates:
                        break
                except:
                    continue
        
        except NoSuchElementException:
            logger.info("No recent updates section found on LinkedIn")
        
        return updates[:5]  # Limit to 5 most recent updates
