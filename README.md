# Project Analyzer

A comprehensive tool for AI-first project analysis and documentation. This tool generates detailed maps of project structure, code relationships, and dependencies, making it easier for AI systems to understand and work with your codebase.

## Features

- 📁 **Project Structure Analysis**
  - Complete directory and file hierarchy
  - File metadata (size, modification dates, encoding)
  - Language statistics and file type detection
  - Entry point identification

- 🔍 **Code Analysis**
  - Function and method definitions with signatures
  - Class hierarchies and relationships
  - Variable tracking and scope analysis
  - Import and dependency mapping
  - Documentation extraction
  - Cyclomatic complexity metrics
  - Function call relationships
  - Dead code detection

- 📊 **Code Quality Metrics**
  - Function complexity scoring
  - Call graph analysis (what calls what)
  - Function coupling analysis
  - Method relationship mapping

- 📊 **Dependency Analysis**
  - File-level dependency graphs
  - Package dependencies
  - Import relationship visualization
  - Circular dependency detection

- 🎨 **Rich Terminal Output**
  - Beautiful directory trees
  - Syntax-highlighted code snippets
  - Detailed statistics tables
  - Progress indicators

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the package:
```bash
pip install .
```

## Usage

### Command Line Interface

Basic usage:
```bash
project-analyzer /path/to/your/project
```

Save analysis to file:
```bash
project-analyzer /path/to/your/project output.json
```

### Python API

```python
from project_analyzer.main import ProjectAnalyzer

# Create analyzer instance
analyzer = ProjectAnalyzer("/path/to/your/project")

# Run analysis
analysis = analyzer.analyze()

# Display results in terminal
analyzer.display_analysis(analysis)

# Save results to file
analyzer.save_analysis(analysis, "output.json")
```

## Analysis Output

The tool generates a comprehensive JSON output containing:

```json
{
  "root_path": "/path/to/project",
  "name": "project-name",
  "total_files": 42,
  "languages": {
    "python": 15,
    "javascript": 8,
    "typescript": 5
  },
  "structure": {
    "name": "project-name",
    "path": ".",
    "is_dir": true,
    "children": [...]
  },
  "files": {
    "src/main.py": {
      "functions": [
        {
          "name": "process_data",
          "complexity": 5,
          "calls": ["validate_input", "transform_data"],
          "called_by": ["main", "batch_process"]
        }
      ],
      "classes": [
        {
          "name": "DataProcessor",
          "methods": [
            {
              "name": "process",
              "complexity": 3,
              "calls": ["validate", "transform"],
              "called_by": ["execute"]
            }
          ]
        }
      ],
      "imports": [...],
      "variables": [...]
    }
  },
  "entry_points": ["src/main.py"]
}
```

## AI Integration

The analysis output is specifically designed to help AI systems:

1. **Context Understanding**
   - Complete project structure visibility
   - Code relationship mapping
   - Dependency tracking

2. **Code Navigation**
   - Clear file relationships
   - Function and class locations
   - Import chains

3. **Semantic Analysis**
   - Documentation extraction
   - Code purpose identification
   - Architecture patterns
   - Code complexity insights
   - Function relationship mapping
   - Coupling analysis

4. **Modification Planning**
   - Impact analysis
   - Dependency checking
   - Entry point identification

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
