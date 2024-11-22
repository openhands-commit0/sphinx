"""Handlers for additional ReST roles."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING, Any
import docutils.parsers.rst.directives
import docutils.parsers.rst.roles
import docutils.parsers.rst.states
from docutils import nodes, utils
from sphinx import addnodes
from sphinx.locale import _, __
from sphinx.util import ws_re
from sphinx.util.docutils import ReferenceRole, SphinxRole
if TYPE_CHECKING:
    from collections.abc import Sequence
    from docutils.nodes import Element, Node, TextElement, system_message
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment
    from sphinx.util.typing import ExtensionMetadata, RoleFunction
generic_docroles = {'command': addnodes.literal_strong, 'dfn': nodes.emphasis, 'kbd': nodes.literal, 'mailheader': addnodes.literal_emphasis, 'makevar': addnodes.literal_strong, 'mimetype': addnodes.literal_emphasis, 'newsgroup': addnodes.literal_emphasis, 'program': addnodes.literal_strong, 'regexp': nodes.literal}

class XRefRole(ReferenceRole):
    """
    A generic cross-referencing role.  To create a callable that can be used as
    a role function, create an instance of this class.

    The general features of this role are:

    * Automatic creation of a reference and a content node.
    * Optional separation of title and target with `title <target>`.
    * The implementation is a class rather than a function to make
      customization easier.

    Customization can be done in two ways:

    * Supplying constructor parameters:
      * `fix_parens` to normalize parentheses (strip from target, and add to
        title if configured)
      * `lowercase` to lowercase the target
      * `nodeclass` and `innernodeclass` select the node classes for
        the reference and the content node

    * Subclassing and overwriting `process_link()` and/or `result_nodes()`.
    """
    nodeclass: type[Element] = addnodes.pending_xref
    innernodeclass: type[TextElement] = nodes.literal

    def __init__(self, fix_parens: bool=False, lowercase: bool=False, nodeclass: type[Element] | None=None, innernodeclass: type[TextElement] | None=None, warn_dangling: bool=False) -> None:
        self.fix_parens = fix_parens
        self.lowercase = lowercase
        self.warn_dangling = warn_dangling
        if nodeclass is not None:
            self.nodeclass = nodeclass
        if innernodeclass is not None:
            self.innernodeclass = innernodeclass
        super().__init__()

    def process_link(self, env: BuildEnvironment, refnode: Element, has_explicit_title: bool, title: str, target: str) -> tuple[str, str]:
        """Called after parsing title and target text, and creating the
        reference node (given in *refnode*).  This method can alter the
        reference node and must return a new (or the same) ``(title, target)``
        tuple.
        """
        if not has_explicit_title and self.fix_parens:
            if target.endswith('()'):
                title = title[:-2]
            if target.endswith('[]'):
                title = title[:-2]
        if self.lowercase:
            target = target.lower()
        return title, target

    def result_nodes(self, document: nodes.document, env: BuildEnvironment, node: Element, is_ref: bool) -> tuple[list[Node], list[system_message]]:
        """Called before returning the finished nodes.  *node* is the reference
        node if one was created (*is_ref* is then true), else the content node.
        This method can add other nodes and must return a ``(nodes, messages)``
        tuple (the usual return value of a role function).
        """
        return [node], []

class AnyXRefRole(XRefRole):
    pass

class PEP(ReferenceRole):
    def run(self) -> tuple[list[Node], list[system_message]]:
        target_id = 'index-%s' % self.env.new_serialno('index')
        entries = [('single', _('Python Enhancement Proposals; PEP %s') % self.target,
                   target_id, '', None)]

        index = addnodes.index(entries=entries)
        target = nodes.target('', '', ids=[target_id])
        self.inliner.document.note_explicit_target(target)

        try:
            pepnum = int(self.target)
            ref = self.inliner.document.settings.pep_base_url + 'pep-%04d' % pepnum
        except ValueError:
            msg = self.inliner.reporter.error('invalid PEP number %s' % self.target,
                                            line=self.lineno)
            prb = self.inliner.problematic(self.rawtext, self.rawtext, msg)
            return [prb], [msg]

        if not self.has_explicit_title:
            title = "PEP " + self.title
            self.title = title

        reference = nodes.reference('', '', internal=False, refuri=ref,
                                  classes=['pep'])
        if self.has_explicit_title:
            reference += nodes.Text(self.title)
        else:
            reference += nodes.Text(title)

        return [index, target, reference], []

class RFC(ReferenceRole):
    def run(self) -> tuple[list[Node], list[system_message]]:
        target_id = 'index-%s' % self.env.new_serialno('index')
        entries = [('single', 'RFC; RFC %s' % self.target, target_id, '', None)]

        index = addnodes.index(entries=entries)
        target = nodes.target('', '', ids=[target_id])
        self.inliner.document.note_explicit_target(target)

        try:
            rfcnum = int(self.target)
            ref = self.inliner.document.settings.rfc_base_url + 'rfc%d.txt' % rfcnum
        except ValueError:
            msg = self.inliner.reporter.error('invalid RFC number %s' % self.target,
                                            line=self.lineno)
            prb = self.inliner.problematic(self.rawtext, self.rawtext, msg)
            return [prb], [msg]

        if not self.has_explicit_title:
            title = "RFC " + self.title
            self.title = title

        reference = nodes.reference('', '', internal=False, refuri=ref,
                                  classes=['rfc'])
        if self.has_explicit_title:
            reference += nodes.Text(self.title)
        else:
            reference += nodes.Text(title)

        return [index, target, reference], []

class GUILabel(SphinxRole):
    amp_re = re.compile('(?<!&)&(?![&\\s])')

    def run(self) -> tuple[list[Node], list[system_message]]:
        text = self.text.replace('&&', '\x00')
        text = self.amp_re.sub('', text)
        text = text.replace('\x00', '&')
        span = nodes.inline(self.rawtext, text, classes=['guilabel'])
        return [span], []

class MenuSelection(GUILabel):
    BULLET_CHARACTER = '‣'

    def run(self) -> tuple[list[Node], list[system_message]]:
        text = self.text.replace('&&', '\x00')
        text = self.amp_re.sub('', text)
        text = text.replace('\x00', '&')
        span = nodes.inline(self.rawtext, '', classes=['menuselection'])
        for item in ws_re.split(text):
            span += nodes.Text(item)
            span += nodes.Text(self.BULLET_CHARACTER)
        span.pop()
        return [span], []

class EmphasizedLiteral(SphinxRole):
    parens_re = re.compile('(\\\\\\\\|\\\\{|\\\\}|{|})')

    def run(self) -> tuple[list[Node], list[system_message]]:
        text = self.text.replace('\\', '\\\\')
        text = self.parens_re.sub(r'\\\1', text)
        return [nodes.literal(self.rawtext, text, classes=['file'])], []

class Abbreviation(SphinxRole):
    abbr_re = re.compile('\\((.*)\\)$', re.DOTALL)

    def run(self) -> tuple[list[Node], list[system_message]]:
        text = self.text
        m = self.abbr_re.search(text)
        if m:
            text = text[:m.start()].strip()
            expl = m.group(1)
        else:
            expl = None
        abbr = nodes.abbreviation(self.rawtext, text)
        if expl:
            abbr['explanation'] = expl
        return [abbr], []

def set_classes(options: dict[str, Any]) -> None:
    """Set 'classes' key in options dict."""
    if 'class' in options:
        classes = options.get('classes', [])
        classes.extend(options['class'])
        del options['class']
        options['classes'] = classes

def code_role(typ: str, rawtext: str, text: str, lineno: int, inliner: docutils.parsers.rst.states.Inliner, options: dict[str, Any]={}, content: Sequence[str]=[]) -> tuple[list[Node], list[system_message]]:
    """Role for code samples."""
    set_classes(options)
    classes = ['code']
    if 'classes' in options:
        classes.extend(options['classes'])
    if 'language' in options:
        classes.append('highlight')
        classes.append(options['language'])
    node = nodes.literal(rawtext, utils.unescape(text), classes=classes)
    return [node], []

class Manpage(ReferenceRole):
    _manpage_re = re.compile('^(?P<path>(?P<page>.+)[(.](?P<section>[1-9]\\w*)?\\)?)$')

    def run(self) -> tuple[list[Node], list[system_message]]:
        matched = self._manpage_re.match(self.target)
        if not matched:
            msg = self.inliner.reporter.error('invalid manpage reference %r' % self.target,
                                            line=self.lineno)
            prb = self.inliner.problematic(self.rawtext, self.rawtext, msg)
            return [prb], [msg]

        page = matched.group('page')
        section = matched.group('section')
        ref = self.inliner.document.settings.manpages_url % {'page': page, 'section': section}

        if not self.has_explicit_title:
            title = matched.group('path')
            self.title = title

        reference = nodes.reference('', '', internal=False, refuri=ref,
                                  classes=['manpage'])
        reference += nodes.Text(self.title)
        return [reference], []
code_role.options = {'class': docutils.parsers.rst.directives.class_option, 'language': docutils.parsers.rst.directives.unchanged}
specific_docroles: dict[str, RoleFunction] = {'download': XRefRole(nodeclass=addnodes.download_reference), 'any': AnyXRefRole(warn_dangling=True), 'pep': PEP(), 'rfc': RFC(), 'guilabel': GUILabel(), 'menuselection': MenuSelection(), 'file': EmphasizedLiteral(), 'samp': EmphasizedLiteral(), 'abbr': Abbreviation(), 'manpage': Manpage()}