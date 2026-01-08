"""
Simple Web Scraper for Company Data Collection
Fallback scraper that focuses on reliable web search and basic data extraction
"""

import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import Dict, List, Optional
import time
import random

logger = logging.getLogger(__name__)

class SimpleWebScraper:
    """Simple web scraper using requests and BeautifulSoup"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def search_company_data(self, company_name: str) -> Dict:
        """Search for company data using simple web search"""
        logger.info(f"Starting simple web search for: {company_name}")
        
        all_data = {}
        
        # Search queries for different types of information
        search_queries = [
            f"{company_name} company information funding revenue",
            f"{company_name} CEO founder team employees",
            f"{company_name} investors funding rounds",
            f"{company_name} business model revenue model"
        ]
        
        for query in search_queries:
            try:
                # Use DuckDuckGo for search (no rate limiting)
                search_results = self._search_duckduckgo(query)
                extracted_data = self._extract_data_from_results(search_results, query)
                
                # Merge extracted data
                for key, value in extracted_data.items():
                    if value:
                        if key not in all_data:
                            all_data[key] = []
                        if isinstance(value, list):
                            all_data[key].extend(value)
                        else:
                            all_data[key].append(value)
                
                # Be respectful
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.warning(f"Error searching for '{query}': {e}")
                continue
        
        # Clean and merge data
        cleaned_data = self._clean_and_merge_data(all_data, company_name)
        logger.info(f"Successfully extracted simple web search data for: {company_name}")
        
        return cleaned_data
    
    def _search_duckduckgo(self, query: str) -> List[str]:
        """Search DuckDuckGo and extract result snippets"""
        try:
            search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract search result snippets
            snippets = []
            result_selectors = [
                '.result__snippet',
                '.result__body',
                '.snippet',
                '.result__description'
            ]
            
            for selector in result_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    if elem.text.strip():
                        snippets.append(elem.text.strip())
            
            return snippets[:10]  # Limit to top 10 results
            
        except Exception as e:
            logger.error(f"Error searching DuckDuckGo: {e}")
            return []
    
    def _extract_data_from_results(self, results: List[str], query_type: str) -> Dict:
        """Extract structured data from search results"""
        extracted = {}
        
        combined_text = ' '.join(results)
        
        # Extract funding information
        if 'funding' in query_type.lower():
            funding_amounts = self._extract_funding_amounts(combined_text)
            if funding_amounts:
                extracted['funding_raised'] = max(funding_amounts)
            
            investors = self._extract_investors(combined_text)
            if investors:
                extracted['investors'] = investors
        
        # Extract leadership information
        if 'ceo' in query_type.lower() or 'founder' in query_type.lower():
            ceo = self._extract_ceo(combined_text)
            if ceo:
                extracted['ceo'] = ceo
            
            founders = self._extract_founders(combined_text)
            if founders:
                extracted['founders'] = founders
        
        # Extract financial information
        if 'revenue' in query_type.lower() or 'business' in query_type.lower():
            revenue = self._extract_revenue(combined_text)
            if revenue:
                extracted['revenue'] = revenue
            
            market_cap = self._extract_market_cap(combined_text)
            if market_cap:
                extracted['market_cap'] = market_cap
        
        # Extract employee information
        if 'team' in query_type.lower() or 'employees' in query_type.lower():
            employees = self._extract_employee_count(combined_text)
            if employees:
                extracted['employees'] = employees
        
        return extracted
    
    def _extract_funding_amounts(self, text: str) -> List[float]:
        """Extract funding amounts from text"""
        amounts = []
        
        # Patterns for funding amounts
        patterns = [
            r'\$[\d,]+\.?\d*\s*(?:million|billion|M|B)',
            r'raised\s+\$[\d,]+\.?\d*\s*(?:million|billion|M|B)',
            r'funding\s+of\s+\$[\d,]+\.?\d*\s*(?:million|billion|M|B)',
            r'valuation\s+of\s+\$[\d,]+\.?\d*\s*(?:million|billion|M|B)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                amount = self._parse_funding_amount(match)
                if amount:
                    amounts.append(amount)
        
        return amounts
    
    def _parse_funding_amount(self, text: str) -> Optional[float]:
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
    
    def _extract_investors(self, text: str) -> List[str]:
        """Extract investor names from text"""
        investors = []
        
        # Common investor patterns
        investor_patterns = [
            r'(?:led by|investors? include|backed by)\s+([A-Z][a-zA-Z\s&]+)',
            r'(?:from|including)\s+([A-Z][a-zA-Z\s&]+)',
            r'([A-Z][a-zA-Z\s&]+)\s+(?:led|invested)'
        ]
        
        for pattern in investor_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                investor = match.strip()
                if len(investor) > 3 and len(investor) < 50:
                    investors.append(investor)
        
        return list(set(investors))  # Remove duplicates
    
    def _extract_ceo(self, text: str) -> Optional[str]:
        """Extract CEO name from text"""
        ceo_patterns = [
            r'CEO\s+([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s+(?:is\s+)?CEO',
            r'chief\s+executive\s+officer\s+([A-Z][a-zA-Z\s]+)'
        ]
        
        for pattern in ceo_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                ceo_name = match.group(1).strip()
                if len(ceo_name) > 3 and len(ceo_name) < 50:
                    return ceo_name
        
        return None
    
    def _extract_founders(self, text: str) -> List[str]:
        """Extract founder names from text"""
        founders = []
        
        founder_patterns = [
            r'founded\s+by\s+([A-Z][a-zA-Z\s,]+)',
            r'founder[s]?\s+([A-Z][a-zA-Z\s,]+)',
            r'co-founder[s]?\s+([A-Z][a-zA-Z\s,]+)'
        ]
        
        for pattern in founder_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                founder_names = [name.strip() for name in match.split(',')]
                founders.extend(founder_names)
        
        return list(set(founders))  # Remove duplicates
    
    def _extract_revenue(self, text: str) -> Optional[float]:
        """Extract revenue from text"""
        revenue_patterns = [
            r'revenue\s+(?:of\s+)?\$[\d,]+\.?\d*\s*(?:million|billion|M|B)',
            r'annual\s+revenue\s+\$[\d,]+\.?\d*\s*(?:million|billion|M|B)'
        ]
        
        for pattern in revenue_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self._parse_funding_amount(match.group())
        
        return None
    
    def _extract_market_cap(self, text: str) -> Optional[float]:
        """Extract market cap from text"""
        market_cap_patterns = [
            r'market\s+cap(?:italization)?\s+(?:of\s+)?\$[\d,]+\.?\d*\s*(?:million|billion|M|B)',
            r'valued\s+at\s+\$[\d,]+\.?\d*\s*(?:million|billion|M|B)'
        ]
        
        for pattern in market_cap_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self._parse_funding_amount(match.group())
        
        return None
    
    def _extract_employee_count(self, text: str) -> Optional[int]:
        """Extract employee count from text"""
        employee_patterns = [
            r'(\d+(?:,\d+)*)\s+employees?',
            r'team\s+of\s+(\d+(?:,\d+)*)',
            r'(\d+(?:,\d+)*)\s+people'
        ]
        
        for pattern in employee_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                count_str = match.group(1).replace(',', '')
                try:
                    return int(count_str)
                except ValueError:
                    continue
        
        return None
    
    def _clean_and_merge_data(self, all_data: Dict, company_name: str) -> Dict:
        """Clean and merge extracted data"""
        cleaned = {"name": company_name}
        
        # Merge lists and remove duplicates
        for key, values in all_data.items():
            if isinstance(values, list):
                # Remove duplicates and empty values
                unique_values = list(set([v for v in values if v]))
                if unique_values:
                    if key in ['funding_raised', 'revenue', 'market_cap']:
                        # Take the maximum value for financial metrics
                        cleaned[key] = max(unique_values)
                    else:
                        cleaned[key] = unique_values
            else:
                cleaned[key] = values
        
        return cleaned
