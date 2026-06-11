# External User Simulation v1.0-rc

This smoke workflow uses synthetic checked-in data and writes generated outputs to a temporary directory.

Temporary output directory: `<temporary directory>`
Steps run: 18
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
| project search | pass | `python -m paper_workbench.cli search photocorrosion --project zis_photocatalysis` |
| files scan | pass | `python -m paper_workbench.cli files scan --project zis_photocatalysis` |
| zotero dry-run import | pass | `python -m paper_workbench.cli import zotero-csv data/examples/zotero_export.csv --project zis_photocatalysis --dry-run --report <temporary directory>/import_zotero.md --force` |
| writing packet | pass | `python -m paper_workbench.cli writing-packet --project zis_photocatalysis --theme photocorrosion --out <temporary directory>/writing_packet.md --force` |
| indexed search rebuild | pass | `python -m paper_workbench.cli index rebuild --project zis_photocatalysis --include-text --index <temporary directory>/index.sqlite` |
| indexed search | pass | `python -m paper_workbench.cli search photocorrosion --project zis_photocatalysis --indexed --text --index <temporary directory>/index.sqlite` |
| file audit | pass | `python -m paper_workbench.cli files audit --project zis_photocatalysis --reports-dir <temporary directory>/file_reports --force` |
| obsidian export | pass | `python -m paper_workbench.cli export obsidian --project zis_photocatalysis --out <temporary directory>/obsidian_zis` |
| report index export | pass | `python -m paper_workbench.cli export report-index --out <temporary directory>/report_index.md --force` |
