"""Web interface for displaying analysis prompts"""
from flask import Flask, render_template_string
from pathlib import Path
from .main import ProjectAnalyzer
from .folder_selector import select_project
from .prompt_generator import PromptGenerator

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Project Analysis Prompts</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.5;
            margin: 0;
            padding: 20px;
            background: #1e1e1e;
            color: #d4d4d4;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: #252526;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }
        .tabs {
            display: flex;
            gap: 2px;
            margin-bottom: 20px;
            background: #2d2d2d;
            padding: 5px;
            border-radius: 6px;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border: none;
            background: none;
            border-radius: 4px;
            font-size: 14px;
            color: #d4d4d4;
            transition: all 0.2s;
        }
        .tab.active {
            background: #3c3c3c;
            font-weight: 500;
            color: #fff;
        }
        .tab:hover:not(.active) {
            background: #3c3c3c50;
        }
        .content {
            display: none;
            white-space: pre-wrap;
            font-family: 'JetBrains Mono', 'Consolas', monospace;
            background: #1e1e1e;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #333;
            font-size: 14px;
            line-height: 1.6;
            overflow-x: auto;
            color: #d4d4d4;
        }
        .content.active {
            display: block;
        }
        h1 {
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 24px;
            font-weight: 500;
            color: #fff;
        }
        .project-name {
            color: #888;
            font-size: 16px;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #333;
        }
        .section-title {
            color: #569cd6;
            font-weight: 500;
            margin-bottom: 10px;
        }
        .section-divider {
            border-top: 1px solid #333;
            margin: 20px 0;
        }
        .function-name {
            color: #dcdcaa;
        }
        .class-name {
            color: #4ec9b0;
        }
        .file-path {
            color: #ce9178;
        }
        .keyword {
            color: #569cd6;
        }
        .comment {
            color: #6a9955;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Project Analysis Prompts</h1>
        <div class="project-name">Analyzing: {{ project_name }}</div>
        <div class="tabs">
            {% for category in prompts.keys() %}
            <button class="tab {% if loop.first %}active{% endif %}" 
                    onclick="showContent('{{ category }}')">
                {{ category|replace('_', ' ')|title }}
            </button>
            {% endfor %}
        </div>
        {% for category, content in prompts.items() %}
        <pre class="content {% if loop.first %}active{% endif %}" id="{{ category }}"><code class="language-markdown">{{ content }}</code></pre>
        {% endfor %}
    </div>
    <script>
        function showContent(category) {
            // Hide all content
            document.querySelectorAll('.content').forEach(el => {
                el.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(el => {
                el.classList.remove('active');
            });
            
            // Show selected content
            document.getElementById(category).classList.add('active');
            document.querySelector(`[onclick="showContent('${category}')"]`).classList.add('active');
        }
        
        // Initialize syntax highlighting
        document.addEventListener('DOMContentLoaded', (event) => {
            document.querySelectorAll('pre code').forEach((el) => {
                hljs.highlightElement(el);
            });
        });
    </script>
</body>
</html>
"""

def run_web_interface():
    """Run the web interface"""
    # Get project path from GUI
    project_path, _ = select_project()
    if project_path is None:
        print("Analysis cancelled.")
        return
    
    try:
        # Analyze project
        analyzer = ProjectAnalyzer(project_path)
        analysis = analyzer.analyze()
        
        # Generate prompts
        prompts = PromptGenerator.generate_prompts(analysis)
        
        # Debug print
        print("\nGenerated prompts:")
        for category, content in prompts.items():
            print(f"\n{category}:")
            print("-" * 40)
            print(content)
            print("-" * 40)
        
        # Define route
        @app.route('/')
        def index():
            return render_template_string(HTML_TEMPLATE, 
                                       prompts=prompts,
                                       project_name=analysis.name)
        
        # Run Flask app
        print("\nStarting web interface...")
        app.run(debug=False, port=5000)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    run_web_interface()
