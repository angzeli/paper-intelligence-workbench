# Stable Surface v3

v3.4 keeps the stable dogfooding surface around local project setup, metadata
validation, structured notes, user-entered claims, core reports, read-only
project status, support diagnostics, and compatibility inspection.

Stable means the command name, primary flags, file safety behavior, and
documented schemas should not change without a migration note.

## Stable CLI Groups

| Command | Stable contract |
| --- | --- |
| `init` | Create missing local workspace folders only. |
| `project` | Create, list, and validate project profiles without overwriting user data. |
| `template` | Create empty or synthetic project scaffolds and refuse existing targets. |
| `dogfood` | Create empty dogfooding scaffolds, show onboarding status/checklists, and generate read-only file plans. |
| `validate-registry` | Validate registry CSV files; non-strict mode reports findings without failing scripts. |
| `validate-bib` | Validate BibTeX files and registry linkage; `--strict` fails on error-level findings. |
| `add-paper` | Append one explicit user-supplied registry row. |
| `list` | Display registry rows with local filters. |
| `note-template` | Generate structured Markdown note templates and refuse overwrites without `--force`. |
| `claims` | Extract claims from structured notes written by the user. |
| `search` | Stable for substring/local-file search; indexed mode remains experimental. |
| `report` | Stable for inventory, reading status, BibTeX audit, citation audit, evidence map, weak claims, missing evidence, and report index. |
| `checklist` | Generate theme review checklists. |
| `doctor` | Read-only workspace diagnostics, except explicit report output. |
| `dashboard` | Read-only terminal and Markdown project summary, except explicit `--out`. |
| `support` | Generate sanitized diagnostic summaries and support bundles without copying private source files. |
| `compatibility` | Inspect historical workspace shapes and migration readiness without modifying files. |

## Stable Data Formats

- Registry CSV stable fields are listed in `docs/SCHEMA_REFERENCE_V3.md`.
- Structured note sections and claim fields are stable for user-authored notes.
- Project profile layout under `projects/<name>/` is stable.
- Theme JSON base fields are stable.
- Compatibility inspection reports are stable diagnostics; migration remains copy-based.
- Core Markdown reports are human-readable artifacts, not machine APIs.

## Stable Safety Guarantees

- No cloud APIs, LLM APIs, embeddings, publisher scraping, PDF downloads, or OCR.
- No fabricated paper metadata, citations, claims, quotes, summaries, or
  conclusions.
- No silent overwrite of notes, registry fields, BibTeX files, backups, sync
  applies, migrations, or restores.
- Generated examples must remain synthetic or empty placeholders.
- Support bundles must not include PDFs, full notes, full drafts, raw audit logs,
  cache databases, backup archives, or private comments by default.

## Public Python Surface

The CLI and documented local file schemas are the public API. Selected Python
helpers remain semi-stable for local scripts and are listed in
`docs/PUBLIC_VS_INTERNAL_API.md`. Most package modules are internal.
