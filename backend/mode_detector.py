import re
from typing import Tuple

class ModeDetector:
    """Detects whether user is asking coding or general questions."""
    
    CODING_KEYWORDS = [
        # Generic programming
        'code', 'function', 'debug', 'error', 'bug', 'fix', 'syntax',
        'variable', 'class', 'method', 'import', 'module', 'library',
        'algorithm', 'data structure', 'api', 'endpoint', 'database',
        'programming', 'developer', 'implement', 'deploy', 'compile',
        'exception', 'traceback', 'stack trace', 'breakpoint',
        
        # Specific languages
        'python', 'javascript', 'java', 'c++', 'rust', 'go', 'php',
        'typescript', 'ruby', 'kotlin', 'swift', 'c#', 'scala',
        'html', 'css', 'sql', 'bash', 'shell',
        
        # Common tasks
        'refactor', 'optimize', 'performance', 'unit test', 'test',
        'deployment', 'devops', 'docker', 'kubernetes', 'ci/cd',
        'authentication', 'validation', 'error handling', 'logging',
        'framework', 'library', 'package', 'dependency',
        
        # Git/Version control
        'git', 'commit', 'merge', 'branch', 'pull request', 'pr',
        'repository', 'push', 'pull', 'clone',
        
        # Code patterns
        'design pattern', 'best practice', 'documentation',
        'variable name', 'function name', 'parameter',
    ]
    
    CODE_PATTERNS = [
        r'```[\s\S]*?```',  # Code blocks
        r'def\s+\w+', r'function\s+\w+', r'class\s+\w+',  # Function/class definitions
        r'import\s+\w+', r'require\s*\(', r'const\s+\w+\s*=',  # Imports
        r'\w+\.\w+\(', r'{\s*.*:\s*.*}',  # Method calls, objects
        r'async\s+def', r'=>', r'function\*',  # Modern syntax
    ]
    
    @staticmethod
    def detect_mode(message: str) -> Tuple[str, float]:
        """
        Detect if message is coding or general.
        Returns: (mode, confidence) - mode is 'coding' or 'general'
        """
        message_lower = message.lower()
        
        # Check for code blocks or code patterns
        for pattern in ModeDetector.CODE_PATTERNS:
            if re.search(pattern, message):
                return 'coding', 0.95
        
        # Count coding keywords
        coding_count = sum(1 for keyword in ModeDetector.CODING_KEYWORDS 
                          if keyword in message_lower)
        
        # Determine mode
        if coding_count > 0:
            confidence = min(0.95, 0.5 + (coding_count * 0.15))
            return 'coding', confidence
        else:
            # Default to general for neutral questions
            return 'general', 0.3
