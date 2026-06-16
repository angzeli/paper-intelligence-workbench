# Legacy Workspaces

Legacy workspaces are older local layouts that predate the current project
profile workflow.

## Common Shapes

- `data/registries/papers.csv`
- `data/bibtex/library.bib`
- `data/notes/`
- `data/examples/themes.json`
- top-level `reports/`

The legacy `data/` workflow is still inspectable. New real projects should use
project profiles under `projects/<name>/`.

## Inspect A Legacy Workspace

```bash
paperwb compatibility inspect path/to/legacy_workspace
paperwb compatibility report path/to/legacy_workspace --out scratch/legacy_compatibility.md
```

Inspection is read-only. It reports whether migration is possible, blocked, or
requires manual repair.

