# FAQ & Troubleshooting

## Usage

### Does mkv-lister modify, move, or delete any files?

No. It only reads directory listings and file metadata (to check `is_file()` /
`is_dir()` and file suffixes). It never writes, moves, renames, or deletes
anything. See [architecture.md](architecture.md#design-decisions).

### Does it match `.MKV` (uppercase) too?

Yes. Matching is case-insensitive by design, regardless of the operating system or
filesystem's own case-sensitivity rules. See
[api-reference.md](api-reference.md#matching-rules).

### What happens if I point it at a folder named `something.mkv`?

If `something.mkv` is itself a directory (not a file), it is never included in the
results — only regular files are matched, in both recursive and non-recursive
mode.

### Why does it print "Keine .mkv-Dateien gefunden." instead of nothing when there are no matches?

This is intentional, explicit feedback so a script or user isn't left wondering
whether the tool ran at all versus silently finding zero files. It's printed to
`stdout` with exit code `0` — it is not an error condition. See
[cli-reference.md](cli-reference.md#output--exit-codes).

### How do I use this from another Python script instead of the shell?

```python
from mkv_lister import find_mkv_files

files = find_mkv_files("/path/to/folder", recursive=True)
```

See the full [api-reference.md](api-reference.md).

### Can I search multiple folders at once?

Not directly as a single CLI invocation. Call `find_mkv_files` in a loop from
Python, or run the CLI once per folder from a shell script:

```bash
for dir in ~/Videos ~/Downloads; do
  mkv-lister "$dir" -r
done
```

## Why are some messages in German?

The project originated with a German-language README and error/status messages
(`Keine .mkv-Dateien gefunden.`, `Fehler: ...`). The top-level `README.md` now
includes an English description alongside the German one, and this `docu/` folder
is written in English, but the CLI's runtime output strings have not yet been
localized or made configurable. If you need English runtime output, either wrap
`find_mkv_files` in your own script with your own messages, or contribute
localization support — see [development.md](development.md#making-changes).

## Errors

### `Fehler: Der Ordner '<path>' existiert nicht.`

The path you passed does not exist on disk (from the perspective of the process
running `mkv-lister` — double-check relative paths and current working directory,
and any symlinks or mounted drives that might not be available in your current
shell/session).

### `Fehler: '<path>' ist kein Ordner.`

The path exists but is a file, not a directory. Point `mkv-lister` at the folder
*containing* the file instead.

### `argparse` usage error / exit code `2`

You likely omitted the required `directory` argument or passed an unrecognized
flag. Run `mkv-lister --help` to see the exact syntax.

## Installation & environment

### `ModuleNotFoundError: No module named 'mkv_lister'`

See [development.md#troubleshooting](development.md#troubleshooting).

### Which Python versions are supported?

Python 3.9 and later (`requires-python = ">=3.9"` in `pyproject.toml`).

### Does this work on Windows?

Yes — the implementation uses `pathlib.Path` and `os.walk` throughout, both of
which are cross-platform. Printed paths will use the native path separator for
the OS the tool runs on.

## Contributing

### I found a bug / want to add a feature — where do I start?

Read [architecture.md](architecture.md) for the design rationale, then
[development.md](development.md) for environment setup and coding conventions.
Every code change needs an accompanying test — the project enforces 100% coverage
(see [testing.md](testing.md)).
