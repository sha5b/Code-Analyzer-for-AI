"""
Data models for project analysis results
"""
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field


class CodeLocation(BaseModel):
    """Represents a location in source code"""
    file: str
    line_start: int
    line_end: int
    column_start: Optional[int] = None
    column_end: Optional[int] = None


class Variable(BaseModel):
    """Variable definition and usage information"""
    name: str
    type_hint: Optional[str] = None
    value: Optional[str] = None
    locations: List[CodeLocation] = Field(default_factory=list)
    is_constant: bool = False
    scope: str = "module"  # module, class, function
    docstring: Optional[str] = None


class ControlFlow(BaseModel):
    """Control flow information for a function"""
    line_no: int
    node_type: str
    condition: Optional[str] = None
    true_branch: List[int] = Field(default_factory=list)
    false_branch: List[int] = Field(default_factory=list)
    parent: Optional[int] = None


class VariableFlow(BaseModel):
    """Variable usage and flow analysis"""
    name: str
    assignments: List[int] = Field(default_factory=list)  # Assignment line numbers
    reads: List[int] = Field(default_factory=list)  # Usage line numbers
    scope: str = "local"  # local, global, nonlocal, parameter
    type_hints: Optional[str] = None
    potential_values: List[str] = Field(default_factory=list)


class FunctionBehavior(BaseModel):
    """Detailed function behavior analysis"""
    entry_points: List[str] = Field(default_factory=list)  # Functions that call this
    exit_points: List[str] = Field(default_factory=list)  # Functions called before return
    return_paths: List[List[int]] = Field(default_factory=list)  # Paths to returns
    control_flow: List[ControlFlow] = Field(default_factory=list)
    pure: bool = True  # No side effects
    side_effects: List[str] = Field(default_factory=list)
    raises: List[str] = Field(default_factory=list)  # Potential exceptions
    async_status: bool = False
    generators: bool = False
    recursion: bool = False
    variables: Dict[str, VariableFlow] = Field(default_factory=dict)  # Variable usage tracking


class Function(BaseModel):
    """Function/method definition and metadata"""
    name: str
    location: CodeLocation
    args: List[Dict[str, Optional[str]]] = Field(default_factory=list)  # name: type_hint
    returns: Optional[str] = None
    docstring: Optional[str] = None
    decorators: List[str] = Field(default_factory=list)
    calls: List[str] = Field(default_factory=list)  # Other functions this calls
    called_by: List[str] = Field(default_factory=list)  # Functions that call this
    variables: List[Variable] = Field(default_factory=list)
    complexity: Optional[int] = None  # Cyclomatic complexity
    
    # New detailed analysis fields
    behavior: Optional[FunctionBehavior] = None
    variable_flow: List[VariableFlow] = Field(default_factory=list)


class Class(BaseModel):
    """Class definition and metadata"""
    name: str
    location: CodeLocation
    base_classes: List[str] = Field(default_factory=list)
    methods: List[Function] = Field(default_factory=list)
    class_variables: List[Variable] = Field(default_factory=list)
    instance_variables: List[Variable] = Field(default_factory=list)
    docstring: Optional[str] = None
    decorators: List[str] = Field(default_factory=list)


class Import(BaseModel):
    """Import statement information"""
    module: str
    names: List[str] = Field(default_factory=list)  # imported names
    alias: Optional[str] = None
    location: CodeLocation
    is_from_import: bool = False


class File(BaseModel):
    """Single file analysis results"""
    path: str
    imports: List[Import] = Field(default_factory=list)
    functions: List[Function] = Field(default_factory=list)
    classes: List[Class] = Field(default_factory=list)
    variables: List[Variable] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)  # Files this depends on
    dependents: List[str] = Field(default_factory=list)  # Files that depend on this
    doc_blocks: List[str] = Field(default_factory=list)  # Major documentation blocks
    size_bytes: int
    last_modified: str
    language: str
    encoding: str = "utf-8"


class ProjectStructure(BaseModel):
    """Directory and file structure information"""
    name: str
    path: str
    is_dir: bool = True
    children: List["ProjectStructure"] = Field(default_factory=list)
    size_bytes: Optional[int] = None
    last_modified: Optional[str] = None


class ProjectAnalysis(BaseModel):
    """Complete project analysis results"""
    root_path: str
    name: str
    files: Dict[str, File] = Field(default_factory=dict)
    structure: ProjectStructure
    total_files: int = 0
    total_lines: int = 0
    languages: Dict[str, int] = Field(default_factory=dict)  # language: num_files
    entry_points: List[str] = Field(default_factory=list)
    package_dependencies: Dict[str, str] = Field(default_factory=dict)  # pkg: version
    git_info: Optional[Dict[str, str]] = None
    readme_content: Optional[str] = None
    license_type: Optional[str] = None
