from __future__ import annotations

import argparse
from typing import List, Optional

from .core import FORMATS, normalizePathString


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project a path string into another path convention.")
    parser.add_argument("pathstr", help="path string to project")
    parser.add_argument(
        "--fmt",
        choices=FORMATS,
        default=None,
        help="target format; default is runtime-native and Python-literal-safe",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    print(normalizePathString(args.pathstr, args.fmt))
    return 0
