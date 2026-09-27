# mkv-lister

Ein kleines Python3-Kommandozeilentool, das alle `.mkv`-Dateien in einem angegebenen Ordner auflistet.

A small Python3 command-line tool that lists all `.mkv` files in a given folder.

## Features

- Listet alle `.mkv`-Dateien (case-insensitive, also auch `.MKV`) in einem Ordner auf
- Optional rekursive Suche in Unterordnern (`-r` / `--recursive`)
- Alphabetisch sortierte Ausgabe
- Optionaler CSV-Export (`--csv`) mit Pfad, Dateiname, Jahr und Größe
- Saubere Fehlermeldungen bei nicht existierendem Pfad oder wenn der Pfad kein Ordner ist
- 100 % Testabdeckung (Zeilen und Branches)

## Voraussetzungen

- Python >= 3.9

## Installation

Im Projektverzeichnis:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Dadurch wird das Paket installiert und der Befehl `mkv-lister` steht zur Verfügung. Die `dev`-Extras installieren zusätzlich `pytest` und `pytest-cov` für die Tests.

## Verwendung

```bash
mkv-lister /pfad/zum/ordner
```

Rekursiv, inklusive aller Unterordner:

```bash
mkv-lister /pfad/zum/ordner --recursive
# oder kurz:
mkv-lister /pfad/zum/ordner -r
```

Alternativ ohne Installation direkt als Modul:

```bash
python3 -m mkv_lister.cli /pfad/zum/ordner
```

### Beispielausgabe

```
$ mkv-lister ~/Videos
/Users/kolja/Videos/film1.mkv
/Users/kolja/Videos/film2.mkv
```

Wenn keine Dateien gefunden werden:

```
$ mkv-lister ~/Videos/leer
Keine .mkv-Dateien gefunden.
```

Bei einem ungültigen Pfad (Exit-Code `1`, Fehlermeldung auf `stderr`):

```
$ mkv-lister /pfad/existiert/nicht
Fehler: Der Ordner '/pfad/existiert/nicht' existiert nicht.
```

### CSV-Export

Mit `--csv <datei>` wird zusätzlich zur normalen Ausgabe eine CSV-Datei geschrieben:

```bash
mkv-lister /pfad/zum/ordner -r --csv ausgabe.csv
```

- Trennzeichen: `;`
- Kodierung: UTF-8
- Header: `Pfad;Dateiname;Jahr;Size`
  - **Pfad**: Ordner, der die Datei enthält (ohne Dateiname)
  - **Dateiname**: Dateiname ohne Endung und ohne eine im Namen in Klammern stehende Jahreszahl
  - **Jahr**: die Jahreszahl aus dem Dateinamen, ohne Klammern (leer, falls keine gefunden wurde)
  - **Size**: Dateigröße menschenlesbar formatiert (z.B. `1.44 GB`)

Beispiel für `/Filme/Argo/Argo (2012).mkv` (1.500.000 Bytes):

```csv
Pfad;Dateiname;Jahr;Size
/Filme/Argo;Argo;2012;1.43 MB
```

## Als Python-Bibliothek verwenden

```python
from mkv_lister import find_mkv_files

files = find_mkv_files("/pfad/zum/ordner", recursive=True)
for file in files:
    print(file)
```

`find_mkv_files` gibt eine sortierte Liste von `pathlib.Path`-Objekten zurück und wirft `FileNotFoundError` bzw. `NotADirectoryError`, falls der übergebene Pfad ungültig ist.

Für den CSV-Export steht ebenfalls `write_csv` zur Verfügung:

```python
from mkv_lister import find_mkv_files, write_csv

files = find_mkv_files("/pfad/zum/ordner", recursive=True)
write_csv(files, "ausgabe.csv")
```

## Projektstruktur

```
.
├── mkv_lister/
│   ├── __init__.py       # Paket-Exporte
│   ├── finder.py          # Kernlogik: Suche nach .mkv-Dateien
│   ├── csv_export.py       # CSV-Export: Jahr-/Namens-Parsing, Größenformatierung
│   └── cli.py                # Kommandozeilen-Interface
├── tests/
│   ├── test_finder.py
│   ├── test_csv_export.py
│   └── test_cli.py
├── conftest.py
├── pyproject.toml
└── README.md
```

## Tests & Coverage

Die Tests laufen mit `pytest` und `pytest-cov` und erzwingen 100 % Testabdeckung (`--cov-fail-under=100`, konfiguriert in `pyproject.toml`):

```bash
pytest
```

Die Konfiguration in `pyproject.toml` misst automatisch sowohl Zeilen- als auch Branch-Abdeckung für das Paket `mkv_lister` und zeigt fehlende Zeilen im Terminal an. Die Zeile `if __name__ == "__main__":` in `cli.py` ist per `# pragma: no cover` ausgenommen, da sie nur beim direkten Skriptaufruf greift und funktional bereits über den integrierten Modul-Aufruf-Test (`python -m mkv_lister.cli`) abgedeckt ist.

Für einen HTML-Bericht:

```bash
pytest --cov-report=html
open htmlcov/index.html
```

## Weiterführende Dokumentation / Further documentation

Ausführliche Dokumentation (Architektur, vollständige CLI- und API-Referenz, Testkonzept, Entwickler-Guide, FAQ) findet sich im Ordner [`docu/`](docu/README.md).

In-depth documentation (architecture, full CLI & API reference, testing strategy, developer guide, FAQ) lives in the [`docu/`](docu/README.md) folder.

## Lizenz

MIT
