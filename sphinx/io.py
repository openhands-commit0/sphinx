"""Input/Output files"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any
from docutils.core import Publisher
from docutils.io import FileInput, Input, NullOutput
from docutils.readers import standalone
from docutils.transforms.references import DanglingReferences
from docutils.writers import UnfilteredWriter
from sphinx import addnodes
from sphinx.transforms import AutoIndexUpgrader, DoctreeReadEvent, SphinxTransformer
from sphinx.transforms.i18n import Locale, PreserveTranslatableMessages, RemoveTranslatableInline
from sphinx.transforms.references import SphinxDomains
from sphinx.util import logging
from sphinx.util.docutils import LoggingReporter
from sphinx.versioning import UIDTransform
if TYPE_CHECKING:
    from docutils import nodes
    from docutils.frontend import Values
    from docutils.parsers import Parser
    from docutils.transforms import Transform
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment
logger = logging.getLogger(__name__)

class SphinxBaseReader(standalone.Reader):
    """
    A base class of readers for Sphinx.

    This replaces reporter by Sphinx's on generating document.
    """
    transforms: list[type[Transform]] = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        from sphinx.application import Sphinx
        if len(args) > 0 and isinstance(args[0], Sphinx):
            self._app = args[0]
            self._env = self._app.env
            args = args[1:]
        super().__init__(*args, **kwargs)

    def new_document(self) -> nodes.document:
        """
        Creates a new document object which has a special reporter object good
        for logging.
        """
        pass

class SphinxStandaloneReader(SphinxBaseReader):
    """
    A basic document reader for Sphinx.
    """

    def read_source(self, env: BuildEnvironment) -> str:
        """Read content from source and do post-process."""
        pass

class SphinxI18nReader(SphinxBaseReader):
    """
    A document reader for i18n.

    This returns the source line number of original text as current source line number
    to let users know where the error happened.
    Because the translated texts are partial and they don't have correct line numbers.
    """

class SphinxDummyWriter(UnfilteredWriter):
    """Dummy writer module used for generating doctree."""
    supported = ('html',)

def SphinxDummySourceClass(source: Any, *args: Any, **kwargs: Any) -> Any:
    """Bypass source object as is to cheat Publisher."""
    pass

class SphinxFileInput(FileInput):
    """A basic FileInput for Sphinx."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs['error_handler'] = 'sphinx'
        super().__init__(*args, **kwargs)