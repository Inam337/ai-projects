# ingest.py
import os
import time
import uuid
import requests
from urllib.parse import urlparse
#from sentence_transformers import SentenceTransformer
import numpy as np
# import chromadb
# from chromadb.config import Settings
from tqdm import tqdm
from datetime import datetime
import config  # copy config_example.py -> config.py and edit

# ensure download dir
os.makedirs(config.DOWNLOAD_DIR, exist_ok=True)
os.makedirs(config.CHROMA_PERSIST_DIRECTORY, exist_ok=True)

# MODEL = SentenceTransformer(config.EMBEDDING_MODEL)  # Disabled for now

# Initialize ChromaDB client (DISABLED FOR NOW)
# chroma_client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIRECTORY)

# Get or create collection (DISABLED FOR NOW)
# try:
#     collection = chroma_client.get_collection(name=config.CHROMA_COLLECTION_NAME)
# except:
#     collection = chroma_client.create_collection(
#         name=config.CHROMA_COLLECTION_NAME,
#         metadata={"hnsw:space": "cosine"}
#     )

def google_image_search(query, site=None, num=10, start=1):
    """
    Uses Google Custom Search JSON API to get image results.
    site: domain string to restrict (e.g., "ikea.com")
    """
    params = {
        "key": config.GOOGLE_API_KEY,
        "cx": config.GOOGLE_CX,
        "searchType": "image",
        "q": query,
        "num": min(num, 10),
        "start": start,
    }
    if site:
        params["q"] = f"{query} site:{site}"
    r = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def download_url(url, dest_dir):
    try:
        r = requests.get(url, stream=True, timeout=20)
        r.raise_for_status()
        parsed = urlparse(url)
        fname = os.path.basename(parsed.path) or str(uuid.uuid4())
        path = os.path.join(dest_dir, fname)
        with open(path, "wb") as f:
            for chunk in r.iter_content(1024*8):
                f.write(chunk)
        return path
    except Exception as e:
        print("download failed:", e, url)
        return None

def upsert_product(doc_id, vector, metadata):
    # ChromaDB accepts vectors as list[float]
    collection.upsert(
        ids=[doc_id],
        embeddings=[vector],
        metadatas=[metadata]
    )

def process_query_and_upsert(query, num_results=20):
    results_indexed = 0
    try:
        # Search across all domains without site restriction
        response = google_image_search(query, site=None, num=num_results)
        items = response.get("items", [])
        for it in items:
            image_url = it.get("link")
            title = it.get("title")
            snippet = it.get("snippet")
            # Some sites include canonical page link in 'image.contextLink' or 'image' subfields
            context = it.get("image", {})
            page_link = it.get("image", {}).get("contextLink") or it.get("contextLink") or it.get("displayLink")
            # Extract domain from the page link or image URL
            source_domain = None
            if page_link:
                from urllib.parse import urlparse
                parsed = urlparse(page_link)
                source_domain = parsed.netloc
            elif image_url:
                from urllib.parse import urlparse
                parsed = urlparse(image_url)
                source_domain = parsed.netloc
            
            # attempt to download image locally (optional)
            local_path = download_url(image_url, config.DOWNLOAD_DIR)
            # collect model links if the page contains them (not available via Google search result):
            # For simplicity, we store page_link and later you can scrape the page for .obj/.glb links if allowed.
            metadata_text = " ".join(filter(None, [title, snippet, page_link, source_domain]))
            embedding = MODEL.encode(metadata_text).tolist()
            doc_id = str(uuid.uuid4())
            metadata = {
                "title": title,
                "snippet": snippet,
                "image_url": image_url,
                "local_image_path": local_path,
                "page_link": page_link,
                "source_domain": source_domain,
                "ingested_at": datetime.utcnow().isoformat() + "Z",
            }
            upsert_product(doc_id, embedding, metadata)
            results_indexed += 1
    except Exception as e:
        print("google api error:", e)
    
    return results_indexed

def vector_search(query, top_k=10):
    """
    Search in vector database only using ChromaDB (DISABLED FOR NOW)
    """
    # Vector search is disabled - return empty results
    print(f"Vector search disabled - query: {query}")
    return []

def search_engine_search(query, num_results=20):
    """
    Search using Google Custom Search API only
    """
    results = []
    try:
        # Search across all domains without site restriction
        response = google_image_search(query, site=None, num=num_results)
        items = response.get("items", [])
        for item in items:
            image_url = item.get("link")
            title = item.get("title")
            snippet = item.get("snippet")
            context = item.get("image", {})
            page_link = item.get("image", {}).get("contextLink") or item.get("contextLink") or item.get("displayLink")
            
            # Extract domain from the page link or image URL
            source_domain = None
            if page_link:
                from urllib.parse import urlparse
                parsed = urlparse(page_link)
                source_domain = parsed.netloc
            elif image_url:
                from urllib.parse import urlparse
                parsed = urlparse(image_url)
                source_domain = parsed.netloc
            
            results.append({
                "id": f"google_{uuid.uuid4()}",
                "score": 1.0,  # Google results don't have similarity scores
                "title": title,
                "image_url": image_url,
                "page_link": page_link,
                "source_domain": source_domain,
                "snippet": snippet,
                "search_type": "google"
            })
    except Exception as e:
        print(f"Google search error: {e}")
    
    return results

def hybrid_search(query, top_k=10, num_results=20):
    """
    Hybrid search: first search vector DB, then search engine
    """
    # First search in vector database
    vector_results = vector_search(query, top_k)
    
    # Then search using Google API
    google_results = search_engine_search(query, num_results)
    
    # Combine results, prioritizing vector results
    combined_results = vector_results + google_results
    
    # Remove duplicates based on image_url
    seen_urls = set()
    unique_results = []
    for result in combined_results:
        if result.get("image_url") not in seen_urls:
            seen_urls.add(result.get("image_url"))
            unique_results.append(result)
    
    return unique_results[:top_k]

if __name__ == "__main__":
    query = "Brown Chair with Rustic Look"
    count = process_query_and_upsert(query, num_results=20)
    print("Indexed:", count)
