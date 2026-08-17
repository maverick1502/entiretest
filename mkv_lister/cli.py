"""Kommandozeilen-Interface für mkv_lister."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .finder import find_mkv_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mkv-lister",
        description="Listet alle .mkv-Dateien in einem angegebenen Ordner auf.",
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Pfad zum zu durchsuchenden Ordner",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Auch Unterordner durchsuchen",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        files = find_mkv_files(args.directory, recursive=args.recursive)
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1

    if not files:
        print("Keine .mkv-Dateien gefunden.")
        return 0

    for file in files:
        print(file)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
