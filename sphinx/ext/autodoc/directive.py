from __future__ import annotations
from collections.abc import Callable
from typing import TYPE_CHECKING, Any
from docutils import nodes
from docutils.statemachine import StringList
from docutils.utils import Reporter, assemble_option_dict
from sphinx.ext.autodoc import Documenter, Options
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective, switch_source_input
from sphinx.util.parsing import nested_parse_to_nodes
if TYPE_CHECKING:
    from docutils.nodes import Node
    from docutils.parsers.rst.states import RSTState
    from sphinx.config import Config
    from sphinx.environment import BuildEnvironment
logger = logging.getLogger(__name__)
AUTODOC_DEFAULT_OPTIONS = ['members', 'undoc-members', 'inherited-members', 'show-inheritance', 'private-members', 'special-members', 'ignore-module-all', 'exclude-members', 'member-order', 'imported-members', 'class-doc-from', 'no-value']
AUTODOC_EXTENDABLE_OPTIONS = ['members', 'private-members', 'special-members', 'exclude-members']

class DummyOptionSpec(dict[str, Callable[[str], str]]):
    """An option_spec allows any options."""

    def __bool__(self) -> bool:
        """Behaves like some options are defined."""
        return True

    def __getitem__(self, _key: str) -> Callable[[str], str]:
        return lambda x: x

class DocumenterBridge:
    """A parameters container for Documenters."""

    def __init__(self, env: BuildEnvironment, reporter: Reporter | None, options: Options, lineno: int, state: Any) -> None:
        self.env = env
        self._reporter = reporter
        self.genopt = options
        self.lineno = lineno
        self.record_dependencies: set[str] = set()
        self.result = StringList()
        self.state = state

def process_documenter_options(documenter: type[Documenter], config: Config, options: dict[str, str]) -> Options:
    """Recognize options of Documenter from user input."""
    pass

def parse_generated_content(state: RSTState, content: StringList, documenter: Documenter) -> list[Node]:
    """Parse an item of content generated by Documenter."""
    pass

class AutodocDirective(SphinxDirective):
    """A directive class for all autodoc directives. It works as a dispatcher of Documenters.

    It invokes a Documenter upon running. After the processing, it parses and returns
    the content generated by Documenter.
    """
    option_spec = DummyOptionSpec()
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True