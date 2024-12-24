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

## Roadmap & TODOs

### 1. Easy Implementation Tasks

#### Add More Design Pattern Detectors
- [ ] Add Builder Pattern detector
  - Implement pattern detection in patterns.py
  - Look for classes with step-by-step construction methods
  - Add builder-specific code smell detection
- [ ] Add Adapter Pattern detector
  - Look for classes that wrap other classes
  - Check for interface conversion patterns
  - Add to pattern visualization
- [ ] Add Command Pattern detector
  - Look for classes with execute/run methods
  - Check for command queuing patterns
  - Add to analysis results

#### Enhance Code Smell Detection
- [ ] Add Long Method detection
  - Count lines in methods/functions
  - Set configurable thresholds
  - Add to quality metrics
- [ ] Add Duplicate Code detection
  - Implement simple string matching
  - Detect similar code blocks
  - Add to code quality report
- [ ] Add Large Class detection
  - Count methods and variables
  - Set size thresholds
  - Add visualization
- [ ] Add Comment smell detection
  - Detect TODO/FIXME comments
  - Find outdated comments
  - Add to quality metrics

#### Enhance Visualization
- [ ] Add basic graph visualization
  - Implement dependency graphs using networkx
  - Add class inheritance trees
  - Add interactive navigation
- [ ] Add code complexity heatmap
  - Color-code files by complexity
  - Add legend and metrics
  - Make interactive
- [ ] Add treemap visualization
  - Show project structure
  - Size by code complexity
  - Color by language/type

### 2. Medium Difficulty Tasks

#### Language Support
- [ ] Add Go support
  - Create analyzers/languages/go.py
  - Implement function/struct detection
  - Add import analysis
  - Add interface detection
- [ ] Plan for Ruby support
- [ ] Plan for Rust support

#### Real-time Analysis
- [ ] Add file system watcher
  - Monitor for file changes
  - Trigger incremental analysis
  - Update UI in real-time
- [ ] Implement partial analysis
  - Only analyze changed files
  - Update existing results
  - Maintain analysis cache

#### Plugin System
- [ ] Create basic plugin architecture
  - Define plugin interface
  - Add plugin loading mechanism
  - Add plugin configuration
- [ ] Create example plugins
  - Custom pattern detector
  - Custom metrics calculator
  - Documentation generator

### 3. Complex Tasks

#### Machine Learning Integration
- [ ] Code Quality Predictions
  - Collect training data
  - Define feature extraction
  - Implement basic ML model
  - Train on code smells
  - Add prediction visualization

#### Advanced Analysis
- [ ] Add data flow analysis
  - Track variable values
  - Detect null references
  - Analyze control flow
- [ ] Add security analysis
  - Find security patterns
  - Detect vulnerabilities
  - Generate security reports

### 4. Current Implementation Improvements

#### Web Interface
- [ ] Fix port number discrepancy (5000 vs 5001)
- [ ] Implement proper dependency visualization
- [ ] Add interactive graph views
- [ ] Add file diff viewer
- [ ] Add search functionality

#### Analysis Enhancements
- [ ] Improve pattern detection accuracy
- [ ] Enhance code smell detection
- [ ] Add test coverage analysis
- [ ] Add documentation coverage metrics

#### Documentation
- [ ] Add API documentation
- [ ] Add developer guide
- [ ] Add contribution guidelines
- [ ] Add architecture documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

Please check the TODO lists above for areas where you can contribute. We especially welcome contributions to the easy implementation tasks as they provide quick wins for the project.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
