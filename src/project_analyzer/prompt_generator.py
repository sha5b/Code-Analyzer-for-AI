"""
Generates AI assistant prompts from project analysis results
"""
from typing import Dict, List
from .models import ProjectAnalysis, File, Function, Class

class PromptGenerator:
    """Generates structured prompts from analysis results"""
    
    @staticmethod
    def generate_prompts(analysis: ProjectAnalysis) -> Dict[str, str]:
        """Generate all prompts from analysis results"""
        prompts = {}
        
        # Always include overview
        prompts["project_overview"] = PromptGenerator._generate_overview_prompt(analysis)
        
        # Architecture section
        arch_prompt = PromptGenerator._generate_architecture_prompt(analysis)
        if arch_prompt.strip():  # Only include if not empty
            prompts["architecture"] = arch_prompt
            
        # Functions section if there are any functions
        has_functions = any(file.functions for file in analysis.files.values())
        if has_functions:
            prompts["functions"] = PromptGenerator._generate_functions_prompt(analysis)
            
        # Classes section if there are any classes
        has_classes = any(file.classes for file in analysis.files.values())
        if has_classes:
            prompts["classes"] = PromptGenerator._generate_classes_prompt(analysis)
            
        # Add suggestions section
        suggestions = []
        
        if not has_functions and not has_classes:
            suggestions.append("- This appears to be a non-code project or contains no analyzable source files")
        
        if has_functions and not any(f.docstring for file in analysis.files.values() for f in file.functions):
            suggestions.append("- Consider adding docstrings to functions to improve code documentation")
            
        if has_classes and not any(c.docstring for file in analysis.files.values() for c in file.classes):
            suggestions.append("- Consider adding docstrings to classes to improve code documentation")
            
        if suggestions:
            prompts["suggestions"] = "\n".join([
                "Suggestions for Improvement:",
                "-------------------------",
                *suggestions
            ])
            
        return prompts

    @staticmethod
    def _generate_overview_prompt(analysis: ProjectAnalysis) -> str:
        """Generate project overview prompt"""
        languages = ", ".join(f"{lang} ({count} files)" 
                            for lang, count in analysis.languages.items())
        entry_points = ", ".join(analysis.entry_points) if analysis.entry_points else "None identified"
        
        return f"""
Project Overview:
----------------
Name: {analysis.name}
Total Files: {analysis.total_files}
Languages: {languages}
Entry Points: {entry_points}

Key Files:
{PromptGenerator._format_structure(analysis.structure, 0)}
"""

    @staticmethod
    def _generate_architecture_prompt(analysis: ProjectAnalysis) -> str:
        """Generate architecture and dependencies prompt"""
        sections = []
        
        # Project structure
        sections.append("Project Structure:")
        sections.append("-----------------")
        sections.append(PromptGenerator._format_structure(analysis.structure, 0))
        
        # Entry points
        sections.append("\nEntry Points:")
        sections.append("-----------------")
        if analysis.entry_points:
            for entry in analysis.entry_points:
                sections.append(f"- {entry}")
        else:
            sections.append("No entry points identified")
            
        # File organization
        sections.append("\nFile Organization:")
        sections.append("-----------------")
        for file_path, file_data in analysis.files.items():
            sections.append(f"\n{file_path}:")
            if file_data.functions:
                sections.append("  Functions:")
                for func in file_data.functions:
                    sections.append(f"    - {func.name}")
            if file_data.classes:
                sections.append("  Classes:")
                for cls in file_data.classes:
                    sections.append(f"    - {cls.name}")
                    
        # Dependencies
        sections.append("\nDependencies and Relationships:")
        sections.append("-----------------")
        for file_path, file_data in analysis.files.items():
            if hasattr(file_data, 'dependencies') and file_data.dependencies:
                sections.append(f"\n{file_path} depends on:")
                for dep in file_data.dependencies:
                    sections.append(f"  - {dep}")
            if hasattr(file_data, 'dependents') and file_data.dependents:
                sections.append(f"\n{file_path} is used by:")
                for dep in file_data.dependents:
                    sections.append(f"  - {dep}")
                    
        return "\n".join(sections)

    @staticmethod
    def _generate_functions_prompt(analysis: ProjectAnalysis) -> str:
        """Generate functions analysis prompt"""
        functions = []
        
        for file_path, file_data in analysis.files.items():
            if file_data.functions:
                functions.append(f"\nFile: {file_path}")
                for func in file_data.functions:
                    functions.append(PromptGenerator._format_function(func))
                    
        return f"""
Function Analysis:
-----------------
{chr(10).join(functions)}
"""

    @staticmethod
    def _generate_classes_prompt(analysis: ProjectAnalysis) -> str:
        """Generate classes analysis prompt"""
        classes = []
        
        for file_path, file_data in analysis.files.items():
            if file_data.classes:
                classes.append(f"\nFile: {file_path}")
                for cls in file_data.classes:
                    classes.append(PromptGenerator._format_class(cls))
                    
        return f"""
Class Analysis:
--------------
{chr(10).join(classes)}
"""

    @staticmethod
    def _format_structure(structure, level: int) -> str:
        """Format project structure recursively"""
        indent = "  " * level
        output = [f"{indent}{structure.name}/"]
        
        for child in sorted(structure.children, key=lambda x: (not x.is_dir, x.name)):
            if child.is_dir:
                output.append(PromptGenerator._format_structure(child, level + 1))
            else:
                output.append(f"{indent}  {child.name}")
                
        return "\n".join(output)

    @staticmethod
    def _format_function(func: Function) -> str:
        """Format function details"""
        args = ", ".join(f"{arg['name']}: {arg['type']}" if arg['type'] 
                        else arg['name'] for arg in func.args)
        
        details = [
            f"  {func.name}({args}) -> {func.returns or 'None'}",
            f"  Documentation: {func.docstring or 'None'}"
        ]
        
        if func.behavior:
            details.extend([
                f"  Pure Function: {'Yes' if func.behavior.pure else 'No'}",
                f"  Side Effects: {', '.join(func.behavior.side_effects) or 'None'}",
                f"  Raises: {', '.join(func.behavior.raises) or 'None'}",
                f"  Async: {'Yes' if func.behavior.async_status else 'No'}",
                f"  Generator: {'Yes' if func.behavior.generators else 'No'}",
                f"  Recursive: {'Yes' if func.behavior.recursion else 'No'}"
            ])
            
        if func.variable_flow:
            var_details = []
            for var in func.variable_flow:
                var_details.append(
                    f"    - {var.name} ({var.scope}): "
                    f"assigned {len(var.assignments)} times, "
                    f"read {len(var.reads)} times"
                )
            details.append("  Variables:")
            details.extend(var_details)
            
        return "\n".join(details)

    @staticmethod
    def _format_class(cls: Class) -> str:
        """Format class details"""
        details = [
            f"  {cls.name}({', '.join(cls.base_classes)})",
            f"  Documentation: {cls.docstring or 'None'}"
        ]
        
        if cls.class_variables:
            details.append("  Class Variables:")
            for var in cls.class_variables:
                details.append(f"    - {var.name}: {var.type_hint or 'Unknown type'}")
                
        if cls.instance_variables:
            details.append("  Instance Variables:")
            for var in cls.instance_variables:
                details.append(f"    - {var.name}: {var.type_hint or 'Unknown type'}")
                
        if cls.methods:
            details.append("  Methods:")
            for method in cls.methods:
                method_details = PromptGenerator._format_function(method)
                details.extend(f"    {line}" for line in method_details.split("\n"))
                
        return "\n".join(details)
