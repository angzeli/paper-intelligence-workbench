# Installation

Paper Intelligence Workbench is a local-first Python package with no runtime dependencies.

## Requirements

- Python 3.10 or newer.
- `pip` and `setuptools` for editable installation.
- `pytest` only when running the test suite.

## Editable Install

From the repository root:

```bash
python -m pip install -e ".[test]"
paperwb --help
```

This installs the `paperwb` console command and test dependency group.

## No-Install Usage

If dependency installation is not available, run the CLI from the repository root:

```bash
python -m paper_workbench.cli --help
python -m paper_workbench.cli validate-registry data/registries/example_papers.csv
```

## Verify The Install

```bash
python -c "import paper_workbench; print(paper_workbench.__version__)"
paperwb --help
python -m pytest -q
```

The printed package version should match the `version` value in `pyproject.toml`.

For a release-candidate workflow check that writes only to a temporary
directory:

```bash
python scripts/clean_room_install_check.py --quick
```

The script uses the current Python environment and `python -m
paper_workbench.cli`, so it also works before the console entry point is
installed.

## Local-Only Boundary

Installation does not configure cloud services, API keys, publisher scraping, PDF downloaders, or LLM APIs. SQLite indexes are local rebuildable caches under `.paperwb/` and should not be committed.

## Troubleshooting

- If `paperwb` is not found, use `python -m paper_workbench.cli ...` or check that the editable install ran in the active Python environment.
- If `pip install -e ".[test]"` cannot fetch packages, install local build/test tools first or use no-install CLI mode.
- If tests fail after running workflows, check for generated files outside ignored folders such as `scratch/` or `exports/`.
