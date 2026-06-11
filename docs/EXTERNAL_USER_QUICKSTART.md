# External User Quickstart

This quickstart assumes a fresh repository checkout. It uses only synthetic data and writes generated outputs under `scratch/`, which is ignored by git.

## 1. Install

```bash
python -m pip install -e ".[test]"
paperwb --help
```

No-install fallback:

```bash
python -m paper_workbench.cli --help
```

## 2. Initialize A Scratch Workspace

```bash
paperwb init --root scratch/first_workspace
```

This creates local folders without overwriting existing user files.

## 3. Validate Example Data

```bash
paperwb validate-registry data/registries/example_papers.csv
paperwb validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv
```

The synthetic examples intentionally contain validation findings.

## 4. Generate A Note Template

```bash
paperwb note-template synth_charge_2024 --registry data/registries/example_papers.csv --output scratch/synth_charge_2024_note.md --force
```

Edit copied templates with your own verified notes. Do not fabricate claims.

## 5. Extract Claims

```bash
paperwb claims data/notes --output scratch/example_claims.csv
```

Claims are extracted from structured note fields only.

## 6. Generate Evidence And Citation Reports

```bash
paperwb report evidence-map --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out scratch/evidence_map.md --force
paperwb report citation-audit --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out scratch/citation_audit.md --force
```

Use these reports to find missing notes, weak claims, and incomplete citation links.

## 7. Use A Project Profile

```bash
paperwb project list
paperwb project validate zis_photocatalysis
paperwb report evidence-map --project zis_photocatalysis --out scratch/zis_evidence_map.md --force
```

Project profiles keep separate registries, notes, BibTeX files, themes, and reports.

## 8. Generate A Writing Packet

```bash
paperwb writing-packet --project zis_photocatalysis --theme photocorrosion --out scratch/photocorrosion_writing_packet.md --force
```

The packet is a planning aid. It does not write your final literature-review prose.

## 9. Search And Index

```bash
paperwb search photocorrosion --project zis_photocatalysis
paperwb index rebuild --project zis_photocatalysis --include-text
paperwb search photocorrosion --project zis_photocatalysis --indexed --text
```

The SQLite index is local and rebuildable.

## 10. Import And Export

```bash
paperwb import zotero-csv data/examples/zotero_export.csv --project zis_photocatalysis --dry-run --report scratch/zotero_import_dry_run.md --force
paperwb export claims-json --project zis_photocatalysis --out scratch/zis_claims.json --force
paperwb export report-index --out scratch/report_index.md --force
```

Start imports with `--dry-run` and review the report before writing.

## 11. Run Release Checks

```bash
python scripts/check_notebooks.py
python scripts/smoke_cli_workflow.py --quick
python scripts/data_safety_audit.py --out scratch/data_safety_audit.md --strict
```

These checks are local and do not require secrets.
