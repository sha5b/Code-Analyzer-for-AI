"""
C++ source code analyzer
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .base import LanguageAnalyzer
from ...models import Function, Class, Variable, Import, CodeLocation

class CppAnalyzer(LanguageAnalyzer):
    """Analyzer for C++ source files"""
    
    def __init__(self, file_path: Path, content: str):
        super().__init__(file_path, content)
        self.current_namespace = []
        self.current_class = None
        
    def analyze(self) -> Dict[str, Any]:
        """Analyze C++ file content"""
        functions = []
        classes = []
        variables = []
        imports = []
        
        lines = self.content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Handle includes
            if line.startswith('#include'):
                import_info = self._parse_include(line, i)
                if import_info:
                    imports.append(import_info)
                    
            # Handle namespaces
            elif line.startswith('namespace'):
                namespace_info = self._parse_namespace(lines, i)
                if namespace_info:
                    self.current_namespace.append(namespace_info[0])
                    i = namespace_info[1]
                    
            # Handle class definitions
            elif any(line.startswith(prefix) for prefix in ['class ', 'struct ', 'template']):
                class_info = self._parse_class(lines, i)
                if class_info:
                    classes.append(class_info[0])
                    i = class_info[1]
                    
            # Handle function definitions
            elif self._is_function_definition(line):
                func_info = self._parse_function(lines, i)
                if func_info:
                    functions.append(func_info[0])
                    i = func_info[1]
                    
            # Handle variable declarations
            elif self._is_variable_declaration(line):
                var_info = self._parse_variable(line, i)
                if var_info:
                    variables.append(var_info)
                    
            i += 1
            
        return {
            "functions": functions,
            "classes": classes,
            "variables": variables,
            "imports": imports
        }
        
    def get_dependencies(self) -> List[str]:
        """Extract file dependencies from includes"""
        deps = []
        for line in self.content.split('\n'):
            line = line.strip()
            if line.startswith('#include'):
                if '"' in line:  # Local include
                    include = line.split('"')[1]
                    if include:
                        deps.append(include)
        return deps
        
    def _parse_include(self, line: str, line_num: int) -> Optional[Import]:
        """Parse #include directive"""
        if '"' in line:  # Local include
            include = line.split('"')[1]
            return Import(
                module=include,
                location=CodeLocation(
                    file=str(self.file_path),
                    line_start=line_num,
                    line_end=line_num,
                    column_start=0,
                    column_end=len(line)
                )
            )
        return None
        
    def _parse_namespace(self, lines: List[str], start: int) -> Optional[Tuple[str, int]]:
        """Parse namespace definition"""
        line = lines[start].strip()
        match = re.match(r'namespace\s+(\w+)\s*{?', line)
        if match:
            name = match.group(1)
            if '{' in line:
                return name, start
            # Find namespace end if on next line
            i = start + 1
            while i < len(lines) and '{' not in lines[i]:
                i += 1
            return name, i
        return None
        
    def _parse_class(self, lines: List[str], start: int) -> Optional[Tuple[Class, int]]:
        """Parse class/struct definition"""
        line = lines[start].strip()
        
        # Handle template classes
        template_params = []
        if line.startswith('template'):
            template_match = re.match(r'template\s*<(.+)>', line)
            if template_match:
                template_params = [p.strip() for p in template_match.group(1).split(',')]
                start += 1
                line = lines[start].strip()
                
        # Parse class declaration
        match = re.match(r'(class|struct)\s+(\w+)(?:\s*:\s*(.+))?', line)
        if match:
            class_type = match.group(1)
            name = match.group(2)
            inheritance = []
            
            if match.group(3):  # Has inheritance
                inheritance = [b.strip() for b in match.group(3).split(',')]
                inheritance = [re.sub(r'(public|private|protected)\s+', '', b) for b in inheritance]
                
            # Find class end
            i = start + 1
            brace_count = 1 if '{' in line else 0
            
            while i < len(lines):
                line = lines[i]
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0:
                    break
                i += 1
                
            # Build full name with namespace
            full_name = '::'.join(self.current_namespace + [name])
            if template_params:
                full_name += f"<{','.join(template_params)}>"
                
            return Class(
                name=full_name,
                base_classes=inheritance,
                docstring=f"{class_type.capitalize()} Template" if template_params else class_type.capitalize(),
                location=CodeLocation(
                    file=str(self.file_path),
                    line_start=start,
                    line_end=i,
                    column_start=0,
                    column_end=len(lines[i])
                )
            ), i
            
        return None
        
    def _is_function_definition(self, line: str) -> bool:
        """Check if line is a function definition"""
        # Basic check for function-like pattern
        if re.match(r'^(?:virtual\s+)?(?:static\s+)?[\w:~<>]+\s+[\w:~]+\s*\(', line):
            return True
        return False
        
    def _parse_function(self, lines: List[str], start: int) -> Optional[Tuple[Function, int]]:
        """Parse function definition"""
        line = lines[start].strip()
        
        # Match function pattern
        match = re.match(r'^(?:virtual\s+)?(?:static\s+)?([\w:~<>]+)\s+([\w:~]+)\s*\((.*?)\)(?:\s*const)?(?:\s*=\s*0)?', line)
        if match:
            return_type = match.group(1)
            name = match.group(2)
            params_str = match.group(3)
            
            # Parse parameters
            params = []
            if params_str.strip():
                param_list = params_str.split(',')
                for param in param_list:
                    param = param.strip()
                    if param:
                        # Extract parameter name and type
                        parts = param.split()
                        if parts:
                            param_name = parts[-1].strip('&*')
                            param_type = ' '.join(parts[:-1])
                            params.append({
                                'name': param_name,
                                'type': param_type
                            })
                            
            # Find function end if it has body
            i = start
            if '{' in line:
                brace_count = 1
                i += 1
                while i < len(lines):
                    line = lines[i]
                    brace_count += line.count('{') - line.count('}')
                    if brace_count == 0:
                        break
                    i += 1
            else:
                while i < len(lines) and '{' not in lines[i]:
                    i += 1
                    
            # Build full name with namespace
            full_name = '::'.join(self.current_namespace + [name])
            
            return Function(
                name=full_name,
                args=params,
                returns=return_type,
                location=CodeLocation(
                    file=str(self.file_path),
                    line_start=start,
                    line_end=i,
                    column_start=0,
                    column_end=len(lines[i])
                )
            ), i
            
        return None
        
    def _is_variable_declaration(self, line: str) -> bool:
        """Check if line is a variable declaration"""
        # Basic check for variable declaration pattern
        if re.match(r'^(?:static\s+)?(?:const\s+)?[\w:]+\s+\w+(?:\s*=.+)?;', line):
            return True
        return False
        
    def _parse_variable(self, line: str, line_num: int) -> Optional[Variable]:
        """Parse variable declaration"""
        # Match variable pattern
        match = re.match(r'^(?:static\s+)?(?:const\s+)?([\w:]+)\s+(\w+)(?:\s*=\s*(.+))?;', line)
        if match:
            var_type = match.group(1)
            name = match.group(2)
            value = match.group(3) if match.group(3) else None
            
            return Variable(
                name=name,
                type=var_type,
                value=value,
                locations=[CodeLocation(
                    file=str(self.file_path),
                    line_start=line_num,
                    line_end=line_num,
                    column_start=0,
                    column_end=len(line)
                )],
                scope='namespace' if self.current_namespace else 'global'
            )
            
        return None
