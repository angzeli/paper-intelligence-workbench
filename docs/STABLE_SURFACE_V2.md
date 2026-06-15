# Stable Surface v2

Paper Intelligence Workbench v2.0 is a local-first release. The
stable surface is the CLI plus documented CSV, JSON, Markdown, BibTeX, and
project-profile file formats. The Python package remains usable for local
scripts, but direct imports outside the documented stable helpers should be
treated as implementation detail.

## Stable CLI Groups

| Command group | Status | Stability promise |
| --- | --- | --- |
| `init` | stable | Create folder structure without overwriting user files. |
| `project` | stable | Manage project profiles under `projects/`. |
| `template` | stable | Create empty/synthetic non-destructive scaffolds. |
| `dogfood` | stable | Create empty real-project onboarding scaffolds and read-only intake plans. |
| `validate-registry` | stable | Validate CSV registries and report findings without auto-correction. |
| `validate-bib` | stable | Validate local BibTeX files and registry links. |
| `add-paper` | stable | Append explicit user-provided paper rows. |
| `list` | stable | Read-only registry listing and filtering. |
| `note-template` | stable | Generate structured notes; no overwrite without force. |
| `claims` | stable | Extract claims from structured Markdown notes. |
| `search` | stable | Substring search is stable; indexed mode is experimental. |
| `report` core reports | stable | Inventory, reading status, BibTeX audit, citation audit, evidence map, missing notes, weak claims. |
| `doctor` | stable | Workspace-health diagnostics. |
| `dashboard` | stable | Read-only terminal summary and optional Markdown output. |

## Stable File Formats

| Format | Status | Notes |
| --- | --- | --- |
| Registry CSV | stable | Fields listed in `docs/SCHEMA_FREEZE_V2.md`. Extra columns should be preserved where possible. |
| Structured note Markdown | stable | Template headings and claim bullet fields are stable. |
| Claims CSV/JSON export | stable | Intended for local analysis and report generation. |
| Themes JSON | stable | `theme_id`, `name`, `tags`, thresholds, and description. |
| Project profile layout | stable | `projects/<name>/registry.csv`, `bibtex/library.bib`, `notes/`, `themes.json`, `reports/`. |
| BibTeX input | stable enough | Parser is conservative and not a full BibTeX implementation. |

## Stable Interpretation Boundary

Stable workflows organize local evidence. They do not fabricate metadata,
claims, citations, summaries, quotes, or final prose. They do not evaluate
scientific truth.

`graph` is experimental in v2.1. It is read-only unless an explicit `--out`
path is supplied, and its analytics are local connectivity checks rather than
truth, quality, or impact scores.
