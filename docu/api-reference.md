# API Reference

`mkv_lister` can be used as a library, independent of the CLI.

```python
from mkv_lister import find_mkv_files
```

This is the only supported public import. Internal module paths
(`mkv_lister.finder`, `mkv_lister.cli`) are implementation details and may change
between versions without notice.

---

## `find_mkv_files(directory, recursive=False)`

```python
def find_mkv_files(
    directory: str | Path,
    recursive: bool = False,
) -> list[Path]
```

Returns an alphabetically (case-insensitively) sorted list of `.mkv` files found in
`directory`.

### Parameters

| Name | Type | Default | Description |
|---|---|---|---|
| `directory` | `str \| pathlib.Path` | — (required) | The folder to search. Accepts either a string or a `Path`; it is converted internally via `Path(directory)`. |
| `recursive` | `bool` | `False` | If `True`, also searches all subdirectories, recursively, via `os.walk`. If `False`, only the immediate contents of `directory` are examined. |

### Returns

`list[pathlib.Path]` — one entry per matching file, sorted case-insensitively by
its string representation (`str(path).lower()`). Returns an empty list if no
matches are found — this is not an error condition.

### Raises

| Exception | Condition |
|---|---|
| `FileNotFoundError` | `directory` does not exist on the filesystem. Message: `Der Ordner '<directory>' existiert nicht.` |
| `NotADirectoryError` | `directory` exists but is not a directory (e.g. it's a regular file). Message: `'<directory>' ist kein Ordner.` |

Both exceptions are the standard library built-ins — no custom exception types are
used. They can be caught individually or together:

```python
try:
    files = find_mkv_files(path)
except (FileNotFoundError, NotADirectoryError) as exc:
    print(f"Cannot search {path}: {exc}")
```

### Matching rules

- Comparison is done on `path.suffix.lower() == ".mkv"`, so `.mkv`, `.MKV`, `.Mkv`,
  etc. are all matched, regardless of filesystem case-sensitivity.
- Only regular files are matched (`Path.is_file()` / `os.walk`'s `filenames` list).
  A directory whose name happens to end in `.mkv` is never included.
- When `recursive=False`, only direct children of `directory` are examined
  (`directory.iterdir()`); subdirectories are not entered.
- When `recursive=True`, the entire subtree is walked via `os.walk(directory)`.

### Examples

Basic, non-recursive usage:

```python
from pathlib import Path
from mkv_lister import find_mkv_files

files = find_mkv_files("/home/user/videos")
for f in files:
    print(f)
```

Recursive search, working with `Path` objects:

```python
from pathlib import Path
from mkv_lister import find_mkv_files

root = Path.home() / "Videos"
files = find_mkv_files(root, recursive=True)
print(f"Found {len(files)} .mkv files")
```

Handling an invalid path:

```python
from mkv_lister import find_mkv_files

try:
    files = find_mkv_files("/does/not/exist")
except FileNotFoundError as exc:
    print(f"Error: {exc}")
```

Filtering results further (e.g. by size), since the return value is plain
`pathlib.Path` objects:

```python
from mkv_lister import find_mkv_files

large_files = [
    f for f in find_mkv_files("/videos", recursive=True)
    if f.stat().st_size > 1_000_000_000  # > 1 GB
]
```

### Type stability & guarantees

- The function has no side effects beyond reading filesystem metadata (it never
  writes, moves, or deletes anything).
- The return type is always `list[Path]`, never `None`, even for zero matches.
- Sorting is deterministic for a given set of paths (ties are impossible since
  paths within one directory are unique).

---

## `mkv_lister.__version__`

```python
from mkv_lister import __version__
```

A `str` containing the current package version (kept in sync with the `version`
field in `pyproject.toml`).

---

## CLI-facing internals (not part of the public API)

`mkv_lister.cli` exposes `build_parser()` and `main(argv=None)`, used by the
console script and `python -m mkv_lister.cli`. These are documented for
completeness in [architecture.md](architecture.md) and [cli-reference.md](cli-reference.md),
but are not intended to be imported and used as a library API — prefer
`find_mkv_files` directly if you're integrating this into other Python code.
