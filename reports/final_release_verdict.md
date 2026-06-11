# Final Release Verdict

Date: 2026-06-11

## Verdict

Ready for local dogfooding.

Paper Intelligence Workbench is coherent enough for a technically comfortable
student or early-stage researcher to install locally, initialize a workspace,
try synthetic examples, and begin a small literature-review project.

## Stable Commands For Dogfooding

- `paperwb init`
- `paperwb project list/init/validate`
- `paperwb template list/inspect/create`
- `paperwb validate-registry`
- `paperwb validate-bib`
- `paperwb list`
- `paperwb note-template`
- `paperwb claims`
- `paperwb search`
- `paperwb report inventory`
- `paperwb report reading-status`
- `paperwb report bibtex-audit`
- `paperwb report citation-audit`
- `paperwb report evidence-map`
- `paperwb doctor`
- `paperwb dashboard`

## Useful But Still Experimental

- Indexed search and sidecar search.
- Import/export round-trips.
- Sync planning and Obsidian round-trip checks.
- Reading sessions and follow-up completion.
- Backup restore and legacy migration workflows.
- Draft and manuscript QA heuristics.
- Rule engine adapters.
- Local file audit workflows.

These workflows are usable, but they should stay conservative and dry-run-first
until more real projects exercise them.

## First Real Use Case

Start with one FYP-style photocatalysis literature review:

1. Create a project from the photocatalysis template.
2. Add 10 to 20 verified registry rows.
3. Import or paste verified BibTeX entries.
4. Generate notes but fill them manually.
5. Extract claims only from user-written notes.
6. Run citation audit, evidence map, dashboard, and a writing packet before
   drafting a subsection.

Do not begin with sync, migration, backup restore, or manuscript QA until the
basic registry-note-claim loop is comfortable.

## What Not To Expand Further Yet

- Do not add LLM summarization or citation suggestions.
- Do not parse PDFs or OCR scans by default.
- Do not add cloud sync.
- Do not add a web app.
- Do not add more report types until existing docs are simplified.
- Do not expand templates with real paper metadata or real claims.
- Do not add arbitrary-code plugins for validation rules.

## Known Limitations

- The CLI is broad and can feel overwhelming.
- Reports are Markdown-first and intentionally plain.
- Evidence matching is lexical and heuristic, not semantic certainty.
- Synthetic fixtures intentionally contain warnings and validation errors.
- Empty project templates produce many expected "missing evidence" warnings.
- Some advanced workflows need more real-world dogfooding before they should be
  called stable.

## Recommended Maintenance Workflow

- Keep changes small and release-note-backed.
- Run `python -m pytest -q` before every handoff.
- Run `python scripts/smoke_cli_workflow.py --quick`.
- Run `python scripts/check_notebooks.py`.
- Run `python scripts/data_safety_audit.py --strict`.
- Regenerate only reports affected by behavior changes.
- Keep all risky workflows dry-run-first.
- Do not commit cache databases, audit logs, backup snapshots, PDFs, or real
  paper full text.

## Before Public Release

- Reduce README density with a shorter "first hour" path.
- De-duplicate overlapping docs.
- Decide which experimental commands should remain visible in top-level help.
- Continue hostile-review cycles after any import/export, sync, backup, or
  manuscript QA changes.
