# 🤖 AAKIF's RAG Chatbot

A powerful Retrieval-Augmented Generation (RAG) chatbot that helps you ask questions about your code and get AI-powered answers with relevant code snippets.

## Features

✨ **RAG-Based Architecture**
- Uses FAISS for efficient vector similarity search
- Supports Mistral LLM via Ollama for local inference
- Context-aware code retrieval and generation

📚 **Multi-Format Code Ingestion**
- Upload individual code files
- Ingest entire directories recursively
- Paste code directly
- Support for 20+ programming languages

💬 **Interactive Chat Interface**
- Clean, modern React UI
- Real-time streaming responses
- Syntax-highlighted code blocks
- Source attribution with code snippets

🔧 **Flexible Deployment**
- Flask API backend
- React frontend
- Docker support
- Local execution with no cloud dependencies

## Tech Stack

**Backend:**
- Flask - Web framework
- LangChain - LLM orchestration
- FAISS - Vector database
- Ollama - Local LLM runtime
- Sentence Transformers - Embeddings

**Frontend:**
- React 18
- Vite - Build tool
- Axios - HTTP client
- CSS3 - Styling

## Prerequisites

1. **Python 3.10+**
2. **Node.js 16+**
3. **Ollama** (for running Mistral locally)
   - Download: https://ollama.ai
   - After installation: `ollama pull mistral`

## Installation

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

### 3. Environment Configuration

```bash
cd backend
cp .env.example .env
# Edit .env with your configuration if needed
```

## Running the Application

### Step 1: Start Ollama (in a separate terminal)

```bash
ollama serve
```

If this is your first time, pull the Mistral model:
```bash
ollama pull mistral
```

### Step 2: Start the Backend API

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

The API will be available at `http://localhost:5000`

### Step 3: Start the Frontend

In another terminal:
```bash
cd frontend
npm run dev
```

The UI will be available at `http://localhost:3000`

## Usage

### Ingesting Code

1. Click the **"📤 Upload Code"** tab
2. Choose one of three methods:
   - **File Upload**: Upload a single code file
   - **Paste Code**: Paste code directly
   - **Directory**: Process an entire directory
3. Wait for confirmation

### Asking Questions

1. Go to the **"💬 Chat"** tab
2. Type your question about the ingested code
3. The chatbot will:
   - Search relevant code chunks
   - Generate an answer using Mistral
   - Show source code snippets

### Example Questions

- "How do you handle authentication?"
- "Show me the database connection code"
- "What validation functions are available?"
- "How is error handling implemented?"
- "Find all API endpoints"

## API Endpoints

### Health Check
```bash
GET /health
```

### Ingest Code

**Upload File:**
```bash
POST /api/ingest/file
Content-Type: multipart/form-data
Body: file=<file>
```

**Ingest Directory:**
```bash
POST /api/ingest/directory
Content-Type: application/json
Body: {"directory_path": "/path/to/code"}
```

**Paste Code:**
```bash
POST /api/ingest/text
Content-Type: application/json
Body: {"code": "<code>", "language": "python"}
```

### Query
```bash
POST /api/query
Content-Type: application/json
Body: {"question": "Your question here"}

Response:
{
  "status": "success",
  "answer": "Generated answer",
  "sources": [
    {
      "content": "Code snippet",
      "source": "filename.py",
      "file_type": ".py"
    }
  ]
}
```

### Statistics
```bash
GET /api/stats
```

## Configuration

Edit `backend/.env` to customize:

```env
# Flask
FLASK_PORT=5000
FLASK_DEBUG=True

# Ollama/Mistral
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
OLLAMA_TEMPERATURE=0.7

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2

# RAG
RETRIEVAL_TOP_K=5
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Supported File Types

- Python: `.py`
- JavaScript/TypeScript: `.js`, `.ts`, `.tsx`, `.jsx`
- Java: `.java`
- C/C++: `.c`, `.cpp`, `.h`
- Go: `.go`
- Rust: `.rs`
- Ruby: `.rb`
- PHP: `.php`
- Swift: `.swift`
- Kotlin: `.kt`
- C#: `.cs`
- Scala: `.scala`
- Shell: `.sh`
- SQL: `.sql`
- YAML: `.yaml`, `.yml`
- JSON: `.json`
- XML: `.xml`
- HTML: `.html`
- CSS: `.css`

## Docker Deployment

Build and run with Docker Compose:

```bash
docker-compose up -d
```

Make sure `docker-compose.yml` is configured with your needs.

## Performance Tips

1. **Chunk Size**: Adjust `CHUNK_SIZE` for better context (larger = more context but slower retrieval)
2. **Retrieval K**: Increase `RETRIEVAL_TOP_K` for more sources (default: 5)
3. **Model Temperature**: Lower values (0.3) for deterministic answers, higher (0.9) for creative responses
4. **Embedding Model**: Use heavier models for better quality but slower performance

## Troubleshooting

### Ollama Not Connecting
```bash
# Make sure Ollama is running
ollama serve

# Try pinging it
curl http://localhost:11434
```

### "No documents indexed yet"
- Upload code files or directories first using the "📤 Upload Code" tab

### Slow Response Times
- Reduce `CHUNK_SIZE` or `RETRIEVAL_TOP_K`
- Use lighter embedding model
- Ensure adequate RAM (at least 8GB recommended)

### FAISS Index Errors
- Delete `faiss_index` folder and re-ingest documents
- Ensure FAISS_DIMENSION matches embedding model output

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues and questions:
- Create a GitHub issue
- Check existing documentation
- Review the troubleshooting section

---

**Made with ❤️ by AAKIF**
