"""
Svelte component analyzer
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .base import LanguageAnalyzer
from .javascript import JavaScriptAnalyzer
from ...models import Function, Class, Variable, Import, CodeLocation

class SvelteAnalyzer(LanguageAnalyzer):
    """Analyzer for Svelte component files"""
    
    def __init__(self, file_path: Path, content: str):
        super().__init__(file_path, content)
        self.script_content = ""
        self.script_offset = 0
        self.is_typescript = False
        
    def analyze(self) -> Dict[str, Any]:
        """Analyze Svelte component file"""
        # Extract different sections
        script_block = self._extract_script_block()
        template_block = self._extract_template_block()
        style_block = self._extract_style_block()
        
        # Initialize results
        functions = []
        classes = []
        variables = []
        imports = []
        
        # Analyze script block if present
        if script_block:
            js_analyzer = JavaScriptAnalyzer(self.file_path, script_block[0])
            script_analysis = js_analyzer.analyze()
            
            # Adjust line numbers to account for script block position
            self._adjust_locations(script_analysis, script_block[1])
            
            functions.extend(script_analysis["functions"])
            classes.extend(script_analysis["classes"])
            variables.extend(script_analysis["variables"])
            imports.extend(script_analysis["imports"])
            
        # Analyze template
        if template_block:
            template_analysis = self._analyze_template(template_block[0], template_block[1])
            functions.extend(template_analysis.get("functions", []))
            variables.extend(template_analysis.get("variables", []))
            
        return {
            "functions": functions,
            "classes": classes,
            "variables": variables,
            "imports": imports,
            "is_typescript": self.is_typescript
        }
        
    def get_dependencies(self) -> List[str]:
        """Extract component dependencies"""
        deps = []
        
        # Get script dependencies
        script_block = self._extract_script_block()
        if script_block:
            js_analyzer = JavaScriptAnalyzer(self.file_path, script_block[0])
            deps.extend(js_analyzer.get_dependencies())
            
        # Get component imports from template
        for line in self.content.split('\n'):
            # Look for component imports in template
            match = re.search(r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]', line)
            if match and match.group(2).startswith('.'):
                deps.append(match.group(2))
                
        return deps
        
    def _extract_script_block(self) -> Optional[Tuple[str, int]]:
        """Extract script block content and starting line"""
        script_match = re.search(
            r'<script(\s+lang="(?:ts|typescript)")?\s*>(.*?)</script>',
            self.content,
            re.DOTALL
        )
        
        if script_match:
            self.is_typescript = bool(script_match.group(1))
            content = script_match.group(2).strip()
            start_line = self.content[:script_match.start()].count('\n')
            return content, start_line
            
        return None
        
    def _extract_template_block(self) -> Optional[Tuple[str, int]]:
        """Extract template content (everything outside script/style tags) and starting line"""
        # Remove script and style blocks
        content = self.content
        content = re.sub(r'<script.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style.*?</style>', '', content, flags=re.DOTALL)
        
        if content.strip():
            start_line = 0  # Template can start from beginning
            return content.strip(), start_line
            
        return None
        
    def _extract_style_block(self) -> Optional[Tuple[str, int]]:
        """Extract style block content and starting line"""
        style_match = re.search(
            r'<style(\s+lang="[^"]+")?\s*>(.*?)</style>',
            self.content,
            re.DOTALL
        )
        
        if style_match:
            content = style_match.group(2).strip()
            start_line = self.content[:style_match.start()].count('\n')
            return content, start_line
            
        return None
        
    def _adjust_locations(self, analysis: Dict[str, List[Any]], offset: int):
        """Adjust CodeLocation line numbers by offset"""
        for item in analysis.get("functions", []):
            item.location.line_start += offset
            item.location.line_end += offset
            
        for item in analysis.get("classes", []):
            item.location.line_start += offset
            item.location.line_end += offset
            
        for item in analysis.get("variables", []):
            for loc in item.locations:
                loc.line_start += offset
                loc.line_end += offset
                
        for item in analysis.get("imports", []):
            item.location.line_start += offset
            item.location.line_end += offset
            
    def _analyze_template(self, content: str, start_line: int) -> Dict[str, List[Any]]:
        """Analyze Svelte template syntax"""
        functions = []
        variables = []
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Extract event handlers
            for handler_match in re.finditer(r'on:(\w+)={([^}]+)}', line):
                event_name = handler_match.group(1)
                handler_code = handler_match.group(2)
                
                functions.append(Function(
                    name=f"on_{event_name}",
                    docstring=f"Event handler for {event_name}",
                    location=CodeLocation(
                        file=str(self.file_path),
                        line_start=start_line + i,
                        line_end=start_line + i,
                        column_start=handler_match.start(),
                        column_end=handler_match.end()
                    )
                ))
                
            # Extract reactive declarations
            if '$:' in line:
                reactive_match = re.match(r'\s*\$:\s*(\w+)\s*=', line)
                if reactive_match:
                    variables.append(Variable(
                        name=reactive_match.group(1),
                        docstring="Reactive declaration",
                        locations=[CodeLocation(
                            file=str(self.file_path),
                            line_start=start_line + i,
                            line_end=start_line + i,
                            column_start=0,
                            column_end=len(line)
                        )],
                        scope="component"
                    ))
                    
            # Extract #each blocks
            each_match = re.match(r'\s*{#each\s+(\w+)', line)
            if each_match:
                variables.append(Variable(
                    name=each_match.group(1),
                    docstring="Each block iterable",
                    locations=[CodeLocation(
                        file=str(self.file_path),
                        line_start=start_line + i,
                        line_end=start_line + i,
                        column_start=0,
                        column_end=len(line)
                    )],
                    scope="template"
                ))
                
        return {
            "functions": functions,
            "variables": variables
        }
