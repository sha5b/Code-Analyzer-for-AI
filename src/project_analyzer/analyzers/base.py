"""
Base analyzer class and common functionality
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..models import ProjectAnalysis


class BaseAnalyzer(ABC):
    """Base class for all analyzers"""
    
    def __init__(self, root_path: str | Path):
        self.root_path = Path(root_path).resolve()
        if not self.root_path.exists():
            raise ValueError(f"Path does not exist: {root_path}")
        
    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """Perform analysis and return results"""
        pass
    
    def get_file_type(self, path: Path) -> str:
        """Determine file type/language from extension"""
        ext = path.suffix.lower()
        return {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react-typescript',
            '.vue': 'vue',
            '.java': 'java',
            '.cpp': 'c++',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.cs': 'c#',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.r': 'r',
            '.scala': 'scala',
            '.m': 'objective-c',
            '.h': 'header',
            '.css': 'css',
            '.scss': 'scss',
            '.less': 'less',
            '.html': 'html',
            '.xml': 'xml',
            '.json': 'json',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.md': 'markdown',
            '.txt': 'text',
            '.sh': 'shell',
            '.bash': 'shell',
            '.zsh': 'shell',
            '.fish': 'shell',
        }.get(ext, 'unknown')
    
    def should_ignore(self, path: Path) -> bool:
        """Check if file/directory should be ignored"""
        ignore_patterns = {
            # Dirs
            '__pycache__', 'node_modules', '.git', '.svn', '.hg',
            'venv', 'env', '.env', '.venv', 'build', 'dist',
            # Files
            '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib',
            '.class', '.o', '.obj',
            # Hidden
            '.DS_Store', '.gitignore', '.gitattributes',
        }
        
        return (
            path.name in ignore_patterns or
            path.name.startswith('.') or
            any(p in path.parts for p in ignore_patterns)
        )
    
    def get_file_encoding(self, path: Path) -> str:
        """Detect file encoding"""
        # TODO: Implement proper encoding detection
        return 'utf-8'
    
    def is_binary(self, path: Path) -> bool:
        """Check if file is binary"""
        try:
            with open(path, 'tr') as f:
                f.read(1024)
                return False
        except UnicodeDecodeError:
            return True
