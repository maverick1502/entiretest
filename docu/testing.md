# Testing & Coverage

## Summary

- Test framework: [`pytest`](https://docs.pytest.org/)
- Coverage tool: [`pytest-cov`](https://pytest-cov.readthedocs.io/) (wraps
  [`coverage.py`](https://coverage.readthedocs.io/))
- Enforced threshold: **100% line and branch coverage** — the test run fails if
  coverage drops below that, via `--cov-fail-under=100` in `pyproject.toml`.
- Test files: [`tests/test_finder.py`](../tests/test_finder.py) and
  [`tests/test_cli.py`](../tests/test_cli.py).

## Running the tests

```bash
pytest
```

This single command runs the full suite and prints a coverage summary, because
coverage options are pre-configured in `pyproject.toml` under
`[tool.pytest.ini_options]`:

```toml
[tool.pytest.ini_options]
addopts = "--cov=mkv_lister --cov-report=term-missing --cov-fail-under=100"
testpaths = ["tests"]
```

Expected output looks like:

```
================================ tests coverage ================================
Name                     Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------
mkv_lister/__init__.py       3      0      0      0   100%
mkv_lister/cli.py           25      0      4      0   100%
mkv_lister/finder.py        16      0      6      0   100%
--------------------------------------------------------------------
TOTAL                       44      0     10      0   100%
Required test coverage of 100% reached. Total coverage: 100.00%
```

### HTML coverage report

For a browsable, line-by-line coverage report:

```bash
pytest --cov-report=html
open htmlcov/index.html   # macOS; use xdg-open on Linux, start on Windows
```

### Running a single test file or test

```bash
pytest tests/test_finder.py
pytest tests/test_cli.py::test_main_prints_found_files
```

Note that running a subset of tests may report coverage below 100% because
`--cov-fail-under=100` still applies to the whole `mkv_lister` package — this is
expected when filtering; run the full `pytest` invocation to get an accurate
pass/fail signal.

## Why 100% coverage, and how it's kept honest

Coverage percentage alone doesn't guarantee correctness, but it does guarantee
every line and every branch has been *exercised* at least once — which catches
entire classes of bugs (unreachable code, forgotten error paths, unimplemented
flags) cheaply. To keep the number meaningful rather than gamed:

- **Branch coverage is enabled** (`branch = true` in `[tool.coverage.run]`), not
  just line coverage — an `if`/`else` only counts as covered when both directions
  have been taken by some test.
- Coverage is scoped to the `mkv_lister` package only (`source = ["mkv_lister"]`),
  so test code itself isn't counted, and the number can't be inflated by
  irrelevant modules.
- Exactly one line is excluded via `# pragma: no cover`: the
  `if __name__ == "__main__":` guard in `cli.py`. This is standard Python practice
  — that branch is only taken when the module is executed directly, not when
  imported — and it is still exercised functionally by
  `test_cli.py::test_cli_runs_as_module`, which runs
  `python -m mkv_lister.cli` in a subprocess and asserts on its output and exit
  code. It's excluded from the *coverage measurement* (subprocess execution isn't
  visible to the coverage instrumentation of the parent test process) but not from
  *testing*.

## Test strategy

### `tests/test_finder.py`

Covers `find_mkv_files` in isolation, using `pytest`'s `tmp_path` fixture to create
real, ephemeral directory trees on disk (no mocking of the filesystem):

- Both exception paths: missing directory, path-is-a-file.
- Empty directory → empty list.
- Case-insensitive matching (`.mkv` and `.MKV` both found; `.mp4`/`.txt` excluded).
- Non-recursive search ignores files in subdirectories.
- Recursive search finds files at multiple nesting depths.
- A directory literally named `something.mkv` is never itself returned, in both
  recursive and non-recursive mode.
- Accepting a plain `str` path, not just `Path`.
- Deterministic alphabetical sort order.

### `tests/test_cli.py`

Covers `build_parser()` and `main()`:

- Argument parsing defaults (`recursive` defaults to `False`) and the `-r`/
  `--recursive` flag.
- `main()` printing found files to stdout with exit code `0`.
- `main()` printing the "no files found" message with exit code `0`.
- `main()` printing errors to stderr with exit code `1`, for both exception types.
- `main()` reading from `sys.argv` when called with `argv=None`
  (via `monkeypatch`).
- A true end-to-end subprocess test invoking `python -m mkv_lister.cli` to verify
  the module is runnable as a script, independent of the installed console
  script.

## Design choices that make the code easy to test

These are covered in more depth in [architecture.md](architecture.md), but from a
testing perspective, the key choices are:

- `find_mkv_files` is a pure function around real filesystem calls — no global
  state, no I/O beyond reading the given directory — so tests only need
  `tmp_path`, never mocking.
- `cli.main(argv)` accepts an explicit `argv` list instead of always reading
  `sys.argv`, so most CLI tests can call it directly with a list of strings rather
  than mutating global process state.
- Error handling raises standard exceptions instead of calling `sys.exit()`
  inside the library function, so `finder.py` tests can use plain
  `pytest.raises(...)` instead of capturing process exit behavior.

## Continuous verification

There is currently no CI workflow configured in this repository (no
`.github/workflows/`). If you add one, it should at minimum run:

```bash
pip install -e ".[dev]"
pytest
```

on the Python versions declared as supported (`requires-python = ">=3.9"` in
`pyproject.toml`). See [development.md](development.md) for local setup.
