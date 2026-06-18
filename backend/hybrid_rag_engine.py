import logging
from typing import Dict, List
from rag_engine import RAGEngine
from mode_detector import ModeDetector

logger = logging.getLogger(__name__)

class HybridRAGEngine:
    """Extends RAG engine with dual-mode capability for coding and general assistance."""
    
    CODING_SYSTEM_PROMPT = """You are an expert coding assistant. You help developers by:
    - Debugging code and explaining errors
    - Writing and optimizing code
    - Explaining programming concepts and patterns
    - Suggesting best practices and improvements
    - Analyzing code quality, performance, and security
    - Explaining error messages and stack traces
    
    When answering coding questions:
    1. Be precise and technical in your explanations
    2. Provide relevant code examples when applicable
    3. Suggest optimizations or alternative approaches
    4. Reference the source code snippets provided in context
    5. Explain the reasoning behind recommendations
    6. Point out potential issues or edge cases
    7. Follow best practices for the language being used
    
    Keep responses focused, clear, and actionable for developers."""
    
    GENERAL_SYSTEM_PROMPT = """You are a helpful, friendly, and knowledgeable assistant. You:
    - Answer general questions with clarity and accuracy
    - Provide helpful information on various topics
    - Engage in natural, conversational dialogue
    - Give clear explanations for complex concepts
    - Stay friendly, professional, and respectful
    - Ask clarifying questions when needed
    
    When answering general questions:
    1. Be clear and concise in your response
    2. Break down complex topics into understandable parts
    3. Use examples to illustrate points when helpful
    4. Be honest if you're uncertain about something
    5. Maintain a conversational and friendly tone
    
    Keep responses relevant and easy to understand."""
    
    def __init__(self, rag_engine: RAGEngine):
        self.rag_engine = rag_engine
        self.mode_detector = ModeDetector()
        logger.info("HybridRAGEngine initialized")
    
    def query_hybrid(self, question: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Query using mode detection and appropriate prompting.
        
        Args:
            question: User question
            conversation_history: Previous messages for context
            
        Returns:
            Dict with answer, mode, sources, and confidence
        """
        # Detect mode
        mode, confidence = self.mode_detector.detect_mode(question)
        logger.info(f"Detected mode: {mode} (confidence: {confidence})")
        
        # Get system prompt based on mode
        system_prompt = (self.CODING_SYSTEM_PROMPT 
                        if mode == 'coding' 
                        else self.GENERAL_SYSTEM_PROMPT)
        
        # Build context from history
        context = self._build_context(conversation_history)
        
        # Build enhanced question with system context
        if context:
            enhanced_question = f"Conversation context:\n{context}\n\nCurrent question: {question}"
        else:
            enhanced_question = question
        
        # Query RAG
        try:
            result = self.rag_engine.query(enhanced_question)
            
            # Add mode information to result
            result['mode'] = mode
            result['mode_confidence'] = confidence
            result['system_context'] = system_prompt
            
            logger.info(f"Query completed successfully. Mode: {mode}")
            return result
        except Exception as e:
            logger.error(f"Error in hybrid query: {e}")
            return {
                "status": "error",
                "error": str(e),
                "mode": mode,
                "mode_confidence": confidence
            }
    
    def _build_context(self, history: List[Dict]) -> str:
        """Build context string from conversation history."""
        if not history:
            return ""
        
        context_lines = []
        # Use last 5 messages for context (excluding current turn)
        relevant_history = history[-5:] if len(history) > 1 else history
        
        for msg in relevant_history:
            role = msg.get('role', 'user').capitalize()
            content = msg.get('content', '')[:200]  # Limit content length
            mode = msg.get('mode', '')
            mode_info = f" [{mode}]" if mode else ""
            context_lines.append(f"{role}{mode_info}: {content}")
        
        return "\n".join(context_lines)
