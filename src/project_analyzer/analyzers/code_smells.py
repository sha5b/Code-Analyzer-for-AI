"""
Code smell detection for various programming languages
"""
from pathlib import Path
import ast
from typing import Dict, List, Set, Any
import re

class CodeSmellDetector:
    """Detects common code smells"""
    
    def __init__(self):
        self.smells: Dict[str, List[Dict[str, Any]]] = {}
        self.config = {
            'max_function_length': 50,  # lines
            'max_class_length': 200,    # lines
            'max_parameters': 5,
            'max_complexity': 10,
            'max_nesting_depth': 3
        }
        
    def analyze_python_smells(self, tree: ast.AST, file_path: str, code_lines: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze Python code for code smells"""
        smells = []
        
        # Long Method Detection
        long_method_visitor = LongMethodVisitor(self.config['max_function_length'], code_lines)
        long_method_visitor.visit(tree)
        smells.extend(long_method_visitor.smells)
        
        # Too Many Parameters Detection
        params_visitor = TooManyParametersVisitor(self.config['max_parameters'])
        params_visitor.visit(tree)
        smells.extend(params_visitor.smells)
        
        # Deep Nesting Detection
        nesting_visitor = DeepNestingVisitor(self.config['max_nesting_depth'])
        nesting_visitor.visit(tree)
        smells.extend(nesting_visitor.smells)
        
        # Large Class Detection
        large_class_visitor = LargeClassVisitor(self.config['max_class_length'], code_lines)
        large_class_visitor.visit(tree)
        smells.extend(large_class_visitor.smells)
        
        if smells:
            self.smells[file_path] = smells
            
        return self.smells

class LongMethodVisitor(ast.NodeVisitor):
    """Detects methods that are too long"""
    
    def __init__(self, max_length: int, code_lines: List[str]):
        self.max_length = max_length
        self.code_lines = code_lines
        self.smells = []
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        length = node.end_lineno - node.lineno
        if length > self.max_length:
            self.smells.append({
                'type': 'Long Method',
                'name': node.name,
                'line': node.lineno,
                'message': f'Method is {length} lines long (max {self.max_length})'
            })
        self.generic_visit(node)

class TooManyParametersVisitor(ast.NodeVisitor):
    """Detects methods with too many parameters"""
    
    def __init__(self, max_params: int):
        self.max_params = max_params
        self.smells = []
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        params_count = len([arg for arg in node.args.args if arg.arg != 'self'])
        if params_count > self.max_params:
            self.smells.append({
                'type': 'Too Many Parameters',
                'name': node.name,
                'line': node.lineno,
                'message': f'Method has {params_count} parameters (max {self.max_params})'
            })
        self.generic_visit(node)

class DeepNestingVisitor(ast.NodeVisitor):
    """Detects deeply nested code"""
    
    def __init__(self, max_depth: int):
        self.max_depth = max_depth
        self.current_depth = 0
        self.smells = []
        
    def visit_If(self, node: ast.If):
        self.current_depth += 1
        if self.current_depth > self.max_depth:
            self.smells.append({
                'type': 'Deep Nesting',
                'line': node.lineno,
                'message': f'Code is nested {self.current_depth} levels deep (max {self.max_depth})'
            })
        self.generic_visit(node)
        self.current_depth -= 1
        
    visit_For = visit_While = visit_If  # Same logic for loops

class LargeClassVisitor(ast.NodeVisitor):
    """Detects classes that are too large"""
    
    def __init__(self, max_length: int, code_lines: List[str]):
        self.max_length = max_length
        self.code_lines = code_lines
        self.smells = []
        
    def visit_ClassDef(self, node: ast.ClassDef):
        length = node.end_lineno - node.lineno
        if length > self.max_length:
            self.smells.append({
                'type': 'Large Class',
                'name': node.name,
                'line': node.lineno,
                'message': f'Class is {length} lines long (max {self.max_length})'
            })
        self.generic_visit(node)
