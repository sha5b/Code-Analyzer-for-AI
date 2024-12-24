"""
Main analyzer class and GUI/CLI interface
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any
import sys

from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.syntax import Syntax

from .models import (
    ProjectAnalysis, 
    ProjectStructure,
    Function,
    FunctionBehavior,
    ControlFlow,
    VariableFlow
)
from .prompt_generator import PromptGenerator
from .analyzers.structure import StructureAnalyzer
from .analyzers.code import CodeAnalyzer
from .analyzers.function import FunctionAnalyzer
from .folder_selector import select_project


class ProjectAnalyzer:
    """Main analyzer class that coordinates all analysis"""
    
    def __init__(self, path: str | Path):
        self.root_path = Path(path).resolve()
        if not self.root_path.exists():
            raise ValueError(f"Path does not exist: {path}")
            
        self.console = Console()
        
    def analyze(self) -> ProjectAnalysis:
        """Run all analyzers and return complete analysis"""
        self.console.print(Panel.fit("🔍 Analyzing project structure...", style="blue"))
        
        # Analyze project structure
        structure_analyzer = StructureAnalyzer(self.root_path)
        structure_results = structure_analyzer.analyze()
        
        self.console.print(Panel.fit("📝 Analyzing source code...", style="blue"))
        
        # Analyze source code and functions
        code_analyzer = CodeAnalyzer(self.root_path)
        code_results = code_analyzer.analyze()
        
        # Get quality metrics
        quality_metrics = code_analyzer.quality_analyzer.analyze()
        
        # Detailed function analysis
        self.console.print(Panel.fit("🔍 Analyzing function behavior...", style="blue"))
        function_analyzer = FunctionAnalyzer(self.root_path)
        function_results = function_analyzer.analyze()
        
        # Update function analysis results
        for file_path, file_analysis in code_results["files"].items():
            for func in file_analysis.functions:
                flow_key = f"{file_path}::{func.name}"
                if flow_key in function_results["function_flows"]:
                    flow = function_results["function_flows"][flow_key]
                    func.behavior = FunctionBehavior(
                        entry_points=flow.entry_points,
                        exit_points=flow.exit_points,
                        return_paths=flow.return_paths,
                        control_flow=[ControlFlow(**node.__dict__) for node in flow.control_flow],
                        pure=flow.pure,
                        side_effects=flow.side_effects,
                        raises=flow.raises,
                        async_status=flow.async_status,
                        generators=flow.generators,
                        recursion=flow.recursion
                    )
                    func.variable_flow = [
                        VariableFlow(
                            name=name,
                            assignments=var.assignments,
                            reads=var.reads,
                            scope=var.scope,
                            type_hints=var.type_hints,
                            potential_values=var.potential_values or []
                        )
                        for name, var in flow.variables.items()
                    ]
            
            # Update class methods
            for cls in file_analysis.classes:
                for method in cls.methods:
                    flow_key = f"{file_path}::{cls.name}.{method.name}"
                    if flow_key in function_results["function_flows"]:
                        flow = function_results["function_flows"][flow_key]
                        method.behavior = FunctionBehavior(
                            entry_points=flow.entry_points,
                            exit_points=flow.exit_points,
                            return_paths=flow.return_paths,
                            control_flow=[ControlFlow(**node.__dict__) for node in flow.control_flow],
                            pure=flow.pure,
                            side_effects=flow.side_effects,
                            raises=flow.raises,
                            async_status=flow.async_status,
                            generators=flow.generators,
                            recursion=flow.recursion
                        )
                        method.variable_flow = [
                            VariableFlow(
                                name=name,
                                assignments=var.assignments,
                                reads=var.reads,
                                scope=var.scope,
                                type_hints=var.type_hints,
                                potential_values=var.potential_values or []
                            )
                            for name, var in flow.variables.items()
                        ]
        
        # Combine results
        analysis = ProjectAnalysis(
            root_path=str(self.root_path),
            name=self.root_path.name,
            structure=structure_results["structure"],
            files=code_results["files"],
            total_files=structure_results["total_files"],
            languages=structure_results["languages"],
            entry_points=structure_analyzer.find_entry_points(),
            patterns=quality_metrics.get("design_patterns", {}),
            smells=quality_metrics.get("code_smells", {})
        )
        
        return analysis
        
    def display_analysis(self, analysis: ProjectAnalysis):
        """Display analysis results in terminal"""
        self.console.print("\n")
        
        # Project Overview
        self.console.print(Panel.fit(
            f"[bold blue]Project Analysis: {analysis.name}[/bold blue]\n"
            f"📁 Total Files: {analysis.total_files}\n"
            f"🔤 Languages: {', '.join(f'{lang}: {count}' for lang, count in analysis.languages.items())}\n"
            f"📌 Entry Points: {', '.join(analysis.entry_points) or 'None found'}"
        ))
        
        # File Structure
        self.console.print("\n[bold blue]File Structure:[/bold blue]")
        tree = self._build_structure_tree(analysis.structure)
        self.console.print(tree)
        
        # Code Analysis
        if analysis.files:
            self.console.print("\n[bold blue]Code Analysis:[/bold blue]")
            
            # Functions and Classes
            # Code Structure
            structure_table = Table(show_header=True, header_style="bold")
            structure_table.add_column("File")
            structure_table.add_column("Functions")
            structure_table.add_column("Classes")
            
            for file_path, file_analysis in analysis.files.items():
                structure_table.add_row(
                    file_path,
                    str(len(file_analysis.functions)),
                    str(len(file_analysis.classes))
                )
                
            self.console.print(structure_table)
            
            # Code Quality and Behavior Analysis
            self.console.print("\n[bold blue]Function Analysis:[/bold blue]")
            
            for file_path, file_analysis in analysis.files.items():
                if file_analysis.functions or file_analysis.classes:
                    self.console.print(f"\n[bold]{file_path}[/bold]")
                    
                    # Basic metrics
                    metrics_table = Table(show_header=True, header_style="bold")
                    metrics_table.add_column("Function")
                    metrics_table.add_column("Complexity")
                    metrics_table.add_column("Pure")
                    metrics_table.add_column("Side Effects")
                    metrics_table.add_column("Raises")
                    
                    # Function flow
                    flow_table = Table(show_header=True, header_style="bold")
                    flow_table.add_column("Function")
                    flow_table.add_column("Entry Points")
                    flow_table.add_column("Exit Points")
                    flow_table.add_column("Variables")
                    flow_table.add_column("Control Flow")
                    
                    def add_function_to_tables(func: Function, prefix: str = ""):
                        # Add to metrics table
                        metrics_table.add_row(
                            prefix + func.name,
                            str(func.complexity or "N/A"),
                            "✓" if func.behavior and func.behavior.pure else "✗",
                            "\n".join(func.behavior.side_effects) if func.behavior else "N/A",
                            ", ".join(func.behavior.raises) if func.behavior else "N/A"
                        )
                        
                        # Add to flow table
                        if func.behavior:
                            var_info = []
                            for v in func.variable_flow:
                                scope = f"[blue]{v.scope}[/blue]"
                                assigns = f"assigned:{len(v.assignments)}"
                                reads = f"read:{len(v.reads)}"
                                var_info.append(f"{v.name} ({scope} {assigns} {reads})")
                            
                            flow_info = []
                            for cf in func.behavior.control_flow:
                                if cf.condition:
                                    flow_info.append(f"{cf.node_type}: {cf.condition}")
                                else:
                                    flow_info.append(cf.node_type)
                            
                            flow_table.add_row(
                                prefix + func.name,
                                "\n".join(func.behavior.entry_points) or "None",
                                "\n".join(func.behavior.exit_points) or "None",
                                "\n".join(var_info),
                                "\n".join(flow_info)
                            )
                    
                    # Add functions
                    for func in file_analysis.functions:
                        add_function_to_tables(func)
                    
                    # Add class methods
                    for cls in file_analysis.classes:
                        for method in cls.methods:
                            add_function_to_tables(method, f"{cls.name}.")
                    
                    self.console.print("\n[bold]Metrics:[/bold]")
                    self.console.print(metrics_table)
                    self.console.print("\n[bold]Flow Analysis:[/bold]")
                    self.console.print(flow_table)
            
    def _build_structure_tree(self, structure: ProjectStructure, tree: Optional[Tree] = None) -> Tree:
        """Build rich Tree from ProjectStructure"""
        if tree is None:
            tree = Tree(
                f"[bold]{structure.name}[/bold]",
                guide_style="blue"
            )
        
        for child in structure.children:
            if child.is_dir:
                branch = tree.add(
                    f"[bold blue]{child.name}/[/bold blue]"
                )
                self._build_structure_tree(child, branch)
            else:
                tree.add(f"[green]{child.name}[/green]")
                
        return tree
        
    def save_analysis(self, analysis: ProjectAnalysis, output_path: str | Path):
        """Save analysis results to JSON file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(analysis.model_dump(), f, indent=2)
            
        self.console.print(f"\n💾 Analysis saved to: {output_path}")


def main():
    """CLI entry point"""
    console = Console()
    
    # Check if web interface is requested
    if "--web" in sys.argv:
        from .web_interface import run_web_interface
        run_web_interface()
        return
    
    # Use GUI folder selector
    project_path, output_file = select_project()
    if project_path is None:
        console.print("[yellow]Analysis cancelled.[/yellow]")
        sys.exit(0)
    
    try:
        analyzer = ProjectAnalyzer(project_path)
        analysis = analyzer.analyze()
        
        # Display results
        analyzer.display_analysis(analysis)
        
        # Generate AI assistant prompts
        prompts = PromptGenerator.generate_prompts(analysis)
        
        # Save results to file if specified
        if output_file:
            # Add prompts to analysis results
            results = analysis.model_dump()
            results["ai_prompts"] = prompts
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
                
            console.print(f"\n💾 Analysis saved to: {output_path}")
            
            # Print instructions for web interface
            console.print("\nTo view results in web interface, run:")
            console.print("[bold]python -m project_analyzer --web[/bold]")
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()
