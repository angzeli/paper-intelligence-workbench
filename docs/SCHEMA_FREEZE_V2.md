# Schema Freeze v2

This page documents the v2.0rc local data schemas. The tool uses files, not a
required database.

## Registry CSV

Stable fields:

`paper_id`, `title`, `authors`, `year`, `journal`, `doi`, `url`,
`local_pdf_path`, `bibtex_key`, `tags`, `reading_status`, `notes_path`,
`added_date`, `last_reviewed_date`, `priority`, `project`, `source_type`,
`relevance_score`, `reading_priority`, `included_in_lit_review`,
`exclude_reason`, `user_comment`.

Experimental or policy-sensitive fields:

- `local_pdf_path`: advisory local reference only; paths should be relative.
- `relevance_score`: local numeric aid, not a scientific quality score.
- `included_in_lit_review`: local planning flag, not evidence validation.

## Structured Note Markdown

Stable sections:

- `Metadata`
- `One-sentence summary`
- `Why this paper matters`
- `Research question or problem`
- `Method / approach`
- `Key findings`
- `Limitations`
- `Useful for my literature review`
- `Not useful for`
- `Claims and evidence`
- `Open questions`
- `Follow-up actions`
- `Personal reading notes`

Stable claim fields:

`Claim`, `Evidence type`, `Section / page`, `Quote or paraphrase`,
`Confidence`, `Tags`, `User comment`, `Strength`, `Supports theme`.

## Claim Data

Claims must originate from user-written structured notes. The tool must not
infer claims from free-form prose, PDFs, abstracts, or draft paragraphs.

## Project Profile

Stable project layout:

```text
projects/<name>/
  project.json
  registry.csv
  themes.json
  bibtex/library.bib
  notes/
  reports/
```

Optional or experimental project paths include `text/`, `files.csv`, `rules.json`,
`backups/`, and ignored `.paperwb/` local state.

## Theme JSON

Stable fields: `theme_id`, `name`, `tags`, `min_claims`, `min_papers`,
`description`.

## Rule JSON

Rule configs are declarative JSON. They may not execute Python code. Supported
rule condition types are documented in `docs/RULE_CONFIG_SCHEMA.md`.

## Generated And Cache Formats

- Generated reports are reproducible artifacts, not stable machine APIs unless
  explicitly documented.
- SQLite search indexes under `.paperwb/` are cache files and may be rebuilt.
- Audit logs, session logs, backup manifests, sync plans, and migration reports
  are local safety artifacts. Treat their schema as experimental unless a future
  release explicitly freezes them.

