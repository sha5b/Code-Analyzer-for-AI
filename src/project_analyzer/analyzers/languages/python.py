"""
Python source code analyzer
"""
import ast
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .base import LanguageAnalyzer
from ...models import Function, Class, Variable, Import, CodeLocation

class PythonAnalyzer(LanguageAnalyzer):
    """Analyzer for Python source files"""
    
    def __init__(self, file_path: Path, content: str):
        super().__init__(file_path, content)
        self.current_class = None
        
    def analyze(self) -> Dict[str, Any]:
        """Analyze Python file content"""
        functions = []
        classes = []
        variables = []
        imports = []
        
        try:
            tree = ast.parse(self.content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(self._handle_import(node))
                elif isinstance(node, ast.ImportFrom):
                    imports.extend(self._handle_import_from(node))
                elif isinstance(node, ast.FunctionDef):
                    if not self.current_class:  # Only top-level functions
                        functions.append(self._handle_function(node))
                elif isinstance(node, ast.ClassDef):
                    classes.append(self._handle_class(node))
                elif isinstance(node, ast.Assign):
                    if not self.current_class:  # Only module-level variables
                        var = self._handle_assignment(node)
                        if var:
                            variables.append(var)
                            
        except SyntaxError:
            return {
                "functions": [],
                "classes": [],
                "variables": [],
                "imports": []
            }
            
        return {
            "functions": functions,
            "classes": classes,
            "variables": variables,
            "imports": imports
        }
        
    def get_dependencies(self) -> List[str]:
        """Extract file dependencies from imports"""
        deps = []
        try:
            tree = ast.parse(self.content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if '.' in name.name:
                            deps.append(name.name.split('.')[0])
                        else:
                            deps.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        if node.level > 0:  # Relative import
                            deps.append('.' * node.level + node.module)
                        else:
                            deps.append(node.module)
        except SyntaxError:
            pass
        return deps
        
    def _handle_import(self, node: ast.Import) -> List[Import]:
        """Handle Import nodes"""
        imports = []
        for name in node.names:
            imports.append(Import(
                module=name.name,
                alias=name.asname,
                location=CodeLocation(
                    file=str(self.file_path),
                    line_start=node.lineno,
                    line_end=node.lineno,
                    column_start=node.col_offset,
                    column_end=node.end_col_offset
                )
            ))
        return imports
        
    def _handle_import_from(self, node: ast.ImportFrom) -> List[Import]:
        """Handle ImportFrom nodes"""
        imports = []
        module = node.module or ''
        for name in node.names:
            imports.append(Import(
                module=module,
                names=[name.name],
                alias=name.asname,
                location=CodeLocation(
                    file=str(self.file_path),
                    line_start=node.lineno,
                    line_end=node.lineno,
                    column_start=node.col_offset,
                    column_end=node.end_col_offset
                ),
                is_from_import=True,
                level=node.level
            ))
        return imports
        
    def _handle_function(self, node: ast.FunctionDef) -> Function:
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
                
        return Function(
            name=node.name,
            location=CodeLocation(
                file=str(self.file_path),
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
        
    def _handle_class(self, node: ast.ClassDef) -> Class:
        """Handle ClassDef nodes"""
        prev_class = self.current_class
        self.current_class = node.name
        
        methods = []
        class_variables = []
        
        # Process class body
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self._handle_function(item))
            elif isinstance(item, ast.Assign):
                var = self._handle_assignment(item)
                if var:
                    class_variables.append(var)
                    
        self.current_class = prev_class
        
        return Class(
            name=node.name,
            location=CodeLocation(
                file=str(self.file_path),
                line_start=node.lineno,
                line_end=node.end_lineno,
                column_start=node.col_offset,
                column_end=node.end_col_offset
            ),
            base_classes=[ast.unparse(b) for b in node.bases],
            docstring=ast.get_docstring(node),
            decorators=[ast.unparse(d) for d in node.decorator_list],
            methods=methods,
            class_variables=class_variables
        )
        
    def _handle_assignment(self, node: ast.Assign) -> Optional[Variable]:
        """Handle Assign nodes"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                return Variable(
                    name=target.id,
                    value=ast.unparse(node.value),
                    locations=[CodeLocation(
                        file=str(self.file_path),
                        line_start=node.lineno,
                        line_end=node.end_lineno,
                        column_start=node.col_offset,
                        column_end=node.end_col_offset
                    )],
                    scope="class" if self.current_class else "module"
                )
        return None
