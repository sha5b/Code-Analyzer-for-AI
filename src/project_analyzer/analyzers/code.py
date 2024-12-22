"""
Code analyzer - Parses and analyzes source code to extract definitions and relationships
"""
import ast
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import networkx as nx

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
        
    def analyze(self) -> Dict[str, Any]:
        """Analyze all source code files in project"""
        files: Dict[str, File] = {}
        
        for path in self.root_path.rglob('*'):
            if not path.is_file() or self.should_ignore(path):
                continue
                
            file_type = self.get_file_type(path)
            if file_type not in ['python', 'javascript', 'typescript']:
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
        
        return {
            "files": files,
            "dependencies": self._get_dependencies()
        }
        
    def analyze_file(self, path: Path) -> Optional[File]:
        """Analyze a single source code file"""
        if not path.is_file() or self.should_ignore(path):
            return None
            
        try:
            content = path.read_text(encoding=self.get_file_encoding(path))
        except UnicodeDecodeError:
            return None
            
        self.current_file = str(path.relative_to(self.root_path))
        
        stat = path.stat()
        file_analysis = File(
            path=self.current_file,
            size_bytes=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            language=self.get_file_type(path),
            encoding=self.get_file_encoding(path)
        )
        
        if self.get_file_type(path) == 'python':
            try:
                tree = ast.parse(content)
                self._analyze_python_ast(tree, file_analysis)
            except SyntaxError:
                return None
                
        return file_analysis
        
    def _analyze_python_ast(self, tree: ast.AST, file_analysis: File):
        """Analyze Python AST"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self._handle_import(node, file_analysis)
            elif isinstance(node, ast.ImportFrom):
                self._handle_import_from(node, file_analysis)
            elif isinstance(node, ast.FunctionDef):
                self._handle_function(node, file_analysis)
            elif isinstance(node, ast.ClassDef):
                self._handle_class(node, file_analysis)
            elif isinstance(node, ast.Assign):
                self._handle_assignment(node, file_analysis)
                
    def _handle_import(self, node: ast.Import, file_analysis: File):
        """Handle Import nodes"""
        for name in node.names:
            import_info = Import(
                module=name.name,
                alias=name.asname,
                location=CodeLocation(
                    file=self.current_file,
                    line_start=node.lineno,
                    line_end=node.lineno,
                    column_start=node.col_offset,
                    column_end=node.end_col_offset
                )
            )
            file_analysis.imports.append(import_info)
            
    def _handle_import_from(self, node: ast.ImportFrom, file_analysis: File):
        """Handle ImportFrom nodes"""
        module = node.module or ''
        for name in node.names:
            import_info = Import(
                module=module,
                names=[name.name],
                alias=name.asname,
                location=CodeLocation(
                    file=self.current_file,
                    line_start=node.lineno,
                    line_end=node.lineno,
                    column_start=node.col_offset,
                    column_end=node.end_col_offset
                ),
                is_from_import=True
            )
            file_analysis.imports.append(import_info)
            
    def _handle_function(self, node: ast.FunctionDef, file_analysis: File):
        """Handle FunctionDef nodes"""
        args = []
        for arg in node.args.args:
            arg_type = None
            if arg.annotation:
                try:
                    arg_type = ast.unparse(arg.annotation)
                except (AttributeError, ValueError):
                    arg_type = None
            args.append({"name": arg.arg, "type": arg_type})
            
        returns = None
        if node.returns:
            try:
                returns = ast.unparse(node.returns)
            except (AttributeError, ValueError):
                returns = None
            
        func = Function(
            name=node.name,
            location=CodeLocation(
                file=self.current_file,
                line_start=node.lineno,
                line_end=node.end_lineno,
                column_start=node.col_offset,
                column_end=node.end_col_offset
            ),
            args=args,
            returns=returns,
            docstring=ast.get_docstring(node),
            decorators=[ast.unparse(d) for d in node.decorator_list]
        )
        
        if self.current_class:
            # Add to current class
            for cls in file_analysis.classes:
                if cls.name == self.current_class:
                    cls.methods.append(func)
                    break
        else:
            file_analysis.functions.append(func)
            
    def _handle_class(self, node: ast.ClassDef, file_analysis: File):
        """Handle ClassDef nodes"""
        prev_class = self.current_class
        self.current_class = node.name
        
        cls = Class(
            name=node.name,
            location=CodeLocation(
                file=self.current_file,
                line_start=node.lineno,
                line_end=node.end_lineno,
                column_start=node.col_offset,
                column_end=node.end_col_offset
            ),
            base_classes=[ast.unparse(b) for b in node.bases],
            docstring=ast.get_docstring(node),
            decorators=[ast.unparse(d) for d in node.decorator_list]
        )
        
        file_analysis.classes.append(cls)
        
        # Process class body
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self._handle_function(item, file_analysis)
            elif isinstance(item, ast.Assign):
                self._handle_assignment(item, file_analysis, cls)
                
        self.current_class = prev_class
        
    def _handle_assignment(self, node: ast.Assign, file_analysis: File, cls: Optional[Class] = None):
        """Handle Assign nodes"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                var = Variable(
                    name=target.id,
                    value=ast.unparse(node.value),
                    locations=[CodeLocation(
                        file=self.current_file,
                        line_start=node.lineno,
                        line_end=node.end_lineno,
                        column_start=node.col_offset,
                        column_end=node.end_col_offset
                    )],
                    scope="class" if cls else "module"
                )
                
                if cls:
                    cls.class_variables.append(var)
                else:
                    file_analysis.variables.append(var)
                    
    def _build_dependency_graph(self, files: Dict[str, File]):
        """Build dependency graph from imports"""
        for file_path, file_analysis in files.items():
            self.dependency_graph.add_node(file_path)
            
            for imp in file_analysis.imports:
                # Convert import to potential file path
                if imp.is_from_import:
                    module_path = imp.module.replace('.', '/')
                else:
                    module_path = imp.module.replace('.', '/')
                    
                # Check if imported module exists in project
                potential_paths = [
                    f"{module_path}.py",
                    f"{module_path}/__init__.py"
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
