"""
Quality analyzer - Analyzes code quality metrics like complexity and maintainability
"""
import ast
from pathlib import Path
from typing import Dict, Set, Any

from .base import BaseAnalyzer
from ..models import File, Function


class QualityAnalyzer(BaseAnalyzer):
    """Analyzes code quality metrics"""
    
    def __init__(self, root_path: str | Path):
        super().__init__(root_path)
        self.function_calls: Dict[str, Set[str]] = {}  # caller -> callee
        
    def analyze(self) -> Dict[str, Any]:
        """Analyze code quality metrics for all files"""
        for path in self.root_path.rglob('*'):
            if not path.is_file() or self.should_ignore(path):
                continue
                
            file_type = self.get_file_type(path)
            if file_type != 'python':  # Start with Python support
                continue
                
            try:
                self.analyze_file_quality(path)
            except Exception as e:
                print(f"Error analyzing quality metrics for {path}: {e}")
                
        return {
            "function_calls": self.function_calls
        }
        
    def analyze_file_quality(self, path: Path):
        """Analyze quality metrics for a single file"""
        try:
            content = path.read_text(encoding=self.get_file_encoding(path))
            tree = ast.parse(content)
            
            # Collect function calls
            call_visitor = FunctionCallVisitor()
            call_visitor.visit(tree)
            
            rel_path = str(path.relative_to(self.root_path))
            self.function_calls[rel_path] = call_visitor.calls
            
            # Calculate complexity for each function
            complexity_visitor = ComplexityVisitor()
            complexity_visitor.visit(tree)
            
            return {
                "complexity_scores": complexity_visitor.complexity_scores
            }
            
        except Exception:
            return None


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor that calculates cyclomatic complexity"""
    
    def __init__(self):
        self.complexity_scores: Dict[str, int] = {}
        self.current_function: str = None
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Calculate complexity for function definition"""
        old_function = self.current_function
        self.current_function = node.name
        
        # Base complexity of 1
        complexity = 1
        
        # Add complexity for each branching statement
        for child in ast.walk(node):
            # Control flow statements add complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Match)):
                complexity += 1
            # Boolean operators can add complexity
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            # Exception handling adds complexity
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
                
        self.complexity_scores[node.name] = complexity
        
        # Visit child nodes
        self.generic_visit(node)
        self.current_function = old_function


class FunctionCallVisitor(ast.NodeVisitor):
    """AST visitor that tracks function calls"""
    
    def __init__(self):
        self.calls: Set[str] = set()
        self.current_function: str = None
        
    def visit_Call(self, node: ast.Call):
        """Record function calls"""
        if isinstance(node.func, ast.Name):
            self.calls.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.calls.add(node.func.attr)
            
        self.generic_visit(node)
