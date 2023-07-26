# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
from datetime import date
from importlib import metadata

sys.path.insert(0, os.path.abspath("."))


# -- Project information -----------------------------------------------------

project = "Architecture-as-Code"
copyright = f"2021 - {str(date.today().year)} , AaC Project Contributors"
author = "AaC Project Contributors"

# The full version, including alpha/beta/rc tags
release = metadata.version("aac")


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.githubpages",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_parser",
    "sphinx_contributors",
    "sphinx_copybutton",
]

# -- Ext: autodoc configuration ----------------------------------------------
autodoc_default_options = {
    "members": True,
}
autodoc_typehints = "both"
autodoc_preserve_defaults = True
autodoc_inherit_docstrings = True

# -- Ext: autosummary configuration ------------------------------------------
autosummary_generate = True
autosummary_generate_overwrite = False

# -- Ext: Napoleon configuration ---------------------------------------------
napoleon_google_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Ext: MYST configuration ---------------------------------------------
myst_heading_anchors = 4

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# The master toctree document.
master_doc = 'index'

# The file extensions of source files. Sphinx considers the files with this
# suffix as sources. The value can be a dictionary mapping file extensions
# to file types.
source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "restructuredtext",
    ".md": "markdown",
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "furo"

# The style name to use for Pygments highlighting of source code. If not set,
# either the theme’s default style or 'sphinx' is selected for HTML output.
pygments_style = "sphinx"
pygments_dark_style = "monokai"

# These options are generally used to change the look and feel of the theme.
html_theme_options = {}

# If given, this must be the name of an image file (path relative to the
# configuration directory) that is the favicon of the docs, or URL that
# points an image file for the favicon.
html_favicon = "favicon.ico"


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []
