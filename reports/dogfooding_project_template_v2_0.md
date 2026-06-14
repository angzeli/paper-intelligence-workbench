# Dogfooding Project Template v2.0

## Purpose

v2.0 adds a dogfooding-ready project scaffold for starting a real local
literature-review workspace without committing real papers, PDFs, claims, or
copied full text.

## Command

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
```

Optional template families:

- `photocatalysis`
- `finance`
- `ml-methods`
- `generic`

## Created Project Files

- `registry.csv`: empty standard registry headers
- `bibtex/library.bib`: empty BibTeX library
- `themes.json`: empty/project-specific theme definitions
- `rules.json`: local declarative rule examples
- `notes/`: empty structured-note folder
- `reports/`: local generated-report folder
- `drafts/`: local draft/manuscript workspace
- `reading_sessions/`: local reading-session workspace
- `project_onboarding.md`
- `first_week_plan.md`
- `evidence_tracking_checklist.md`
- `README.md`

## Safety Behavior

- Existing project paths are refused.
- The scaffold contains no real paper metadata.
- No PDFs or copied full text are created.
- No registry rows are generated from filenames.
- User notes are not overwritten.

## Intended First Use

Create the scaffold, review the onboarding files, add one verified paper row,
validate registry and BibTeX, generate a note template, read the paper manually,
then extract user-written claims.
