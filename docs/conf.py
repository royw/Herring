# -*- coding: utf-8 -*-

"""
Herring documentation build configuration file, created by
sphinx-quickstart on Mon Jul 29 13:39:31 2013.

This file is execfile()d with the current directory set to its containing dir.

Note that not all possible configuration values are present in this
autogenerated file.

All configuration values have a default; values that are commented out
serve to show the default.
"""
import re
import sys
import os
from datetime import datetime

# import sphinx_bootstrap_theme

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(1, os.path.abspath('..'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '_sphinx-ditaa/sphinxext')))
print("sys.path => %s" % sys.path)

# -- Project variables

# limit template substitutions to here to make it easier to update (merge) the rest of the file
project_name = u'Herring'
project_title = u'{project_name} Documentation'.format(project_name=project_name)
project_author = u'Roy Wright'
project_author_email = u'roy@wright.org'
project_description = u'Python make'
project_package = u'herring'

# -- General configuration -----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.graphviz',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.napoleon',
    # 'sphinx_pyreverse',
    # 'rst2pdf.pdfbuilder',     # python2.x only
    'sphinxcontrib.plantuml',
    'sphinxcontrib.blockdiag',
    'sphinxcontrib.actdiag',
    'sphinxcontrib.nwdiag',
    'sphinxcontrib.rackdiag',
    'sphinxcontrib.packetdiag',
    'sphinxcontrib.seqdiag',
    'sphinxcontrib.autoprogram',
    'ext.ditaa',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = project_name
copyright_ = u'{year}, {project_author}'.format(year=datetime.now().year, project_author=project_author)

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#


VERSION_REGEX = r'__version__\s*=\s*[\'\"](\S+)[\'\"]'


# noinspection PyArgumentEqualDefault
def get_project_version():
    """
    Get the version from __init__.py with a line: /^__version__\s*=\s*(\S+)/
    If it doesn't exist try to load it from the VERSION.txt file.
    If still no joy, then return '0.0.0'

    :returns: the version string
    :rtype: str
    """

    # trying __init__.py first
    try:
        file_name = os.path.join(os.getcwd(), '..', project_package, '__init__.py')
        with open(file_name, 'r') as inFile:
            for line in inFile.readlines():
                match = re.match(VERSION_REGEX, line)
                if match:
                    return match.group(1)
    except IOError:
        pass

    # no joy, so try getting the version from a VERSION.txt file.
    try:
        file_name = os.path.join(os.getcwd(), '..', project_package, 'VERSION.txt')
        with open(file_name, 'r') as inFile:
            return inFile.read().strip()
    except IOError:
        pass

    # no joy again, so return default
    return '0.0.0'


# The short X.Y version.
version = get_project_version()
# The full version, including alpha/beta/rc tags.
release = get_project_version()

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
# language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
# today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The reST default role (used for this markup: `text`) to use for all documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False

# -- Options for PlantUML --------------------------------------------------
# plantuml
# Path to plantuml executable. (default: 'plantuml')
plantuml = ['java', '-jar', '/usr/local/bin/plantuml.jar']
plantuml_latex_output_format = 'eps'

# -- sphinxcontrib-actdiag -----------------------------------------------------
# http://blockdiag.com/en/actdiag/index.html

# Fontpath for actdiag (truetype font)
# actdiag_fontpath = '/usr/share/fonts/truetype/ipafont/ipagp.ttf'

# -- sphinxcontrib-blockdiag -----------------------------------------------------
# http://blockdiag.com/en/blockdiag/index.html

# Fontpath for blockdiag (truetype font)
# blockdiag_fontpath = '/usr/share/fonts/truetype/ipafont/ipagp.ttf'

# -- sphinxcontrib-nwdiag -----------------------------------------------------
# http://blockdiag.com/en/nwdiag/index.html

# Fontpath for nwdiag (truetype font)
# nwdiag_fontpath = '/usr/share/fonts/truetype/ipafont/ipagp.ttf'

# -- sphinxcontrib-seqdiag -----------------------------------------------------
# http://blockdiag.com/en/seqdiag/index.html

# Fontpath for seqdiag (truetype font)
# seqdiag_fontpath = '/usr/share/fonts/truetype/ipafont/ipagp.ttf'

# -- Autodoc options -----------------------------------------------------------

# autoclass_content
#
#   This value selects what content will be inserted into the main body of an
#   autoclass directive. The possible values are:
#
#       "class"
#           Only the class’ docstring is inserted. This is the default. You can
#           still document __init__ as a separate method using automethod or the
#           members option to autoclass.
#       "both"
#           Both the class’ and the __init__ method’s docstring are concatenated
#           and inserted.
#       "init"
#           Only the __init__ method’s docstring is inserted.
#
#   New in version 0.3.
#
autoclass_content = "both"

# autodoc_member_order
#
#   This value selects if automatically documented members are sorted alphabetical
#   (value 'alphabetical'), by member type (value 'groupwise') or by source order
#   (value 'bysource'). The default is alphabetical.
#
#   Note that for source order, the module must be a Python module with the source
#   code available.
#
#   New in version 0.6.
#
#   Changed in version 1.0: Support for 'bysource'.
#
autodoc_member_order = "alphabetical"

# autodoc_default_flags
#
#   This value is a list of autodoc directive flags that should be automatically
#   applied to all autodoc directives. The supported flags are 'members',
#   'undoc-members', 'private-members', 'special-members', 'inherited-members' and
#   'show-inheritance'.
#
#   If you set one of these flags in this config value, you can use a negated form,
#   'no-flag', in an autodoc directive, to disable it once. For example, if
#   autodoc_default_flags is set to ['members', 'undoc-members'], and you write a
#   directive like this:
#
#     .. automodule:: foo
#        :no-undoc-members:
#
#   the directive will be interpreted as if only :members: was given.
#
#   New in version 1.0.
#
# autodoc_default_flags = ['members', 'undoc-members', 'private-members', 'special-members', 'inherited-members',
#                          'show-inheritance']
autodoc_default_flags = ['members', 'undoc-members', 'inherited-members', 'show-inheritance']

# autodoc_docstring_signature
#
#   Functions imported from C modules cannot be introspected, and therefore the
#   signature for such functions cannot be automatically determined. However, it
#   is an often-used convention to put the signature into the first line of the
#   function’s docstring.
#
#   If this boolean value is set to True (which is the default), autodoc will look
#   at the first line of the docstring for functions and methods, and if it looks
#   like a signature, use the line as the signature and remove it from the docstring
#   content.
#
#   New in version 1.1.

# -- inheritance_diagram options
#
# inheritance_graph_attrs
#
#     A dictionary of graphviz graph attributes for inheritance diagrams.
#
#     For example:
#
#     inheritance_graph_attrs = dict(rankdir="LR", size='"6.0, 8.0"',
#                                    fontsize=14, ratio='compress')
#
# inheritance_node_attrs
#
#     A dictionary of graphviz node attributes for inheritance diagrams.
#
#     For example:
#
#     inheritance_node_attrs = dict(shape='ellipse', fontsize=14, height=0.75,
#                                   color='dodgerblue1', style='filled')
#
# inheritance_edge_attrs
#
#     A dictionary of graphviz edge attributes for inheritance diagrams.

# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
# html_theme = 'default'
# html_theme = 'solar'
html_theme = 'nature'
# html_theme = 'scrolls'    # crashes

# html_theme = 'bootstrap'  # crashes
# html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
# html_theme_options = {}
html_theme_options = {
    'sidebarwidth': 400,
    # 'headbgcolor': 'black'
}

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []
html_theme_path = ['_themes']

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
# html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None
html_logo = "Herring.gif"

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
# html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = '{project_name}Doc'.format(project_name=project_name)


# -- Options for LaTeX output --------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    # 'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
    ('index',
     '{project_name}.tex'.format(project_name=project_name),
     project_title,
     project_author,
     'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', project_package,
     project_title,
     [project_author], 1)
]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for Texinfo output ------------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    ('index',
     project_name,
     project_title,
     project_author,
     project_name,
     project_description,
     'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
# texinfo_no_detailmenu = False

# -- Options for PDF output --------------------------------------------------
# Grouping the document tree into PDF files. List of tuples
# (source start file, target name, title, author, options).
#
# If there is more than one author, separate them with \\.
# For example: r'Guido van Rossum\\Fred L. Drake, Jr., editor'
#
# The options element is a dictionary that lets you override
# this config per-document.
# For example,
# ('index', u'MyProject', u'My Project', u'Author Name',
# dict(pdf_compressed = True))
# would mean that specific document would be compressed
# regardless of the global pdf_compressed setting.
pdf_documents = [
    ('index', project_name, project_title, project_author),
]

# A comma-separated list of custom stylesheets. Example:
pdf_stylesheets = ['sphinx', 'kerning', 'a4']

# A list of folders to search for stylesheets. Example:
pdf_style_path = ['.', '_styles']

# Create a compressed PDF
# Use True/False or 1/0
# Example: compressed=True
# pdf_compressed = False

# A colon-separated list of folders to search for fonts. Example:
# pdf_font_path = ['/usr/share/fonts', '/usr/share/texmf-dist/fonts/']

# Language to be used for hyphenation support
# pdf_language = "en_US"

# Mode for literal blocks wider than the frame. Can be
# overflow, shrink or truncate
# pdf_fit_mode = "shrink"

# Section level that forces a break page.
# For example: 1 means top-level sections start in a new page
# 0 means disabled
# pdf_break_level = 0

# When a section starts in a new page, force it to be 'even', 'odd',
# or just use 'any'
# pdf_breakside = 'any'

# Insert footnotes where they are defined instead of
# at the end.
# pdf_inline_footnotes = True

# verbosity level. 0 1 or 2
# pdf_verbosity = 0

# If false, no index is generated.
# pdf_use_index = True

# If false, no modindex is generated.
# pdf_use_modindex = True

# If false, no coverpage is generated.
# pdf_use_coverpage = True
pdf_use_coverpage = False

# Name of the cover page template to use
# pdf_cover_template = 'sphinxcover.tmpl'

# Documents to append as an appendix to all manuals.
# pdf_appendices = []

# Enable experimental feature to split table cells. Use it
# if you get "DelayedTable too big" errors
# pdf_splittables = False

# Set the default DPI for images
pdf_default_dpi = 72

# Enable rst2pdf extension modules (default is only vectorpdf)
# you need vectorpdf if you want to use sphinx's graphviz support
# pdf_extensions = ['vectorpdf']

# Page template name for "regular" pages
# pdf_page_template = 'cutePage'

# Show Table Of Contents at the beginning?
# pdf_use_toc = True
pdf_use_toc = False

# How many levels deep should the table of contents be?
pdf_toc_depth = 9999

# Add section number to section references
pdf_use_numbered_links = False

# Background images fitting mode
pdf_fit_background_mode = 'scale'

#  -- Options for intersphinx ---------------------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'http://docs.python.org/': None,
    'python27': ('http://docs.python.org/2.7', None),
    'six': ('http://pythonhosted.org/six/', None),
    'dateutil': ('https://dateutil.readthedocs.org/en/latest/', None),
}
