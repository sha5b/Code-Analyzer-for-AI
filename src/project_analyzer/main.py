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

from .models import ProjectAnalysis, ProjectStructure
from .analyzers.structure import StructureAnalyzer
from .analyzers.code import CodeAnalyzer
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
        
        # Analyze source code
        code_analyzer = CodeAnalyzer(self.root_path)
        code_results = code_analyzer.analyze()
        
        # Combine results
        analysis = ProjectAnalysis(
            root_path=str(self.root_path),
            name=self.root_path.name,
            structure=structure_results["structure"],
            files=code_results["files"],
            total_files=structure_results["total_files"],
            languages=structure_results["languages"],
            entry_points=structure_analyzer.find_entry_points()
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
            table = Table(show_header=True, header_style="bold")
            table.add_column("File")
            table.add_column("Functions")
            table.add_column("Classes")
            
            for file_path, file_analysis in analysis.files.items():
                table.add_row(
                    file_path,
                    str(len(file_analysis.functions)),
                    str(len(file_analysis.classes))
                )
                
            self.console.print(table)
            
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
    """GUI/CLI entry point"""
    console = Console()
    
    # Check if running in CLI mode
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
    else:
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
        
        # Save to file if specified
        if output_file:
            analyzer.save_analysis(analysis, output_file)
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()
