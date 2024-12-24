# File Structure Generator

A powerful multi-language code analysis tool that generates comprehensive documentation of your codebase structure, dependencies, and behavior. It analyzes source code to extract definitions, relationships, and provides insights about code quality and patterns.

## Features

- **Multi-Language Support**:
  - Python (with type hints and docstrings)
  - JavaScript/TypeScript (with React support)
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
  - Design pattern detection:
    - Singleton Pattern
    - Factory Pattern
    - Observer Pattern
    - Strategy Pattern
    - Decorator Pattern
  - Code smell detection
  - Pure function detection
  - Side effect analysis
  - Async behavior detection
  - Generator function analysis
  - Recursion detection

- **Variable Analysis**:
  - Type inference
  - Assignment tracking
  - Usage analysis
  - Scope detection
  - Value tracking
  - Constant detection

- **Project Structure**:
  - Directory structure visualization
  - Entry point detection
  - File categorization
  - Language statistics
  - Dependency graphs
  - Call graphs
  - Git repository information
  - Package dependencies

- **Documentation Generation**:
  - Project overview documentation
  - Architecture documentation
  - Function and class documentation
  - Design pattern documentation
  - Code quality suggestions
  - Improvement recommendations

- **Rich Output**:
  - Terminal-based visualization using Rich
  - Web interface for interactive exploration
  - Dependency analysis using NetworkX
  - Quality metrics visualization
  - Syntax highlighting
  - Interactive file browser

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/yourusername/file-structure-generator.git
cd file-structure-generator

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Dependencies

Core dependencies:
- Flask==3.0.2 - Web interface framework
- networkx==3.4.2 - Dependency analysis
- pydantic==2.10.4 - Data validation
- rich==13.9.4 - Terminal formatting and output
- annotated-types==0.7.0 - Type annotation support
- markdown-it-py==3.0.0 - Documentation generation
- Pygments==2.18.0 - Syntax highlighting
- typing_extensions==4.12.2 - Enhanced type hints

## Project Structure

```
src/
└── project_analyzer/
    ├── analyzers/         # Code analysis modules
    │   ├── code.py       # Core code analysis
    │   ├── languages/    # Language-specific analyzers
    │   │   ├── python.py
    │   │   ├── javascript.py
    │   │   ├── cpp.py
    │   │   ├── csharp.py
    │   │   └── svelte.py
    │   ├── patterns.py   # Design pattern detection
    │   └── quality.py    # Code quality metrics
    ├── models.py         # Data models
    ├── prompt_generator.py # Documentation generation
    ├── main.py           # Main application logic
    └── web_interface.py  # Web UI implementation
```

## Usage

1. Start the analyzer:
```bash
python -m project_analyzer
```

2. Select your project directory when prompted

3. View the analysis results in your terminal or web interface

The tool will analyze your codebase and provide:
- Project structure visualization
- Code quality metrics
- Function and class analysis
- Design pattern detection
- Documentation generation
- Improvement suggestions

## Web Interface

Access the web interface for interactive exploration of your codebase:

1. Start the web server:
```bash
python -m project_analyzer --web
```

2. Open your browser to `http://localhost:5000`

Features include:
- Interactive file browser
- Dependency visualization
- Code quality metrics
- Design pattern view
- Documentation browser
- Syntax-highlighted code view

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Roadmap

- [ ] Add support for more programming languages (Go, Ruby, Rust)
- [ ] Enhance visualization options
- [ ] Add plugin system for custom analyzers
- [ ] Add machine learning-based code quality predictions
- [ ] Implement real-time analysis capabilities
- [ ] Add more design pattern detectors
- [ ] Enhance code smell detection
