"""Builder superclass for all builders."""
from __future__ import annotations
import os
import re
from datetime import datetime, timezone
from os import path
from typing import TYPE_CHECKING, NamedTuple
import babel.dates
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po
from sphinx.errors import SphinxError
from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.osutil import SEP, _last_modified_time, canon_path, relpath
if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import Iterator
    from typing import Protocol, TypeAlias
    from babel.core import Locale
    from sphinx.environment import BuildEnvironment

    class DateFormatter(Protocol):

        def __call__(self, date: dt.date | None=..., format: str=..., locale: str | Locale | None=...) -> str:
            ...

    class TimeFormatter(Protocol):

        def __call__(self, time: dt.time | dt.datetime | float | None=..., format: str=..., tzinfo: dt.tzinfo | None=..., locale: str | Locale | None=...) -> str:
            ...

    class DatetimeFormatter(Protocol):

        def __call__(self, datetime: dt.date | dt.time | float | None=..., format: str=..., tzinfo: dt.tzinfo | None=..., locale: str | Locale | None=...) -> str:
            ...
    Formatter: TypeAlias = DateFormatter | TimeFormatter | DatetimeFormatter
logger = logging.getLogger(__name__)

class LocaleFileInfoBase(NamedTuple):
    base_dir: str
    domain: str
    charset: str

class CatalogInfo(LocaleFileInfoBase):
    pass

class CatalogRepository:
    """A repository for message catalogs."""

    def __init__(self, basedir: str | os.PathLike[str], locale_dirs: list[str], language: str, encoding: str) -> None:
        self.basedir = basedir
        self._locale_dirs = locale_dirs
        self.language = language
        self.encoding = encoding

def docname_to_domain(docname: str, compaction: bool | str) -> str:
    """Convert docname to domain for catalogs."""
    if not compaction:
        return docname

    if isinstance(compaction, str):
        return compaction

    parts = [part for part in docname.split(SEP) if part]
    if len(parts) > 2:
        return '-'.join(parts[:2])
    else:
        return docname

def format_date(date_str: str | None=None, format: str='%b %d, %Y', language: str | None=None) -> str:
    """Format a date according to the given format and language."""
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return date_str
    else:
        date = datetime.now(timezone.utc).date()

    try:
        result = babel.dates.format_date(date, format=format, locale=language)
    except (ValueError, babel.core.UnknownLocaleError):
        result = babel.dates.format_date(date, format=format)
    return result
date_format_mappings = {'%a': 'EEE', '%A': 'EEEE', '%b': 'MMM', '%B': 'MMMM', '%c': 'medium', '%-d': 'd', '%d': 'dd', '%-H': 'H', '%H': 'HH', '%-I': 'h', '%I': 'hh', '%-j': 'D', '%j': 'DDD', '%-m': 'M', '%m': 'MM', '%-M': 'm', '%M': 'mm', '%p': 'a', '%-S': 's', '%S': 'ss', '%U': 'WW', '%w': 'e', '%-W': 'W', '%W': 'WW', '%x': 'medium', '%X': 'medium', '%y': 'YY', '%Y': 'yyyy', '%Z': 'zzz', '%z': 'ZZZ', '%%': '%'}
date_format_re = re.compile('(%s)' % '|'.join(date_format_mappings))