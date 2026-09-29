# Vector Search Setup Guide (Optional)

Vector search is an optional feature that provides semantic search capabilities using FAISS and sentence transformers.

## Installation (Optional)

If you want to enable vector search, install the following dependencies:

```bash
pip install torch sentence-transformers huggingface-hub
```

Or update requirements.txt by uncommenting the vector search dependencies:

```bash
pip install -r requirements.txt
```

## Version Compatibility

The following versions are compatible:
- `sentence-transformers>=2.2.0,<3.0.0`
- `torch>=1.13.0` (CPU version: `torch` or GPU version: `torch` with CUDA)
- `huggingface-hub>=0.16.0,<0.20.0`

## Note

Vector search is **optional**. The backend will start and function normally without it. Only the `/api/search/enhanced` endpoint will be unavailable if vector search is not installed.

## Current Status

The backend works perfectly fine without vector search. All other features (fuzzy search, autocomplete, filtered search) work without it.





