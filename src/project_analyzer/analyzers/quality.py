"""
Quality analyzer - Analyzes code quality metrics like complexity and maintainability
"""
import ast
from pathlib import Path
from typing import Dict, Set, Any, List

from .base import BaseAnalyzer
from .patterns import DesignPatternDetector
from .code_smells import CodeSmellDetector
from ..models import File, Function


class QualityAnalyzer(BaseAnalyzer):
    """Analyzes code quality metrics"""
    
    def __init__(self, root_path: str | Path):
        super().__init__(root_path)
        self.function_calls: Dict[str, Set[str]] = {}  # caller -> callee
        self.pattern_detector = DesignPatternDetector()
        self.smell_detector = CodeSmellDetector()
        self.patterns: Dict[str, List[str]] = {}
        self.smells: Dict[str, List[Dict[str, Any]]] = {}
        
    def analyze(self) -> Dict[str, Any]:
        """Analyze code quality metrics for all files"""
        
        for path in self.root_path.rglob('*'):
            if not path.is_file() or self.should_ignore(path):
                continue
                
            file_type = self.get_file_type(path)
            if file_type not in ['python', 'javascript', 'typescript', 'c++', 'c#', 'svelte']:
                continue
                
            try:
                quality_metrics = self.analyze_file_quality(path)
                if quality_metrics:
                    rel_path = str(path.relative_to(self.root_path))
                    if quality_metrics.get('patterns'):
                        self.patterns[rel_path] = quality_metrics['patterns']
                    if quality_metrics.get('smells'):
                        self.smells[rel_path] = quality_metrics['smells']
            except Exception as e:
                print(f"Error analyzing quality metrics for {path}: {e}")
                
        return {
            "function_calls": self.function_calls,
            "design_patterns": self.patterns,
            "code_smells": self.smells
        }
        
    def analyze_file_quality(self, path: Path) -> Dict[str, Any]:
        """Analyze quality metrics for a single file"""
        try:
            content = path.read_text(encoding=self.get_file_encoding(path))
            file_type = self.get_file_type(path)
            rel_path = str(path.relative_to(self.root_path))
            
            patterns: List[str] = []
            smells: List[Dict[str, Any]] = []
            complexity_scores = {}
            
            if file_type == 'python':
                tree = ast.parse(content)
                code_lines = content.splitlines()
                
                # Collect function calls
                call_visitor = FunctionCallVisitor()
                call_visitor.visit(tree)
                self.function_calls[rel_path] = call_visitor.calls
                
                # Calculate complexity
                complexity_visitor = ComplexityVisitor()
                complexity_visitor.visit(tree)
                complexity_scores = complexity_visitor.complexity_scores
                
                # Detect patterns and smells
                pattern_results = self.pattern_detector.analyze_python_patterns(tree, rel_path)
                smell_results = self.smell_detector.analyze_python_smells(tree, rel_path, code_lines)
                
                if pattern_results and rel_path in pattern_results:
                    patterns.extend(pattern_results[rel_path])
                if smell_results and rel_path in smell_results:
                    smells.extend(smell_results[rel_path])
                
            elif file_type in ['javascript', 'typescript']:
                # Basic JS/TS pattern detection
                if 'class' in content and ('constructor' in content or 'prototype' in content):
                    patterns.append('Class-based OOP')
                if 'function*' in content or 'yield' in content:
                    patterns.append('Generator Pattern')
                if 'async' in content and 'await' in content:
                    patterns.append('Async/Await Pattern')
                    
                # Basic JS/TS smell detection
                lines = content.splitlines()
                for i, line in enumerate(lines, 1):
                    if len(line.strip()) > 120:
                        smells.append({
                            'type': 'Long Line',
                            'line': i,
                            'message': f'Line exceeds 120 characters'
                        })
                    if line.count('if') > 3 or line.count('&&') > 3 or line.count('||') > 3:
                        smells.append({
                            'type': 'Complex Condition',
                            'line': i,
                            'message': 'Condition is too complex'
                        })
                        
            elif file_type in ['c++', 'c#']:
                # Basic C++/C# pattern detection
                if 'interface' in content:
                    patterns.append('Interface Segregation')
                if 'virtual' in content or 'override' in content:
                    patterns.append('Template Method')
                if 'private static' in content and ('instance' in content or 'Instance' in content):
                    patterns.append('Singleton')
                    
                # Basic C++/C# smell detection
                lines = content.splitlines()
                for i, line in enumerate(lines, 1):
                    if line.count('{') > 3:
                        smells.append({
                            'type': 'Nested Blocks',
                            'line': i,
                            'message': 'Too many nested blocks'
                        })
                        
            elif file_type == 'svelte':
                # Basic Svelte pattern detection
                if '<script context="module">' in content:
                    patterns.append('Module Context Pattern')
                if 'export let' in content:
                    patterns.append('Props Pattern')
                if '$:' in content:
                    patterns.append('Reactive Statement Pattern')
                    
                # Basic Svelte smell detection
                if content.count('<style') > 1:
                    smells.append({
                        'type': 'Multiple Style Blocks',
                        'line': 1,
                        'message': 'Multiple style blocks should be consolidated'
                    })
            
            return {
                "complexity_scores": complexity_scores,
                "patterns": patterns,
                "smells": smells
            }
            
        except Exception as e:
            print(f"Error in analyze_file_quality: {e}")
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
