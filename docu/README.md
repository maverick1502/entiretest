# mkv-lister Documentation

This folder contains the comprehensive documentation for **mkv-lister**, a Python 3
command-line tool and library that lists `.mkv` files in a folder.

The top-level [README.md](../README.md) is a short, bilingual quick-start. This folder
goes deeper: architecture, full API/CLI reference, error behavior, testing strategy,
and a contributor guide.

## Contents

| Document | Description |
|---|---|
| [architecture.md](architecture.md) | How the project is structured, module responsibilities, and the design decisions behind them |
| [cli-reference.md](cli-reference.md) | Full command-line reference: arguments, flags, exit codes, output format |
| [api-reference.md](api-reference.md) | Using `mkv_lister` as a Python library: `find_mkv_files`, exceptions, types |
| [testing.md](testing.md) | Test strategy, how to run the suite, coverage requirements and configuration |
| [development.md](development.md) | Setting up a dev environment, project layout, coding conventions, release process |
| [faq.md](faq.md) | Frequently asked questions and troubleshooting |

## At a glance

```bash
pip install -e ".[dev]"
mkv-lister /path/to/folder --recursive
```

```python
from mkv_lister import find_mkv_files

files = find_mkv_files("/path/to/folder", recursive=True)
```

For installation and a minimal usage example, see the [project README](../README.md).
For everything else, start with [architecture.md](architecture.md).
