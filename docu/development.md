# Development Guide

## Requirements

- Python >= 3.9 (per `requires-python` in `pyproject.toml`)
- No runtime dependencies beyond the standard library
- Dev-only dependencies: `pytest>=7`, `pytest-cov>=4`

## Setting up a local environment

```bash
git clone <repo-url>
cd entiretest
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

`pip install -e ".[dev]"` installs the package in editable mode (so code changes
take effect immediately, without reinstalling) plus the `dev` extras (`pytest`,
`pytest-cov`). It also registers the `mkv-lister` console script inside the
virtual environment.

Verify the setup:

```bash
mkv-lister --help
pytest
```

## Project layout

```
.
├── mkv_lister/            # the installable package
│   ├── __init__.py         # public API surface: exports find_mkv_files, __version__
│   ├── finder.py            # core filesystem-search logic (no CLI/argparse concerns)
│   └── cli.py                # argparse-based CLI, exit codes, stdout/stderr formatting
├── tests/
│   ├── test_finder.py
│   └── test_cli.py
├── docu/                   # this documentation folder
├── conftest.py             # empty; present so pytest reliably resolves imports
│                           #   without requiring the package to be pre-installed
├── pyproject.toml           # packaging, console script, pytest & coverage config
├── .gitignore
└── README.md                # bilingual (DE/EN) quick-start
```

See [architecture.md](architecture.md) for the reasoning behind this split.

## Making changes

1. Create a branch for your change.
2. Make the change in `mkv_lister/`.
3. Add or update tests in `tests/` — the project enforces **100% line and branch
   coverage** (see [testing.md](testing.md)), so any new code path needs a test
   that exercises it.
4. Run the full suite locally:

   ```bash
   pytest
   ```

   A failing coverage threshold (`Required test coverage of 100%... FAILED`) means
   some new line or branch isn't exercised by any test — add a test rather than
   lowering the threshold.
5. Update documentation if behavior changed:
   - [`README.md`](../README.md) for user-facing quick-start changes.
   - [`docu/cli-reference.md`](cli-reference.md) for CLI flag/output/exit-code
     changes.
   - [`docu/api-reference.md`](api-reference.md) for changes to
     `find_mkv_files`'s signature, return value, or raised exceptions.
   - [`docu/architecture.md`](architecture.md) for structural or design changes.

## Coding conventions

- Standard library only for runtime code — do not add a runtime dependency without
  a strong reason; this project's simplicity is a feature.
- Prefer `pathlib.Path` over raw string path manipulation.
- Raise standard built-in exceptions (`FileNotFoundError`, `NotADirectoryError`,
  etc.) instead of introducing custom exception classes, unless a genuinely new
  error condition can't be expressed by an existing built-in.
- Keep `finder.py` free of `print()`, `sys.exit()`, or any other CLI/process
  concerns — those belong exclusively in `cli.py`.
- Match existing code style: type hints on public functions, `from __future__
  import annotations`, docstrings on public functions using the existing
  Args/Raises format.

## Releasing a new version

1. Bump `version` in `pyproject.toml` (`[project]` section) following
   [SemVer](https://semver.org/).
2. Update `__version__` in [`mkv_lister/__init__.py`](../mkv_lister/__init__.py)
   to match.
3. Ensure `pytest` passes with 100% coverage.
4. Tag the release in git and push the tag.

There is currently no automated publishing (e.g. to PyPI) configured; releases are
consumed via `pip install -e .` / `pip install .` directly from the repository, or
via `python -m build` to produce a wheel/sdist locally if a package artifact is
needed.

## Troubleshooting

**`ModuleNotFoundError: No module named 'mkv_lister'` when running `pytest`**
Make sure you've run `pip install -e ".[dev]"` inside an activated virtual
environment, or that you're running `pytest` from the repository root (the empty
root-level `conftest.py` ensures pytest adds the repo root to `sys.path`, but this
still requires invoking pytest from — or below — that root).

**Coverage fails at less than 100% after adding a new branch**
Add a test that takes the untaken branch. Run `pytest --cov-report=html` and open
`htmlcov/index.html` to see exactly which lines/branches are uncovered, per file.

**`mkv-lister: command not found` after installing**
Confirm the virtual environment is activated (`source .venv/bin/activate`) and
that `pip install -e ".[dev]"` completed without errors.
