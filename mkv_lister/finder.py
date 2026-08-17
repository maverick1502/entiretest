"""Kernlogik zum Auffinden von .mkv-Dateien in einem Ordner."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Union

MKV_SUFFIX = ".mkv"


def find_mkv_files(directory: Union[str, Path], recursive: bool = False) -> List[Path]:
    """Gibt eine alphabetisch sortierte Liste aller .mkv-Dateien in ``directory`` zurück.

    Args:
        directory: Pfad zu dem zu durchsuchenden Ordner.
        recursive: Falls True, werden auch Unterordner durchsucht.

    Raises:
        FileNotFoundError: Wenn der angegebene Ordner nicht existiert.
        NotADirectoryError: Wenn der angegebene Pfad kein Ordner ist.
    """
    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Der Ordner '{directory}' existiert nicht.")
    if not directory.is_dir():
        raise NotADirectoryError(f"'{directory}' ist kein Ordner.")

    if recursive:
        candidates = (
            Path(root) / name
            for root, _dirnames, filenames in os.walk(directory)
            for name in filenames
        )
    else:
        candidates = (entry for entry in directory.iterdir() if entry.is_file())

    matches = [path for path in candidates if path.suffix.lower() == MKV_SUFFIX]
    return sorted(matches, key=lambda path: str(path).lower())
