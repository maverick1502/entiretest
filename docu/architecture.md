# Architecture

## Overview

mkv-lister is intentionally small: one package with a few modules, a thin CLI layer
on top of pure library functions. The split exists so the core logic can be used
programmatically (imported into other Python code) independently of the
command-line interface.

```
┌─────────────────────────────┐
│         cli.py              │   argument parsing, process exit codes,
│  build_parser() / main()    │   stdout / stderr formatting
└──────┬───────────────┬───────┘
       │ calls          │ calls
       ▼                ▼
┌───────────────┐  ┌─────────────────┐
│  finder.py     │  │  csv_export.py   │   pure, side-effect-free (besides
│ find_mkv_files │  │    write_csv     │   reading the filesystem / writing
└──────┬─────────┘  └────────┬─────────┘   the destination CSV) logic
       │ uses                │ uses
       ▼                     ▼
    pathlib.Path / os.walk   csv (stdlib) / re
```

## Module responsibilities

### `mkv_lister/finder.py`

Contains the single public function `find_mkv_files(directory, recursive=False)`.
This is the core of the project and has no knowledge of the CLI, `argparse`, or
`stdout`/`stderr`. It:

1. Validates that `directory` exists and is a directory, raising standard Python
   exceptions (`FileNotFoundError`, `NotADirectoryError`) rather than inventing
   custom exception types — this keeps the library idiomatic and lets callers use
   normal `try/except` patterns they already know.
2. Walks the filesystem — either only the top level (`directory.iterdir()`) or
   recursively (`os.walk`) — depending on the `recursive` flag.
3. Filters entries to files whose suffix matches `.mkv`, case-insensitively.
4. Returns a case-insensitively sorted `list[Path]`.

See [api-reference.md](api-reference.md) for the full contract.

### `mkv_lister/csv_export.py`

Contains `write_csv(files, destination)` plus two internal helpers,
`parse_filename(stem)` and `format_size(num_bytes)`. Like `finder.py`, this module
has no knowledge of the CLI — it takes an iterable of `Path`s and a destination
`Path`, and writes a CSV file. It:

1. For each file, separates a parenthesized 4-digit year (if present) from the
   rest of the filename via a regular expression (`parse_filename`).
2. Formats the file's size in human-readable form (`format_size`), using
   1024-based units.
3. Writes one row per file to `destination` using the standard library's `csv`
   module with `;` as the delimiter and UTF-8 encoding.

See [api-reference.md](api-reference.md#write_csvfiles-destination) for the full
contract.

### `mkv_lister/cli.py`

Contains `build_parser()` and `main(argv=None)`. This module is the only place that
knows about `argparse`, process exit codes, and printing. It:

1. Builds an `argparse.ArgumentParser` with a positional `directory` argument, an
   optional `-r` / `--recursive` flag, and an optional `--csv FILE` flag.
2. Calls `find_mkv_files()` and translates its outcome into terminal-friendly
   behavior:
   - Success with results → one path per line on `stdout`, exit code `0`.
   - Success with no results → a human-readable "no files found" message on
     `stdout`, exit code `0`.
   - `FileNotFoundError` / `NotADirectoryError` → a prefixed error message on
     `stderr`, exit code `1`.
3. If `--csv FILE` was given, calls `write_csv()` with the same file list and
   prints a confirmation line, or — if writing fails (`OSError`) — a prefixed
   error message on `stderr` and exit code `1`.
4. Exposes a `if __name__ == "__main__":` guard so the module can be run directly
   via `python -m mkv_lister.cli`, in addition to the installed `mkv-lister`
   console script.

See [cli-reference.md](cli-reference.md) for the full contract.

### `mkv_lister/__init__.py`

Re-exports `find_mkv_files` and `write_csv` at the package level (`from
mkv_lister import find_mkv_files, write_csv`) and defines `__version__`. This is
the intended import surface for library consumers — internal module layout
(`mkv_lister.finder`, `mkv_lister.csv_export`) is not part of the public API and
may change.

## Design decisions

**Why separate `finder.py` from `cli.py`?**
Keeping filesystem logic free of `print`/`sys.exit` calls makes it directly usable
as a library and directly unit-testable without capturing stdout or spawning
subprocesses.

**Why standard exceptions instead of custom ones?**
`FileNotFoundError` and `NotADirectoryError` are built-in, well-understood, and
already carry the right semantics. Introducing a custom exception hierarchy would
add a public API surface with no behavioral benefit for a tool this size.

**Why filter by suffix instead of `Path.glob("*.mkv")`?**
`Path.glob`'s case sensitivity depends on the underlying filesystem (case-sensitive
on most Linux filesystems, case-insensitive but case-preserving on default macOS/
Windows filesystems). Manually comparing `path.suffix.lower() == ".mkv"` gives
deterministic, cross-platform behavior — `.mkv` and `.MKV` are always both matched,
regardless of which OS or filesystem the tool runs on. This also makes the test
suite deterministic across machines.

**Why `os.walk` for the recursive case instead of `Path.rglob`?**
`os.walk` gives explicit access to the file list per directory, which is what's
needed for the suffix filter above; `rglob` would reintroduce the filesystem-
dependent case-sensitivity problem `glob` has.

**Why sort by `str(path).lower()`?**
Ensures stable, case-insensitive, human-friendly ordering in the CLI output,
regardless of the order the filesystem/OS returns directory entries in (which is
unspecified and platform-dependent).

**Why does the CSV's `Pfad` column exclude the filename?**
The CSV already has a dedicated `Dateiname` column; repeating the filename inside
`Pfad` as well would be redundant. Separating them also matches how media files
are commonly organized (one folder per title), so `Pfad` reflects the folder a
title lives in while `Dateiname` is the cleaned-up title itself.

**Why is `Size` formatted human-readable instead of as raw bytes?**
The CSV is meant to be opened and skimmed directly (e.g. in a spreadsheet), where
"1.44 GB" is immediately meaningful and "1548576000" is not. This is a deliberate
trade-off against direct numeric sortability/computation in the CSV — a consumer
that needs raw bytes should call `Path.stat().st_size` directly via the library
API instead of parsing the CSV.

**Why extract the year via a `\((\d{4})\)` regex instead of a more general parser?**
Requiring exactly four digits inside literal parentheses is a narrow, predictable
rule that reliably matches the common `Title (YYYY).mkv` naming convention while
avoiding false positives on other parenthesized content (e.g. `(Director's Cut)`,
`(Part 1)`). A more permissive date parser would risk misinterpreting non-year
numbers.

## Data flow for a typical invocation

```
$ mkv-lister ~/Videos -r
```

1. `cli.main(["~/Videos", "-r"])` is invoked (or, when run as a script, with
   `argv=None` and `sys.argv` is used).
2. `build_parser().parse_args(...)` produces `Namespace(directory=Path("~/Videos"),
   recursive=True)`.
3. `finder.find_mkv_files(Path("~/Videos"), recursive=True)` is called.
4. The function validates the path, walks the tree with `os.walk`, filters for
   `.mkv` files, and returns a sorted `list[Path]`.
5. `cli.main` prints each path on its own line and returns `0`.
6. The process exits with that return code.

## Dependencies

The package has **zero runtime dependencies** — only the Python standard library
(`argparse`, `os`, `pathlib`, `sys`). Development dependencies (`pytest`,
`pytest-cov`) are declared as an optional extra (`pip install -e ".[dev]"`) and are
not required to use the tool.
