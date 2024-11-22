"""Pattern-matching utility functions for Sphinx."""
from __future__ import annotations
import os.path
import re
from typing import TYPE_CHECKING
from sphinx.util.osutil import canon_path, path_stabilize
if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator

def compile_matchers(patterns: list[str]) -> list[Callable[[str], bool]]:
    """Convert a list of glob patterns to a list of functions that match paths."""
    return [lambda x, pat=pat: bool(patmatch(x, pat)) for pat in patterns]

def _translate_pattern(pat: str) -> str:
    """Translate a shell-style glob pattern to a regular expression.

    Adapted from the fnmatch module, but enhanced so that single stars don't
    match slashes.
    """
    i, n = 0, len(pat)
    res = []
    while i < n:
        c = pat[i]
        i += 1
        if c == '*':
            if i < n and pat[i] == '*':
                # double star matches slashes too
                i += 1
                res.append('.*')
            else:
                # single star doesn't match slashes
                res.append('[^/]*')
        elif c == '?':
            # question mark doesn't match slashes
            res.append('[^/]')
        elif c == '[':
            j = i
            if j < n and pat[j] == '!':
                j += 1
            if j < n and pat[j] == ']':
                j += 1
            while j < n and pat[j] != ']':
                j += 1
            if j >= n:
                res.append('\\[')
            else:
                stuff = pat[i:j].replace('\\', '\\\\')
                i = j + 1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elif stuff[0] == '^':
                    stuff = '\\' + stuff
                res.append('[%s]' % stuff)
        else:
            res.append(re.escape(c))
    res.append('$')
    return ''.join(res)

class Matcher:
    """A pattern matcher for Multiple shell-style glob patterns.

    Note: this modifies the patterns to work with copy_asset().
          For example, "**/index.rst" matches with "index.rst"
    """

    def __init__(self, exclude_patterns: Iterable[str]) -> None:
        expanded = [pat[3:] for pat in exclude_patterns if pat.startswith('**/')]
        self.patterns = compile_matchers(list(exclude_patterns) + expanded)

    def __call__(self, string: str) -> bool:
        return self.match(string)

    def match(self, string: str) -> bool:
        """Return if string matches any of the patterns."""
        return any(pat(string) for pat in self.patterns)
DOTFILES = Matcher(['**/.*'])
_pat_cache: dict[str, re.Pattern[str]] = {}

def patmatch(name: str, pat: str) -> re.Match[str] | None:
    """Return if name matches the regular expression (pattern)
    ``pat```. Adapted from fnmatch module.
    """
    if pat not in _pat_cache:
        _pat_cache[pat] = re.compile(_translate_pattern(pat))
    return _pat_cache[pat].match(name)

def patfilter(names: Iterable[str], pat: str) -> list[str]:
    """Return the subset of the list ``names`` that match
    the regular expression (pattern) ``pat``.

    Adapted from fnmatch module.
    """
    return [name for name in names if patmatch(name, pat)]

def get_matching_files(dirname: str | os.PathLike[str], include_patterns: Iterable[str]=('**',), exclude_patterns: Iterable[str]=()) -> Iterator[str]:
    """Get all file names in a directory, recursively.

    Filter file names by the glob-style include_patterns and exclude_patterns.
    The default values include all files ("**") and exclude nothing ("").

    Only files matching some pattern in *include_patterns* are included, and
    exclusions from *exclude_patterns* take priority over inclusions.

    """
    dirname = os.fspath(dirname)
    if not os.path.isdir(dirname):
        return

    # normalize patterns
    include_patterns = [path_stabilize(pat) for pat in include_patterns]
    exclude_patterns = [path_stabilize(pat) for pat in exclude_patterns]

    for root, _dirs, files in os.walk(dirname):
        reldir = canon_path(os.path.relpath(root, dirname))
        for filename in files:
            relpath = canon_path(os.path.join(reldir, filename))
            if any(patmatch(relpath, pat) for pat in exclude_patterns):
                continue
            if any(patmatch(relpath, pat) for pat in include_patterns):
                yield relpath