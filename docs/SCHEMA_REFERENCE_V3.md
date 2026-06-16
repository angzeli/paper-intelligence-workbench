# Schema Reference v3

Paper Intelligence Workbench uses local files instead of a required database.
v3.2 keeps the core user-facing schemas below stable for local dogfooding.

## Registry CSV

Stable fields:

`paper_id`, `title`, `authors`, `year`, `journal`, `doi`, `url`,
`local_pdf_path`, `bibtex_key`, `tags`, `reading_status`, `notes_path`,
`added_date`, `last_reviewed_date`, `priority`, `project`, `source_type`,
`relevance_score`, `reading_priority`, `included_in_lit_review`,
`exclude_reason`, `user_comment`.

Policy-sensitive fields:

- `local_pdf_path` is advisory. Prefer relative paths and do not commit real
  PDFs.
- `relevance_score` is a local planning aid, not a paper-quality score.
- `included_in_lit_review` is a writing-planning flag, not proof of evidence.
- Extra user columns may exist in historical registries. Core loaders ignore
  unknown columns, and compatibility/migration workflows should preserve raw CSV
  files rather than rewriting those columns away.

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

Claims must originate from user-written structured notes. The tool must not
infer claims from PDFs, abstracts, draft paragraphs, or filenames.

## Project Profile Layout

Stable layout:

```text
projects/<name>/
  project.json
  registry.csv
  themes.json
  bibtex/library.bib
  notes/
  reports/
```

Optional or experimental paths include `drafts/`, `reading_sessions/`,
`workflows/`, `review_packets/`, `rules.json`, `files.csv`, `backups/`, `text/`,
and ignored `.paperwb/` local state.

## Theme JSON

Stable fields:

`theme_id`, `name`, `tags`, `min_claims`, `min_papers`, `description`.

## Experimental Sidecars

These are local review metadata and are not schema-frozen in v3:

- `claim_lifecycle.json`
- `contradictions.json`
- `reviewer_comments.json`
- workflow recipe JSON files
- sync plan JSON files
- backup manifests
- rebuild metadata
- SQLite indexes and cache files under `.paperwb/`

## Generated Reports

Markdown reports are reproducible human-readable artifacts. Their headings and
tables may evolve unless a command contract explicitly treats a report as a
stable output.
