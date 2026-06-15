# Workflow Safety

Workflow recipes are intentionally limited.

They may:

- call built-in local workflow steps
- read local registry, BibTeX, notes, themes, rules, drafts, and project files
- generate reports and exports
- run in dry-run mode
- create local backups when explicitly run with `--run-writes`

They must not:

- execute arbitrary shell commands
- execute arbitrary Python from JSON
- scrape publishers
- use cloud or LLM APIs
- silently overwrite user files
- fabricate paper metadata, claims, citations, quotes, or final prose

The recipe validator rejects unknown step types and fields such as `command`,
`shell`, `python`, `script`, `exec`, and `subprocess`.

Recipes that default to dry-run require an explicit `--run-writes` opt-in from
the CLI before step outputs or backups are written.

Use:

```bash
paperwb workflow validate path/to/workflow.json --strict
```

before sharing or running project-local recipes.
