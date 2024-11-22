"""Docutils node-related utility functions for Sphinx."""
from __future__ import annotations
import contextlib
import re
import unicodedata
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast
from docutils import nodes
from docutils.nodes import Node
from sphinx import addnodes
from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.parsing import _fresh_title_style_context
if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator
    from docutils.nodes import Element
    from docutils.parsers.rst import Directive
    from docutils.parsers.rst.states import Inliner, RSTState
    from docutils.statemachine import StringList
    from sphinx.builders import Builder
    from sphinx.environment import BuildEnvironment
    from sphinx.util.tags import Tags
logger = logging.getLogger(__name__)
explicit_title_re = re.compile('^(.+?)\\s*(?<!\\x00)<([^<]*?)>$', re.DOTALL)
caption_ref_re = explicit_title_re
N = TypeVar('N', bound=Node)

class NodeMatcher(Generic[N]):
    """A helper class for Node.findall().

    It checks that the given node is an instance of the specified node-classes and
    has the specified node-attributes.

    For example, following example searches ``reference`` node having ``refdomain``
    and ``reftype`` attributes::

        matcher = NodeMatcher(nodes.reference, refdomain='std', reftype='citation')
        matcher.findall(doctree)
        # => [<reference ...>, <reference ...>, ...]

    A special value ``typing.Any`` matches any kind of node-attributes.  For example,
    following example searches ``reference`` node having ``refdomain`` attributes::

        matcher = NodeMatcher(nodes.reference, refdomain=Any)
        matcher.findall(doctree)
        # => [<reference ...>, <reference ...>, ...]
    """

    def __init__(self, *node_classes: type[N], **attrs: Any) -> None:
        self.classes = node_classes
        self.attrs = attrs

    def __call__(self, node: Node) -> bool:
        return self.match(node)

    def findall(self, node: Node) -> Iterator[N]:
        """An alternative to `Node.findall` with improved type safety.

        While the `NodeMatcher` object can be used as an argument to `Node.findall`, doing so
        confounds type checkers' ability to determine the return type of the iterator.
        """
        return (cast(N, found) for found in node.findall(self.match))

    def match(self, node: Node) -> bool:
        """Return True if the given node matches the criteria."""
        if not isinstance(node, self.classes):
            return False

        for key, value in self.attrs.items():
            if value is Any:
                if not hasattr(node, key):
                    return False
            else:
                if not hasattr(node, key) or getattr(node, key) != value:
                    return False
        return True

def get_full_module_name(node: Node) -> str:
    """
    Return full module dotted path like: 'docutils.nodes.paragraph'

    :param nodes.Node node: target node
    :return: full module dotted path
    """
    module = node.__module__ or ''
    module = module.replace('docutils_', 'docutils.')  # for apidoc build
    return '%s.%s' % (module, node.__class__.__name__)

def repr_domxml(node: Node, length: int=80) -> str:
    """
    return DOM XML representation of the specified node like:
    '<paragraph translatable="False"><inline classes="versionadded">Added in version...'

    :param nodes.Node node: target node
    :param int length:
       length of return value to be striped. if false-value is specified, repr_domxml
       returns full of DOM XML representation.
    :return: DOM XML representation
    """
    xml = node.asdom().toxml()
    if length:
        return xml[:length] + '...'
    else:
        return xml
IGNORED_NODES = (nodes.Invisible, nodes.literal_block, nodes.doctest_block, addnodes.versionmodified)
LITERAL_TYPE_NODES = (nodes.literal_block, nodes.doctest_block, nodes.math_block, nodes.raw)
IMAGE_TYPE_NODES = (nodes.image,)

def extract_messages(doctree: Element) -> Iterable[tuple[Element, str]]:
    """Extract translatable messages from a document tree."""
    for node in doctree.findall(nodes.TextElement):
        if not isinstance(node, IGNORED_NODES) and node.get('translatable', True):
            # extract message from text nodes
            if isinstance(node, LITERAL_TYPE_NODES):
                msg = node.astext()
            else:
                msg = node.rawsource or node.astext()
            if msg:
                yield node, msg

            # extract message from image nodes
            for img in node.findall(IMAGE_TYPE_NODES):
                for attr in ('alt', 'title'):
                    val = img.get(attr, '')
                    if val:
                        yield img, val

def traverse_translatable_index(doctree: Element) -> Iterable[tuple[Element, list[tuple[str, str, str, str, str | None]]]]:
    """Traverse translatable index node from a document tree."""
    for node in doctree.findall(addnodes.index):
        if 'raw_entries' in node:
            entries = node['raw_entries']
        else:
            entries = node['entries']
        yield node, entries

def nested_parse_with_titles(state: RSTState, content: StringList, node: Node, content_offset: int=0) -> str:
    """Version of state.nested_parse() that allows titles and does not require
    titles to have the same decoration as the calling document.

    This is useful when the parsed content comes from a completely different
    context, such as docstrings.

    This function is retained for compatibility and will be deprecated in
    Sphinx 8. Prefer ``nested_parse_to_nodes()``.
    """
    with _fresh_title_style_context(state):
        state.nested_parse(content, content_offset, node)
    return ''

def clean_astext(node: Element) -> str:
    """Like node.astext(), but ignore images."""
    node_copy = node.deepcopy()
    for img in node_copy.findall(nodes.image):
        img.parent.remove(img)
    return node_copy.astext()

def split_explicit_title(text: str) -> tuple[bool, str, str]:
    """Split role content into title and target, if given."""
    match = explicit_title_re.match(text)
    if match:
        return True, match.group(1), match.group(2)
    return False, text, text
indextypes = ['single', 'pair', 'double', 'triple', 'see', 'seealso']

def inline_all_toctrees(builder: Builder, docnameset: set[str], docname: str, tree: nodes.document, colorfunc: Callable[[str], str], traversed: list[str], indent: str='') -> nodes.document:
    """Inline all toctrees in the *tree*.

    Record all docnames in *docnameset*, and output docnames with *colorfunc*.
    """
    tree = tree.deepcopy()
    for toctreenode in tree.findall(addnodes.toctree):
        newnodes = []
        includefiles = map(str, toctreenode['includefiles'])
        for includefile in includefiles:
            if includefile not in traversed:
                try:
                    traversed.append(includefile)
                    logger.info(colorfunc(includefile) + indent)
                    subtree = inline_all_toctrees(builder, docnameset, includefile,
                                                builder.env.get_doctree(includefile),
                                                colorfunc, traversed,
                                                indent + '   ')
                    docnameset.add(includefile)
                except Exception:
                    logger.warning(__('toctree contains ref to nonexisting file %r'),
                                 includefile, location=docname)
                else:
                    sof = addnodes.start_of_file(docname=includefile)
                    sof.children = subtree.children
                    newnodes.append(sof)
        toctreenode.parent.replace(toctreenode, newnodes)
    return tree

def _make_id(string: str) -> str:
    """Convert `string` into an identifier and return it.

    This function is a modified version of ``docutils.nodes.make_id()`` of
    docutils-0.16.

    Changes:

    * Allow to use capital alphabet characters
    * Allow to use dots (".") and underscores ("_") for an identifier
      without a leading character.

    # Author: David Goodger <goodger@python.org>
    # Maintainer: docutils-develop@lists.sourceforge.net
    # Copyright: This module has been placed in the public domain.
    """
    id = string.translate(_non_id_translate_digraphs)
    id = id.translate(_non_id_translate)
    id = unicodedata.normalize('NFKD', id).encode('ascii', 'ignore').decode('ascii')
    id = _non_id_chars.sub('-', id)
    id = _non_id_at_ends.sub('', id)
    return id
_non_id_chars = re.compile('[^a-zA-Z0-9._]+')
_non_id_at_ends = re.compile('^[-0-9._]+|-+$')
_non_id_translate = {248: 'o', 273: 'd', 295: 'h', 305: 'i', 322: 'l', 359: 't', 384: 'b', 387: 'b', 392: 'c', 396: 'd', 402: 'f', 409: 'k', 410: 'l', 414: 'n', 421: 'p', 427: 't', 429: 't', 436: 'y', 438: 'z', 485: 'g', 549: 'z', 564: 'l', 565: 'n', 566: 't', 567: 'j', 572: 'c', 575: 's', 576: 'z', 583: 'e', 585: 'j', 587: 'q', 589: 'r', 591: 'y'}
_non_id_translate_digraphs = {223: 'sz', 230: 'ae', 339: 'oe', 568: 'db', 569: 'qp'}

def make_id(env: BuildEnvironment, document: nodes.document, prefix: str='', term: str | None=None) -> str:
    """Generate an appropriate node_id for given *prefix* and *term*."""
    if prefix:
        id_prefix = _make_id(prefix)
        if term:
            id_suffix = _make_id(term)
        else:
            id_suffix = None
    else:
        id_prefix = _make_id(term) if term else ''
        id_suffix = None

    if id_prefix:
        if id_suffix:
            new_id = f'{id_prefix}-{id_suffix}'
        else:
            new_id = id_prefix
    else:
        new_id = id_suffix if id_suffix else ''

    i = 0
    while new_id + (str(i) if i else '') in document.ids:
        i += 1
    if i:
        new_id += str(i)

    document.ids[new_id] = True
    return new_id

def find_pending_xref_condition(node: addnodes.pending_xref, condition: str) -> Element | None:
    """Pick matched pending_xref_condition node up from the pending_xref."""
    for subnode in node:
        if isinstance(subnode, addnodes.pending_xref_condition):
            if subnode['condition'] == condition:
                return subnode
    return None

def make_refnode(builder: Builder, fromdocname: str, todocname: str, targetid: str | None, child: Node | list[Node], title: str | None=None) -> nodes.reference:
    """Shortcut to create a reference node."""
    node = nodes.reference('', '', internal=True)
    if fromdocname == todocname and targetid:
        node['refid'] = targetid
    else:
        if targetid:
            node['refuri'] = (builder.get_relative_uri(fromdocname, todocname) +
                            '#' + targetid)
        else:
            node['refuri'] = builder.get_relative_uri(fromdocname, todocname)
    if title:
        node['reftitle'] = title
    if isinstance(child, list):
        node.extend(child)
    else:
        node.append(child)
    return node
NON_SMARTQUOTABLE_PARENT_NODES = (nodes.FixedTextElement, nodes.literal, nodes.math, nodes.image, nodes.raw, nodes.problematic, addnodes.not_smartquotable)

def is_smartquotable(node: Node) -> bool:
    """Check whether the node is smart-quotable or not."""
    for ancestor in node.traverse(ascending=True, include_self=True):
        if isinstance(ancestor, NON_SMARTQUOTABLE_PARENT_NODES):
            return False
    return True

def process_only_nodes(document: Node, tags: Tags) -> None:
    """Filter ``only`` nodes which do not match *tags*."""
    for node in document.findall(addnodes.only):
        try:
            ret = _only_node_keep_children(node, tags)
        except Exception as err:
            logger.warning(__('exception while evaluating only directive expression: %s'), err,
                         location=node)
            node.replace_self(node.children or [])
        else:
            if ret:
                node.replace_self(node.children or [])
            else:
                # A failing condition removes that node and its children
                node.parent.remove(node)

def _only_node_keep_children(node: addnodes.only, tags: Tags) -> bool:
    """Keep children if tags match or error."""
    if node.get('expr') in (None, ''):
        # A blank condition should always fail
        return False
    return tags.eval_condition(node['expr'])

def _copy_except__document(el: Element) -> Element:
    """Monkey-patch ```nodes.Element.copy``` to not copy the ``_document``
    attribute.

    xref: https://github.com/sphinx-doc/sphinx/issues/11116#issuecomment-1376767086
    """
    newel = el.__class__()
    for attr in el.attlist():
        if attr != '_document':
            setattr(newel, attr, getattr(el, attr))
    return newel
nodes.Element.copy = _copy_except__document

def get_node_line(node: Node) -> int:
    """Get the line number of a node."""
    source = node.get('source')
    if source and ':' in source:
        return int(source.split(':', 1)[1])
    return 0

def is_translatable(node: Node) -> bool:
    """Check the node is translatable."""
    if isinstance(node, nodes.TextElement):
        if not node.source:
            return False
        if isinstance(node, IGNORED_NODES):
            return False
        if not node.get('translatable', True):
            return False
        return True

    return False

def apply_source_workaround(node: Node) -> None:
    """Apply a workaround for source-attributes of nodes.

    Docutils appends a line number to the source-attribute of nodes if possible.
    Some builders don't want the line number in the source-attribute.
    This function removes the line number.
    """
    try:
        source = node.get('source')
        if source and ':' in source:
            node['source'] = source.split(':', 1)[0]
    except Exception:
        pass

def _deepcopy(el: Element) -> Element:
    """Monkey-patch ```nodes.Element.deepcopy``` for speed."""
    copy = el.copy()
    copy.children = [child.deepcopy() for child in el.children]
    for child in copy.children:
        child.parent = copy
    return copy
nodes.Element.deepcopy = _deepcopy