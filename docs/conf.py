# Sphinx configuration for RAG LLM Interface Service
import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

project = 'RAG LLM Interface Service & File-Watcher Sidecar'
copyright = '2025, Your Name'
author = 'Your Name'
release = '0.1.0'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
html_theme = 'alabaster'
