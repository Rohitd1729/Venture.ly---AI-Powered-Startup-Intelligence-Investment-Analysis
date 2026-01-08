# 🚀 AI Startup Analyst - Web Scraping Edition

An intelligent startup analysis tool that processes pitch decks and generates comprehensive investment memos using AI-powered analysis with real-time web scraping from multiple sources including Crunchbase, LinkedIn, and general web search.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Integration](#api-integration)
- [Project Structure](#project-structure)
- [Analysis Sections](#analysis-sections)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🔍 Overview

The AI Startup Analyst is a sophisticated tool designed to automate the startup screening process for investors, VCs, and analysts. It combines advanced PDF processing, AI-powered analysis, and real-time data integration to generate comprehensive investment memos.

### Key Capabilities

- **Automated Pitch Deck Analysis**: Extract and analyze content from PDF pitch decks with OCR fallback
- **AI-Powered Investment Memos**: Generate professional investment recommendations using Google Gemini AI
- **Real-Time Web Scraping**: Comprehensive data collection from Crunchbase, LinkedIn, and web search
- **Multi-Source Data Aggregation**: Intelligent merging of data from multiple sources with fallback mechanisms
- **Interactive Visualizations**: Dynamic charts and graphs for investment decision making
- **Multi-Dimensional Analysis**: Comprehensive evaluation across business, financial, and market dimensions
- **Professional Reporting**: Export detailed analysis reports with visualizations

## ✨ Features

### 🎯 Core Functionality
- **PDF Processing**: Advanced text extraction with OCR fallback for image-based PDFs
- **AI Analysis**: Leverages Google Gemini 2.0 Flash for intelligent content analysis
- **Multi-Source Web Scraping**: Real-time data collection from Crunchbase, LinkedIn, and web search
- **Selenium Automation**: Advanced browser automation with anti-detection measures
- **Simple Web Scraper**: Fallback scraper using DuckDuckGo for reliable data extraction
- **Vector Search**: ChromaDB-powered semantic search for relevant information
- **Interactive Dashboard**: Real-time visualizations and investment scoring
- **Multi-Tab Interface**: Organized analysis across multiple specialized sections

### 📊 Analysis Components
- **Quick Investment Decision**: Real-time scoring and immediate investment recommendation
- **Funding Analysis**: Comprehensive funding rounds, investors, and valuation tracking
- **Team & Leadership**: CEO, founders, and leadership team analysis
- **Financial Health**: Revenue, profit/loss, and financial metrics visualization
- **Market Position**: Competitive analysis, market share, and industry standing
- **Interactive Visualizations**: Dynamic charts for funding timeline, revenue growth, and team structure

### 🔧 Technical Features
- **Multi-Source Scraping**: Selenium-based scraping from Crunchbase, LinkedIn, and web search
- **Anti-Detection Measures**: Advanced browser automation to avoid bot detection
- **Fallback Mechanisms**: Simple web scraper as reliable backup when Selenium fails
- **Data Aggregation**: Intelligent merging of data from multiple sources
- **Error Handling**: Robust error management with graceful fallbacks
- **Logging**: Comprehensive logging for debugging and monitoring
- **Modular Design**: Clean, maintainable code architecture with dedicated scrapers
- **Environment Management**: Secure API key handling
- **Export Capabilities**: Download analysis reports with visualizations

## 🏗️ Architecture

The application follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│   AI Core       │────│   Google AI     │
│ (app_selenium.py)│    │   (ai_core.py)  │    │   (Gemini 2.0)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Data Processor  │    │   ChromaDB      │    │  Web Scrapers   │
│ (data_processor)│    │   Vector Store  │    │   (Selenium)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Visualization   │    │ Data Aggregator │    │ Simple Web      │
│ Dashboard       │    │ (Multi-Source)  │    │ Scraper         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Installation

### Prerequisites

- **Python 3.8+**
- **Tesseract OCR** (for PDF processing)
- **Google AI API Key** (for AI analysis)
- **Chrome Browser** (for Selenium web scraping)
- **ChromeDriver** (automatically managed by webdriver-manager)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd ai-startup-analyst
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Tesseract OCR

#### Windows:
1. Download from [GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install to default location: `C:\Program Files\Tesseract-OCR\`

#### macOS:
```bash
brew install tesseract
```

#### Linux:
```bash
sudo apt-get install tesseract-ocr
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Google AI API Key
GOOGLE_API_KEY=your_google_api_key_here

# Tesseract OCR Path (Windows)
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

# Optional: Custom ChromaDB path
CHROMA_DB_PATH=./vector_store

# Selenium Configuration (Optional)
SELENIUM_HEADLESS=true
SELENIUM_TIMEOUT=10
CHROME_DRIVER_PATH=auto
```

### API Key Setup

#### Google AI API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to `.env` file as `GOOGLE_API_KEY`

#### Chrome Browser Setup
1. Install Google Chrome browser
2. ChromeDriver is automatically managed by webdriver-manager
3. No additional configuration required

## 🎮 Usage

### Starting the Application

```bash
streamlit run app_selenium.py
```

The application will be available at `http://localhost:8501`

### Analysis Workflow

1. **Enter Company Name**: Provide the company name for comprehensive web scraping
2. **Upload PDF** (Optional): Upload a startup pitch deck for additional analysis
3. **Configure Data Sources**: Select which sources to scrape (Crunchbase, LinkedIn, Web Search)
4. **Enable AI Analysis**: Toggle AI-powered analysis for investment recommendations
5. **Scrape & Analyze**: Click "Scrape & Analyze Company Data" to start processing
6. **Review Dashboard**: Navigate through interactive visualization tabs
7. **Export Report**: Download the complete analysis with visualizations

### Analysis Options

- **Data Sources**: Toggle Crunchbase, LinkedIn, and Web Search scraping
- **AI Analysis**: Enable/disable AI-powered investment recommendations
- **Headless Mode**: Run browser in background for faster processing
- **Display Options**: Customize visualization and dashboard settings

## 🔌 Web Scraping Integration

### Multi-Source Data Collection

The application uses advanced web scraping to collect real-time data:

- **Crunchbase Website**: Direct scraping from Crunchbase.com for company data
- **LinkedIn**: Professional network data for leadership and team information
- **Web Search**: General web search for comprehensive company information
- **Simple Web Scraper**: Fallback using DuckDuckGo for reliable data extraction
- **Anti-Detection**: Advanced browser automation to avoid bot detection
- **Fallback Mechanisms**: Multiple approaches ensure data collection success

### Google AI Integration

- **Model**: Gemini 2.0 Flash
- **Capabilities**: Text analysis, content generation, semantic understanding
- **Features**: Multi-turn conversations, context retention, structured output

## 📁 Project Structure

```
ai-startup-analyst/
├── app_selenium.py          # Main Streamlit application (Web Scraping Edition)
├── ai_core.py               # AI analysis engine and ChromaDB integration
├── data_processor.py        # PDF processing and OCR functionality
├── data_aggregator.py       # Multi-source data aggregation
├── selenium_scraper.py      # Base Selenium scraper framework
├── crunchbase_scraper.py    # Crunchbase website scraper
├── linkedin_scraper.py      # LinkedIn scraper
├── web_search_scraper.py    # General web search scraper
├── simple_web_scraper.py    # Fallback web scraper (DuckDuckGo)
├── visualization_dashboard.py # Interactive dashboard and charts
├── prompts.py               # AI analysis prompts and templates
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create this)
├── README.md               # Project documentation
├── vector_store/           # ChromaDB vector database
└── data/                   # Sample pitch decks
    ├── Startup_One_Airbnb/
    ├── Startup_One_dropbox/
    ├── Startup_One_Linkdin/
    ├── Startup_One_plum/
    └── Startup_One_uber/
```

### Key Files

- **`app_selenium.py`**: Main application with Streamlit interface and web scraping
- **`ai_core.py`**: Core AI functionality, ChromaDB integration, and analysis orchestration
- **`data_processor.py`**: PDF text extraction and OCR processing
- **`data_aggregator.py`**: Multi-source data collection and intelligent merging
- **`selenium_scraper.py`**: Base Selenium framework with anti-detection measures
- **`crunchbase_scraper.py`**: Crunchbase website scraper with multiple search approaches
- **`linkedin_scraper.py`**: LinkedIn scraper with anti-bot handling
- **`web_search_scraper.py`**: General web search scraper using Selenium
- **`simple_web_scraper.py`**: Fallback scraper using DuckDuckGo and BeautifulSoup
- **`visualization_dashboard.py`**: Interactive charts and investment scoring
- **`prompts.py`**: Expert-designed prompts for different analysis sections

## 📊 Analysis Sections

### 1. Quick Investment Decision
- Real-time investment scoring (0-100)
- Immediate recommendation (INVEST/HOLD/PASS)
- Key metrics overview with visual indicators
- Investment confidence level

### 2. Funding Analysis
- Comprehensive funding timeline visualization
- Investor network analysis
- Valuation growth tracking
- Funding rounds breakdown

### 3. Team & Leadership
- CEO and founder information
- Leadership team analysis
- Team structure visualization
- Key personnel insights

### 4. Financial Health
- Revenue growth visualization
- Profit/loss trend analysis
- Financial metrics dashboard
- Economic indicators

### 5. Market Position
- Competitive landscape analysis
- Market share estimation
- Industry positioning
- Growth potential assessment

## 🛠️ Troubleshooting

### Common Issues

#### 1. OCR Not Working
**Problem**: PDF text extraction fails
**Solution**: 
- Verify Tesseract installation
- Check `TESSERACT_CMD` path in `.env`
- Ensure PDF contains readable text or images

#### 2. API Errors
**Problem**: Google AI or Crunchbase API failures
**Solutions**:
- Verify API keys are valid and active
- Check API quotas and limits
- Review error messages in logs

#### 3. PDF Processing Issues
**Problem**: Cannot extract text from PDF
**Solutions**:
- Try different PDF formats
- Ensure PDF is not password-protected
- Check file size limits

#### 4. Web Scraping Issues
**Problem**: Scraping fails or returns no data
**Solutions**:
- Check internet connection
- Try different company name variations
- Enable simple web scraper fallback
- Check if websites are accessible
- Application will continue with available data sources

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `AI not configured` | Invalid Google API key | Check API key in `.env` |
| `Search functionality not accessible` | Website structure changed | Try simple web scraper fallback |
| `Could not extract text from PDF` | PDF processing failed | Try OCR or check PDF quality |
| `LinkedIn search not accessible` | Anti-bot measures or login required | Use other data sources |
| `ChromeDriver not found` | Chrome browser not installed | Install Google Chrome |

### Debug Mode

Enable detailed logging by setting log level to INFO in the application code:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 🧪 Testing

### Test the Installation

```bash
# Test PDF processing
python -c "from data_processor import extract_text_from_pdf; print('PDF processing OK')"

# Test AI integration
python -c "from ai_core import configure_ai; configure_ai(); print('AI integration OK')"

# Test web scraping integration
python -c "from simple_web_scraper import SimpleWebScraper; scraper = SimpleWebScraper(); print('Web scraping OK')"
```

### Sample Analysis

The `data/` folder contains sample pitch decks for testing:
- Airbnb pitch deck
- Dropbox pitch deck
- LinkedIn pitch deck
- Plum fintech pitch deck
- Uber pitch deck

## 📈 Performance

### Optimization Features

- **Vector Caching**: ChromaDB stores processed embeddings for faster retrieval
- **Multi-Source Fallback**: Graceful degradation when scraping sources fail
- **Anti-Detection Measures**: Advanced browser automation to avoid bot detection
- **Batch Processing**: Efficient PDF processing with progress indicators
- **Memory Management**: Optimized for large document processing
- **Headless Mode**: Faster processing without browser UI

### Scalability

- **Modular Design**: Easy to extend with new analysis modules and scrapers
- **Multi-Source Integration**: Supports multiple web scraping sources
- **Database Backend**: ChromaDB scales with document volume
- **Cloud Ready**: Can be deployed on cloud platforms with headless browsers
- **Fallback Systems**: Multiple data collection strategies ensure reliability

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to functions
- Include type hints where possible
- Write tests for new features

### Areas for Contribution

- Additional web scraping sources
- New analysis dimensions and visualizations
- UI/UX improvements
- Anti-detection measures
- Performance optimizations
- Documentation enhancements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

1. **Check Documentation**: Review this README and code comments
2. **Troubleshooting**: See the troubleshooting section above
3. **Error Messages**: Review application logs for specific error details
4. **API Status**: Verify API keys and quotas

### Common Solutions

- **Restart Application**: Often resolves temporary issues
- **Check Dependencies**: Ensure all packages are installed correctly
- **Verify Configuration**: Double-check `.env` file settings
- **Update APIs**: Ensure API keys are current and have sufficient quota

## 🚀 Quick Start Summary

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 3. Run the application
streamlit run app_selenium.py

# 4. Open browser to http://localhost:8501
# 5. Enter a company name and start analyzing with real-time web scraping!
```

---

**Ready to revolutionize startup analysis?** 🚀

The AI Startup Analyst - Web Scraping Edition combines the power of modern AI with real-time web scraping to deliver comprehensive investment insights. Start analyzing startups with live data today!