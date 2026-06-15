# CLI Smoke Workflow v2.2

This smoke workflow uses synthetic checked-in data and writes generated outputs to a temporary directory.

Temporary output directory: `<temporary directory>`
Steps run: 14
Failures: 0

| Step | Result | Command |
| --- | --- | --- |
| help | pass | `python -m paper_workbench.cli --help` |
| init temp workspace | pass | `python -m paper_workbench.cli init --root <temporary directory>/workspace` |
| validate registry | pass | `python -m paper_workbench.cli validate-registry data/registries/example_papers.csv` |
| validate bibtex | pass | `python -m paper_workbench.cli validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv` |
| note template | pass | `python -m paper_workbench.cli note-template synth_charge_2024 --registry data/registries/example_papers.csv --output <temporary directory>/synth_charge_2024_note.md --force` |
| claims extraction | pass | `python -m paper_workbench.cli claims data/notes --output <temporary directory>/claims.csv` |
| evidence map | pass | `python -m paper_workbench.cli report evidence-map --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out <temporary directory>/evidence_map.md --force` |
| citation audit | pass | `python -m paper_workbench.cli report citation-audit --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out <temporary directory>/citation_audit.md --force` |
| project list | pass | `python -m paper_workbench.cli project list` |
| template list | pass | `python -m paper_workbench.cli template list` |
| template create | pass | `python -m paper_workbench.cli template create photocatalysis --project smoke_photocatalysis --root <temporary directory>/template_workspace` |
| project search | pass | `python -m paper_workbench.cli search photocorrosion --project zis_photocatalysis` |
| files scan | pass | `python -m paper_workbench.cli files scan --project zis_photocatalysis` |
| dashboard next actions | pass | `python -m paper_workbench.cli dashboard --project zis_photocatalysis --view next-actions --limit 3 --no-audit-log` |
