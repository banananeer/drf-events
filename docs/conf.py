# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import re

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
from django.conf import settings

settings.configure()

sys.path.append("../")

regex = re.compile("version.*")
with open("../pyproject.toml") as f:
    data = f.read()
    match = regex.search(data)

version = match.group(0).split(" = ")[1].replace('"', "")

project = f"DRF Events {version}"
copyright = "2024, cloud9.sh"
author = "cloud9.sh"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # Core library for html generation from docstrings
    "sphinx.ext.autosummary",  # Create neat summary tables
]
autosummary_generate = True
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
# html_static_path = ["_static"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "default"
pygments_dark_style = "monokai"

html_baseurl = os.environ.get("HTML_BASEURL", "")
