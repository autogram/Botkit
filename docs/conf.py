# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys

from importlib.metadata import version

try:
    __version__ = version(__name__)
except:
    pass

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "Autogram Botkit"
copyright = "2020, Joscha Götzer"
author = "Joscha Götzer"

# def format_version(v: ScmVersion):
#     version_string: str = guess_next_dev_version(v)
#     components = version_string.split(".")
#     return ".".join(components[0:2])


# -- General configuration ---------------------------------------------------

extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx"]

exclude_patterns = ["build", "Thumbs.db", ".DS_Store"]

warning_is_error = True

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
extensions.append("sphinx_rtd_theme")

html_static_path = ["static"]

intersphinx_mapping = {
    "pymongo": ("https://pymongo.readthedocs.io/en/stable/", None),
    "py": ("https://docs.python.org/3/", None),
}
