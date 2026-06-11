# CLI Reference

For the v1.2 stability inventory, see [CLI Surface](CLI_SURFACE.md) and
[Command Contracts](COMMAND_CONTRACTS.md). The CLI is the stable external
interface; direct Python imports are documented separately in
[API Surface](API_SURFACE.md).

Core commands:

```bash
paperwb init
paperwb project init NAME
paperwb project list
paperwb project validate NAME
paperwb validate-registry data/registries/papers.csv
paperwb validate-bib data/bibtex/library.bib --registry data/registries/papers.csv
paperwb add-paper --title "..." --year 2026
paperwb list --tag photocorrosion
paperwb note-template PAPER_ID
paperwb claims data/notes --output scratch/claims.csv
paperwb search "charge separation" --claims
paperwb index rebuild --project zis_photocatalysis --include-text
paperwb index status --project zis_photocatalysis --check-files
paperwb search "charge separation" --project zis_photocatalysis --indexed
paperwb files scan --project zis_photocatalysis
paperwb files audit --project zis_photocatalysis --reports-dir scratch/file_reports --force
paperwb doctor --out scratch/workspace_health.md
paperwb reading queue --project zis_photocatalysis
paperwb reading start PAPER_ID --project zis_photocatalysis
paperwb followups list --project zis_photocatalysis
```

Imports:

```bash
paperwb import zotero-csv data/examples/zotero_export.csv --dry-run
paperwb import csv data/examples/generic_papers.csv --mapping data/examples/generic_mapping.json --dry-run
paperwb import bibtex data/examples/library_import.bib --dry-run
paperwb import ris data/examples/library.ris --dry-run
```

Import commands preserve existing registry rows. `--fill-missing` fills only blank fields on matched rows. Import reports are written to the selected reports directory unless `--report` is provided. If the report path already exists and `--force` is not provided, the command fails before writing the registry.

Sync planning:

```bash
paperwb sync plan --project zis_photocatalysis --source data/examples/zotero_export.csv --source-type zotero-csv --out scratch/sync_plan.md --json-out scratch/sync_plan.json --force
paperwb sync conflicts scratch/sync_plan.json --out scratch/sync_conflicts.md --force
paperwb sync apply scratch/sync_plan.json --dry-run --out scratch/sync_apply_dry_run.md --force-report
paperwb sync plan-obsidian --project zis_photocatalysis --vault scratch/obsidian_zis --out scratch/obsidian_roundtrip.md --json-out scratch/obsidian_roundtrip.json --force
```

Sync commands compare local files only. `sync apply` is dry-run by default and
forced applies create a backup unless `--no-backup` is explicitly supplied.
v1.3 applies safe registry creates and blank-field fills only; conflicts and
note differences are manual-review items.

Report types:

```bash
paperwb report inventory
paperwb report reading-status
paperwb report papers-by-tag
paperwb report bibtex-audit
paperwb report claims-by-theme
paperwb report evidence-map
paperwb report citation-audit
paperwb report missing-notes
paperwb report weak-claims
paperwb report theme-dashboard
paperwb report missing-evidence
paperwb report workspace-health
paperwb report section-outline --theme photocorrosion
paperwb report evidence-matrix --theme photocorrosion
paperwb report claim-bank --theme photocorrosion
paperwb report citation-bank --theme photocorrosion
paperwb report paragraph-plan --theme photocorrosion
paperwb report subsection-readiness --theme photocorrosion
paperwb report all
```

Report commands refuse to overwrite an existing output file unless `--force` is provided. `paperwb report all` writes multiple files under `--reports-dir`, preflights every output before writing, and rejects `--out` because it is a single-report destination. The same no-overwrite behavior applies to `claims --output`, `doctor --out`, `validate-bib --report`, and `validate-registry --json`.

Authoring reports:

```bash
paperwb report evidence-matrix --project zis_photocatalysis --theme photocorrosion --out scratch/photocorrosion_evidence_matrix.md --force
paperwb report evidence-matrix --project zis_photocatalysis --theme charge_separation --csv-out scratch/charge_matrix.csv --json-out scratch/charge_matrix.json --force
paperwb report claim-bank --project zis_photocatalysis --theme photocorrosion --out scratch/photocorrosion_claim_bank.md --force
paperwb report citation-bank --project zis_photocatalysis --theme photocorrosion --out scratch/photocorrosion_citation_bank.md --force
paperwb report paragraph-plan --project zis_photocatalysis --theme photocorrosion --out scratch/photocorrosion_paragraph_plan.md --force
paperwb report subsection-readiness --project zis_photocatalysis --theme photocorrosion --out scratch/photocorrosion_readiness.md --force
paperwb writing-packet --project zis_photocatalysis --theme photocorrosion --out scratch/photocorrosion_writing_packet.md --force
```

These commands generate evidence-based planning aids, not final prose.

Draft citation audit:

```bash
paperwb draft parse drafts/synthetic_photocorrosion_section.md
paperwb draft citations drafts/synthetic_photocorrosion_section.md --project zis_photocatalysis --out scratch/draft_citations.md --force
paperwb draft audit drafts/synthetic_photocorrosion_section.md --project zis_photocatalysis --out scratch/draft_audit.md --force
paperwb draft checklist drafts/synthetic_photocorrosion_section.md --project zis_photocatalysis --out scratch/draft_checklist.md --force
paperwb draft evidence-matrix drafts/synthetic_photocorrosion_section.md --project zis_photocatalysis --out scratch/draft_paragraph_matrix.md --force
```

Draft commands audit user-written Markdown against local citations, notes, and
claims. They do not rewrite final prose or infer unsupported claims.

Reading sessions and follow-ups:

```bash
paperwb reading queue --project zis_photocatalysis
paperwb reading queue --project zis_photocatalysis --theme photocorrosion --limit 10 --out scratch/reading_queue.md --force
paperwb reading start zis_charge_2025 --project zis_photocatalysis --goal "Check evidence locations"
paperwb reading finish SESSION_ID --project zis_photocatalysis --status deeply_read --duration-minutes 45 --claims-added 1 --follow-up "Add missing section/page evidence"
paperwb reading status --project zis_photocatalysis
paperwb reading review --project zis_photocatalysis --out scratch/weekly_reading_review.md --force
paperwb reading review --project zis_photocatalysis --as-of 2026-06-11 --out scratch/reproducible_reading_review.md --force
paperwb followups list --project zis_photocatalysis
paperwb followups export --project zis_photocatalysis --out scratch/followups.md --force
paperwb followups done note:zis_charge_2025:1 --project zis_photocatalysis
```

Reading commands do not read papers automatically or fabricate notes. `reading
start` preserves an existing note by default and requires `--force-note` to
overwrite it. Session logs and follow-up completion state default to ignored
local `.paperwb/` files. `reading review --as-of` makes the review window
reproducible. `followups done` validates the action ID against actions found in
the selected notes and session logs before updating completion state.

Exports:

```bash
paperwb export registry-csv --out data/processed/registry.csv
paperwb export registry-json --out data/processed/registry.json
paperwb export claims --out data/processed/claims.csv
paperwb export claims-json --out data/processed/claims.json
paperwb export reading-list --tag photocorrosion --out scratch/reading_list.md
paperwb export unread --out scratch/unread.md
paperwb export theme-claims --theme photocorrosion --out data/processed/photocorrosion_claims.json
paperwb export reading-list --theme photocorrosion --out scratch/photocorrosion.md
paperwb export reading-list --high-priority --format csv --out scratch/high_priority.csv
paperwb export obsidian --project zis_photocatalysis --out exports/obsidian_zis
paperwb export bundle --project zis_photocatalysis --out exports/zis_bundle
paperwb export project-summary --project zis_photocatalysis --out scratch/project_summary.md
paperwb export report-index --project zis_photocatalysis --out scratch/report_index.md
```

Export commands refuse to overwrite an existing output file unless `--force` is provided. Directory exports such as `obsidian` and `bundle` require a new or empty output directory; they do not merge into or clean non-empty directories.

Indexed search:

```bash
paperwb index rebuild --project zis_photocatalysis --include-text
paperwb index status --project zis_photocatalysis --include-text --check-files --out scratch/index_status.md --force
paperwb index clear --project zis_photocatalysis
paperwb search photocorrosion --project zis_photocatalysis --indexed
paperwb search photocorrosion --project zis_photocatalysis --indexed --text
paperwb search "charge separation" --project zis_photocatalysis --indexed --out scratch/search_charge_separation.md --force
```

The original substring search remains the default unless `--indexed` is provided. Cache databases live under `.paperwb/` and should not be committed.

Local files:

```bash
paperwb files scan --project zis_photocatalysis
paperwb files scan --project zis_photocatalysis --write-registry
paperwb files status --project zis_photocatalysis
paperwb files audit --project zis_photocatalysis --reports-dir scratch/file_reports --force
paperwb files link PAPER_ID projects/zis_photocatalysis/papers/PAPER_ID.pdf --project zis_photocatalysis
paperwb files unlink PAPER_ID --project zis_photocatalysis
paperwb files hash projects/zis_photocatalysis/text/PAPER_ID.txt
paperwb files sidecars --project zis_photocatalysis
```

Local-file commands do not download, scrape, OCR, copy, move, or delete documents. PDF links update `local_pdf_path`; existing values require `--force` to replace. `files scan --write-registry` merges with existing `files.csv` rows so curated notes are preserved. `files unlink` clears `local_pdf_path` only when it removed at least one matching file-registry row, unless `--keep-pdf-path` is used.

Data integrity:

```bash
paperwb integrity check --project zis_photocatalysis
paperwb integrity check --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json
```

`integrity check` is read-only. Use `--out` and `--force` to write a Markdown report.

Audit log:

```bash
paperwb audit-log show --project zis_photocatalysis --markdown
paperwb audit-log clear --project zis_photocatalysis --force
```

Audit logs are local JSONL files under `.paperwb/` and are ignored by git.

Backups and restore:

```bash
paperwb backup create --project zis_photocatalysis
paperwb backup list --project zis_photocatalysis
paperwb backup inspect BACKUP_ID --project zis_photocatalysis
paperwb backup plan-restore BACKUP_ID --project zis_photocatalysis
paperwb backup restore BACKUP_ID --project zis_photocatalysis --dry-run
paperwb backup restore BACKUP_ID --project zis_photocatalysis --force
```

Restore defaults to dry-run behavior unless `--force` is passed. A forced restore creates a pre-restore backup unless `--no-pre-restore-backup` is provided.

Migration:

```bash
paperwb migrate plan --from legacy --to-project migrated_lit_review
paperwb migrate run --from legacy --to-project migrated_lit_review --dry-run
paperwb migrate run --from legacy --to-project migrated_lit_review --force
```

Migration copies files into a new project. It does not move or delete legacy `data/` files.

Most workflow commands accept `--project NAME` to use profile paths. When `--project` is used, registry, notes, BibTeX, themes, and reports path flags are rejected to avoid silently ignoring user input. Use `--out` for an explicit single report or export destination.
