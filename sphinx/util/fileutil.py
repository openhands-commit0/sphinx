"""File utility functions for Sphinx."""
from __future__ import annotations
import os
import posixpath
from typing import TYPE_CHECKING, Any
from docutils.utils import relative_path
from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.osutil import copyfile, ensuredir
if TYPE_CHECKING:
    from collections.abc import Callable
    from sphinx.util.template import BaseRenderer
    from sphinx.util.typing import PathMatcher
logger = logging.getLogger(__name__)

def _template_basename(filename: str | os.PathLike[str]) -> str | None:
    """Given an input filename:
    If the input looks like a template, then return the filename output should
    be written to.  Otherwise, return no result (None).
    """
    pass

def copy_asset_file(source: str | os.PathLike[str], destination: str | os.PathLike[str], context: dict[str, Any] | None=None, renderer: BaseRenderer | None=None, *, force: bool=False) -> None:
    """Copy an asset file to destination.

    On copying, it expands the template variables if context argument is given and
    the asset is a template file.

    :param source: The path to source file
    :param destination: The path to destination file or directory
    :param context: The template variables.  If not given, template files are simply copied
    :param renderer: The template engine.  If not given, SphinxRenderer is used by default
    :param bool force: Overwrite the destination file even if it exists.
    """
    pass

def copy_asset(source: str | os.PathLike[str], destination: str | os.PathLike[str], excluded: PathMatcher=lambda path: False, context: dict[str, Any] | None=None, renderer: BaseRenderer | None=None, onerror: Callable[[str, Exception], None] | None=None, *, force: bool=False) -> None:
    """Copy asset files to destination recursively.

    On copying, it expands the template variables if context argument is given and
    the asset is a template file.

    Use ``copy_asset_file`` instead to copy a single file.

    :param source: The path to source file or directory
    :param destination: The path to destination directory
    :param excluded: The matcher to determine the given path should be copied or not
    :param context: The template variables.  If not given, template files are simply copied
    :param renderer: The template engine.  If not given, SphinxRenderer is used by default
    :param onerror: The error handler.
    :param bool force: Overwrite the destination file even if it exists.
    """
    pass