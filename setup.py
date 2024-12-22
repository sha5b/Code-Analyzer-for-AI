from setuptools import setup, find_packages

setup(
    name="project-analyzer",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "annotated-types>=0.7.0",
        "Flask>=3.0.2",
        "markdown-it-py>=3.0.0",
        "mdurl>=0.1.2",
        "networkx>=3.4.2",
        "pydantic>=2.10.4",
        "pydantic_core>=2.27.2",
        "Pygments>=2.18.0",
        "rich>=13.9.4",
        "typing_extensions>=4.12.2"
    ],
    entry_points={
        "console_scripts": [
            "project-analyzer=project_analyzer.main:main",
        ],
    },
    author="AI Project Analyzer",
    description="A powerful multi-language code analysis tool for project structure, dependencies, and behavior analysis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="project-analysis, code-analysis, documentation, multi-language, static-analysis, dependency-analysis",
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
