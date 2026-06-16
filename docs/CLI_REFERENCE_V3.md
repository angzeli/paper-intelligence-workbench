# CLI Reference v3

Use `paperwb --help` and `paperwb COMMAND --help` for exact flags.

## Stable Starting Points

```bash
paperwb init
paperwb project list
paperwb template list
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb validate-registry projects/clean_demo/registry.csv --strict
paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry projects/clean_demo/registry.csv --strict
paperwb list --project clean_demo
paperwb note-template PAPER_ID --project clean_demo
paperwb claims projects/clean_demo/notes --output scratch/claims.csv
paperwb dashboard --project clean_demo --no-audit-log
paperwb doctor --project clean_demo
```

## Stable Core Reports

```bash
paperwb report inventory --project clean_demo --out scratch/inventory.md --force
paperwb report reading-status --project clean_demo --out scratch/reading_status.md --force
paperwb report bibtex-audit --project clean_demo --out scratch/bibtex_audit.md --force
paperwb report evidence-map --project clean_demo --out scratch/evidence_map.md --force
paperwb report citation-audit --project clean_demo --out scratch/citation_audit.md --force
paperwb report weak-claims --project clean_demo --out scratch/weak_claims.md --force
paperwb report missing-evidence --project clean_demo --out scratch/missing_evidence.md --force
paperwb export report-index --out reports/index.md --force
```

## Experimental Command Groups

```bash
paperwb workflow --help
paperwb review-packet --help
paperwb sync --help
paperwb index --help
paperwb rebuild --help
paperwb files --help
paperwb draft --help
paperwb manuscript --help
paperwb reading --help
paperwb graph --help
paperwb rules --help
paperwb claim-review --help
paperwb contradictions --help
```

Experimental commands remain local and tested, but their schemas and report
formats are not frozen. Use `--dry-run` when available.

## Safety Flags

- `--strict`: fail validation scripts on error-level findings.
- `--out`: write a report or export.
- `--force`: overwrite an existing output where supported.
- `--dry-run`: plan without applying writes where supported.
- `--project`: use a project profile under `projects/`.
