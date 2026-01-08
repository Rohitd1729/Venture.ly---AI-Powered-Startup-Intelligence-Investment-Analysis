"""
Venture.ly - AI Startup Analyst
Enhanced Professional UI with Modern Design
"""

import streamlit as st
import os
import logging
from datetime import datetime
from typing import Dict
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Venture.ly - AI Startup Analyst",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
def load_custom_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main color palette - Light Theme */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --accent-color: #ec4899;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --bg-light: #f8fafc;
        --bg-medium: #f1f5f9;
        --text-primary: #0f172a;
        --text-secondary: #64748b;
        --border-color: #cbd5e1;
    }
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Header styling */
    h1 {
        color: var(--text-primary);
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h2 {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1.75rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1.25rem;
        margin-bottom: 0.75rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f1f5f9 0%, #f8fafc 100%);
        border-right: 1px solid var(--border-color);
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--text-primary);
    }
    
    /* Cards and containers */
    .stMetric {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .stMetric label {
        color: var(--text-secondary) !important;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: var(--primary-color) !important;
        font-size: 1.875rem;
        font-weight: 700;
    }
    
    /* Input fields */
    .stTextInput input {
        background: #f1f5f9;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(99, 102, 241, 0.2);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(99, 102, 241, 0.3);
    }
    
    .stButton button:active {
        transform: translateY(0);
    }
    
    /* Primary button override */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
        box-shadow: 0 4px 6px rgba(236, 72, 153, 0.2);
    }
    
    .stButton button[kind="primary"]:hover {
        box-shadow: 0 6px 12px rgba(236, 72, 153, 0.3);
    }
    
    /* Checkbox styling */
    .stCheckbox {
        color: var(--text-primary);
    }
    
    .stCheckbox > label {
        color: var(--text-primary) !important;
    }
    
    /* Select box */
    .stSelectbox select {
        background: #f1f5f9;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 0.75rem;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #f1f5f9;
        border: 2px dashed var(--border-color);
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--primary-color);
        background: #e2e8f0;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--accent-color) 100%);
        border-radius: 10px;
    }
    
    /* Success/Error/Warning messages */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid var(--success-color);
        border-radius: 8px;
        color: var(--success-color);
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid var(--error-color);
        border-radius: 8px;
        color: var(--error-color);
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid var(--warning-color);
        border-radius: 8px;
        color: var(--warning-color);
    }
    
    .stInfo {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid var(--primary-color);
        border-radius: 8px;
        color: var(--primary-color);
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, var(--border-color) 50%, transparent 100%);
        margin: 2rem 0;
    }
    
    /* Custom card component */
    .custom-card {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    
    /* Header badge */
    .header-badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        color: white;
        margin-left: 1rem;
    }
    
    /* Status indicator */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 0.5rem;
        animation: pulse 2s infinite;
    }
    
    .status-success {
        background: var(--success-color);
    }
    
    .status-warning {
        background: var(--warning-color);
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Markdown content */
    .stMarkdown {
        color: var(--text-primary);
    }
    
    .stMarkdown a {
        color: var(--primary-color);
        text-decoration: none;
        transition: color 0.3s ease;
    }
    
    .stMarkdown a:hover {
        color: var(--accent-color);
    }
    
    /* Footer styling */
    .footer-container {
        text-align: center;
        color: var(--text-secondary);
        padding: 3rem 0 2rem 0;
        margin-top: 3rem;
        border-top: 1px solid var(--border-color);
    }
    
    .footer-logo {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    /* Analysis history items */
    .history-item {
        background: #f1f5f9;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        border-left: 3px solid var(--primary-color);
        margin-bottom: 0.5rem;
        color: var(--text-primary);
        transition: all 0.3s ease;
    }
    
    .history-item:hover {
        background: #e2e8f0;
        transform: translateX(4px);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        color: var(--text-secondary);
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #f1f5f9;
        color: var(--text-primary);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-color);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'company_data' not in st.session_state:
        st.session_state.company_data = None
    
    if 'last_company' not in st.session_state:
        st.session_state.last_company = None
    
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    if 'api_configured' not in st.session_state:
        st.session_state.api_configured = False


def check_api_configuration():
    """Check if API is properly configured"""
    if st.session_state.api_configured:
        return True
    
    try:
        from ai_core import test_api_connection
        result = test_api_connection()
        
        if result['status'] == 'success':
            st.session_state.api_configured = True
            return True
        else:
            st.sidebar.error(f"⚠️ API Configuration Error: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        st.sidebar.error(f"⚠️ API Error: {str(e)}")
        return False


def display_header():
    """Display enhanced header"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        <h1 style='margin-bottom: 0;'>
            🚀 Venture.ly
        </h1>
        <p style='color: var(--text-secondary); font-size: 1.1rem; margin-top: 0.5rem;'>
            AI-Powered Startup Intelligence & Investment Analysis
        </p>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.session_state.api_configured:
            st.markdown("""
            <div style='text-align: right; margin-top: 1rem;'>
                <span class='status-indicator status-success'></span>
                <span style='color: var(--success-color); font-weight: 600;'>AI Ready</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='text-align: right; margin-top: 1rem;'>
                <span class='status-indicator status-warning'></span>
                <span style='color: var(--warning-color); font-weight: 600;'>API Setup Required</span>
            </div>
            """, unsafe_allow_html=True)


def main():
    """Main application function"""
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    init_session_state()
    
    # Display header
    display_header()
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # API Configuration Check
        st.markdown("#### 🔑 API Status")
        if st.session_state.api_configured:
            st.success("✅ Google AI API Connected")
        else:
            st.warning("⚠️ API Not Configured")
            if st.button("🔄 Test API Connection", width='stretch'):
                with st.spinner("Testing API connection..."):
                    check_api_configuration()
        
        st.divider()
        
        # Scraping options
        st.markdown("#### 📊 Data Sources")
        include_crunchbase = st.checkbox(
            "Crunchbase Data", 
            value=True, 
            help="Company funding and metrics"
        )
        include_linkedin = st.checkbox(
            "LinkedIn Data", 
            value=True, 
            help="Leadership and team information"
        )
        include_web_search = st.checkbox(
            "Web Search Data", 
            value=True, 
            help="General company information"
        )
        
        st.divider()
        
        # Display options
        st.markdown("#### 🎨 Performance")
        headless_mode = st.checkbox(
            "Headless Mode", 
            value=True, 
            help="Faster scraping in background"
        )
        
        st.divider()
        
        # AI Analysis options
        st.markdown("#### 🤖 AI Analysis")
        include_ai_analysis = st.checkbox(
            "Enable AI Analysis", 
            value=True, 
            help="Generate AI-powered insights"
        )
        
        if include_ai_analysis and not st.session_state.api_configured:
            st.warning("⚠️ Configure API key in .env file")
        
        analysis_prompt = st.selectbox(
            "Analysis Type",
            [
                "Investment Recommendation",
                "Market Analysis",
                "Competitive Analysis",
                "Risk Assessment",
                "Growth Potential"
            ],
            index=0
        )
        
        # Analysis history
        if st.session_state.analysis_history:
            st.divider()
            st.markdown("#### 📜 Recent Analyses")
            for item in reversed(st.session_state.analysis_history[-5:]):
                st.markdown(f"""
                <div class='history-item'>
                    📊 {item['company']}
                </div>
                """, unsafe_allow_html=True)
    
    # Main content area
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    # Company Analysis Section
    st.markdown("### 🔍 Company Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        company_name = st.text_input(
            "Company Name", 
            placeholder="e.g., Tesla, Stripe, Anthropic, OpenAI",
            help="Enter the company you want to analyze",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
    
    # Quick Stats Display
    if st.session_state.company_data:
        st.markdown("### 📊 Key Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        data = st.session_state.company_data
        
        with col1:
            funding = data.get('funding_raised', 0)
            funding_str = f"${funding/1e6:.1f}M" if funding >= 1e6 else f"${funding:,.0f}"
            if funding == 0:
                funding_str = "N/A"
            st.metric("💰 Total Funding", funding_str)
        
        with col2:
            employees = data.get('employees', 0)
            employee_str = f"{employees:,}" if employees else "N/A"
            st.metric("👥 Team Size", employee_str)
        
        with col3:
            age = data.get('company_age', 0)
            age_str = f"{age} years" if age else "N/A"
            st.metric("📅 Company Age", age_str)
        
        with col4:
            stage = data.get('funding_stage', 'Unknown')
            st.metric("🚀 Stage", stage)
    
    # PDF Upload Section
    st.markdown("### 📄 Pitch Deck Analysis (Optional)")
    
    uploaded_file = st.file_uploader(
        "Upload Pitch Deck PDF",
        type=['pdf'],
        help="Upload a PDF for comprehensive analysis",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        with st.spinner("Validating PDF..."):
            try:
                from data_processor import validate_pdf_file, get_pdf_info
                is_valid, message = validate_pdf_file(uploaded_file)
                
                if is_valid:
                    st.success(f"✅ {message}")
                    pdf_info = get_pdf_info(uploaded_file)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"📄 Pages: {pdf_info.get('num_pages', 'N/A')}")
                    with col2:
                        st.info(f"💾 Size: {pdf_info.get('file_size_kb', 0):.1f} KB")
                else:
                    st.error(f"❌ {message}")
                    uploaded_file = None
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                uploaded_file = None
    
    # Action buttons
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        analyze_button = st.button(
            "🚀 Analyze Company", 
            type="primary", 
            width='stretch'
        )
    
    with col2:
        if st.session_state.company_data:
            if st.button("🔄 New Analysis", width='stretch'):
                st.session_state.company_data = None
                st.session_state.last_company = None
                st.rerun()
    
    with col3:
        if st.session_state.company_data:
            if st.button("💾 Export", width='stretch'):
                st.info("Export feature coming soon!")
    
    with col4:
        if st.session_state.company_data:
            if st.button("📊 Report", width='stretch'):
                st.info("Report generation coming soon!")
    
    # Main analysis logic
    if analyze_button:
        if not company_name:
            st.error("❌ Please enter a company name")
            return
        
        # Progress tracking
        progress_container = st.container()
        
        with progress_container:
            st.markdown("### 🔄 Analysis in Progress")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Import required modules
                status_text.markdown("**Initializing analysis engine...**")
                progress_bar.progress(0.05)
                
                from data_aggregator import CompanyDataAggregator
                from ai_core import configure_ai, generate_analysis
                from data_processor import load_pdf_with_ocr
                
                # Initialize data aggregator
                status_text.markdown("**🌐 Connecting to data sources...**")
                progress_bar.progress(0.1)
                
                company_data = {}
                
                # Scrape company data
                try:
                    with CompanyDataAggregator(headless=headless_mode) as aggregator:
                        def update_progress(message, progress):
                            status_text.markdown(f"**🔍 {message}**")
                            progress_bar.progress(min(0.1 + (progress * 0.6), 0.7))
                        
                        status_text.markdown("**🔍 Gathering intelligence from multiple sources...**")
                        company_data = aggregator.get_comprehensive_data(
                            company_name, 
                            update_progress
                        )
                        
                        progress_bar.progress(0.7)
                        status_text.markdown("**✅ Data collection completed!**")
                        
                except Exception as e:
                    logger.error(f"Scraping error: {e}")
                    st.error(f"❌ Data Collection Error: {str(e)}")
                    st.info("💡 This may be due to network issues or rate limiting. Please try again.")
                    return
                
                # Process PDF if uploaded
                pdf_text = ""
                if uploaded_file:
                    status_text.markdown("**📄 Analyzing pitch deck...**")
                    progress_bar.progress(0.75)
                    
                    try:
                        pdf_text = load_pdf_with_ocr(uploaded_file)
                        
                        if pdf_text and not pdf_text.startswith("Error:"):
                            status_text.markdown("**✅ Pitch deck processed!**")
                            company_data['pitch_deck_text'] = pdf_text[:5000]
                        else:
                            st.warning(f"⚠️ PDF processing issue: {pdf_text}")
                            
                    except Exception as e:
                        logger.error(f"PDF processing error: {e}")
                        st.warning("⚠️ Could not process PDF. Continuing with web data.")
                
                progress_bar.progress(0.8)
                
                # AI Analysis
                if include_ai_analysis and st.session_state.api_configured:
                    status_text.markdown("**🤖 Generating AI insights...**")
                    progress_bar.progress(0.85)
                    
                    try:
                        configure_ai()
                        
                        context_parts = [f"Company: {company_name}"]
                        
                        if company_data:
                            context_parts.append(f"Funding: ${company_data.get('funding_raised', 0):,.0f}")
                            context_parts.append(f"Employees: {company_data.get('employees', 'Unknown')}")
                            context_parts.append(f"Stage: {company_data.get('funding_stage', 'Unknown')}")
                            
                            if company_data.get('description'):
                                context_parts.append(f"Description: {company_data['description'][:500]}")
                        
                        if pdf_text and not pdf_text.startswith("Error:"):
                            context_parts.append(f"Pitch Deck: {pdf_text[:2000]}")
                        
                        context = "\n\n".join(context_parts)
                        
                        from prompts import COMPREHENSIVE_INVESTMENT_ANALYSIS_PROMPT
                        prompt = COMPREHENSIVE_INVESTMENT_ANALYSIS_PROMPT
                        
                        ai_analysis = generate_analysis(context, prompt)
                        company_data['ai_analysis'] = ai_analysis
                        company_data['analysis_type'] = analysis_prompt
                        
                        status_text.markdown("**✅ AI analysis completed!**")
                        progress_bar.progress(0.95)
                        
                    except Exception as e:
                        logger.error(f"AI analysis error: {e}")
                        st.warning(f"⚠️ Could not generate AI analysis: {str(e)}")
                
                # Store in session state
                st.session_state.company_data = company_data
                st.session_state.last_company = company_name
                
                # Add to history
                st.session_state.analysis_history.append({
                    'company': company_name,
                    'timestamp': datetime.now().isoformat(),
                    'data': company_data
                })
                
                progress_bar.progress(1.0)
                status_text.markdown("**✅ Analysis completed successfully!**")
                
                st.success(f"✅ Successfully analyzed **{company_name}**!")
                
                # Auto-display results
                st.rerun()
            
            except Exception as e:
                logger.error(f"Analysis error: {e}")
                logger.error(traceback.format_exc())
                st.error(f"❌ Analysis Error: {str(e)}")
                st.info("💡 Please check the logs for details.")
    
    # Display results
    if st.session_state.company_data:
        st.divider()
        
        # AI Analysis Section
        if st.session_state.company_data.get('ai_analysis'):
            st.markdown("### 🤖 AI Investment Analysis")
            
            analysis_type = st.session_state.company_data.get('analysis_type', 'Analysis')
            
            st.markdown(f"""
            <div class='custom-card'>
                <h4 style='color: var(--primary-color); margin-bottom: 1rem;'>
                    📊 {analysis_type}
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(st.session_state.company_data['ai_analysis'])
            st.divider()
        
        # Detailed Dashboard
        st.markdown("### 📈 Comprehensive Analysis Dashboard")
        try:
            from visualization_dashboard import display_complete_dashboard
            display_complete_dashboard(st.session_state.company_data)
        except Exception as e:
            logger.error(f"Dashboard display error: {e}")
            st.error(f"Error displaying dashboard: {str(e)}")
    
    # Footer
    st.markdown("""
    <div class='footer-container'>
        <div class='footer-logo'>Venture.ly</div>
        <p style='margin: 0.5rem 0;'>AI-Powered Startup Intelligence Platform</p>
        <p style='font-size: 0.875rem; color: var(--text-secondary);'>
            Powered by Advanced Web Scraping & Google Gemini AI
        </p>
        <p style='font-size: 0.75rem; color: var(--text-secondary); margin-top: 1rem;'>
            © 2025 Venture.ly. All rights reserved.
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise