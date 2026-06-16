# CLI Reference v2

Use `paperwb --help` and `paperwb COMMAND --help` for exact options. This page
classifies command groups for the v2 release line.

## Stable Core

- `init`
- `project`
- `template`
- `dogfood`
- `validate-registry`
- `validate-bib`
- `add-paper`
- `list`
- `note-template`
- `claims`
- `search` without `--indexed`
- `report` core reports
- `doctor`
- `dashboard`

## Experimental But Usable

- `workflow`
- `review-packet`
- `index`
- `graph`
- `claim-review`
- `contradictions`
- `files`
- `draft`
- `manuscript`
- `reading`
- `followups`
- `import`
- `export` advanced outputs
- `sync`
- `integrity`
- `audit-log`
- `backup`
- `migrate`
- `rules`
- `writing-packet`
- `synthetic`

## Dogfood Commands

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb dogfood status --project fyp_zis_lit_review
paperwb dogfood checklist --project fyp_zis_lit_review
paperwb dogfood plan-from-files photocatalysis --project fyp_zis_lit_review --references-dir <references_dir> --bibtex <ref.bib> --out scratch/fyp_15_paper_plan.md --force
```

`dogfood create` is non-destructive and refuses an existing project path.
`plan-from-files` is a planning command only: it compares local PDF filenames
with BibTeX keys and does not copy files, read PDF text, or write registry rows.

## Common Flags

- `--project PROJECT`: use a project profile.
- `--out PATH`: write a report/export.
- `--force`: overwrite an output where the command allows it.
- `--dry-run`: plan without writing for risky workflows.

Stable commands should produce user-facing errors and avoid Python tracebacks
for normal bad input.

## Workflow Runner Commands

```bash
paperwb workflow list
paperwb workflow show daily_check
paperwb workflow run daily_check --project zis_photocatalysis --dry-run
paperwb workflow run pre_writing_check --project zis_photocatalysis --theme photocorrosion --dry-run
paperwb workflow run pre_backup_check --project zis_photocatalysis --run-writes --force
paperwb workflow validate projects/zis_photocatalysis/workflows/daily_check.json --strict
```

Workflow recipes are declarative JSON only. They can call built-in local steps
such as validation, report generation, dashboard, rules, manuscript QA, and
backup creation, but they cannot execute arbitrary shell or Python code. Use
`--dry-run` before running recipes that write reports, backups, or indexes.
Recipes that default to dry-run require `--run-writes` before those step writes
are allowed from the CLI.

## Review Packet Commands

```bash
paperwb review-packet create --project zis_photocatalysis --theme photocorrosion --out scratch/review_packet_photocorrosion --force
paperwb review-packet import-comments scratch/review_packet_photocorrosion/comments.csv --project zis_photocatalysis --theme photocorrosion --dry-run
paperwb review-packet import-comments scratch/review_packet_photocorrosion/comments.csv --project zis_photocatalysis --theme photocorrosion --force --out scratch/reviewer_comment_import.md --force-report
paperwb review-packet comments --project zis_photocatalysis --out scratch/reviewer_comments.md --force
paperwb review-packet response --project zis_photocatalysis --theme photocorrosion --out scratch/response_to_review.md --force
paperwb review-packet followups --project zis_photocatalysis --theme photocorrosion --out scratch/review_followups.md --force
```

Review packets are experimental in the v2 line. They export local Markdown,
CSV, and JSON review artifacts without PDFs. Imported comments are stored as
separate `.paperwb/reviewer_comments.json` metadata and never rewrite claims,
notes, registry rows, BibTeX, or evidence locations.

## Evidence Graph Commands

```bash
paperwb graph build --project zis_photocatalysis
paperwb graph summary --project zis_photocatalysis --out scratch/evidence_graph_summary.md --force
paperwb graph export --project zis_photocatalysis --format json --out scratch/evidence_graph.json --force
paperwb graph export --project zis_photocatalysis --format dot --out scratch/evidence_graph.dot --force
```

The graph commands remain experimental in the v2 line. They are read-only unless `--out`
is supplied, and they derive nodes and edges only from local workbench data.

## Claim Lifecycle Commands

```bash
paperwb claim-review queue --project zis_photocatalysis
paperwb claim-review mark PAPER_ID:c1 --project zis_photocatalysis --status verified
paperwb claim-review deprecated --project zis_photocatalysis --out scratch/deprecated_claims.md --force
paperwb contradictions create --project zis_photocatalysis --theme photocorrosion
paperwb contradictions add contradiction_photocorrosion_1 PAPER_ID:c1 --project zis_photocatalysis
paperwb contradictions report --project zis_photocatalysis --out scratch/contradictions.md --force
```

The claim lifecycle commands are experimental in the v2 line. They store explicit
review state in local JSON sidecars and do not edit notes, registry rows, or
claim CSV exports. Contradiction groups are user-managed review aids, not
automatic truth judgments.
