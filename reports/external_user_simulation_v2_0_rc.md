# External User Simulation v2.0rc

## Persona

Technically comfortable undergraduate or early-stage researcher using synthetic
data before starting a real local literature-review project.

## Workflow To Simulate

1. Understand project from README and v2 getting-started docs.
2. Install editable package in a temporary environment or use no-install CLI.
3. Run `paperwb --help`.
4. Initialize a workspace.
5. Create a synthetic project from a template.
6. Validate registry and BibTeX.
7. Generate a note template.
8. Extract claims.
9. Generate evidence map and citation audit.
10. Run dashboard.
11. Run stable safety checks.

## Validation Status

Passed.

## Results

| Step | Result | Notes |
| --- | --- | --- |
| Understand project from README and v2 docs | pass | README links v2 getting-started, stable surface, and command contracts. |
| Editable install | pass | Temporary venv installed `paper-intelligence-workbench==2.0.0rc1`. |
| Package import | pass | `paper_workbench.__version__` returned `2.0.0rc1`. |
| CLI help | pass | `paperwb --help` listed expected command groups. |
| Initialize workspace | pass | `paperwb init --root <tmp>` created local folders only. |
| Create project from template | pass | Photocatalysis template created an empty synthetic scaffold non-destructively. |
| Validate project | pass | Reported expected warnings for empty notes/evidence, no unexpected crash. |
| Validate example registry | pass | Reported intentional duplicate DOI/title findings. |
| Validate example BibTeX | pass | Reported intentional incomplete-entry findings. |
| Generate note template | pass | Wrote to a temporary output path with explicit `--force`. |
| Extract claims | pass | Wrote 3 synthetic claims. |
| Generate evidence map and citation audit | pass | Wrote Markdown reports. |
| Run dashboard and rules | pass | Generated project summary and local rule findings. |
| Import/export | pass | Zotero CSV dry-run and registry/reading-list exports succeeded. |
| Local search/index | pass | Rebuilt a temporary SQLite index and searched synthetic sidecar text. |
| Draft/manuscript QA | pass | Synthetic draft and manuscript QA reports generated without rewriting drafts. |
| Reading/follow-up workflow | pass | Queue and follow-up listings worked against synthetic data. |
| Backup/integrity/migration | pass | Backup, restore dry-run, integrity check, migration plan, and migration dry-run passed. |

## Fix Applied

The installation and v2 getting-started docs now clarify that
`python -m paper_workbench.cli ...` is a repository-root fallback. Installed
users should run `paperwb` inside initialized workspaces to avoid local
workspace folders shadowing the Python package.

## Verdict

Ready for local dogfooding.
