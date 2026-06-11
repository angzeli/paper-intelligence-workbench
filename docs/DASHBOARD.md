# Terminal Dashboard

`paperwb dashboard` gives a read-only terminal summary of local workbench state.
It is designed as a fast starting point before a reading or writing session.

The dashboard aggregates local data from:

- registry rows
- structured notes and extracted claims
- BibTeX validation
- citation-audit findings
- workspace-health findings
- project-specific rule findings
- optional manuscript QA findings
- reading queue items
- open follow-up actions
- recent audit-log events
- generated Markdown reports

It does not modify registry rows, notes, BibTeX files, drafts, session logs, or
rules. It writes only when `--out` is provided.

## Commands

Default workspace dashboard:

```bash
paperwb dashboard
```

Project dashboard:

```bash
paperwb dashboard --project zis_photocatalysis
```

Markdown dashboard report:

```bash
paperwb dashboard --project zis_photocatalysis --no-audit-log --out reports/dashboard_v1_6.md --force
```

Dashboard with manuscript QA warnings:

```bash
paperwb dashboard --project zis_photocatalysis --manuscript drafts/synthetic_unknown_citations.md
```

Focused views:

```bash
paperwb dashboard --project zis_photocatalysis --view next-actions
paperwb dashboard --project zis_photocatalysis --view health
```

Use `--no-audit-log` for release-facing or shared reports when you do not want
ignored local `.paperwb/audit_log.jsonl` events included. `--limit` must be a
positive integer; invalid values are rejected instead of silently hiding rows.

## Interpretation

The dashboard reports completeness and workflow status. It does not decide
whether a scientific claim is true and does not infer claims from papers. Weak
evidence, missing notes, and citation findings are based only on local user
metadata and structured notes.
