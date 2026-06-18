import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from rag_engine import RAGEngine
from code_loader import CodeLoader
from config import FLASK_PORT, FLASK_DEBUG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = './uploads'
CORS(app)

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize RAG engine and code loader
rag_engine = None
code_loader = CodeLoader()

def init_rag_engine():
    """Initialize RAG engine."""
    global rag_engine
    try:
        rag_engine = RAGEngine()
        logger.info("RAG engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG engine: {e}")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "AAKIF's Chatbot RAG API"}), 200

@app.route('/api/ingest/directory', methods=['POST'])
def ingest_directory():
    """
    Ingest code files from a directory.
    
    Expected JSON:
    {
        "directory_path": "/path/to/code"
    }
    """
    try:
        data = request.get_json()
        directory_path = data.get('directory_path')
        
        if not directory_path:
            return jsonify({"error": "directory_path is required"}), 400
        
        if not os.path.isdir(directory_path):
            return jsonify({"error": f"Directory not found: {directory_path}"}), 404
        
        # Load documents
        documents = code_loader.load_from_directory(directory_path)
        if not documents:
            return jsonify({"error": "No supported code files found in directory"}), 400
        
        # Ingest into RAG engine
        result = rag_engine.ingest_documents(documents)
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error ingesting directory: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ingest/file', methods=['POST'])
def ingest_file():
    """
    Ingest a single code file.
    Supports both file upload and file path.
    """
    try:
        if 'file' in request.files:
            # Handle file upload
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            documents = code_loader.load_from_file(filepath)
        else:
            # Handle file path from request
            data = request.get_json()
            file_path = data.get('file_path')
            
            if not file_path:
                return jsonify({"error": "file_path is required"}), 400
            
            documents = code_loader.load_from_file(file_path)
        
        if not documents:
            return jsonify({"error": "Failed to load file or unsupported file type"}), 400
        
        result = rag_engine.ingest_documents(documents)
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error ingesting file: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ingest/text', methods=['POST'])
def ingest_text():
    """
    Ingest raw code text.
    
    Expected JSON:
    {
        "code": "code content here",
        "language": "python" (optional)
    }
    """
    try:
        data = request.get_json()
        code = data.get('code')
        language = data.get('language', 'unknown')
        
        if not code:
            return jsonify({"error": "code field is required"}), 400
        
        documents = code_loader.load_from_text(code, f"uploaded_{language}")
        result = rag_engine.ingest_documents(documents)
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error ingesting text: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/query', methods=['POST'])
def query():
    """
    Query the RAG system.
    
    Expected JSON:
    {
        "question": "How do I authenticate users?"
    }
    """
    try:
        data = request.get_json()
        question = data.get('question')
        
        if not question:
            return jsonify({"error": "question field is required"}), 400
        
        result = rag_engine.query(question)
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error querying: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def stats():
    """
    Get RAG system statistics.
    """
    try:
        stats = rag_engine.get_index_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    init_rag_engine()
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=False)
