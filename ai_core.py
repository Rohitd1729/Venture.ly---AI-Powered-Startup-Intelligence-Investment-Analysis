"""
AI Core Module - FINAL FIX with correct Gemini model

The issue was the model name format. Google's API expects:
- 'gemini-1.5-flash-latest' or 'gemini-1.5-pro-latest'
- NOT 'models/gemini-1.5-flash'
"""

import os
import google.generativeai as genai
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import logging
from typing import List, Optional, Dict, Any
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for configuration
_ai_configured = False
_embedding_model = None
_rate_limit_delay = 1.0


def configure_ai() -> None:
    """Configure the Google AI API and initialize the embedding model."""
    global _ai_configured, _embedding_model
    
    if _ai_configured:
        logger.info("AI already configured, skipping...")
        return
    
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        error_msg = (
            "GOOGLE_API_KEY not found in environment variables. "
            "Please create a .env file with your Google AI API key:\n"
            "GOOGLE_API_KEY=your_api_key_here"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        genai.configure(api_key=api_key)
        
        # Test API connection and list available models
        try:
            models = list(genai.list_models())
            available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
            logger.info(f"Successfully connected to Google AI API")
            logger.info(f"Available models: {available_models[:3]}")  # Show first 3
        except Exception as e:
            raise ValueError(f"API key validation failed: {str(e)}")
        
        # Initialize embedding model
        _embedding_model = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
        
        _ai_configured = True
        logger.info("AI configuration successful")
        
    except Exception as e:
        logger.error(f"Failed to configure AI: {str(e)}")
        raise ValueError(f"Failed to configure AI: {str(e)}")


def get_available_models() -> List[str]:
    """Get list of available Gemini models."""
    try:
        models = list(genai.list_models())
        gemini_models = [
            m.name for m in models 
            if 'gemini' in m.name.lower() and 'generateContent' in m.supported_generation_methods
        ]
        return gemini_models
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return []


def generate_analysis(context: str, prompt: str, max_retries: int = 3) -> str:
    """
    Generate analysis using Gemini model with automatic model selection.
    
    Args:
        context: Context to analyze
        prompt: Analysis prompt
        max_retries: Maximum number of retry attempts
        
    Returns:
        Generated analysis text
    """
    if not _ai_configured:
        try:
            configure_ai()
        except Exception as e:
            return f"Error: AI not configured. {str(e)}"
    
    if not context.strip():
        return "Warning: No context provided for analysis. Please provide company data or upload a pitch deck."
    
    # Try multiple model names in order of preference
    model_names_to_try = [
        'gemini-2.0-flash',
        'gemini-2.5-flash',
        'gemini-flash-latest',
        'gemini-pro-latest',
        'models/gemini-2.0-flash',
        'models/gemini-2.0-flash',
        'models/gemini-flash-latest',
        'models/gemini-pro-latest',
        'gemini-1.5-flash-latest',
        'gemini-1.5-flash',
        'gemini-1.5-pro-latest',
        'gemini-1.5-pro',
        'gemini-pro'
    ]
    
    try:
        # Truncate context if too long
        max_context_length = 30000
        if len(context) > max_context_length:
            context = context[:max_context_length] + "\n...(truncated)"
            logger.warning(f"Context truncated to {max_context_length} characters")
        
        full_prompt = f"""{prompt}

Context:
---
{context}
---

Please provide a comprehensive analysis based on the above context."""
        
        # Try each model name
        last_error = None
        for model_name in model_names_to_try:
            for attempt in range(max_retries):
                try:
                    logger.info(f"Generating analysis with model '{model_name}' (attempt {attempt + 1}/{max_retries})")
                    
                    model = genai.GenerativeModel(model_name)
                    
                    response = model.generate_content(
                        full_prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.7,
                            top_p=0.8,
                            top_k=40,
                            max_output_tokens=2048,
                        ),
                        safety_settings={
                            'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                            'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                            'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                            'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                        }
                    )
                    
                    if response and response.text:
                        logger.info(f"Analysis generated successfully with {model_name}")
                        return response.text
                    else:
                        logger.warning(f"Empty response from {model_name} on attempt {attempt + 1}")
                        
                except Exception as e:
                    error_msg = str(e).lower()
                    last_error = e
                    
                    # If model not found, try next model immediately
                    if '404' in error_msg or 'not found' in error_msg:
                        logger.warning(f"Model '{model_name}' not available, trying next...")
                        break  # Break attempt loop, try next model
                    
                    # Handle specific error types
                    if 'quota' in error_msg or 'rate limit' in error_msg:
                        wait_time = (2 ** attempt) * 2
                        logger.warning(f"Rate limit hit, waiting {wait_time}s...")
                        time.sleep(wait_time)
                    elif 'invalid api key' in error_msg:
                        return "Error: Invalid API key. Please check your GOOGLE_API_KEY in .env file."
                    else:
                        logger.warning(f"Attempt {attempt + 1} failed with {model_name}: {e}")
                        
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
        
        # If we get here, all models failed
        logger.error("All model attempts failed")
        
        # Provide helpful error message
        available_models = get_available_models()
        if available_models:
            return (
                f"Error: Could not generate analysis. Tried multiple models but all failed.\n\n"
                f"Available models: {', '.join(available_models[:3])}\n\n"
                f"Last error: {str(last_error)}\n\n"
                f"Please check your API key and internet connection."
            )
        else:
            return (
                f"Error: Could not generate analysis.\n\n"
                f"Last error: {str(last_error)}\n\n"
                f"Please check your API key and ensure you have access to Gemini models."
            )
        
    except Exception as e:
        logger.error(f"Error generating analysis: {e}")
        return f"An error occurred during analysis generation: {str(e)}\n\nPlease check your API key and internet connection."


def create_vector_store(chunks: List[str], collection_name: str) -> Optional[chromadb.Collection]:
    """Create a ChromaDB vector store from text chunks."""
    if not _ai_configured:
        logger.error("AI not configured. Call configure_ai() first.")
        return None
        
    if not chunks:
        logger.warning("No chunks provided for vector store creation")
        return None
    
    try:
        logger.info(f"Creating vector store with {len(chunks)} chunks")
        
        # Sanitize collection name
        safe_collection_name = "".join(
            c if c.isalnum() or c in ['_', '-'] else '_' 
            for c in collection_name
        )[:63]
        
        client = chromadb.PersistentClient(path="./vector_store")
        
        # Delete existing collection if it exists
        try:
            client.delete_collection(name=safe_collection_name)
            logger.info(f"Deleted existing collection: {safe_collection_name}")
        except Exception:
            pass
        
        collection = client.create_collection(
            name=safe_collection_name,
            metadata={"description": f"Startup analysis data for {collection_name}"}
        )
        
        # Add documents in batches
        batch_size = 10
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            ids = [f"chunk_{j}" for j in range(i, i + len(batch))]
            metadatas = [{"chunk_index": j, "source": "pitch_deck"} for j in range(i, i + len(batch))]
            
            try:
                collection.add(
                    documents=batch,
                    ids=ids,
                    metadatas=metadatas
                )
                logger.info(f"Added batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
                time.sleep(_rate_limit_delay)
            except Exception as e:
                logger.error(f"Error adding batch {i//batch_size + 1}: {e}")
                continue
        
        logger.info(f"Successfully created vector store with {len(chunks)} documents")
        return collection
        
    except Exception as e:
        logger.error(f"Error creating vector store: {e}")
        return None


def get_relevant_context(query: str, collection: chromadb.Collection, n_results: int = 5) -> str:
    """Retrieve relevant context from the vector store."""
    if not collection:
        logger.warning("No collection provided for context retrieval")
        return ""
    
    try:
        logger.info(f"Searching for context with query: {query[:50]}...")
        
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, collection.count())
        )
        
        if results and 'documents' in results and results['documents']:
            context = "\n\n".join(results['documents'][0])
            logger.info(f"Retrieved {len(results['documents'][0])} relevant chunks")
            return context
        else:
            logger.warning("No relevant context found")
            return ""
            
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return ""


def cleanup_vector_store(collection_name: str) -> bool:
    """Clean up a specific vector store collection."""
    try:
        safe_collection_name = "".join(
            c if c.isalnum() or c in ['_', '-'] else '_' 
            for c in collection_name
        )[:63]
        
        client = chromadb.PersistentClient(path="./vector_store")
        client.delete_collection(safe_collection_name)
        logger.info(f"Successfully deleted collection: {safe_collection_name}")
        return True
    except Exception as e:
        logger.error(f"Error deleting collection {collection_name}: {e}")
        return False


def get_collection_info(collection_name: str) -> Dict[str, Any]:
    """Get information about a vector store collection."""
    try:
        safe_collection_name = "".join(
            c if c.isalnum() or c in ['_', '-'] else '_' 
            for c in collection_name
        )[:63]
        
        client = chromadb.PersistentClient(path="./vector_store")
        collection = client.get_collection(safe_collection_name)
        
        count = collection.count()
        return {
            'name': collection_name,
            'safe_name': safe_collection_name,
            'document_count': count,
            'status': 'active'
        }
    except Exception as e:
        logger.error(f"Error getting collection info: {e}")
        return {
            'name': collection_name,
            'document_count': 0,
            'status': 'error',
            'error': str(e)
        }


def test_api_connection() -> Dict[str, Any]:
    """Test the Google AI API connection and return available models."""
    try:
        configure_ai()
        available_models = get_available_models()
        
        return {
            'status': 'success',
            'configured': _ai_configured,
            'available_models': available_models[:5],
            'message': 'API connection successful'
        }
    except Exception as e:
        return {
            'status': 'error',
            'configured': False,
            'error': str(e),
            'message': 'API connection failed'
        }
