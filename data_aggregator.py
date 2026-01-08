"""
Multi-Source Company Data Aggregator
"""

from selenium_scraper import CompanyMetrics
from crunchbase_scraper import CrunchbaseScraper
from crunchbase_simple_search import CrunchbaseSimpleScraper
from linkedin_scraper import LinkedInScraper
from linkedin_simple_search import LinkedInSimpleScraper
from web_search_scraper import WebSearchScraper
from simple_web_scraper import SimpleWebScraper
import logging
import time
from typing import Dict, List, Optional
import streamlit as st

logger = logging.getLogger(__name__)

class CompanyDataAggregator:
    """Aggregates company data from multiple web sources"""
    
    def __init__(self, headless=True):
        self.scrapers = {
            'crunchbase': CrunchbaseSimpleScraper(headless),  # Use simple search approach
            'linkedin': LinkedInSimpleScraper(headless),      # Use simple search approach
            'web_search': WebSearchScraper(headless),
            'simple_web': SimpleWebScraper()  # Fallback scraper
        }
        
    def get_comprehensive_data(self, company_name: str, progress_callback=None) -> Dict:
        """Aggregate data from multiple sources"""
        logger.info(f"Starting comprehensive data collection for: {company_name}")
        
        all_data = {}
        successful_sources = 0
        
        # Progress tracking
        total_sources = len(self.scrapers)
        
        for i, (source_name, scraper) in enumerate(self.scrapers.items()):
            try:
                if progress_callback:
                    progress_callback(f"Scraping {source_name}...", (i + 1) / total_sources)
                
                logger.info(f"Scraping {source_name} for {company_name}")
                
                # Scrape data from source
                if source_name == 'web_search':
                    data = scraper.search_company_data(company_name)
                elif source_name == 'simple_web':
                    data = scraper.search_company_data(company_name)
                else:
                    data = scraper.scrape_company_data(company_name)
                
                if data and 'error' not in data:
                    all_data[source_name] = data
                    successful_sources += 1
                    logger.info(f"Successfully scraped {source_name}")
                else:
                    logger.warning(f"Failed to scrape {source_name}: {data.get('error', 'Unknown error')}")
                    all_data[source_name] = {"error": data.get('error', 'No data found')}
                
                # Be respectful to websites
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error scraping {source_name} for {company_name}: {e}")
                all_data[source_name] = {"error": str(e)}
        
        # Merge and clean data
        merged_data = self._merge_data_sources(all_data, company_name)
        
        # Add metadata
        merged_data['metadata'] = {
            'successful_sources': successful_sources,
            'total_sources': total_sources,
            'scraped_sources': list(all_data.keys()),
            'timestamp': time.time()
        }
        
        logger.info(f"Data aggregation completed for {company_name}. "
                   f"Successfully scraped {successful_sources}/{total_sources} sources")
        
        return merged_data
    
    def _merge_data_sources(self, data_sources: Dict, company_name: str) -> Dict:
        """Intelligently merge data from different sources"""
        merged = {"name": company_name}
        
        # Priority order for data sources (higher priority first)
        source_priority = ['crunchbase', 'linkedin', 'web_search', 'simple_web']
        
        # Merge funding data (take highest value)
        funding_values = []
        for source in source_priority:
            if source in data_sources and 'funding_raised' in data_sources[source]:
                value = data_sources[source]['funding_raised']
                if value and isinstance(value, (int, float)) and value > 0:
                    funding_values.append(value)
        
        if funding_values:
            merged['funding_raised'] = max(funding_values)
        
        # Merge valuation data
        valuation_values = []
        for source in source_priority:
            if source in data_sources and 'valuation' in data_sources[source]:
                value = data_sources[source]['valuation']
                if value and isinstance(value, (int, float)) and value > 0:
                    valuation_values.append(value)
        
        if valuation_values:
            merged['valuation'] = max(valuation_values)
        
        # Merge employee count (take highest value)
        employee_counts = []
        for source in source_priority:
            if source in data_sources and 'employees' in data_sources[source]:
                value = data_sources[source]['employees']
                if value and isinstance(value, (int, float)) and value > 0:
                    employee_counts.append(value)
        
        if employee_counts:
            merged['employees'] = max(employee_counts)
        
        # Merge revenue data
        revenue_values = []
        for source in source_priority:
            if source in data_sources and 'revenue' in data_sources[source]:
                value = data_sources[source]['revenue']
                if value and isinstance(value, (int, float)) and value > 0:
                    revenue_values.append(value)
        
        if revenue_values:
            merged['revenue'] = max(revenue_values)
        
        # Merge founders (combine unique names)
        all_founders = []
        for source in source_priority:
            if source in data_sources and 'founders' in data_sources[source]:
                founders = data_sources[source]['founders']
                if founders and isinstance(founders, list):
                    all_founders.extend(founders)
        
        if all_founders:
            merged['founders'] = list(set([f for f in all_founders if f]))
        
        # Merge investors (combine unique names)
        all_investors = []
        for source in source_priority:
            if source in data_sources and 'investors' in data_sources[source]:
                investors = data_sources[source]['investors']
                if investors and isinstance(investors, list):
                    all_investors.extend(investors)
        
        if all_investors:
            merged['investors'] = list(set([i for i in all_investors if i]))
        
        # Merge CEO (take first non-empty value)
        for source in source_priority:
            if source in data_sources and 'ceo' in data_sources[source]:
                ceo = data_sources[source]['ceo']
                if ceo and isinstance(ceo, str) and ceo.strip():
                    merged['ceo'] = ceo.strip()
                    break
        
        # Merge founded year (take first non-empty value)
        for source in source_priority:
            if source in data_sources and 'founded_year' in data_sources[source]:
                year = data_sources[source]['founded_year']
                if year and isinstance(year, int) and year > 1900:
                    merged['founded_year'] = year
                    break
        
        # Merge description (take longest/most detailed)
        descriptions = []
        for source in source_priority:
            if source in data_sources and 'description' in data_sources[source]:
                desc = data_sources[source]['description']
                if desc and isinstance(desc, str) and desc.strip():
                    descriptions.append(desc.strip())
        
        if descriptions:
            # Take the longest description
            merged['description'] = max(descriptions, key=len)
        
        # Merge website (take first valid URL)
        for source in source_priority:
            if source in data_sources and 'website' in data_sources[source]:
                website = data_sources[source]['website']
                if website and isinstance(website, str) and website.strip() and website.startswith('http'):
                    merged['website'] = website.strip()
                    break
        
        # Merge location (take first non-empty value)
        for source in source_priority:
            if source in data_sources and 'location' in data_sources[source]:
                location = data_sources[source]['location']
                if location and isinstance(location, str) and location.strip():
                    merged['location'] = location.strip()
                    break
        
        # Merge funding rounds (combine unique rounds)
        all_rounds = []
        for source in source_priority:
            if source in data_sources and 'funding_rounds' in data_sources[source]:
                rounds = data_sources[source]['funding_rounds']
                if rounds and isinstance(rounds, list):
                    all_rounds.extend(rounds)
        
        if all_rounds:
            # Remove duplicate rounds based on amount and type
            unique_rounds = []
            seen_rounds = set()
            for round_data in all_rounds:
                if isinstance(round_data, dict):
                    round_key = f"{round_data.get('amount', '')}-{round_data.get('type', '')}"
                    if round_key not in seen_rounds:
                        unique_rounds.append(round_data)
                        seen_rounds.add(round_key)
            merged['funding_rounds'] = unique_rounds
        
        # Calculate additional metrics
        merged = self._calculate_derived_metrics(merged)
        
        return merged
    
    def _calculate_derived_metrics(self, data: Dict) -> Dict:
        """Calculate additional metrics from available data"""
        
        # Company age
        if data.get('founded_year'):
            current_year = 2024
            data['company_age'] = current_year - data['founded_year']
        
        # Funding stage estimation
        if data.get('funding_raised'):
            funding = data['funding_raised']
            if funding < 1_000_000:
                data['funding_stage'] = "Pre-Seed"
            elif funding < 5_000_000:
                data['funding_stage'] = "Seed"
            elif funding < 20_000_000:
                data['funding_stage'] = "Series A"
            elif funding < 50_000_000:
                data['funding_stage'] = "Series B"
            elif funding < 100_000_000:
                data['funding_stage'] = "Series C+"
            else:
                data['funding_stage'] = "Late Stage"
        
        # Employee size category
        if data.get('employees'):
            employees = data['employees']
            if employees < 10:
                data['employee_size'] = "Startup (1-9)"
            elif employees < 50:
                data['employee_size'] = "Small (10-49)"
            elif employees < 200:
                data['employee_size'] = "Medium (50-199)"
            elif employees < 1000:
                data['employee_size'] = "Large (200-999)"
            else:
                data['employee_size'] = "Enterprise (1000+)"
        
        return data
    
    def close_all_scrapers(self):
        """Close all scraper instances"""
        for scraper in self.scrapers.values():
            try:
                scraper.close()
            except:
                pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_all_scrapers()
