
import os
import sys
import logging
import time
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_separator(title):
    print("\n" + "="*50)
    print(f" {title}")
    print("="*50)

def test_imports():
    print_separator("TESTING IMPORTS")
    modules = [
        "streamlit", "google.generativeai", "langchain", "chromadb", 
        "selenium", "pypdf", "pytesseract", "pdf2image"
    ]
    
    all_passed = True
    for module in modules:
        try:
            __import__(module)
            logger.info(f"✅ Import successful: {module}")
        except ImportError as e:
            logger.error(f"❌ Import failed: {module} - {e}")
            all_passed = False
            
    return all_passed

def test_environment():
    print_separator("TESTING ENVIRONMENT")
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        logger.info("✅ GOOGLE_API_KEY found")
        return True
    else:
        logger.error("❌ GOOGLE_API_KEY not found in .env")
        return False

def test_ai_connection():
    print_separator("TESTING AI CONNECTION")
    try:
        from ai_core import test_api_connection
        result = test_api_connection()
        if result.get('status') == 'success':
            logger.info(f"✅ AI API connection successful: {result.get('message')}")
            return True
        else:
            logger.error(f"❌ AI API connection failed: {result.get('error')}")
            return False
    except Exception as e:
        logger.error(f"❌ AI Test Error: {e}")
        return False

def test_scraping():
    print_separator("TESTING SCRAPING (Web Search)")
    try:
        from web_search_scraper import WebSearchScraper
        
        scraper = WebSearchScraper(headless=True)
        results = scraper.search_company_data("OpenAI")
        scraper.close()
        
        if results and results.get('name') == "OpenAI":
            logger.info(f"✅ Scraping successful: Found data for {results.get('name')}")
            return True
        else:
            logger.warning(f"⚠️ Scraping returned unexpected results: {results}")
            return False # Warning but maybe not critical failure if network is flaky
            
    except Exception as e:
        logger.error(f"❌ Scraping Test Error: {e}")
        return False

def test_pdf_processing():
    print_separator("TESTING PDF PROCESSING")
    try:
        from data_processor import validate_pdf_file
        
        # Create a dummy PDF
        from reportlab.pdfgen import canvas
        dummy_pdf = "test_doc.pdf"
        c = canvas.Canvas(dummy_pdf)
        c.drawString(100, 750, "Hello World PDF Test")
        c.save()
        
        is_valid, msg = validate_pdf_file(dummy_pdf)
        
        # Clean up
        if os.path.exists(dummy_pdf):
            os.remove(dummy_pdf)
            
        if is_valid:
            logger.info(f"✅ PDF Validation successful: {msg}")
            return True
        else:
            logger.error(f"❌ PDF Validation failed: {msg}")
            return False
            
    except ImportError:
        logger.warning("⚠️ reportlab not installed, skipping PDF creation test")
        return True # Skip
    except Exception as e:
        logger.error(f"❌ PDF Test Error: {e}")
        return False

def run_all_tests():
    print_separator("STARTING COMPREHENSIVE VERIFICATION")
    
    results = {
        "Imports": test_imports(),
        "Environment": test_environment(),
        "AI Connection": test_ai_connection(),
        "PDF Processing": test_pdf_processing(),
        "Scraping": test_scraping()
    }
    
    print_separator("VERIFICATION SUMMARY")
    all_passed = True
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test}: {status}")
        if not passed:
            all_passed = False
            
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
