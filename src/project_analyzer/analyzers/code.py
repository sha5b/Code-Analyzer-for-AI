"""
Code analyzer - Parses and analyzes source code to extract definitions and relationships
"""
import ast
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, cast, Type
import networkx as nx

from .quality import QualityAnalyzer
from .languages.base import LanguageAnalyzer
from .languages.python import PythonAnalyzer
from .languages.javascript import JavaScriptAnalyzer
from .languages.cpp import CppAnalyzer
from .languages.csharp import CSharpAnalyzer
from .languages.svelte import SvelteAnalyzer

from ..models import (
    CodeLocation,
    Function,
    Class,
    Variable,
    Import,
    File
)
from .base import BaseAnalyzer


class CodeAnalyzer(BaseAnalyzer):
    """Analyzes source code to extract definitions and relationships"""
    
    def __init__(self, root_path: str | Path):
        super().__init__(root_path)
        self.dependency_graph = nx.DiGraph()
        self.current_file: Optional[str] = None
        self.current_class: Optional[str] = None
        self.current_function: Optional[str] = None
        self.quality_analyzer = QualityAnalyzer(root_path)
        
    def analyze(self) -> Dict[str, Any]:
        """Analyze all source code files in project"""
        files: Dict[str, File] = {}
        
        for path in self.root_path.rglob('*'):
            if not path.is_file() or self.should_ignore(path):
                continue
                
            file_type = self.get_file_type(path)
            if file_type not in [
                'python', 'javascript', 'typescript', 'react', 'react-typescript',
                'c++', 'c', 'c#', 'svelte'
            ]:
                continue
                
            try:
                file_analysis = self.analyze_file(path)
                if file_analysis:
                    rel_path = str(path.relative_to(self.root_path))
                    files[rel_path] = file_analysis
            except Exception as e:
                print(f"Error analyzing {path}: {e}")
                
        # Build dependency graph
        self._build_dependency_graph(files)
        
        # Get quality metrics
        quality_results = self.quality_analyzer.analyze()
        
        # Update files with quality metrics
        for file_path, file_analysis in files.items():
            # Update function calls
            if file_path in quality_results["function_calls"]:
                calls = quality_results["function_calls"][file_path]
                for func in file_analysis.functions:
                    func.calls = [c for c in calls if c != func.name]
                for cls in file_analysis.classes:
                    for method in cls.methods:
                        method.calls = [c for c in calls if c != method.name]
                        
                # Update called_by (reverse mapping)
                for func in file_analysis.functions:
                    func.called_by = [
                        f for f, calls in quality_results["function_calls"].items()
                        if func.name in calls and f != file_path
                    ]
                for cls in file_analysis.classes:
                    for method in cls.methods:
                        method.called_by = [
                            f for f, calls in quality_results["function_calls"].items()
                            if method.name in calls and f != file_path
                        ]
            
            # Add design patterns
            if file_path in quality_results.get("design_patterns", {}):
                file_analysis.design_patterns = quality_results["design_patterns"][file_path]
                
            # Add code smells
            if file_path in quality_results.get("code_smells", {}):
                file_analysis.code_smells = quality_results["code_smells"][file_path]
        
        return {
            "files": files,
            "dependencies": self._get_dependencies(),
            "quality_metrics": quality_results
        }
        
    def analyze_file(self, path: Path) -> Optional[File]:
        """Analyze a single source code file"""
        if not path.is_file() or self.should_ignore(path):
            return None
            
        try:
            file_type = self.get_file_type(path)
            rel_path = str(path.relative_to(self.root_path))
            
            file_analysis = File(
                path=rel_path,
                type=file_type,
                language=file_type,
                size_bytes=path.stat().st_size,
                last_modified=datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
                encoding=self.get_file_encoding(path)
            )
            
            content = path.read_text(encoding=self.get_file_encoding(path))
        except UnicodeDecodeError:
            return None
            
        self.current_file = rel_path
        
        # Get appropriate analyzer for file type
        analyzer_class = self._get_analyzer_class(path)
        if analyzer_class:
            try:
                analyzer = analyzer_class(path, content)
                analysis_result = analyzer.analyze()
                
                # Update file analysis with results
                file_analysis.functions.extend(analysis_result.get("functions", []))
                file_analysis.classes.extend(analysis_result.get("classes", []))
                file_analysis.variables.extend(analysis_result.get("variables", []))
                file_analysis.imports.extend(analysis_result.get("imports", []))
                file_analysis.dependencies.extend(analyzer.get_dependencies())
                
            except Exception as e:
                print(f"Error analyzing {path}: {e}")
                return None
                
        return file_analysis
        
    def _get_analyzer_class(self, path: Path) -> Optional[Type[LanguageAnalyzer]]:
        """Get appropriate language analyzer for file type"""
        file_type = self.get_file_type(path)
        
        return {
            'python': PythonAnalyzer,
            'javascript': JavaScriptAnalyzer,
            'typescript': JavaScriptAnalyzer,
            'react': JavaScriptAnalyzer,
            'react-typescript': JavaScriptAnalyzer,
            'c++': CppAnalyzer,
            'c': CppAnalyzer,
            'c#': CSharpAnalyzer,
            'svelte': SvelteAnalyzer
        }.get(file_type)
        
    def _build_dependency_graph(self, files: Dict[str, File]):
        """Build dependency graph from imports"""
        for file_path, file_analysis in files.items():
            self.dependency_graph.add_node(file_path)
            
            # Handle Python imports
            for imp in file_analysis.imports:
                # Convert import to potential file path
                current_dir = Path(file_path).parent
                
                if imp.is_from_import:
                    # Handle relative imports
                    if imp.module.startswith('.'):
                        dots = len(imp.module) - len(imp.module.lstrip('.'))
                        module_parts = imp.module.lstrip('.').split('.')
                        # Go up directories based on dot count
                        target_dir = current_dir
                        for _ in range(dots):
                            target_dir = target_dir.parent
                        module_path = str(target_dir.joinpath(*module_parts))
                    else:
                        module_path = imp.module.replace('.', '/')
                else:
                    module_path = imp.module.replace('.', '/')
                
                # Check if imported module exists in project
                potential_paths = []
                
                # For Python files
                if file_analysis.language == 'python':
                    potential_paths.extend([
                        f"{module_path}.py",
                        f"{module_path}/__init__.py"
                    ])
                # For JS/TS files
                elif file_analysis.language in ['javascript', 'typescript']:
                    potential_paths.extend([
                        f"{module_path}.js",
                        f"{module_path}.ts",
                        f"{module_path}.jsx",
                        f"{module_path}.tsx",
                        f"{module_path}/index.js",
                        f"{module_path}/index.ts"
                    ])
                
                for path in potential_paths:
                    if path in files:
                        self.dependency_graph.add_edge(file_path, path)
                        if path not in file_analysis.dependencies:
                            file_analysis.dependencies.append(path)
                        if file_path not in files[path].dependents:
                            files[path].dependents.append(file_path)
                        break
            
            # Handle JS/TS dependencies
            if file_analysis.language in ['javascript', 'typescript']:
                for dep in file_analysis.dependencies:
                    # Handle different extensions
                    potential_paths = [
                        f"{dep}.js",
                        f"{dep}.ts",
                        f"{dep}.jsx",
                        f"{dep}.tsx",
                        f"{dep}/index.js",
                        f"{dep}/index.ts"
                    ]
                    
                    for path in potential_paths:
                        if path in files:
                            self.dependency_graph.add_edge(file_path, path)
                            if path not in file_analysis.dependencies:
                                file_analysis.dependencies.append(path)
                            if file_path not in files[path].dependents:
                                files[path].dependents.append(file_path)
                            break
                        
    def _get_dependencies(self) -> Dict[str, List[str]]:
        """Get file dependencies from graph"""
        return {
            node: list(self.dependency_graph.successors(node))
            for node in self.dependency_graph.nodes()
        }
