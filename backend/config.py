import os
from dotenv import load_dotenv

load_dotenv()

# Flask Config
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))

# FAISS Config
FAISS_INDEX_PATH = os.getenv('FAISS_INDEX_PATH', './faiss_index')
FAISS_DIMENSION = int(os.getenv('FAISS_DIMENSION', 384))

# Ollama Config (Mistral)
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')
OLLAMA_TEMPERATURE = float(os.getenv('OLLAMA_TEMPERATURE', 0.7))

# Embedding Config
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

# RAG Config
RETRIEVAL_TOP_K = int(os.getenv('RETRIEVAL_TOP_K', 5))
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))

# Supported file extensions for code ingestion
SUPPORTED_EXTENSIONS = [
    '.py', '.js', '.ts', '.tsx', '.jsx',
    '.java', '.cpp', '.c', '.h', '.go',
    '.rs', '.rb', '.php', '.swift', '.kt',
    '.cs', '.scala', '.sh', '.sql', '.yaml',
    '.yml', '.json', '.xml', '.html', '.css'
]
