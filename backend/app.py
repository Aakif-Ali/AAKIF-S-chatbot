import os
import logging
import time
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from rag_engine import RAGEngine
from code_loader import CodeLoader
from conversation_manager import ConversationManager
from hybrid_rag_engine import HybridRAGEngine
from mode_detector import ModeDetector
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

# Initialize components
rag_engine = None
code_loader = CodeLoader()
conversation_manager = None
hybrid_engine = None
mode_detector = ModeDetector()

def init_engines():
    """Initialize all engines."""
    global rag_engine, conversation_manager, hybrid_engine
    try:
        rag_engine = RAGEngine()
        logger.info("RAG engine initialized successfully")
        
        conversation_manager = ConversationManager()
        logger.info("Conversation manager initialized successfully")
        
        hybrid_engine = HybridRAGEngine(rag_engine)
        logger.info("Hybrid RAG engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize engines: {e}")

# ==================== HEALTH CHECK ====================
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy", 
        "service": "AAKIF's Hybrid Chatbot - Personal Assistant & Coding Helper"
    }), 200

# ==================== CODE INGESTION ENDPOINTS ====================
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
        logger.info(f"Ingested {result.get('documents_processed', 0)} documents from directory")
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
        logger.info(f"Ingested code file successfully")
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
        logger.info(f"Ingested code text in {language}")
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error ingesting text: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== CHAT SESSION ENDPOINTS ====================
@app.route('/api/chat/start-session', methods=['POST'])
def start_session():
    """
    Start a new chat session.
    
    Expected JSON (optional):
    {
        "session_id": "custom-session-id" (optional, auto-generated if not provided)
    }
    
    Returns:
    {
        "session_id": "session-id",
        "created_at": "timestamp"
    }
    """
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id') or f"session_{uuid.uuid4().hex[:12]}"
        
        result = conversation_manager.create_session(session_id)
        logger.info(f"Started new chat session: {session_id}")
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    """
    Send a message to the chatbot with full conversation memory.
    
    Expected JSON:
    {
        "session_id": "session-id",
        "message": "Your message here"
    }
    
    Returns:
    {
        "status": "success",
        "mode": "coding" or "general",
        "mode_confidence": 0.85,
        "answer": "Response from chatbot",
        "sources": [...],
        "conversation_memory": [...]
    }
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        user_message = data.get('message')
        
        if not session_id or not user_message:
            return jsonify({"error": "session_id and message are required"}), 400
        
        # Add user message to history
        conversation_manager.add_message(session_id, 'user', user_message)
        logger.info(f"[{session_id}] User message received")
        
        # Get conversation history for context
        history = conversation_manager.get_history(session_id, limit=6)
        
        # Get response using hybrid engine (detects coding vs general)
        result = hybrid_engine.query_hybrid(user_message, history)
        
        # Add assistant message to history with mode
        assistant_message = result.get('answer', '')
        mode = result.get('mode', 'unknown')
        conversation_manager.add_message(session_id, 'assistant', assistant_message, mode)
        
        logger.info(f"[{session_id}] Response generated in {mode} mode")
        
        # Add conversation memory to response
        result['conversation_memory'] = conversation_manager.get_history(session_id, limit=6)
        result['session_id'] = session_id
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/quick-query', methods=['POST'])
def quick_query():
    """
    One-off query without session memory.
    Good for quick questions without conversation context.
    
    Expected JSON:
    {
        "message": "Your message here",
        "detect_mode": true (optional, auto-detect coding/general)
    }
    
    Returns:
    {
        "status": "success",
        "mode": "coding" or "general",
        "mode_confidence": 0.85,
        "answer": "Response",
        "sources": [...]
    }
    """
    try:
        data = request.get_json()
        message = data.get('message')
        detect_mode = data.get('detect_mode', True)
        
        if not message:
            return jsonify({"error": "message is required"}), 400
        
        # Query without conversation history
        result = hybrid_engine.query_hybrid(message, conversation_history=None)
        
        logger.info(f"Quick query processed in {result.get('mode')} mode")
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in quick query: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """
    Get conversation history for a session.
    
    Query parameters:
    - limit: number of messages to retrieve (default: 10)
    
    Returns:
    {
        "session_id": "session-id",
        "history": [...]
    }
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        history = conversation_manager.get_history(session_id, limit)
        
        logger.info(f"Retrieved {len(history)} messages from session {session_id}")
        return jsonify({
            "session_id": session_id, 
            "history": history,
            "total_messages": len(history)
        }), 200
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/clear/<session_id>', methods=['POST'])
def clear_history(session_id):
    """
    Clear conversation history for a session.
    
    Returns:
    {
        "status": "success",
        "message": "History cleared",
        "session_id": "session-id"
    }
    """
    try:
        conversation_manager.clear_history(session_id)
        logger.info(f"Cleared history for session {session_id}")
        return jsonify({
            "status": "success", 
            "message": "History cleared",
            "session_id": session_id
        }), 200
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== MODE DETECTION ENDPOINT ====================
@app.route('/api/mode/detect', methods=['POST'])
def detect_mode():
    """
    Detect if a message is coding or general question.
    
    Expected JSON:
    {
        "message": "Your message here"
    }
    
    Returns:
    {
        "mode": "coding" or "general",
        "confidence": 0.85
    }
    """
    try:
        data = request.get_json()
        message = data.get('message')
        
        if not message:
            return jsonify({"error": "message is required"}), 400
        
        mode, confidence = mode_detector.detect_mode(message)
        logger.info(f"Mode detection: {mode} (confidence: {confidence})")
        
        return jsonify({
            "mode": mode,
            "confidence": confidence
        }), 200
    except Exception as e:
        logger.error(f"Error detecting mode: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== STATS ENDPOINT ====================
@app.route('/api/stats', methods=['GET'])
def stats():
    """
    Get RAG system statistics.
    
    Returns:
    {
        "status": "ready" or "empty",
        "index_path": "...",
        "embedding_model": "..."
    }
    """
    try:
        stats = rag_engine.get_index_stats()
        logger.info("Stats retrieved")
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

# ==================== MAIN ====================
if __name__ == '__main__':
    init_engines()
    logger.info(f"Starting AAKIF's Hybrid Chatbot on port {FLASK_PORT}")
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=FLASK_DEBUG)
