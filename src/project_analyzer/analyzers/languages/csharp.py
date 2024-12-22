"""
C# source code analyzer
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .base import LanguageAnalyzer
from ...models import Function, Class, Variable, Import, CodeLocation

class CSharpAnalyzer(LanguageAnalyzer):
    """Analyzer for C# source files"""
    
    def __init__(self, file_path: Path, content: str):
        super().__init__(file_path, content)
        self.current_namespace = None
        self.current_class = None
        
    def analyze(self) -> Dict[str, Any]:
        """Analyze C# file content"""
        functions = []
        classes = []
        variables = []
        imports = []
        
        lines = self.content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Handle using directives
            if line.startswith('using '):
                import_info = self._parse_using(line, i)
                if import_info:
                    imports.append(import_info)
                    
            # Handle namespace
            elif line.startswith('namespace '):
                namespace_info = self._parse_namespace(lines, i)
                if namespace_info:
                    self.current_namespace = namespace_info[0]
                    i = namespace_info[1]
                    
            # Handle class/interface/enum definitions
            elif self._is_type_definition(line):
                type_info = self._parse_type_definition(lines, i)
                if type_info:
                    classes.append(type_info[0])
                    i = type_info[1]
                    
            # Handle method definitions
            elif self._is_method_definition(line):
                method_info = self._parse_method(lines, i)
                if method_info:
                    functions.append(method_info[0])
                    i = method_info[1]
                    
            # Handle property/field definitions
            elif self._is_member_definition(line):
                member_info = self._parse_member(line, i)
                if member_info:
                    variables.append(member_info)
                    
            i += 1
            
        return {
            "functions": functions,
            "classes": classes,
            "variables": variables,
            "imports": imports
        }
        
    def get_dependencies(self) -> List[str]:
        """Extract file dependencies from using directives"""
        deps = []
        for line in self.content.split('\n'):
            line = line.strip()
            if line.startswith('using '):
                if not any(keyword in line for keyword in ['static', '=']):
                    namespace = line.replace('using', '').strip().rstrip(';')
                    deps.append(namespace)
        return deps
        
    def _parse_using(self, line: str, line_num: int) -> Optional[Import]:
        """Parse using directive"""
        if '=' in line:  # Alias directive
            match = re.match(r'using\s+(\w+)\s*=\s*([\w.]+)\s*;', line)
            if match:
                return Import(
                    module=match.group(2),
                    alias=match.group(1),
                    location=CodeLocation(
                        file=str(self.file_path),
                        line_start=line_num,
                        line_end=line_num,
                        column_start=0,
                        column_end=len(line)
                    )
                )
        else:  # Normal using
            match = re.match(r'using\s+([\w.]+)\s*;', line)
            if match:
                return Import(
                    module=match.group(1),
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
        match = re.match(r'namespace\s+([\w.]+)\s*{?', line)
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
        
    def _is_type_definition(self, line: str) -> bool:
        """Check if line starts a type definition"""
        type_keywords = ['class', 'interface', 'struct', 'enum', 'record']
        return any(re.match(rf'^(?:public |internal |private |protected |abstract |sealed )*{keyword}\s+\w+', line)
                  for keyword in type_keywords)
                  
    def _parse_type_definition(self, lines: List[str], start: int) -> Optional[Tuple[Class, int]]:
        """Parse class/interface/struct/enum/record definition"""
        line = lines[start].strip()
        
        # Get attributes if any
        attributes = []
        while start > 0 and lines[start - 1].strip().startswith('['):
            attr_line = lines[start - 1].strip()
            attr_match = re.match(r'\[([\w,\s\(\)]+)\]', attr_line)
            if attr_match:
                attributes.extend(attr.strip() for attr in attr_match.group(1).split(','))
            start -= 1
            
        # Parse type definition
        match = re.match(r'^(?:public |internal |private |protected |abstract |sealed )*(\w+)\s+(\w+)(?:\s*:\s*(.+))?', line)
        if match:
            type_kind = match.group(1)  # class, interface, etc.
            name = match.group(2)
            inheritance = []
            
            if match.group(3):  # Has inheritance/implementation
                inheritance = [b.strip() for b in match.group(3).split(',')]
                
            # Find type end
            i = start + 1
            brace_count = 1 if '{' in line else 0
            
            while i < len(lines):
                line = lines[i]
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0:
                    break
                i += 1
                
            # Build full name with namespace
            full_name = f"{self.current_namespace}.{name}" if self.current_namespace else name
            
            return Class(
                name=full_name,
                base_classes=inheritance,
                docstring=f"{type_kind.capitalize()}" + (f" with attributes: {', '.join(attributes)}" if attributes else ""),
                location=CodeLocation(
                    file=str(self.file_path),
                    line_start=start,
                    line_end=i,
                    column_start=0,
                    column_end=len(lines[i])
                )
            ), i
            
        return None
        
    def _is_method_definition(self, line: str) -> bool:
        """Check if line is a method definition"""
        access_modifiers = r'(?:public |private |protected |internal |static |virtual |override |abstract )*'
        return re.match(rf'^{access_modifiers}[\w<>[\],\s]+\s+\w+\s*\(', line)
        
    def _parse_method(self, lines: List[str], start: int) -> Optional[Tuple[Function, int]]:
        """Parse method definition"""
        line = lines[start].strip()
        
        # Get attributes if any
        attributes = []
        while start > 0 and lines[start - 1].strip().startswith('['):
            attr_line = lines[start - 1].strip()
            attr_match = re.match(r'\[([\w,\s\(\)]+)\]', attr_line)
            if attr_match:
                attributes.extend(attr.strip() for attr in attr_match.group(1).split(','))
            start -= 1
            
        # Parse method signature
        match = re.match(r'^(?:[\w\s]+\s+)?([\w<>[\],\s]+)\s+(\w+)\s*\((.*?)\)', line)
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
                        # Handle ref/out parameters
                        param = re.sub(r'^(?:ref|out|in)\s+', '', param)
                        parts = param.split()
                        if len(parts) >= 2:
                            params.append({
                                'name': parts[-1],
                                'type': ' '.join(parts[:-1])
                            })
                            
            # Find method end
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
                    
            return Function(
                name=name,
                args=params,
                returns=return_type,
                docstring=f"Method with attributes: {', '.join(attributes)}" if attributes else None,
                location=CodeLocation(
                    file=str(self.file_path),
                    line_start=start,
                    line_end=i,
                    column_start=0,
                    column_end=len(lines[i])
                )
            ), i
            
        return None
        
    def _is_member_definition(self, line: str) -> bool:
        """Check if line is a property or field definition"""
        access_modifiers = r'(?:public |private |protected |internal |static |readonly |const )*'
        return re.match(rf'^{access_modifiers}[\w<>[\],\s]+\s+\w+\s*[{{;=]', line)
        
    def _parse_member(self, line: str, line_num: int) -> Optional[Variable]:
        """Parse property or field definition"""
        # Get attributes if any
        attributes = []
        if line_num > 0 and lines[line_num - 1].strip().startswith('['):
            attr_line = lines[line_num - 1].strip()
            attr_match = re.match(r'\[([\w,\s\(\)]+)\]', attr_line)
            if attr_match:
                attributes.extend(attr.strip() for attr in attr_match.group(1).split(','))
                
        # Parse member
        match = re.match(r'^(?:[\w\s]+\s+)?([\w<>[\],\s]+)\s+(\w+)\s*(?:=\s*(.+))?[;{]', line)
        if match:
            var_type = match.group(1)
            name = match.group(2)
            value = match.group(3).rstrip(';') if match.group(3) else None
            
            return Variable(
                name=name,
                type=var_type,
                value=value,
                docstring=f"Member with attributes: {', '.join(attributes)}" if attributes else None,
                locations=[CodeLocation(
                    file=str(self.file_path),
                    line_start=line_num,
                    line_end=line_num,
                    column_start=0,
                    column_end=len(line)
                )],
                scope='class' if self.current_class else 'namespace'
            )
            
        return None
