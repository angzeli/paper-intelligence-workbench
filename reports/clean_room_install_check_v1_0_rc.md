# Clean-room Install Check v1.0-rc

This check runs in the current Python environment and writes generated files to a temporary directory.
It does not create a virtual environment, publish packages, call network services, or modify checked-in examples.

Temporary output directory: `<temporary directory>`
Steps run: 16
Failures: 0

| Step | Result | Command |
| --- | --- | --- |
| import package | pass | `python -c import paper_workbench; print(paper_workbench.__version__)` |
| CLI help | pass | `python -m paper_workbench.cli --help` |
| initialize temp workspace | pass | `python -m paper_workbench.cli init --root <temporary directory>/clean_workspace` |
| create temp project | pass | `python -m paper_workbench.cli project init rc_demo --description Synthetic RC demo` |
| list temp projects | pass | `python -m paper_workbench.cli project list` |
| validate example registry | pass | `python -m paper_workbench.cli validate-registry data/registries/example_papers.csv` |
| validate example BibTeX | pass | `python -m paper_workbench.cli validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv` |
| generate note template | pass | `python -m paper_workbench.cli note-template synth_charge_2024 --registry data/registries/example_papers.csv --output <temporary directory>/synth_charge_2024_note.md --force` |
| extract claims | pass | `python -m paper_workbench.cli claims data/notes --output <temporary directory>/claims.csv` |
| generate evidence matrix | pass | `python -m paper_workbench.cli report evidence-matrix --project zis_photocatalysis --theme photocorrosion --out <temporary directory>/evidence_matrix.md --force` |
| generate citation audit | pass | `python -m paper_workbench.cli report citation-audit --project zis_photocatalysis --out <temporary directory>/citation_audit.md --force` |
| generate writing packet | pass | `python -m paper_workbench.cli writing-packet --project zis_photocatalysis --theme photocorrosion --out <temporary directory>/writing_packet.md --force` |
| rebuild local index | pass | `python -m paper_workbench.cli index rebuild --project zis_photocatalysis --include-text --index <temporary directory>/index.sqlite` |
| indexed search | pass | `python -m paper_workbench.cli search photocorrosion --project zis_photocatalysis --indexed --index <temporary directory>/index.sqlite` |
| workspace integrity | pass | `python -m paper_workbench.cli integrity check --project zis_photocatalysis` |
| notebook structure check | pass | `python scripts/check_notebooks.py` |

## Manual Fresh-Venv Check

For a stricter local clean-room install, run these commands in a disposable directory:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[test]"
paperwb --help
python scripts/smoke_cli_workflow.py --quick
```

The scripted check uses `python -m paper_workbench.cli` so it also works before the console entry point is installed.
