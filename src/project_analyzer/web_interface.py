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
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.5;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .tabs {
            display: flex;
            gap: 2px;
            margin-bottom: 20px;
            background: #eee;
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
        }
        .tab.active {
            background: white;
            font-weight: 500;
        }
        .tab:hover:not(.active) {
            background: rgba(255,255,255,0.5);
        }
        .content {
            display: none;
            white-space: pre-wrap;
            font-family: 'Consolas', 'Monaco', monospace;
            background: #f8f8f8;
            padding: 20px;
            border-radius: 6px;
            border: 1px solid #eee;
            font-size: 14px;
            line-height: 1.6;
            overflow-x: auto;
            color: #333;
        }
        .content.active {
            display: block;
        }
        h1 {
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 24px;
            font-weight: 500;
            color: #2c3e50;
        }
        .project-name {
            color: #666;
            font-size: 16px;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
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
        <pre class="content {% if loop.first %}active{% endif %}" id="{{ category }}">{{ content }}</pre>
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
