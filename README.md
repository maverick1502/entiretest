# mkv-lister

Ein kleines Python3-Kommandozeilentool, das alle `.mkv`-Dateien in einem angegebenen Ordner auflistet.

## Features

- Listet alle `.mkv`-Dateien (case-insensitive, also auch `.MKV`) in einem Ordner auf
- Optional rekursive Suche in Unterordnern (`-r` / `--recursive`)
- Alphabetisch sortierte Ausgabe
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

## Als Python-Bibliothek verwenden

```python
from mkv_lister import find_mkv_files

files = find_mkv_files("/pfad/zum/ordner", recursive=True)
for file in files:
    print(file)
```

`find_mkv_files` gibt eine sortierte Liste von `pathlib.Path`-Objekten zurück und wirft `FileNotFoundError` bzw. `NotADirectoryError`, falls der übergebene Pfad ungültig ist.

## Projektstruktur

```
.
├── mkv_lister/
│   ├── __init__.py    # Paket-Exporte
│   ├── finder.py       # Kernlogik: Suche nach .mkv-Dateien
│   └── cli.py           # Kommandozeilen-Interface
├── tests/
│   ├── test_finder.py
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

## Lizenz

MIT
