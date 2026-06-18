import os
import logging
from pathlib import Path
from typing import List, Dict
from langchain.schema import Document
from config import SUPPORTED_EXTENSIONS

logger = logging.getLogger(__name__)

class CodeLoader:
    """Load code files and convert them to LangChain documents."""
    
    def __init__(self):
        self.supported_extensions = SUPPORTED_EXTENSIONS
    
    def load_from_directory(self, directory_path: str) -> List[Document]:
        """
        Load all code files from a directory recursively.
        
        Args:
            directory_path: Path to the directory containing code files
            
        Returns:
            List of LangChain Document objects
        """
        documents = []
        directory = Path(directory_path)
        
        if not directory.exists():
            logger.error(f"Directory does not exist: {directory_path}")
            return documents
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    content = self._read_file(file_path)
                    if content:
                        doc = Document(
                            page_content=content,
                            metadata={
                                'source': str(file_path.relative_to(directory)),
                                'file_path': str(file_path),
                                'file_type': file_path.suffix
                            }
                        )
                        documents.append(doc)
                        logger.info(f"Loaded: {file_path}")
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")
        
        logger.info(f"Total files loaded: {len(documents)}")
        return documents
    
    def load_from_file(self, file_path: str) -> List[Document]:
        """
        Load a single code file.
        
        Args:
            file_path: Path to the code file
            
        Returns:
            List containing a single LangChain Document
        """
        file_obj = Path(file_path) 

        print("filepath received:", file_path)
        print("file_obj:", file_obj)
        print("suffix:", repr(file_obj.suffix))
        print("suffix lower:", repr(file_obj.suffix.lower()))
        
        if not file_obj.exists():
            logger.error(f"File does not exist: {file_path}")
            return []
        
        print("Uploaded file:", file_obj)
        print("Extension:", repr(file_obj.suffix.lower()))
        print("Supported:", self.supported_extensions)

        if file_obj.suffix.lower() not in self.supported_extensions:
            logger.error(f"Unsupported file type: {file_obj.suffix}")
            return []
        
        try:
            content = self._read_file(file_obj)
            doc = Document(
                page_content=content,
                metadata={
                    'source': file_obj.name,
                    'file_path': str(file_obj),
                    'file_type': file_obj.suffix
                }
            )
            return [doc]
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return []
    
    def load_from_text(self, code_text: str, file_name: str = 'uploaded_code') -> List[Document]:
        """
        Load code from raw text.
        
        Args:
            code_text: Raw code content
            file_name: Name to assign to the document
            
        Returns:
            List containing a single LangChain Document
        """
        doc = Document(
            page_content=code_text,
            metadata={
                'source': file_name,
                'file_type': 'txt'
            }
        )
        return [doc]
    
    @staticmethod
    def _read_file(file_path: Path, max_size_mb: int = 10) -> str:
        """
        Read file content with size limit.
        
        Args:
            file_path: Path object to the file
            max_size_mb: Maximum file size in MB
            
        Returns:
            File content as string
        """
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            logger.warning(f"File too large: {file_path} ({file_size_mb:.2f}MB)")
            return ""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            logger.warning(f"Could not decode file as UTF-8: {file_path}")
            return ""
