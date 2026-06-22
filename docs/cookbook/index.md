# Cookbook

Each recipe is local-first and uses synthetic paths or explicit user-supplied
project data. Do not copy PDFs, paper full text, private notes, or fabricated
metadata into the repository.

## Create A New Project

Purpose: create an empty project profile.

```bash
paperwb template list
paperwb template create generic --project my_review
paperwb project validate my_review
```

Expected output: a project under `projects/my_review/`.

Common mistakes: reusing an existing project name; treating templates as real
metadata.

Safety notes: templates are empty or synthetic and should refuse existing
project paths.

## Add A Paper Manually

Purpose: append one explicit registry row.

```bash
paperwb add-paper my_paper_001 --project my_review --title "User Verified Title" --year 2026 --bibtex-key UserVerified2026 --reading-status unread
paperwb validate-registry projects/my_review/registry.csv --strict
```

Expected output: one new registry row and validation findings if required
fields are missing.

Common mistakes: adding guessed titles, guessed years, or fake DOI values.

Safety notes: use only metadata you verified yourself.

## Import From Zotero CSV

Purpose: inspect a local CSV export before changing a registry.

```bash
paperwb import zotero-csv data/examples/zotero_export.csv --project clean_demo --dry-run --report scratch/zotero_import_dry_run.md --force
```

Expected output: a Markdown dry-run report with imported, skipped, and updated
counts.

Common mistakes: running an import without `--dry-run` first.

Safety notes: imports must not overwrite non-empty user fields silently.

## Validate BibTeX

Purpose: check citation-key coverage and registry linkage.

```bash
paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry projects/clean_demo/registry.csv --strict
```

Expected output: no findings for the clean synthetic project.

Common mistakes: assuming BibTeX titles or DOI values are authoritative.

Safety notes: treat BibTeX metadata as imported metadata that still needs user
review.

## Write A Structured Note

Purpose: create a user-editable note template.

```bash
paperwb note-template clean_demo_2026 --project clean_demo --output scratch/clean_demo_note.md --force
```

Expected output: a Markdown note template.

Common mistakes: expecting the tool to write paper summaries or claims.

Safety notes: only the user should write notes and claims after reading.

## Extract Claims

Purpose: extract structured user-entered claims from notes.

```bash
paperwb claims --project clean_demo --output scratch/clean_demo_claims.csv --force
```

Expected output: a CSV of claims found in structured notes.

Common mistakes: treating empty output as a parser bug when notes do not contain
claim sections.

Safety notes: extraction is from notes only; it does not infer claims from PDFs.

## Generate An Evidence Map

Purpose: see which themes have supporting claims and where evidence is weak.

```bash
paperwb report evidence-map --project clean_demo --out scratch/evidence_map.md --force
```

Expected output: a Markdown evidence map.

Common mistakes: reading the report as scientific truth rather than a local
evidence inventory.

Safety notes: evidence strength depends on user-entered notes and locations.

## Generate A Citation Audit

Purpose: check citation coverage and local evidence readiness.

```bash
paperwb report citation-audit --project clean_demo --out scratch/citation_audit.md --force
```

Expected output: a Markdown citation audit.

Common mistakes: expecting the tool to validate paper truth claims.

Safety notes: the audit checks local metadata, notes, claims, and themes.

## Generate A Writing Packet

Purpose: prepare planning artifacts for a theme.

```bash
paperwb writing-packet --project clean_demo --theme clean-theme --out scratch/writing_packet.md --force
```

Expected output: a planning packet with local evidence, claims, and gaps.

Common mistakes: treating the packet as final prose.

Safety notes: writing packets must not rewrite final literature-review prose.

## Audit A Draft Section

Purpose: audit a Markdown or LaTeX-ish draft against local evidence.

```bash
paperwb manuscript qa drafts/synthetic_good_section.md --project clean_demo --out scratch/manuscript_qa.md --force
```

Expected output: a reviewer-style QA report.

Common mistakes: assuming paragraph-to-claim matches are semantically certain.

Safety notes: matching is heuristic and should prompt manual review.

## Start A Reading Session

Purpose: create a local session record and note checklist.

```bash
paperwb reading queue --project clean_demo
paperwb reading start clean_demo_2026 --project clean_demo
```

Expected output: a ranked reading queue and a session record.

Common mistakes: marking papers as read without actually reading them.

Safety notes: reading status changes should be explicit user actions.

## Create A Backup

Purpose: checkpoint local project state before risky work.

```bash
paperwb integrity check --project clean_demo --out scratch/integrity.md --force
paperwb backup create --project clean_demo --notes "Before import cleanup"
```

Expected output: an integrity report and a local backup snapshot.

Common mistakes: treating backup archives as shareable public artifacts.

Safety notes: do not include PDFs or raw paper full text in backups by default.

## Run A Weekly Review

Purpose: summarize reading sessions, follow-ups, and next papers.

```bash
paperwb reading review --project clean_demo --out scratch/weekly_review.md --force
```

Expected output: a Markdown weekly review.

Common mistakes: expecting the tool to write session summaries for you.

Safety notes: summaries and outcomes should remain user-entered.

## Use The Dashboard

Purpose: inspect project health without modifying source data.

```bash
paperwb dashboard --project clean_demo --no-audit-log
paperwb dashboard --project clean_demo --out scratch/dashboard.md --force --no-audit-log
```

Expected output: terminal or Markdown project summary.

Common mistakes: assuming next actions run automatically.

Safety notes: dashboard actions are suggestions only.

## Create A Support Bundle

Purpose: share sanitized diagnostics for debugging.

```bash
paperwb support redact-preview --project clean_demo
paperwb support bundle --project clean_demo --out scratch/clean_demo_support_bundle
```

Expected output: a directory with diagnostic summaries and sanitized samples.

Common mistakes: using verbose local-only mode for shareable bundles.

Safety notes: default support bundles should not contain PDFs, full notes, full
drafts, cache DBs, backups, raw audit logs, or private comments.

## Migrate A Legacy Workspace

Purpose: inspect historical data before any migration.

```bash
paperwb compatibility inspect tests/fixtures/workspaces/v0_1_legacy_data
paperwb migrate run --root tests/fixtures/workspaces/v0_1_legacy_data --to-project migrated_review --dry-run --out scratch/migration_plan.md --force-report
```

Expected output: compatibility findings and a dry-run migration plan.

Common mistakes: running forced migration directly on real data.

Safety notes: copy fixtures or real workspaces before migration tests; preserve
extra columns and user files.

## Use The Workflow Runner

Purpose: run repeatable local workflow recipes.

```bash
paperwb workflow list
paperwb workflow show daily_check
paperwb workflow run daily_check --project clean_demo --dry-run --out scratch/daily_check.md --force
```

Expected output: a workflow report with step results.

Common mistakes: adding arbitrary shell commands to workflow JSON.

Safety notes: recipes are declarative only and must not execute arbitrary code.
