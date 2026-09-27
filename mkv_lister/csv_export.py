"""CSV-Export für gefundene .mkv-Dateien."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Iterable, Tuple

CSV_DELIMITER = ";"
CSV_HEADER = ["Pfad", "Dateiname", "Jahr", "Size"]

_YEAR_PATTERN = re.compile(r"\((\d{4})\)")
_SIZE_UNITS = ("B", "KB", "MB", "GB", "TB", "PB")


def parse_filename(stem: str) -> Tuple[str, str]:
    """Trennt eine in Klammern stehende Jahreszahl vom restlichen Dateinamen.

    Args:
        stem: Dateiname ohne Endung (z.B. ``Path.stem``).

    Returns:
        Tupel ``(name_ohne_jahr, jahr)``. Ist keine Jahreszahl vorhanden, ist
        ``jahr`` ein leerer String und der Name bleibt unverändert (getrimmt).
    """
    match = _YEAR_PATTERN.search(stem)
    if not match:
        return stem.strip(), ""

    year = match.group(1)
    cleaned = stem[: match.start()] + stem[match.end() :]
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned, year


def format_size(num_bytes: int) -> str:
    """Formatiert eine Byte-Anzahl menschenlesbar (z.B. ``1.44 GB``)."""
    size = float(num_bytes)
    for unit in _SIZE_UNITS:
        if size < 1024.0:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} EB"


def write_csv(files: Iterable[Path], destination: Path) -> None:
    """Schreibt die übergebenen Dateien als CSV nach ``destination``.

    Spalten: ``Pfad;Dateiname;Jahr;Size``. ``Pfad`` ist der Ordner, der die
    Datei enthält (ohne Dateiname). ``Dateiname`` ist der Dateiname ohne
    Endung und ohne eine in Klammern stehende Jahreszahl. ``Size`` ist die
    Dateigröße menschenlesbar formatiert (z.B. ``1.44 GB``).
    """
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter=CSV_DELIMITER)
        writer.writerow(CSV_HEADER)
        for file in files:
            name, year = parse_filename(file.stem)
            size = format_size(file.stat().st_size)
            writer.writerow([str(file.parent), name, year, size])
