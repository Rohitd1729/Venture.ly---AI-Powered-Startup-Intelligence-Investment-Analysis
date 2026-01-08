"""
AI Startup Analyst - Streamlit Web Application

A sophisticated tool for automated startup analysis using RAG (Retrieval-Augmented Generation)
architecture with Gemini 1.5 Flash and ChromaDB vector storage.
"""

import streamlit as st
import data_processor
import ai_core
import prompts
import os
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Startup Analyst",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .analysis-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

def initialize_app():
    """Initialize the application and configure AI."""
    try:
        ai_core.configure_ai()
        return True
    except ValueError as e:
        st.error(f"Configuration Error: {e}")
        st.error("Please ensure you have a .env file with GOOGLE_API_KEY set.")
        return False
    except Exception as e:
        st.error(f"Unexpected error during initialization: {e}")
        return False

def display_header():
    """Display the application header."""
    st.markdown('<h1 class="main-header">🚀 AI Startup Analyst</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #666;">
            Upload a startup's pitch deck and enter their company name to generate a comprehensive investment memo.
        </p>
        <p style="font-size: 1rem; color: #888;">
            Powered by Google Gemini 1.5 Flash • Enhanced with Crunchbase Data • Built with RAG Architecture
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display the sidebar with information and controls."""
    with st.sidebar:
        st.header("📊 Analysis Settings")
        
        # Analysis options
        st.subheader("Analysis Options")
        include_crunchbase = st.checkbox("Include Crunchbase Data", value=True, help="Fetch additional company data from Crunchbase API")
        chunk_size = st.slider("Text Chunk Size", min_value=1000, max_value=2000, value=1500, help="Size of text chunks for analysis")
        max_context_chunks = st.slider("Max Context Chunks", min_value=3, max_value=10, value=5, help="Maximum number of context chunks to use for each analysis")
        
        st.subheader("📈 Analysis Sections")
        analysis_sections = {
            "Team Analysis": st.checkbox("Team Analysis", value=True),
            "Problem & Solution": st.checkbox("Problem & Solution", value=True),
            "Market Opportunity": st.checkbox("Market Opportunity", value=True),
            "Product & Technology": st.checkbox("Product & Technology", value=True),
            "Traction & GTM": st.checkbox("Traction & GTM", value=True),
            "Risk Analysis": st.checkbox("Risk Analysis", value=True)
        }
        
        st.subheader("ℹ️ About")
        st.info("""
        This tool uses advanced AI to analyze startup pitch decks and generate comprehensive investment memos.
        
        **Key Features:**
        - PDF processing with OCR
        - Crunchbase data enrichment
        - Multi-faceted analysis
        - Structured investment recommendations
        """)
        
        return include_crunchbase, chunk_size, max_context_chunks, analysis_sections

def process_uploaded_file(uploaded_file):
    """Process the uploaded PDF file."""
    if uploaded_file is None:
        return None, None
    
    # Validate file type
    if not uploaded_file.name.lower().endswith('.pdf'):
        st.error("Please upload a PDF file.")
        return None, None
    
    # Validate PDF
    if not data_processor.validate_pdf_file(uploaded_file):
        st.error("Invalid PDF file. Please ensure the file is not corrupted or encrypted.")
        return None, None
    
    # Reset file pointer
    uploaded_file.seek(0)
    
    return uploaded_file, uploaded_file.name

def display_analysis_progress():
    """Display analysis progress with status updates."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    return progress_bar, status_text

def run_analysis(uploaded_file, company_name, include_crunchbase, chunk_size, max_context_chunks, analysis_sections):
    """Run the complete analysis pipeline."""
    
    # Initialize progress tracking
    progress_bar, status_text = display_analysis_progress()
    analysis_results = {}
    
    try:
        # Step 1: Fetch Crunchbase data
        progress_bar.progress(10)
        status_text.text("Step 1/6: Fetching data from Crunchbase...")
        
        crunchbase_text = ""
        if include_crunchbase and company_name:
            crunchbase_text = ai_core.get_crunchbase_data(company_name)
            if crunchbase_text:
                st.success("✅ Successfully fetched data from Crunchbase")
            else:
                st.warning("⚠️ Could not fetch data from Crunchbase. Proceeding with PDF only.")
        else:
            st.info("ℹ️ Skipping Crunchbase data (disabled or no company name provided)")
        
        # Step 2: Process PDF
        progress_bar.progress(25)
        status_text.text("Step 2/6: Processing PDF document...")
        
        pdf_text = data_processor.load_pdf_with_ocr(uploaded_file)
        if not pdf_text or len(pdf_text.strip()) < 100:
            st.error("❌ Could not extract sufficient text from the PDF. Please ensure the document contains readable text.")
            return None
        
        st.success(f"✅ Successfully extracted {len(pdf_text)} characters from PDF")
        
        # Step 3: Create vector store
        progress_bar.progress(40)
        status_text.text("Step 3/6: Creating vector store...")
        
        combined_text = pdf_text + crunchbase_text
        chunks = data_processor.chunk_data(combined_text, chunk_size=chunk_size)
        
        if not chunks:
            st.error("❌ Failed to process text into chunks. The document may be empty.")
            return None
        
        collection_name = f"startup_analysis_{int(time.time())}"
        collection = ai_core.create_vector_store(chunks, collection_name)
        
        if not collection:
            st.error("❌ Failed to create vector store. Please try again.")
            return None
        
        st.success(f"✅ Created vector store with {len(chunks)} chunks")
        
        # Step 4: Generate analysis sections
        progress_bar.progress(50)
        status_text.text("Step 4/6: Generating analysis sections...")
        
        # Define analysis mapping
        analysis_map = {
            "Team Analysis": (prompts.TEAM_ANALYSIS_PROMPT, "founding team experience background"),
            "Problem & Solution": (prompts.PROBLEM_SOLUTION_PROMPT, "problem solution market fit"),
            "Market Opportunity": (prompts.MARKET_ANALYSIS_PROMPT, "market size opportunity TAM SAM"),
            "Product & Technology": (prompts.PRODUCT_TECH_PROMPT, "product technology development innovation"),
            "Traction & GTM": (prompts.TRACTION_GTM_PROMPT, "traction revenue customers growth metrics"),
            "Risk Analysis": (prompts.RISK_ANALYSIS_PROMPT, "risks challenges threats weaknesses")
        }
        
        # Run selected analyses
        completed_sections = 0
        total_sections = sum(1 for enabled in analysis_sections.values() if enabled)
        
        for title, (prompt, query) in analysis_map.items():
            if analysis_sections.get(title, False):
                st.markdown("---")
                st.subheader(f"📋 {title}")
                
                with st.spinner(f"Analyzing {title.lower()}..."):
                    context = ai_core.get_relevant_context(query, collection, n_results=max_context_chunks)
                    analysis = ai_core.generate_analysis(context, prompt)
                    
                    # Display analysis in a styled container
                    st.markdown(f'<div class="analysis-section">{analysis}</div>', unsafe_allow_html=True)
                    analysis_results[title] = analysis
                    
                    completed_sections += 1
                    progress = 50 + (completed_sections / total_sections) * 30
                    progress_bar.progress(int(progress))
                    status_text.text(f"Step 4/6: Completed {completed_sections}/{total_sections} analysis sections...")
        
        # Step 5: Generate final synthesis
        progress_bar.progress(85)
        status_text.text("Step 5/6: Synthesizing final recommendation...")
        
        st.markdown("---")
        st.header("🎯 Final Investment Recommendation")
        
        with st.spinner("Generating final synthesis and recommendation..."):
            synthesis_context = "\n\n".join([f"## {title}\n{text}" for title, text in analysis_results.items()])
            final_summary = ai_core.generate_analysis(synthesis_context, prompts.FINAL_SYNTHESIS_PROMPT)
            
            # Display final recommendation in a prominent container
            st.markdown(f'<div class="analysis-section" style="background-color: #e8f5e8; border-left-color: #28a745;">{final_summary}</div>', unsafe_allow_html=True)
            analysis_results["Final Recommendation"] = final_summary
        
        # Step 6: Complete
        progress_bar.progress(100)
        status_text.text("Step 6/6: Analysis complete!")
        
        st.success("🎉 Analysis Complete!")
        st.balloons()
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("PDF Characters", f"{len(pdf_text):,}")
        with col2:
            st.metric("Text Chunks", len(chunks))
        with col3:
            st.metric("Analysis Sections", len(analysis_results))
        with col4:
            st.metric("Processing Time", f"{time.time():.1f}s")
        
        return analysis_results
        
    except Exception as e:
        st.error(f"❌ An error occurred during analysis: {str(e)}")
        logger.error(f"Analysis error: {e}")
        return None
    finally:
        # Clean up
        try:
            if 'collection_name' in locals():
                ai_core.cleanup_vector_store(collection_name)
        except:
            pass

def main():
    """Main application function."""
    # Initialize app
    if not initialize_app():
        st.stop()
    
    # Display header
    display_header()
    
    # Display sidebar and get settings
    include_crunchbase, chunk_size, max_context_chunks, analysis_sections = display_sidebar()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📄 Upload Pitch Deck")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload the startup's pitch deck in PDF format"
        )
    
    with col2:
        st.subheader("🏢 Company Information")
        company_name = st.text_input(
            "Company Name",
            placeholder="Enter official company name",
            help="Used for Crunchbase data enrichment"
        )
    
    # Analysis button
    if st.button("🚀 Analyze Startup", type="primary", use_container_width=True):
        if uploaded_file and company_name:
            # Process file
            processed_file, filename = process_uploaded_file(uploaded_file)
            if processed_file is None:
                st.stop()
            
            # Run analysis
            analysis_results = run_analysis(
                processed_file, 
                company_name, 
                include_crunchbase, 
                chunk_size, 
                max_context_chunks, 
                analysis_sections
            )
            
            if analysis_results:
                # Display download option
                st.markdown("---")
                st.subheader("💾 Download Results")
                
                # Create a simple text report
                report_text = f"""
AI Startup Analyst Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Company: {company_name}
File: {filename}

{'='*50}

"""
                for title, content in analysis_results.items():
                    report_text += f"\n{title}\n{'-'*len(title)}\n{content}\n\n"
                
                st.download_button(
                    label="📥 Download Analysis Report",
                    data=report_text,
                    file_name=f"startup_analysis_{company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        else:
            st.warning("⚠️ Please upload a PDF file and enter a company name to begin analysis.")

if __name__ == "__main__":
    main()