# Architecture

## Overview

mkv-lister is intentionally small: one package with two modules, a thin CLI layer on
top of a pure library function. The split exists so the core logic can be used
programmatically (imported into other Python code) independently of the
command-line interface.

```
┌─────────────────────────────┐
│         cli.py              │   argument parsing, process exit codes,
│  build_parser() / main()    │   stdout / stderr formatting
└──────────────┬───────────────┘
               │ calls
               ▼
┌─────────────────────────────┐
│        finder.py            │   pure, side-effect-free (besides reading
│      find_mkv_files()       │   the filesystem) file discovery logic
└──────────────┬───────────────┘
               │ uses
               ▼
        pathlib.Path / os.walk
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

### `mkv_lister/cli.py`

Contains `build_parser()` and `main(argv=None)`. This module is the only place that
knows about `argparse`, process exit codes, and printing. It:

1. Builds an `argparse.ArgumentParser` with a positional `directory` argument and an
   optional `-r` / `--recursive` flag.
2. Calls `find_mkv_files()` and translates its outcome into terminal-friendly
   behavior:
   - Success with results → one path per line on `stdout`, exit code `0`.
   - Success with no results → a human-readable "no files found" message on
     `stdout`, exit code `0`.
   - `FileNotFoundError` / `NotADirectoryError` → a prefixed error message on
     `stderr`, exit code `1`.
3. Exposes a `if __name__ == "__main__":` guard so the module can be run directly
   via `python -m mkv_lister.cli`, in addition to the installed `mkv-lister`
   console script.

See [cli-reference.md](cli-reference.md) for the full contract.

### `mkv_lister/__init__.py`

Re-exports `find_mkv_files` at the package level (`from mkv_lister import
find_mkv_files`) and defines `__version__`. This is the intended import surface for
library consumers — internal module layout (`mkv_lister.finder`) is not part of the
public API and may change.

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
