import json
import sqlite3
from datetime import datetime
from typing import List, Dict

class ConversationManager:
    """Manages conversation history and context."""
    
    def __init__(self, db_path='./conversations.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for conversation storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                messages TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def create_session(self, session_id: str) -> Dict:
        """Create a new conversation session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        try:
            cursor.execute('''
                INSERT INTO conversations (session_id, messages, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (session_id, json.dumps([]), now, now))
            conn.commit()
        except sqlite3.IntegrityError:
            # Session already exists
            pass
        finally:
            conn.close()
        return {"session_id": session_id, "created_at": now}
    
    def add_message(self, session_id: str, role: str, content: str, mode: str = None):
        """Add a message to conversation history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get existing messages
        cursor.execute('SELECT messages FROM conversations WHERE session_id = ?', (session_id,))
        result = cursor.fetchone()
        
        if not result:
            self.create_session(session_id)
            cursor.execute('SELECT messages FROM conversations WHERE session_id = ?', (session_id,))
            result = cursor.fetchone()
        
        messages = json.loads(result[0])
        
        # Add new message
        messages.append({
            "role": role,
            "content": content,
            "mode": mode,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update database
        cursor.execute('''
            UPDATE conversations SET messages = ?, updated_at = ?
            WHERE session_id = ?
        ''', (json.dumps(messages), datetime.now().isoformat(), session_id))
        conn.commit()
        conn.close()
    
    def get_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Retrieve conversation history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT messages FROM conversations WHERE session_id = ?', (session_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return []
        
        messages = json.loads(result[0])
        return messages[-limit:]  # Return last N messages
    
    def clear_history(self, session_id: str):
        """Clear conversation history for a session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE conversations SET messages = ?, updated_at = ?
            WHERE session_id = ?
        ''', (json.dumps([]), datetime.now().isoformat(), session_id))
        conn.commit()
        conn.close()
