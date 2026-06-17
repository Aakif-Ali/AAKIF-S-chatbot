import os
import logging
from typing import List, Dict, Tuple
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
from config import (
    FAISS_INDEX_PATH, EMBEDDING_MODEL, OLLAMA_BASE_URL,
    OLLAMA_MODEL, OLLAMA_TEMPERATURE, RETRIEVAL_TOP_K,
    CHUNK_SIZE, CHUNK_OVERLAP
)

logger = logging.getLogger(__name__)

class RAGEngine:
    """RAG engine using FAISS and Mistral via Ollama."""
    
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.qa_chain = None
        self.llm = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
        self._initialize()
    
    def _initialize(self):
        """Initialize embeddings and LLM."""
        try:
            logger.info(f"Initializing embeddings with model: {EMBEDDING_MODEL}")
            self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
            
            logger.info(f"Initializing Mistral LLM at {OLLAMA_BASE_URL}")
            self.llm = Ollama(
                base_url=OLLAMA_BASE_URL,
                model=OLLAMA_MODEL,
                temperature=OLLAMA_TEMPERATURE
            )
            
            # Try to load existing FAISS index
            if os.path.exists(FAISS_INDEX_PATH):
                logger.info(f"Loading existing FAISS index from {FAISS_INDEX_PATH}")
                self.vectorstore = FAISS.load_local(
                    FAISS_INDEX_PATH,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                self._setup_qa_chain()
        except Exception as e:
            logger.error(f"Error initializing RAG engine: {e}")
            raise
    
    def ingest_documents(self, documents: List[Document]) -> Dict:
        """
        Ingest documents and create/update FAISS index.
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            Dictionary with ingestion statistics
        """
        try:
            logger.info(f"Processing {len(documents)} documents")
            
            # Split documents into chunks
            splits = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(splits)} text chunks")
            
            # Create or update FAISS index
            if self.vectorstore is None:
                logger.info("Creating new FAISS index")
                self.vectorstore = FAISS.from_documents(
                    splits,
                    self.embeddings
                )
            else:
                logger.info("Adding documents to existing FAISS index")
                self.vectorstore.add_documents(splits)
            
            # Save index
            os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
            self.vectorstore.save_local(FAISS_INDEX_PATH)
            logger.info(f"FAISS index saved to {FAISS_INDEX_PATH}")
            
            # Setup QA chain
            self._setup_qa_chain()
            
            return {
                "status": "success",
                "documents_processed": len(documents),
                "chunks_created": len(splits),
                "index_saved": True
            }
        except Exception as e:
            logger.error(f"Error ingesting documents: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _setup_qa_chain(self):
        """Setup RetrievalQA chain."""
        if self.vectorstore is None or self.llm is None:
            logger.warning("Cannot setup QA chain: vectorstore or LLM not initialized")
            return
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": RETRIEVAL_TOP_K}
            ),
            return_source_documents=True,
            verbose=True
        )
    
    def query(self, question: str) -> Dict:
        """
        Query the RAG system.
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and source documents
        """
        if self.qa_chain is None:
            return {
                "status": "error",
                "error": "No documents have been ingested yet. Please ingest code files first."
            }
        
        try:
            logger.info(f"Processing query: {question}")
            result = self.qa_chain({"query": question})
            
            sources = []
            for doc in result.get("source_documents", []):
                sources.append({
                    "content": doc.page_content[:500],  # First 500 chars
                    "source": doc.metadata.get("source", "unknown"),
                    "file_type": doc.metadata.get("file_type", "unknown")
                })
            
            return {
                "status": "success",
                "answer": result["result"],
                "sources": sources
            }
        except Exception as e:
            logger.error(f"Error querying: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_index_stats(self) -> Dict:
        """
        Get statistics about the current FAISS index.
        
        Returns:
            Dictionary with index statistics
        """
        if self.vectorstore is None:
            return {"status": "empty", "documents": 0}
        
        try:
            # FAISS stores index info
            stats = {
                "status": "ready",
                "index_path": FAISS_INDEX_PATH,
                "embedding_model": EMBEDDING_MODEL
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {"status": "error", "error": str(e)}
