"""
Data Processor Module for AI Startup Analyst - FIXED VERSION

Fixed Issues:
- Cross-platform Tesseract detection
- Better PDF validation
- Improved error handling
- Memory optimization
"""

import os
import io
import logging
import platform
import shutil
from typing import Union, List, Tuple, Dict, Any, Optional
from dotenv import load_dotenv

# PDF processing imports
try:
    import pypdf
    from pypdf import PdfReader
except ImportError:
    pypdf = None
    PdfReader = None

# OCR imports
try:
    import pytesseract
    from pdf2image import convert_from_bytes
    from PIL import Image
except ImportError:
    pytesseract = None
    convert_from_bytes = None
    Image = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def find_tesseract() -> Optional[str]:
    """
    Find Tesseract executable across different platforms.
    
    Returns:
        Path to Tesseract executable or None if not found
    """
    # Check if Tesseract is in PATH
    tesseract_path = shutil.which('tesseract')
    if tesseract_path:
        logger.info(f"Found Tesseract in PATH: {tesseract_path}")
        return tesseract_path
    
    # Platform-specific paths
    system = platform.system()
    
    if system == 'Windows':
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
            r'C:\tools\tesseract\tesseract.exe',
            r'C:\msys64\mingw64\bin\tesseract.exe'
        ]
    elif system == 'Darwin':  # macOS
        possible_paths = [
            '/usr/local/bin/tesseract',
            '/opt/homebrew/bin/tesseract',
            '/usr/bin/tesseract',
            '/opt/local/bin/tesseract'
        ]
    else:  # Linux and others
        possible_paths = [
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract',
            '/bin/tesseract',
            '/snap/bin/tesseract'
        ]
    
    # Check each possible path
    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            logger.info(f"Found Tesseract at: {path}")
            return path
    
    # Check environment variable
    env_path = os.getenv('TESSERACT_CMD')
    if env_path and os.path.exists(env_path):
        logger.info(f"Found Tesseract via TESSERACT_CMD: {env_path}")
        return env_path
    
    logger.warning("Tesseract not found. OCR functionality will be disabled.")
    return None


def validate_pdf_file(pdf_file: Union[str, bytes, io.BytesIO]) -> Tuple[bool, str]:
    """
    Validate PDF file before processing.
    
    Args:
        pdf_file: PDF file to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    try:
        if isinstance(pdf_file, str):
            if not os.path.exists(pdf_file):
                return False, "File does not exist"
            with open(pdf_file, 'rb') as f:
                pdf_data = f.read()
        elif isinstance(pdf_file, bytes):
            pdf_data = pdf_file
        elif hasattr(pdf_file, 'read'):
            pdf_data = pdf_file.read()
            pdf_file.seek(0)  # Reset file pointer
        else:
            return False, "Invalid file type"
        
        # Check if it's actually a PDF
        if not pdf_data.startswith(b'%PDF'):
            return False, "Not a valid PDF file"
        
        # Try to read with PyPDF
        if PdfReader:
            try:
                pdf_reader = PdfReader(io.BytesIO(pdf_data))
                num_pages = len(pdf_reader.pages)
                
                if num_pages == 0:
                    return False, "PDF has no pages"
                
                # Check for encryption
                if pdf_reader.is_encrypted:
                    return False, "PDF is encrypted and cannot be processed"
                
                return True, f"Valid PDF with {num_pages} pages"
                
            except Exception as e:
                return False, f"PDF reading error: {str(e)}"
        else:
            return True, "PDF appears valid (PyPDF not available for detailed validation)"
            
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def get_pdf_info(pdf_file: Union[str, bytes, io.BytesIO]) -> Dict[str, Any]:
    """
    Get information about a PDF file.
    
    Args:
        pdf_file: PDF file to analyze
        
    Returns:
        Dictionary with PDF information
    """
    info = {
        'num_pages': 0,
        'file_size_kb': 0,
        'is_encrypted': False,
        'has_text': False
    }
    
    try:
        if isinstance(pdf_file, str):
            info['file_size_kb'] = os.path.getsize(pdf_file) / 1024
            with open(pdf_file, 'rb') as f:
                pdf_data = f.read()
        elif isinstance(pdf_file, bytes):
            info['file_size_kb'] = len(pdf_file) / 1024
            pdf_data = pdf_file
        elif hasattr(pdf_file, 'read'):
            pdf_data = pdf_file.read()
            pdf_file.seek(0)
            info['file_size_kb'] = len(pdf_data) / 1024
        else:
            return info
        
        if PdfReader:
            try:
                pdf_reader = PdfReader(io.BytesIO(pdf_data))
                info['num_pages'] = len(pdf_reader.pages)
                info['is_encrypted'] = pdf_reader.is_encrypted
                
                # Check if PDF has extractable text
                if not pdf_reader.is_encrypted:
                    try:
                        first_page_text = pdf_reader.pages[0].extract_text()
                        info['has_text'] = len(first_page_text.strip()) > 0
                    except:
                        info['has_text'] = False
                        
            except Exception as e:
                logger.warning(f"Error reading PDF info: {e}")
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting PDF info: {e}")
        return info


def extract_text_from_pdf(pdf_file: Union[str, bytes, io.BytesIO]) -> str:
    """
    Extract text from PDF using PyPDF (direct text extraction).
    
    Args:
        pdf_file: PDF file to process
        
    Returns:
        Extracted text or error message
    """
    if not PdfReader:
        return "Error: PyPDF not available. Please install with: pip install pypdf"
    
    try:
        # Get PDF data
        if isinstance(pdf_file, str):
            with open(pdf_file, 'rb') as f:
                pdf_data = f.read()
        elif isinstance(pdf_file, bytes):
            pdf_data = pdf_file
        elif hasattr(pdf_file, 'read'):
            pdf_data = pdf_file.read()
            pdf_file.seek(0)
        else:
            return "Error: Invalid file type"
        
        # Read PDF
        pdf_reader = PdfReader(io.BytesIO(pdf_data))
        
        if pdf_reader.is_encrypted:
            return "Error: PDF is encrypted and cannot be processed"
        
        # Extract text from all pages
        text_content = []
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text.strip():
                    text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                continue
        
        if text_content:
            full_text = "\n\n".join(text_content)
            logger.info(f"Successfully extracted text from PDF ({len(pdf_reader.pages)} pages)")
            return full_text
        else:
            return "Warning: No text could be extracted from PDF. The PDF may contain only images."
            
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return f"Error: Failed to extract text from PDF: {str(e)}"


def extract_text_with_ocr(pdf_file: Union[str, bytes, io.BytesIO]) -> str:
    """
    Extract text from PDF using OCR (for image-based PDFs).
    
    Args:
        pdf_file: PDF file to process
        
    Returns:
        Extracted text or error message
    """
    if not pytesseract or not convert_from_bytes or not Image:
        return "Error: OCR dependencies not available. Please install with: pip install pytesseract pdf2image Pillow"
    
    # Find Tesseract
    tesseract_path = find_tesseract()
    if not tesseract_path:
        return "Error: Tesseract OCR not found. Please install Tesseract OCR."
    
    # Configure Tesseract
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    try:
        # Get PDF data
        if isinstance(pdf_file, str):
            with open(pdf_file, 'rb') as f:
                pdf_data = f.read()
        elif isinstance(pdf_file, bytes):
            pdf_data = pdf_file
        elif hasattr(pdf_file, 'read'):
            pdf_data = pdf_file.read()
            pdf_file.seek(0)
        else:
            return "Error: Invalid file type"
        
        # Convert PDF to images
        logger.info("Converting PDF to images for OCR...")
        images = convert_from_bytes(
            pdf_data,
            dpi=200,  # Lower DPI for faster processing
            first_page=1,
            last_page=10  # Limit to first 10 pages for performance
        )
        
        if not images:
            return "Error: Could not convert PDF to images"
        
        # Extract text from images
        text_content = []
        for i, image in enumerate(images):
            try:
                logger.info(f"Processing page {i + 1} with OCR...")
                
                # Preprocess image for better OCR
                # Convert to grayscale
                if image.mode != 'L':
                    image = image.convert('L')
                
                # Extract text
                page_text = pytesseract.image_to_string(
                    image,
                    config='--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?;:()[]{}"\' '
                )
                
                if page_text.strip():
                    text_content.append(f"--- Page {i + 1} (OCR) ---\n{page_text}")
                    
            except Exception as e:
                logger.warning(f"Error processing page {i + 1} with OCR: {e}")
                continue
        
        if text_content:
            full_text = "\n\n".join(text_content)
            logger.info(f"Successfully extracted text using OCR ({len(images)} pages)")
            return full_text
        else:
            return "Warning: OCR could not extract any text from the PDF images."
            
    except Exception as e:
        logger.error(f"Error during OCR processing: {e}")
        return f"Error: OCR processing failed: {str(e)}"


def load_pdf_with_ocr(pdf_file: Union[str, bytes, io.BytesIO]) -> str:
    """
    Load PDF and extract text, trying direct extraction first, then OCR if needed.
    
    Args:
        pdf_file: PDF file to process
        
    Returns:
        Extracted text or error message
    """
    logger.info("Starting PDF text extraction...")
    
    # First, validate the PDF
    is_valid, message = validate_pdf_file(pdf_file)
    if not is_valid:
        return f"Error: {message}"
    
    logger.info(f"PDF validation passed: {message}")
    
    # Try direct text extraction first
    logger.info("Attempting direct text extraction...")
    direct_text = extract_text_from_pdf(pdf_file)
    
    # Check if direct extraction was successful
    if not direct_text.startswith("Error:") and not direct_text.startswith("Warning:"):
        return direct_text
    
    # If direct extraction failed, try OCR
    logger.info("Direct extraction failed, trying OCR...")
    ocr_text = extract_text_with_ocr(pdf_file)
    
    if not ocr_text.startswith("Error:"):
        return ocr_text
    
    # If both methods failed, return the better error message
    if "encrypted" in direct_text.lower():
        return direct_text
    else:
        return ocr_text


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks for vector storage.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings within the last 100 characters
            search_start = max(start + chunk_size - 100, start)
            sentence_end = text.rfind('.', search_start, end)
            if sentence_end > search_start:
                end = sentence_end + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap
        if start >= len(text):
            break
    
    logger.info(f"Created {len(chunks)} text chunks")
    return chunks


def process_pdf_for_analysis(pdf_file: Union[str, bytes, io.BytesIO]) -> Dict[str, Any]:
    """
    Process PDF file and return structured data for analysis.
    
    Args:
        pdf_file: PDF file to process
        
    Returns:
        Dictionary with processed data
    """
    result = {
        'success': False,
        'text': '',
        'chunks': [],
        'info': {},
        'error': None
    }
    
    try:
        # Get PDF info
        result['info'] = get_pdf_info(pdf_file)
        
        # Extract text
        text = load_pdf_with_ocr(pdf_file)
        
        if text.startswith("Error:"):
            result['error'] = text
            return result
        
        result['text'] = text
        
        # Create chunks
        chunks = chunk_text(text)
        result['chunks'] = chunks
        
        result['success'] = True
        logger.info(f"Successfully processed PDF: {len(text)} characters, {len(chunks)} chunks")
        
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        result['error'] = f"Processing error: {str(e)}"
    
    return result
