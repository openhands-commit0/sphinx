from __future__ import annotations

def _split_into(n: int, type: str, value: str) -> list[str]:
    """Split an index entry into a given number of parts at semicolons."""
    parts = [x.strip() for x in value.split(';', n - 1)]
    if len(parts) < n:
        msg = f'index {type} should be separated by {n - 1} semicolons: {value!r}'
        raise ValueError(msg)
    return parts

def split_index_msg(type: str, value: str) -> tuple[str, str, str, str, str]:
    """Split a node's index entry into its components."""
    return tuple(_split_into(5, type, value))  # type: ignore