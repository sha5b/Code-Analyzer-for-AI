"""
Design pattern detection for various programming languages
"""
from pathlib import Path
import ast
from typing import Dict, List, Set, Any
import re

class DesignPatternDetector:
    """Detects common design patterns in code"""
    
    def __init__(self):
        self.patterns: Dict[str, List[str]] = {}
        
    def analyze_python_patterns(self, tree: ast.AST, file_path: str) -> Dict[str, List[str]]:
        """Analyze Python code for design patterns"""
        patterns = []
        
        # Singleton Pattern Detection
        singleton_visitor = SingletonPatternVisitor()
        singleton_visitor.visit(tree)
        if singleton_visitor.has_instance or singleton_visitor.has_private_constructor:
            patterns.append("Singleton")
            
        # Factory Pattern Detection
        factory_visitor = FactoryPatternVisitor()
        factory_visitor.visit(tree)
        if factory_visitor.has_factory_method:  # More lenient - just need factory method
            patterns.append("Factory")
            
        # Observer Pattern Detection
        observer_visitor = ObserverPatternVisitor()
        observer_visitor.visit(tree)
        if observer_visitor.has_observers or observer_visitor.has_notify:
            patterns.append("Observer")
            
        # Strategy Pattern Detection
        strategy_visitor = StrategyPatternVisitor()
        strategy_visitor.visit(tree)
        if strategy_visitor.is_strategy:
            patterns.append("Strategy")
            
        # Decorator Pattern Detection
        decorator_visitor = DecoratorPatternVisitor()
        decorator_visitor.visit(tree)
        if decorator_visitor.is_decorator:
            patterns.append("Decorator")
            
        if patterns:
            self.patterns[file_path] = patterns
            
        return self.patterns

class SingletonPatternVisitor(ast.NodeVisitor):
    """Detects Singleton pattern implementation"""
    
    def __init__(self):
        self.is_singleton = False
        self.has_instance = False
        self.has_private_constructor = False
        
    def visit_ClassDef(self, node: ast.ClassDef):
        # Check for instance variable
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                if item.target.id == '_instance':
                    self.has_instance = True
                    
            # Check for private constructor
            elif isinstance(item, ast.FunctionDef) and item.name == '__init__':
                for decorator in item.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'private':
                        self.has_private_constructor = True
                        
        # If both conditions are met, it's likely a singleton
        self.is_singleton = self.has_instance and self.has_private_constructor
        self.generic_visit(node)

class FactoryPatternVisitor(ast.NodeVisitor):
    """Detects Factory pattern implementation"""
    
    def __init__(self):
        self.is_factory = False
        self.creates_objects = False
        self.has_factory_method = False
        
    def visit_ClassDef(self, node: ast.ClassDef):
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Check for create/factory method
                if 'create' in item.name.lower() or 'factory' in item.name.lower():
                    self.has_factory_method = True
                    
                # Check if method returns different types
                returns_found = self._find_return_types(item)
                if len(returns_found) > 1:
                    self.creates_objects = True
                    
        self.is_factory = self.has_factory_method and self.creates_objects
        self.generic_visit(node)
        
    def _find_return_types(self, node: ast.FunctionDef) -> Set[str]:
        returns = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and isinstance(child.value, ast.Call):
                if isinstance(child.value.func, ast.Name):
                    returns.add(child.value.func.id)
        return returns

class ObserverPatternVisitor(ast.NodeVisitor):
    """Detects Observer pattern implementation"""
    
    def __init__(self):
        self.is_observer = False
        self.has_observers = False
        self.has_notify = False
        
    def visit_ClassDef(self, node: ast.ClassDef):
        for item in node.body:
            # Check for observer list
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                if 'observer' in item.target.id.lower():
                    self.has_observers = True
                    
            # Check for notify method
            if isinstance(item, ast.FunctionDef):
                if 'notify' in item.name.lower():
                    self.has_notify = True
                    
        self.is_observer = self.has_observers and self.has_notify
        self.generic_visit(node)

class StrategyPatternVisitor(ast.NodeVisitor):
    """Detects Strategy pattern implementation"""
    
    def __init__(self):
        self.is_strategy = False
        self.has_strategy_interface = False
        self.has_context = False
        
    def visit_ClassDef(self, node: ast.ClassDef):
        # Check for strategy interface/abstract class
        if any('abstract' in base.id.lower() for base in node.bases if isinstance(base, ast.Name)):
            self.has_strategy_interface = True
            
        # Check for strategy context
        if 'context' in node.name.lower():
            self.has_context = True
            
        # Check for strategy method
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if 'strategy' in item.name.lower() or 'algorithm' in item.name.lower():
                    self.is_strategy = True
                    break
        
        self.generic_visit(node)

class DecoratorPatternVisitor(ast.NodeVisitor):
    """Detects Decorator pattern implementation"""
    
    def __init__(self):
        self.is_decorator = False
        self.has_wrapper = False
        self.has_component = False
        
    def visit_ClassDef(self, node: ast.ClassDef):
        # Check for decorator/wrapper class
        if 'decorator' in node.name.lower() or 'wrapper' in node.name.lower():
            self.has_wrapper = True
            
        # Check for component interface
        for base in node.bases:
            if isinstance(base, ast.Name) and ('component' in base.id.lower() or 'interface' in base.id.lower()):
                self.has_component = True
                
        self.is_decorator = self.has_wrapper or self.has_component
        self.generic_visit(node)
