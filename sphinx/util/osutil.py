"""Operating system-related utility functions for Sphinx."""
from __future__ import annotations
import contextlib
import filecmp
import os
import re
import shutil
import sys
import unicodedata
from io import StringIO
from os import path
from pathlib import Path
from typing import TYPE_CHECKING
from sphinx.locale import __
if TYPE_CHECKING:
    from types import TracebackType
    from typing import Any
SEP = '/'

def canon_path(native_path: str | os.PathLike[str], /) -> str:
    """Return path in OS-independent form"""
    return str(native_path).replace(os.path.sep, SEP)

def path_stabilize(filepath: str | os.PathLike[str], /) -> str:
    """Normalize path separator and unicode string"""
    filepath = str(filepath)
    filepath = unicodedata.normalize('NFC', filepath)
    return filepath.replace(os.path.sep, SEP)

def relative_uri(base: str, to: str) -> str:
    """Return a relative URL from ``base`` to ``to``."""
    if not base or not to:
        return to
    b2 = base.split(SEP)
    t2 = to.split(SEP)
    # remove common segments
    for x, y in zip(b2, t2):
        if x != y:
            break
        b2.pop(0)
        t2.pop(0)
    if not b2 and not t2:
        return ''
    return ('../' * (len(b2) - 1) + './' * bool(b2) +
            SEP.join(t2) + ('/' if to.endswith('/') else ''))

def ensuredir(file: str | os.PathLike[str]) -> None:
    """Ensure that a path exists."""
    path = os.path.dirname(os.fspath(file))
    if path and not os.path.exists(path):
        os.makedirs(path)

def _last_modified_time(source: str | os.PathLike[str], /) -> int:
    """Return the last modified time of ``filename``.

    The time is returned as integer microseconds.
    The lowest common denominator of modern file-systems seems to be
    microsecond-level precision.

    We prefer to err on the side of re-rendering a file,
    so we round up to the nearest microsecond.
    """
    st = os.stat(source)
    return int(st.st_mtime * 1_000_000)

def _copy_times(source: str | os.PathLike[str], dest: str | os.PathLike[str]) -> None:
    """Copy a file's modification times."""
    st = os.stat(source)
    os.utime(dest, (st.st_atime, st.st_mtime))

def copyfile(source: str | os.PathLike[str], dest: str | os.PathLike[str], *, force: bool=False) -> None:
    """Copy a file and its modification times, if possible.

    :param source: An existing source to copy.
    :param dest: The destination path.
    :param bool force: Overwrite the destination file even if it exists.
    :raise FileNotFoundError: The *source* does not exist.

    .. note:: :func:`copyfile` is a no-op if *source* and *dest* are identical.
    """
    source = os.fspath(source)
    dest = os.fspath(dest)

    if not os.path.exists(source):
        raise FileNotFoundError(source)
    if source == dest:
        return

    if os.path.exists(dest) and not force:
        if filecmp.cmp(source, dest, shallow=True):
            return
        msg = __('Cannot copy %r to %r: file exists') % (source, dest)
        raise OSError(msg)

    try:
        shutil.copyfile(source, dest)
        _copy_times(source, dest)
    except shutil.SameFileError:
        pass
_no_fn_re = re.compile('[^a-zA-Z0-9_-]')

def make_filename(string: str) -> str:
    """Convert string to a filename-friendly string."""
    return _no_fn_re.sub('', string)

def relpath(path: str | os.PathLike[str], start: str | os.PathLike[str] | None=os.curdir) -> str:
    """Return a relative filepath to *path* either from the current directory or
    from an optional *start* directory.

    This is an alternative of ``os.path.relpath()``.  This returns original path
    if *path* and *start* are on different drives (for Windows platform).
    """
    path = os.fspath(path)
    if start is None:
        start = os.curdir
    start = os.fspath(start)

    try:
        return os.path.relpath(path, start)
    except ValueError:
        # if on Windows, and path and start are on different drives, return original path
        if os.name == 'nt':
            return path
        raise
safe_relpath = relpath
fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
abspath = path.abspath
os_path = path

class _chdir:
    """Remove this fall-back once support for Python 3.10 is removed."""

    def __init__(self, target_dir: str, /) -> None:
        self.path = target_dir
        self._dirs: list[str] = []

    def __enter__(self) -> None:
        self._dirs.append(os.getcwd())
        os.chdir(self.path)

    def __exit__(self, type: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None, /) -> None:
        os.chdir(self._dirs.pop())
if sys.version_info[:2] < (3, 11):
    cd = _chdir

class FileAvoidWrite:
    """File-like object that buffers output and only writes if content changed.

    Use this class like when writing to a file to avoid touching the original
    file if the content hasn't changed. This is useful in scenarios where file
    mtime is used to invalidate caches or trigger new behavior.

    When writing to this file handle, all writes are buffered until the object
    is closed.

    Objects can be used as context managers.
    """

    def __init__(self, path: str | Path) -> None:
        self._path = path
        self._io: StringIO | None = None

    def close(self) -> None:
        """Stop accepting writes and write file, if needed."""
        if not self._io:
            return

        content = self._io.getvalue()
        self._io.close()
        self._io = None

        try:
            with open(self._path, 'r', encoding='utf-8') as f:
                original_content = f.read()
                if content == original_content:
                    return
        except Exception:
            pass

        with open(self._path, 'w', encoding='utf-8') as f:
            f.write(content)

    def __enter__(self) -> FileAvoidWrite:
        return self

    def __exit__(self, exc_type: type[Exception], exc_value: Exception, traceback: Any) -> bool:
        self.close()
        return True

    def __getattr__(self, name: str) -> Any:
        if not self._io:
            msg = 'Must write to FileAvoidWrite before other methods can be used'
            raise Exception(msg)
        return getattr(self._io, name)