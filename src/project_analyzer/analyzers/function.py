"""
Function analyzer - Deep analysis of function behavior, flow, and relationships
"""
import ast
from pathlib import Path
from typing import Dict, List, Set, Any, Optional

from ..models import (
    ControlFlow,
    FunctionBehavior,
    VariableFlow
)
from .base import BaseAnalyzer


class FunctionAnalyzer(BaseAnalyzer):
    """Analyzes detailed function behavior and relationships"""
    
    def __init__(self, root_path: str | Path):
        super().__init__(root_path)
        self.current_function: Optional[str] = None
        self.flows: Dict[str, FunctionBehavior] = {}
        
    def analyze(self) -> Dict[str, Any]:
        """Analyze all functions in project"""
        for path in self.root_path.rglob('*'):
            if not path.is_file() or self.should_ignore(path):
                continue
                
            file_type = self.get_file_type(path)
            if file_type != 'python':  # Start with Python support
                continue
                
            try:
                self.analyze_file_functions(path)
            except Exception as e:
                print(f"Error analyzing functions in {path}: {e}")
                
        return {
            "function_flows": self.flows
        }
        
    def analyze_file_functions(self, path: Path):
        """Analyze functions in a single file"""
        try:
            content = path.read_text(encoding=self.get_file_encoding(path))
            tree = ast.parse(content)
            
            analyzer = DetailedFunctionVisitor()
            analyzer.visit(tree)
            
            rel_path = str(path.relative_to(self.root_path))
            for name, flow in analyzer.function_flows.items():
                qualified_name = f"{rel_path}::{name}"
                self.flows[qualified_name] = flow
                
        except Exception:
            return None


class DetailedFunctionVisitor(ast.NodeVisitor):
    """AST visitor that performs detailed function analysis"""
    
    def __init__(self):
        self.function_flows: Dict[str, FunctionBehavior] = {}
        self.current_function: Optional[str] = None
        self.current_variables: Dict[str, VariableFlow] = {}
        self.control_flow: List[ControlFlow] = []
        self.return_paths: List[List[int]] = []
        self.side_effects: List[str] = []
        self.raises: Set[str] = set()
        self.is_pure = True
        
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Analyze a function definition"""
        old_function = self.current_function
        self.current_function = node.name
        
        # Reset analysis state
        self.current_variables = {}
        self.control_flow = []
        self.return_paths = []
        self.side_effects = []
        self.raises = set()
        self.is_pure = True
        
        # Analyze parameters
        for arg in node.args.args:
            self.current_variables[arg.arg] = VariableFlow(
                name=arg.arg,
                assignments=[node.lineno],
                reads=[],
                scope='parameter',
                type_hints=ast.unparse(arg.annotation) if arg.annotation else None
            )
            
        # Visit function body
        self.generic_visit(node)
        
        # Create function flow
        self.function_flows[node.name] = FunctionBehavior(
            entry_points=[],  # Filled in later by call analysis
            exit_points=self._find_exit_points(node),
            return_paths=self.return_paths,
            control_flow=[ControlFlow(
                line_no=cf.line_no,
                node_type=cf.node_type,
                condition=cf.condition,
                true_branch=cf.true_branch or [],
                false_branch=cf.false_branch or [],
                parent=cf.parent
            ) for cf in self.control_flow],
            pure=self.is_pure,
            side_effects=self.side_effects,
            raises=list(self.raises),
            async_status=isinstance(node, ast.AsyncFunctionDef),
            generators=any(isinstance(n, ast.Yield) for n in ast.walk(node)),
            recursion=node.name in str(ast.dump(node))
        )
        
        self.current_function = old_function
        
    def visit_Name(self, node: ast.Name):
        """Track variable usage"""
        if self.current_function:
            var_name = node.id
            if isinstance(node.ctx, ast.Store):
                if var_name not in self.current_variables:
                    self.current_variables[var_name] = VariableFlow(
                        name=var_name,
                        assignments=[node.lineno],
                        reads=[],
                        scope='local'
                    )
                else:
                    self.current_variables[var_name].assignments.append(node.lineno)
            elif isinstance(node.ctx, ast.Load):
                if var_name in self.current_variables:
                    self.current_variables[var_name].reads.append(node.lineno)
                else:
                    # Might be global/nonlocal
                    self.current_variables[var_name] = VariableFlow(
                        name=var_name,
                        assignments=[],
                        reads=[node.lineno],
                        scope='global'
                    )
                    self.is_pure = False
                    self.side_effects.append(f"Uses global variable {var_name}")
                    
        self.generic_visit(node)
        
    def visit_Global(self, node: ast.Global):
        """Track global variables"""
        if self.current_function:
            for name in node.names:
                if name in self.current_variables:
                    self.current_variables[name].scope = 'global'
                else:
                    self.current_variables[name] = VariableFlow(
                        name=name,
                        assignments=[],
                        reads=[],
                        scope='global'
                    )
                self.is_pure = False
                self.side_effects.append(f"Uses global variable {name}")
                
    def visit_Nonlocal(self, node: ast.Nonlocal):
        """Track nonlocal variables"""
        if self.current_function:
            for name in node.names:
                if name in self.current_variables:
                    self.current_variables[name].scope = 'nonlocal'
                else:
                    self.current_variables[name] = VariableFlow(
                        name=name,
                        assignments=[],
                        reads=[],
                        scope='nonlocal'
                    )
                self.is_pure = False
                self.side_effects.append(f"Uses nonlocal variable {name}")
                
    def visit_Return(self, node: ast.Return):
        """Track return statements and paths"""
        if self.current_function:
            # Add return node to control flow
            self.control_flow.append(ControlFlow(
                line_no=node.lineno,
                node_type='return'
            ))
            
            # Add return path
            current_path = self._get_current_path()
            self.return_paths.append(current_path + [node.lineno])
            
        self.generic_visit(node)
        
    def visit_If(self, node: ast.If):
        """Track if statements in control flow"""
        if self.current_function:
            self.control_flow.append(ControlFlow(
                line_no=node.lineno,
                node_type='if',
                condition=ast.unparse(node.test),
                true_branch=self._get_node_lines(node.body),
                false_branch=self._get_node_lines(node.orelse)
            ))
            
        self.generic_visit(node)
        
    def visit_While(self, node: ast.While):
        """Track while loops in control flow"""
        if self.current_function:
            self.control_flow.append(ControlFlow(
                line_no=node.lineno,
                node_type='while',
                condition=ast.unparse(node.test),
                true_branch=self._get_node_lines(node.body)
            ))
            
        self.generic_visit(node)
        
    def visit_For(self, node: ast.For):
        """Track for loops in control flow"""
        if self.current_function:
            self.control_flow.append(ControlFlow(
                line_no=node.lineno,
                node_type='for',
                condition=f"for {ast.unparse(node.target)} in {ast.unparse(node.iter)}",
                true_branch=self._get_node_lines(node.body)
            ))
            
        self.generic_visit(node)
        
    def visit_Try(self, node: ast.Try):
        """Track try/except blocks and potential exceptions"""
        if self.current_function:
            for handler in node.handlers:
                if handler.type:
                    if isinstance(handler.type, ast.Name):
                        self.raises.add(handler.type.id)
                    elif isinstance(handler.type, ast.Tuple):
                        for exc in handler.type.elts:
                            if isinstance(exc, ast.Name):
                                self.raises.add(exc.id)
                                
        self.generic_visit(node)
        
    def visit_Call(self, node: ast.Call):
        """Track function calls and side effects"""
        if self.current_function:
            if isinstance(node.func, ast.Name):
                # Built-in functions that indicate side effects
                if node.func.id in {'print', 'open', 'write', 'input'}:
                    self.is_pure = False
                    self.side_effects.append(f"Calls {node.func.id}")
                    
        self.generic_visit(node)
        
    def _find_exit_points(self, node: ast.FunctionDef) -> List[str]:
        """Find all functions called immediately before returning"""
        exit_points = []
        for n in ast.walk(node):
            if isinstance(n, ast.Return) and isinstance(n.value, ast.Call):
                if isinstance(n.value.func, ast.Name):
                    exit_points.append(n.value.func.id)
        return exit_points
        
    def _get_node_lines(self, nodes: List[ast.AST]) -> List[int]:
        """Get line numbers for a list of nodes"""
        return [node.lineno for node in nodes if hasattr(node, 'lineno')]
        
    def _get_current_path(self) -> List[int]:
        """Get current execution path based on control flow"""
        path = []
        for node in self.control_flow:
            path.append(node.line_no)
        return path
