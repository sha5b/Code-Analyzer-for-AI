"""
Base language analyzer class
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any

from ...models import File, Function, Class, Variable, Import, CodeLocation

class LanguageAnalyzer(ABC):
    """Base class for language-specific analyzers"""
    
    def __init__(self, file_path: Path, content: str):
        self.file_path = file_path
        self.content = content
        
    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """Analyze the file and return extracted information"""
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Get file dependencies"""
        pass
    
    def extract_docstring(self, content: str) -> Optional[str]:
        """Extract docstring/comments from code"""
        pass
    
    def parse_type_annotations(self, annotation: str) -> str:
        """Parse and normalize type annotations"""
        pass
