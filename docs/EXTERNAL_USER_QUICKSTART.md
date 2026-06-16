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

## 3. Validate Bundled Synthetic Metadata

```bash
paperwb validate-registry projects/zis_photocatalysis/registry.csv --strict
paperwb validate-bib projects/zis_photocatalysis/bibtex/library.bib --registry projects/zis_photocatalysis/registry.csv --strict
```

Use `--strict` when a validation error should fail a script or CI job. The
`zis_photocatalysis` project has clean registry structure but intentionally
imperfect evidence tracking so later reports have findings to display. The
legacy `data/` examples also intentionally contain validation findings and are
useful for seeing what audits catch.

## 4. Generate A Note Template

```bash
paperwb note-template zis_charge_2025 --project zis_photocatalysis --output scratch/zis_charge_2025_note.md --force
```

Edit copied templates with your own verified notes. Do not fabricate claims.

## 5. Extract Claims

```bash
paperwb claims --project zis_photocatalysis --output scratch/zis_claims.csv --force
```

Claims are extracted from structured note fields only.

## 6. Generate Evidence And Citation Reports

```bash
paperwb report evidence-map --project zis_photocatalysis --out scratch/zis_evidence_map.md --force
paperwb report citation-audit --project zis_photocatalysis --out scratch/zis_citation_audit.md --force
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
