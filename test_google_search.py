"""
Test Google Search for Crunchbase Links
"""

from selenium_scraper import SeleniumCompanyScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_google_search():
    scraper = SeleniumCompanyScraper(headless=False)  # Run with browser visible
    
    try:
        company_name = "swiggy"
        google_search_url = f"https://www.google.com/search?q=crunchbase+{company_name.replace(' ', '+')}"
        logger.info(f"Searching: {google_search_url}")
        
        scraper.driver.get(google_search_url)
        scraper.random_delay()
        
        # Wait for results
        try:
            scraper.wait.until(EC.presence_of_element_located((By.ID, "search")))
            logger.info("Google search results loaded")
        except TimeoutException:
            logger.warning("Google search results did not load")
        
        # Find all links
        all_links = scraper.driver.find_elements(By.TAG_NAME, "a")
        logger.info(f"Found {len(all_links)} total links")
        
        # Check for Crunchbase links
        crunchbase_links = []
        for link in all_links:
            href = link.get_attribute('href')
            if href and 'crunchbase.com' in href:
                crunchbase_links.append(href)
                logger.info(f"Crunchbase link: {href}")
        
        logger.info(f"Found {len(crunchbase_links)} Crunchbase links")
        
        # Print page source snippet for debugging
        page_source = scraper.driver.page_source
        if 'crunchbase' in page_source.lower():
            logger.info("Found 'crunchbase' in page source")
        else:
            logger.warning("No 'crunchbase' found in page source")
        
        input("Press Enter to close browser...")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    test_google_search()
