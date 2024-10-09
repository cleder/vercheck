"""Sphinx configuration."""

project = "Vercheck"
author = "Christian Ledermann"
copyright = "2024, Christian Ledermann"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
