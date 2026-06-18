# Cookbook Inventory v3.4

The v3.4 cookbook lives at `docs/cookbook/index.md`.

## Recipes Added

| Recipe | Purpose | Safety note |
| --- | --- | --- |
| Create a new project | Create an empty project profile. | Templates are empty or synthetic and refuse existing paths. |
| Add a paper manually | Add one explicit registry row. | Use only verified metadata. |
| Import from Zotero CSV | Inspect a local import before writing. | Run dry-run first. |
| Validate BibTeX | Check citation-key coverage and registry linkage. | Treat BibTeX metadata as advisory. |
| Write a structured note | Generate a user-editable note template. | The tool does not write paper summaries. |
| Extract claims | Extract user-entered claims from notes. | No PDF or abstract inference. |
| Generate an evidence map | Show theme support and evidence gaps. | Local evidence inventory only. |
| Generate a citation audit | Check citation readiness. | Does not validate scientific truth. |
| Generate a writing packet | Prepare planning artifacts. | Not final prose. |
| Audit a draft section | Run local heuristic manuscript QA. | Manual review required. |
| Start a reading session | Create a local session record. | Reading status changes must be explicit. |
| Create a backup | Checkpoint local project state. | Do not treat backups as public artifacts. |
| Run a weekly review | Summarize local reading activity. | User outcomes remain user-entered. |
| Use the dashboard | Inspect project health. | Suggestions do not run automatically. |
| Create a support bundle | Share sanitized diagnostics. | Safe mode should not include private content. |
| Migrate a legacy workspace | Inspect and dry-run migration. | Never force migration first. |
| Use the workflow runner | Run declarative recipes. | No arbitrary shell or Python execution. |

## Common Recipe Pattern

Each recipe includes:

- purpose
- command sequence
- expected output
- common mistakes
- safety notes

## Known Limitations

- Recipes are intentionally concise and do not replace full reference docs.
- Experimental recipes may need updates after real dogfooding.
- The cookbook does not include screenshots or rendered site navigation.
