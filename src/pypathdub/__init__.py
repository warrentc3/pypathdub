import sys

if sys.version_info < (3, 7):
    raise RuntimeError(
        f"pypathdub requires Python 3.7+; running {sys.version}"
    )

from .core import normalizePathString, normalize_path_string

__all__ = ["normalizePathString", "normalize_path_string"]
