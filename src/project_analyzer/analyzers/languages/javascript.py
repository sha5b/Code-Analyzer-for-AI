"""
JavaScript/TypeScript analyzer with JSDoc support
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .base import LanguageAnalyzer
from ...models import Function, Class, Variable, Import, CodeLocation

class JavaScriptAnalyzer(LanguageAnalyzer):
    """Analyzer for JavaScript and TypeScript files"""
    
    def __init__(self, file_path: Path, content: str):
        super().__init__(file_path, content)
        self.is_typescript = file_path.suffix in ['.ts', '.tsx']
        
    def analyze(self) -> Dict[str, Any]:
        """Analyze JS/TS file content"""
        functions = []
        classes = []
        variables = []
        imports = []
        
        # Split content into lines for analysis
        lines = self.content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Handle JSDoc comments
            jsdoc = self._extract_jsdoc(lines, i)
            if jsdoc:
                i = jsdoc[1]  # Skip JSDoc block
                next_line = lines[i].strip() if i < len(lines) else ""
                
                if next_line.startswith(('function', 'class', 'const', 'let', 'var')):
                    definition = self._parse_definition(next_line, jsdoc[0])
                    if definition:
                        if isinstance(definition, Function):
                            functions.append(definition)
                        elif isinstance(definition, Class):
                            classes.append(definition)
                        elif isinstance(definition, Variable):
                            variables.append(definition)
            
            # Handle imports
            elif line.startswith('import ') or line.startswith('require('):
                import_info = self._parse_import(line)
                if import_info:
                    imports.append(import_info)
            
            # Handle TypeScript interfaces and types
            elif self.is_typescript and (line.startswith('interface ') or line.startswith('type ')):
                type_def = self._parse_typescript_type(lines, i)
                if type_def:
                    classes.append(type_def)
            
            i += 1
            
        return {
            "functions": functions,
            "classes": classes,
            "variables": variables,
            "imports": imports
        }
        
    def get_dependencies(self) -> List[str]:
        """Extract file dependencies from imports"""
        deps = []
        for line in self.content.split('\n'):
            line = line.strip()
            
            if line.startswith('import '):
                # ES6 imports
                if ' from ' in line:
                    module = line.split(' from ')[1].strip("'").strip('"').strip(';')
                    if module.startswith('.'):
                        deps.append(module)
            elif 'require(' in line:
                # CommonJS require
                match = re.search(r'require\([\'"]([^\'"]*)[\'"]\)', line)
                if match and match.group(1).startswith('.'):
                    deps.append(match.group(1))
                    
        return deps
        
    def _extract_jsdoc(self, lines: List[str], start: int) -> Optional[Tuple[str, int]]:
        """Extract JSDoc comment block and return (comment, end_line)"""
        if not lines[start].strip().startswith('/**'):
            return None
            
        comment_lines = []
        i = start
        
        while i < len(lines) and '*/' not in lines[i]:
            comment_lines.append(lines[i].strip().lstrip('* '))
            i += 1
            
        if i < len(lines) and '*/' in lines[i]:
            comment_lines.append(lines[i].strip().lstrip('* ').rstrip('*/'))
            return '\n'.join(comment_lines), i + 1
            
        return None
        
    def _parse_definition(self, line: str, jsdoc: str) -> Optional[Function | Class | Variable]:
        """Parse code definition with JSDoc"""
        # Extract JSDoc tags
        param_types = {}
        return_type = None
        description = []
        
        for line in jsdoc.split('\n'):
            line = line.strip()
            if line.startswith('@param'):
                # Parse @param {type} name description
                match = re.match(r'@param\s+\{([^}]+)\}\s+(\w+)(?:\s+(.*))?', line)
                if match:
                    param_types[match.group(2)] = {
                        'type': match.group(1),
                        'description': match.group(3) or ''
                    }
            elif line.startswith('@returns'):
                # Parse @returns {type} description
                match = re.match(r'@returns?\s+\{([^}]+)\}(?:\s+(.*))?', line)
                if match:
                    return_type = {
                        'type': match.group(1),
                        'description': match.group(2) or ''
                    }
            elif not line.startswith('@'):
                description.append(line)
                
        # Parse definition
        if line.startswith('function'):
            # Function definition
            match = re.match(r'function\s+(\w+)\s*\((.*?)\)', line)
            if match:
                name = match.group(1)
                params = [p.strip() for p in match.group(2).split(',') if p.strip()]
                
                return Function(
                    name=name,
                    args=[{
                        'name': p.split('=')[0].strip(),
                        'type': param_types.get(p.split('=')[0].strip(), {}).get('type')
                    } for p in params],
                    returns=return_type['type'] if return_type else None,
                    docstring='\n'.join(description),
                    location=CodeLocation(
                        file=str(self.file_path),
                        line_start=0,  # TODO: Track actual line numbers
                        line_end=0,
                        column_start=0,
                        column_end=0
                    )
                )
                
        elif line.startswith('class'):
            # Class definition
            match = re.match(r'class\s+(\w+)(?:\s+extends\s+(\w+))?', line)
            if match:
                return Class(
                    name=match.group(1),
                    base_classes=[match.group(2)] if match.group(2) else [],
                    docstring='\n'.join(description),
                    location=CodeLocation(
                        file=str(self.file_path),
                        line_start=0,
                        line_end=0,
                        column_start=0,
                        column_end=0
                    )
                )
                
        return None
        
    def _parse_import(self, line: str) -> Optional[Import]:
        """Parse import statement"""
        if ' from ' in line:
            # ES6 import
            parts = line.split(' from ')
            if len(parts) == 2:
                module = parts[1].strip("'").strip('"').strip(';')
                names = []
                
                # Extract imported names
                import_part = parts[0].replace('import', '').strip()
                if import_part.startswith('{'):
                    # Named imports
                    names = [n.strip() for n in import_part.strip('{}').split(',')]
                elif import_part:
                    # Default import
                    names = [import_part]
                    
                return Import(
                    module=module,
                    names=names,
                    location=CodeLocation(
                        file=str(self.file_path),
                        line_start=0,
                        line_end=0,
                        column_start=0,
                        column_end=0
                    )
                )
                
        elif 'require(' in line:
            # CommonJS require
            match = re.search(r'(?:const|let|var)\s+(\w+)\s*=\s*require\([\'"]([^\'"]*)[\'"]\)', line)
            if match:
                return Import(
                    module=match.group(2),
                    names=[match.group(1)],
                    location=CodeLocation(
                        file=str(self.file_path),
                        line_start=0,
                        line_end=0,
                        column_start=0,
                        column_end=0
                    )
                )
                
        return None
        
    def _parse_typescript_type(self, lines: List[str], start: int) -> Optional[Class]:
        """Parse TypeScript interface or type definition"""
        line = lines[start].strip()
        
        if line.startswith('interface '):
            # Interface definition
            match = re.match(r'interface\s+(\w+)(?:\s+extends\s+(\w+))?', line)
            if match:
                return Class(
                    name=match.group(1),
                    base_classes=[match.group(2)] if match.group(2) else [],
                    docstring="TypeScript Interface",
                    location=CodeLocation(
                        file=str(self.file_path),
                        line_start=start,
                        line_end=start,
                        column_start=0,
                        column_end=0
                    )
                )
        elif line.startswith('type '):
            # Type alias
            match = re.match(r'type\s+(\w+)\s*=', line)
            if match:
                return Class(
                    name=match.group(1),
                    base_classes=[],
                    docstring="TypeScript Type Alias",
                    location=CodeLocation(
                        file=str(self.file_path),
                        line_start=start,
                        line_end=start,
                        column_start=0,
                        column_end=0
                    )
                )
                
        return None
