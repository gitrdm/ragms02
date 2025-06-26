#!/bin/bash
# Publish Sphinx docs to GitHub Pages (gh-pages branch)
# Usage: ./scripts/publish_docs.sh
set -e

# Build the docs
make docs

# Import the built HTML to gh-pages branch and push
pip show ghp-import >/dev/null 2>&1 || pip install ghp-import

ghp-import -n -p -f docs/_build/html

echo "Sphinx docs published to gh-pages branch and pushed to origin."
