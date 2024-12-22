"""
File structure analyzer - Analyzes project directory structure and file metadata
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..models import ProjectStructure, File
from .base import BaseAnalyzer


class StructureAnalyzer(BaseAnalyzer):
    """Analyzes project structure and generates file metadata"""
    
    def __init__(self, root_path: str | Path):
        super().__init__(root_path)
        self.total_files = 0
        self.total_size = 0
        self.languages: Dict[str, int] = {}
        
    def analyze(self) -> Dict[str, any]:
        """Analyze project structure and return results"""
        structure = self._analyze_path(self.root_path)
        
        return {
            "structure": structure,
            "total_files": self.total_files,
            "total_size": self.total_size,
            "languages": self.languages
        }
    
    def _analyze_path(self, path: Path) -> ProjectStructure:
        """Recursively analyze directory or file"""
        if self.should_ignore(path):
            return None
            
        is_dir = path.is_dir()
        name = path.name or path.anchor
        
        # Get file/dir metadata
        try:
            stat = path.stat()
            size = stat.st_size if not is_dir else None
            modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
        except (OSError, PermissionError):
            size = None
            modified = None
            
        structure = ProjectStructure(
            name=name,
            path=str(path.relative_to(self.root_path)),
            is_dir=is_dir,
            size_bytes=size,
            last_modified=modified
        )
        
        if is_dir:
            # Recursively process directory contents
            try:
                for child in sorted(path.iterdir()):
                    child_structure = self._analyze_path(child)
                    if child_structure:
                        structure.children.append(child_structure)
            except (OSError, PermissionError):
                pass
                
        else:
            # Process file
            self.total_files += 1
            if size:
                self.total_size += size
                
            # Track language statistics
            lang = self.get_file_type(path)
            self.languages[lang] = self.languages.get(lang, 0) + 1
            
        return structure
    
    def get_files_by_type(self, file_type: str) -> List[Path]:
        """Get all files of a specific type/language"""
        files: List[Path] = []
        
        def collect_files(path: Path):
            if path.is_file() and not self.should_ignore(path):
                if self.get_file_type(path) == file_type:
                    files.append(path)
            elif path.is_dir():
                try:
                    for child in path.iterdir():
                        collect_files(child)
                except (OSError, PermissionError):
                    pass
                    
        collect_files(self.root_path)
        return files
    
    def get_file_metadata(self, path: Path) -> Optional[File]:
        """Get detailed metadata for a single file"""
        if not path.is_file() or self.should_ignore(path):
            return None
            
        try:
            stat = path.stat()
            
            return File(
                path=str(path.relative_to(self.root_path)),
                size_bytes=stat.st_size,
                last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                language=self.get_file_type(path),
                encoding=self.get_file_encoding(path)
            )
        except (OSError, PermissionError):
            return None
            
    def find_entry_points(self) -> List[str]:
        """Find likely project entry points"""
        entry_points = []
        
        # Common entry point patterns
        patterns = {
            'python': ['main.py', 'app.py', 'run.py'],
            'javascript': ['index.js', 'main.js', 'app.js'],
            'typescript': ['index.ts', 'main.ts', 'app.ts'],
            'java': ['Main.java', 'App.java'],
            'go': ['main.go'],
            'rust': ['main.rs'],
        }
        
        def check_entry_points(path: Path):
            if path.is_file():
                if path.name.lower() in [p.lower() for patterns in patterns.values() for p in patterns]:
                    entry_points.append(str(path.relative_to(self.root_path)))
            elif path.is_dir() and not self.should_ignore(path):
                try:
                    for child in path.iterdir():
                        check_entry_points(child)
                except (OSError, PermissionError):
                    pass
                    
        check_entry_points(self.root_path)
        return entry_points
