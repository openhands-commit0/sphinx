"""constants for LaTeX builder."""
from __future__ import annotations
from typing import Any
PDFLATEX_DEFAULT_FONTPKG = '\n\\usepackage{tgtermes}\n\\usepackage{tgheros}\n\\renewcommand{\\ttdefault}{txtt}\n'
PDFLATEX_DEFAULT_FONTSUBSTITUTION = '\n\\expandafter\\ifx\\csname T@LGR\\endcsname\\relax\n\\else\n% LGR was declared as font encoding\n  \\substitutefont{LGR}{\\rmdefault}{cmr}\n  \\substitutefont{LGR}{\\sfdefault}{cmss}\n  \\substitutefont{LGR}{\\ttdefault}{cmtt}\n\\fi\n\\expandafter\\ifx\\csname T@X2\\endcsname\\relax\n  \\expandafter\\ifx\\csname T@T2A\\endcsname\\relax\n  \\else\n  % T2A was declared as font encoding\n    \\substitutefont{T2A}{\\rmdefault}{cmr}\n    \\substitutefont{T2A}{\\sfdefault}{cmss}\n    \\substitutefont{T2A}{\\ttdefault}{cmtt}\n  \\fi\n\\else\n% X2 was declared as font encoding\n  \\substitutefont{X2}{\\rmdefault}{cmr}\n  \\substitutefont{X2}{\\sfdefault}{cmss}\n  \\substitutefont{X2}{\\ttdefault}{cmtt}\n\\fi\n'
XELATEX_DEFAULT_FONTPKG = '\n\\setmainfont{FreeSerif}[\n  Extension      = .otf,\n  UprightFont    = *,\n  ItalicFont     = *Italic,\n  BoldFont       = *Bold,\n  BoldItalicFont = *BoldItalic\n]\n\\setsansfont{FreeSans}[\n  Extension      = .otf,\n  UprightFont    = *,\n  ItalicFont     = *Oblique,\n  BoldFont       = *Bold,\n  BoldItalicFont = *BoldOblique,\n]\n\\setmonofont{FreeMono}[\n  Extension      = .otf,\n  UprightFont    = *,\n  ItalicFont     = *Oblique,\n  BoldFont       = *Bold,\n  BoldItalicFont = *BoldOblique,\n]\n'
XELATEX_GREEK_DEFAULT_FONTPKG = XELATEX_DEFAULT_FONTPKG + '\n\\newfontfamily\\greekfont{FreeSerif}' + '\n\\newfontfamily\\greekfontsf{FreeSans}' + '\n\\newfontfamily\\greekfonttt{FreeMono}'
LUALATEX_DEFAULT_FONTPKG = XELATEX_DEFAULT_FONTPKG
DEFAULT_SETTINGS: dict[str, Any] = {'latex_engine': 'pdflatex', 'papersize': '', 'pointsize': '', 'pxunit': '.75bp', 'classoptions': '', 'extraclassoptions': '', 'maxlistdepth': '', 'sphinxpkgoptions': '', 'sphinxsetup': '', 'fvset': '\\fvset{fontsize=auto}', 'passoptionstopackages': '', 'geometry': '\\usepackage{geometry}', 'inputenc': '', 'utf8extra': '', 'cmappkg': '\\usepackage{cmap}', 'fontenc': '\\usepackage[T1]{fontenc}', 'amsmath': '\\usepackage{amsmath,amssymb,amstext}', 'multilingual': '', 'babel': '\\usepackage{babel}', 'polyglossia': '', 'fontpkg': PDFLATEX_DEFAULT_FONTPKG, 'fontsubstitution': PDFLATEX_DEFAULT_FONTSUBSTITUTION, 'substitutefont': '', 'textcyrillic': '', 'textgreek': '\\usepackage{textalpha}', 'fncychap': '\\usepackage[Bjarne]{fncychap}', 'hyperref': '% Include hyperref last.\n\\usepackage{hyperref}\n% Fix anchor placement for figures with captions.\n\\usepackage{hypcap}% it must be loaded after hyperref.\n% Set up styles of URL: it should be placed after hyperref.\n\\urlstyle{same}', 'contentsname': '', 'extrapackages': '', 'preamble': '', 'title': '', 'release': '', 'author': '', 'releasename': '', 'makeindex': '\\makeindex', 'shorthandoff': '', 'maketitle': '\\sphinxmaketitle', 'tableofcontents': '\\sphinxtableofcontents', 'atendofbody': '', 'printindex': '\\printindex', 'transition': '\n\n\\bigskip\\hrule\\bigskip\n\n', 'figure_align': 'htbp', 'tocdepth': '', 'secnumdepth': ''}
ADDITIONAL_SETTINGS: dict[Any, dict[str, Any]] = {'pdflatex': {'inputenc': '\\usepackage[utf8]{inputenc}', 'utf8extra': '\\ifdefined\\DeclareUnicodeCharacter\n% support both utf8 and utf8x syntaxes\n  \\ifdefined\\DeclareUnicodeCharacterAsOptional\n    \\def\\sphinxDUC#1{\\DeclareUnicodeCharacter{"#1}}\n  \\else\n    \\let\\sphinxDUC\\DeclareUnicodeCharacter\n  \\fi\n  \\sphinxDUC{00A0}{\\nobreakspace}\n  \\sphinxDUC{2500}{\\sphinxunichar{2500}}\n  \\sphinxDUC{2502}{\\sphinxunichar{2502}}\n  \\sphinxDUC{2514}{\\sphinxunichar{2514}}\n  \\sphinxDUC{251C}{\\sphinxunichar{251C}}\n  \\sphinxDUC{2572}{\\textbackslash}\n\\fi'}, 'xelatex': {'latex_engine': 'xelatex', 'polyglossia': '\\usepackage{polyglossia}', 'babel': '', 'fontenc': '\\usepackage{fontspec}\n\\defaultfontfeatures[\\rmfamily,\\sffamily,\\ttfamily]{}', 'fontpkg': XELATEX_DEFAULT_FONTPKG, 'fvset': '\\fvset{fontsize=\\small}', 'fontsubstitution': '', 'textgreek': '', 'utf8extra': '\\catcode`^^^^00a0\\active\\protected\\def^^^^00a0{\\leavevmode\\nobreak\\ }'}, 'lualatex': {'latex_engine': 'lualatex', 'polyglossia': '\\usepackage{polyglossia}', 'babel': '', 'fontenc': '\\usepackage{fontspec}\n\\defaultfontfeatures[\\rmfamily,\\sffamily,\\ttfamily]{}', 'fontpkg': LUALATEX_DEFAULT_FONTPKG, 'fvset': '\\fvset{fontsize=\\small}', 'fontsubstitution': '', 'textgreek': '', 'utf8extra': '\\catcode`^^^^00a0\\active\\protected\\def^^^^00a0{\\leavevmode\\nobreak\\ }'}, 'platex': {'latex_engine': 'platex', 'babel': '', 'classoptions': ',dvipdfmx', 'fontpkg': PDFLATEX_DEFAULT_FONTPKG, 'fontsubstitution': '', 'textgreek': '', 'fncychap': '', 'geometry': '\\usepackage[dvipdfm]{geometry}'}, 'uplatex': {'latex_engine': 'uplatex', 'babel': '', 'classoptions': ',dvipdfmx', 'fontpkg': PDFLATEX_DEFAULT_FONTPKG, 'fontsubstitution': '', 'textgreek': '', 'fncychap': '', 'geometry': '\\usepackage[dvipdfm]{geometry}'}, ('lualatex', 'fr'): {'polyglossia': '', 'babel': '\\usepackage{babel}'}, ('xelatex', 'fr'): {'polyglossia': '', 'babel': '\\usepackage{babel}'}, ('xelatex', 'zh'): {'polyglossia': '', 'babel': '\\usepackage{babel}', 'fontenc': '\\usepackage{xeCJK}', 'fvset': '\\fvset{fontsize=\\small,formatcom=\\xeCJKVerbAddon}'}, ('xelatex', 'el'): {'fontpkg': XELATEX_GREEK_DEFAULT_FONTPKG}}
SHORTHANDOFF = '\n\\ifdefined\\shorthandoff\n  \\ifnum\\catcode`\\=\\string=\\active\\shorthandoff{=}\\fi\n  \\ifnum\\catcode`\\"=\\active\\shorthandoff{"}\\fi\n\\fi\n'