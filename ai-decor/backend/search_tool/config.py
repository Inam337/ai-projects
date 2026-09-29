"""
Configuration for the search tool module.
This file provides the configuration values needed by search.py
"""
import os
import sys

# Add the app directory to the Python path to import settings
app_path = os.path.join(os.path.dirname(__file__), '..', 'app')
if app_path not in sys.path:
    sys.path.append(app_path)

try:
    from app.core.config import settings
    
    # Google Custom Search API
    GOOGLE_API_KEY = settings.GOOGLE_API_KEY
    GOOGLE_CX = settings.GOOGLE_CX
    
    # File and directory paths
    DOWNLOAD_DIR = settings.DOWNLOAD_DIR
    CHROMA_PERSIST_DIRECTORY = settings.CHROMA_PERSIST_DIRECTORY
    CHROMA_COLLECTION_NAME = settings.CHROMA_COLLECTION_NAME
    
    # Embedding model
    EMBEDDING_MODEL = settings.EMBEDDING_MODEL
    
except ImportError:
    # Fallback values if FastAPI config is not available
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_CX = os.getenv("GOOGLE_CX", "")
    DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "./assets")
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "products")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
