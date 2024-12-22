from setuptools import setup, find_packages

setup(
    name="project-analyzer",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "networkx>=3.4.2",
        "pydantic>=2.10.4",
        "rich>=13.9.4",
    ],
    entry_points={
        "console_scripts": [
            "project-analyzer=project_analyzer.main:main",
        ],
    },
    author="AI Project Analyzer",
    description="A comprehensive tool for AI-first project analysis and documentation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="project-analysis, code-analysis, documentation, ai",
    url="https://github.com/yourusername/project-analyzer",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
)
