# Project Analyzer

A powerful multi-language code analysis tool that provides deep insights into your codebase structure, dependencies, and behavior.

## Features

- **Multi-Language Support**:
  - Python (with type hints and docstrings)
  - JavaScript/TypeScript (with JSDoc support)
  - React/React-TypeScript
  - C/C++ (with templates and namespaces)
  - C# (with attributes and type definitions)
  - Svelte (component analysis)

- **Code Analysis**:
  - Function and class definitions
  - Variable scopes and dependencies
  - Import/dependency tracking
  - Control flow analysis
  - Code quality metrics
  - Function behavior analysis
  - Type inference
  - Documentation extraction

- **Project Structure**:
  - Directory structure visualization
  - Entry point detection
  - File categorization
  - Language statistics

- **Visualization**:
  - Rich terminal output
  - Web interface for interactive exploration
  - Dependency graphs
  - Control flow diagrams

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Windows

```bash
# Clone the repository
git clone https://github.com/yourusername/project-analyzer.git
cd project-analyzer

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### macOS/Linux

```bash
# Clone the repository
git clone https://github.com/yourusername/project-analyzer.git
cd project-analyzer

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Usage

### Command Line Interface

1. Basic Analysis:
```bash
python -m project_analyzer
```
This will open a folder selection dialog. Choose your project directory and optionally specify an output file for the analysis results.

2. Web Interface:
```bash
python -m project_analyzer --web
```
This launches the web interface for interactive exploration of analysis results.

### Python API

```python
from project_analyzer import ProjectAnalyzer

# Initialize analyzer
analyzer = ProjectAnalyzer("path/to/your/project")

# Run analysis
analysis = analyzer.analyze()

# Display results in terminal
analyzer.display_analysis(analysis)

# Save results to file
analyzer.save_analysis(analysis, "output.json")
```

## Analysis Output

The tool provides comprehensive analysis including:

1. **Project Overview**:
   - Total file count
   - Language distribution
   - Entry points
   - Directory structure

2. **Code Analysis**:
   - Function and class definitions
   - Dependencies between files
   - Import relationships
   - Code complexity metrics

3. **Function Analysis**:
   - Control flow
   - Variable usage
   - Side effects
   - Pure function detection
   - Exception paths
   - Async behavior

4. **Quality Metrics**:
   - Code complexity
   - Function length
   - Documentation coverage
   - Type hint coverage

## Web Interface

The web interface provides an interactive way to explore your codebase:

1. Start the web interface:
```bash
python -m project_analyzer --web
```

2. Open your browser and navigate to `http://localhost:5000`

3. Features:
   - Interactive file browser
   - Dependency visualization
   - Code structure diagrams
   - Search functionality
   - Metric dashboards

## Configuration

The analyzer can be configured through a `pyproject.toml` file in your project root:

```toml
[tool.project-analyzer]
exclude = [
    "tests/*",
    "docs/*",
    "*.pyc",
    "__pycache__"
]

[tool.project-analyzer.quality]
max_complexity = 10
max_line_length = 88
min_documentation_coverage = 80
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Uses [NetworkX](https://networkx.org/) for dependency analysis
- Web interface powered by Flask

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'project_analyzer'**
   - Ensure you've installed the package in development mode: `pip install -e .`
   - Check that your virtual environment is activated

2. **Permission denied when running the analyzer**
   - On Unix systems, ensure the script has execute permissions:
     ```bash
     chmod +x venv/bin/project_analyzer
     ```

3. **Web interface not starting**
   - Check if port 5000 is available
   - Ensure Flask is installed correctly

### Getting Help

- Open an issue on GitHub
- Check the documentation
- Join our community discussions

## Roadmap

- [ ] Add support for more languages (Rust, Go, Ruby)
- [ ] Implement machine learning-based code quality predictions
- [ ] Add real-time analysis capabilities
- [ ] Enhance visualization options
- [ ] Add plugin system for custom analyzers
