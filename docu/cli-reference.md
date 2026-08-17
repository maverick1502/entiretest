# CLI Reference

## Synopsis

```
mkv-lister DIRECTORY [-r | --recursive]
```

Equivalent forms:

```bash
mkv-lister DIRECTORY [-r]
python3 -m mkv_lister.cli DIRECTORY [-r]
```

Both invoke the same `main()` function; the `mkv-lister` console script is
installed by `pip install -e .` (see [development.md](development.md)) via the
`[project.scripts]` entry point in `pyproject.toml`.

## Arguments

| Argument | Required | Description |
|---|---|---|
| `directory` | Yes | Path to the folder to search. May be relative or absolute. Parsed as a `pathlib.Path`. |

## Options

| Option | Short | Description |
|---|---|---|
| `--recursive` | `-r` | Also search all subdirectories, recursively. Without this flag, only the top level of `directory` is searched. |
| `--help` | `-h` | Show the auto-generated `argparse` help text and exit (exit code `0`). |

## Behavior

- Matching is **case-insensitive**: both `.mkv` and `.MKV` (and any other casing)
  are matched.
- A directory whose *name* ends in `.mkv` (e.g. a folder literally called
  `Season.mkv/`) is never itself listed — only regular files are matched.
- Output is **sorted alphabetically**, case-insensitively, one path per line.
- Paths are printed exactly as `pathlib.Path` renders them for the current OS
  (e.g. `/home/user/movie.mkv` on Linux/macOS, `C:\Users\user\movie.mkv` on
  Windows).

## Output & exit codes

| Scenario | stdout | stderr | Exit code |
|---|---|---|---|
| One or more `.mkv` files found | One absolute/relative path per line | — | `0` |
| No `.mkv` files found | `Keine .mkv-Dateien gefunden.` | — | `0` |
| `directory` does not exist | — | `Fehler: Der Ordner '<path>' existiert nicht.` | `1` |
| `directory` exists but is not a directory (e.g. it's a file) | — | `Fehler: '<path>' ist kein Ordner.` | `1` |
| Invalid arguments (e.g. missing `directory`) | — | `argparse` usage/error text | `2` (standard `argparse` behavior) |

> Note: The "no files found" and error messages are currently in German, matching
> the primary README. See [faq.md](faq.md#why-are-some-messages-in-german) for
> context, and [development.md](development.md) if you want to contribute
> localization.

## Examples

List files in a folder, non-recursively:

```bash
$ mkv-lister ~/Videos
/Users/kolja/Videos/film1.mkv
/Users/kolja/Videos/film2.mkv
```

Recursive search across all subfolders:

```bash
$ mkv-lister ~/Videos --recursive
/Users/kolja/Videos/film1.mkv
/Users/kolja/Videos/Series/S01E01.mkv
/Users/kolja/Videos/Series/S01E02.mkv
```

Empty result:

```bash
$ mkv-lister ~/Videos/empty
Keine .mkv-Dateien gefunden.
```

Non-existent path:

```bash
$ mkv-lister /no/such/folder
Fehler: Der Ordner '/no/such/folder' existiert nicht.
$ echo $?
1
```

Path exists but is a file, not a directory:

```bash
$ mkv-lister ~/Videos/film1.mkv
Fehler: '/Users/kolja/Videos/film1.mkv' ist kein Ordner.
$ echo $?
1
```

Piping output, e.g. counting files or feeding another tool:

```bash
mkv-lister ~/Videos -r | wc -l
mkv-lister ~/Videos -r | xargs -I{} mv {} /archive/
```

## Scripting notes

- Because output on `stdout` is one plain path per line with no extra decoration,
  it composes well with standard Unix tools (`wc`, `grep`, `xargs`, `while read`).
- Check the exit code (`$?` in shells) rather than parsing stdout to detect
  errors — error text is only ever written to `stderr`.
- The "no files found" message is printed on `stdout` with exit code `0` (this is
  not treated as an error condition), so scripts that only check the exit code
  should also inspect whether any lines were printed if they need to distinguish
  "found nothing" from "found something".
