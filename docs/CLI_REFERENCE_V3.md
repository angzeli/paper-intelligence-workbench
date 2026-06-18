# CLI Reference v3

Use `paperwb --help` and `paperwb COMMAND --help` for exact flags. For a
grouped user-facing command map, see [command-reference/index.md](command-reference/index.md).

## Stable Starting Points

```bash
paperwb init
paperwb project list
paperwb template list
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb external add fyp_zis_real <external_workspace> --project fyp_zis_real
paperwb external validate fyp_zis_real --strict
paperwb validate-registry projects/clean_demo/registry.csv --strict
paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry projects/clean_demo/registry.csv --strict
paperwb list --project clean_demo
paperwb note-template PAPER_ID --project clean_demo
paperwb claims projects/clean_demo/notes --output scratch/claims.csv
paperwb dashboard --project clean_demo --no-audit-log
paperwb doctor --project clean_demo
paperwb support doctor --project clean_demo
paperwb support bundle --project clean_demo --out scratch/clean_demo_support_bundle
paperwb compatibility inspect tests/fixtures/workspaces/v0_1_legacy_data
```

## External Private Workspaces

```bash
paperwb external add NAME <external_workspace> --project PROJECT
paperwb external list
paperwb external validate NAME --strict
paperwb external run NAME doctor
paperwb external run NAME dashboard
paperwb external run NAME validate-registry --strict
paperwb external run NAME validate-bib --strict
paperwb external run NAME support-bundle
paperwb external remove NAME
```

External registrations are stored in ignored `.paperwb-local/workspaces.json`.
They point at local workspaces outside the repository and do not copy private
data into tracked files. External validation reports and run summaries redact
private local paths by default; add `--show-paths` only for local debugging
outputs that will not be committed or shared. See
[EXTERNAL_WORKSPACES.md](EXTERNAL_WORKSPACES.md).

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

## Support Bundle Diagnostics

```bash
paperwb support doctor --project clean_demo
paperwb support redact-preview --project clean_demo
paperwb support reproduce --project clean_demo
paperwb support bundle --project clean_demo --safe --out scratch/clean_demo_support_bundle
```

`support bundle` writes generated diagnostics and sanitized CSV samples. It does
not copy PDFs, full notes, full drafts, raw audit logs, cache databases, or
backup archives. Use `--verbose-local-only` only for private debugging after
reading [REDACTION.md](REDACTION.md).

## Compatibility Diagnostics

```bash
paperwb compatibility inspect path/to/workspace
paperwb compatibility report path/to/workspace --out scratch/compatibility.md
paperwb compatibility matrix
```

Compatibility commands are read-only unless `--out` is used to write a report.
Use them before migrating legacy `data/` workspaces, early project profiles,
partial migrations, or registries with extra user columns.

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
