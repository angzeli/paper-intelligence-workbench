# Registry Schema

The paper registry is a CSV file, usually under `data/registries/`.

Default path:

```text
data/registries/papers.csv
```

Example path:

```text
data/registries/example_papers.csv
```

## Fields

| Field | Required | Description |
| --- | --- | --- |
| `paper_id` | yes | Stable local ID, preferably human-readable. |
| `title` | yes | User-provided title. |
| `authors` | yes | Semicolon-separated authors or BibTeX-style names. |
| `year` | yes | Four-digit year when known. |
| `journal` | no | Journal, booktitle, venue, publisher, or source label. |
| `doi` | no | DOI normalized for comparison. |
| `url` | no | Local or public URL supplied by the user. |
| `local_pdf_path` | no | Workspace-relative path to a local file if the user owns it. |
| `bibtex_key` | no | Key linking to a BibTeX entry. |
| `tags` | no | Tags separated by semicolons, commas, or pipes. |
| `reading_status` | yes | One of the supported reading-status values. |
| `notes_path` | no | Workspace-relative Markdown note path. |
| `added_date` | no | ISO date when added. |
| `last_reviewed_date` | no | ISO date when last reviewed. |
| `priority` | no | User-defined priority. |
| `project` | no | Project/profile label. |
| `source_type` | no | Source category such as `journal_article`, `conference_paper`, `book`, `thesis`, `preprint`, `report`, `review`, `dataset`, or `other`. |
| `relevance_score` | no | Optional numeric score from 0 to 5. |
| `reading_priority` | no | Reading priority: `low`, `medium`, `high`, or `critical`. |
| `included_in_lit_review` | no | Boolean-like value such as `true`/`false` or `yes`/`no`. |
| `exclude_reason` | no | Reason for excluding a paper from the review. |
| `user_comment` | no | User notes about the registry row. |

## Validation Rules

Registry validation checks:

- missing required IDs, titles, authors, or years
- invalid reading status
- invalid year format
- missing BibTeX key warnings
- duplicate DOI values
- duplicate normalized titles
- duplicate BibTeX keys
- absolute local PDF paths
- invalid priority or reading priority
- invalid source type
- invalid relevance score
- read or deeply read papers without `notes_path`
- included papers without extracted claims when claims are supplied to validation
- excluded papers without `exclude_reason`
- DOI-like strings with malformed DOI shape
- missing local PDF paths as warnings only

The validator reports findings and suggestions. It does not auto-correct user data.
