# Command Contracts v3

This page documents v3.0rc command behavior for local dogfooding. It freezes
contracts for stable commands and labels advanced workflows honestly.

## Global Contract

- `paperwb --help` works after editable install.
- `python -m paper_workbench.cli --help` works from the repository root.
- Commands remain local-first and require no cloud APIs, LLM APIs, publisher
  scraping, secrets, copyrighted PDFs, or copied paper full text.
- Normal bad input returns a user-facing error rather than a traceback.
- Report, export, note-template, backup, migration, sync, and restore outputs
  do not overwrite user files without explicit force flags.
- Validation commands default to review mode and complete with printed findings;
  use `--strict` when error-level findings should fail a script.

## Command Map

| Command group | Purpose | Primary inputs | Files written | Destructive behavior | Status |
| --- | --- | --- | --- | --- | --- |
| `init` | Create workspace folders | optional `--root` | missing folders | none | stable |
| `project` | Manage project profiles | project name | `projects/<name>` files | refuses unsafe overwrites | stable |
| `template` | Create empty/synthetic scaffolds | template id, project | project scaffold | refuses existing target | stable |
| `dogfood` | Real-project onboarding | template id, project, optional local paths | empty scaffold or planning report | plan-from-files is read-only | stable |
| `validate-registry` | Audit registry CSV | CSV path | optional report/JSON | none | stable |
| `validate-bib` | Audit BibTeX and registry linkage | `.bib`, optional registry | optional report | none | stable |
| `add-paper` | Append explicit metadata | user-supplied flags | registry CSV row | append only | stable |
| `list` | List local registry rows | registry/project filters | stdout only | none | stable |
| `note-template` | Create structured note template | paper id, registry/project | Markdown note | refuses overwrite without `--force` | stable |
| `claims` | Extract user-entered claims | notes dir | CSV/Markdown/stdout | output only | stable |
| `search` | Search local data | query | stdout/report | none unless `--out` | stable core; indexed experimental |
| `report` | Generate Markdown reports | registry, BibTeX, notes, themes | Markdown reports | refuses overwrite without `--force` | stable core |
| `checklist` | Generate theme checklist | project/theme | stdout/Markdown | output only | stable |
| `doctor` | Workspace diagnostics | workspace/project | stdout/report | none unless `--out` | stable |
| `dashboard` | Project health summary | workspace/project | stdout/Markdown | none unless `--out` | stable |
| `index` | SQLite search cache | project/local files | `.paperwb/index.sqlite` | cache only | experimental |
| `rebuild` | Incremental rebuild metadata | project | `.paperwb/rebuild_metadata.json`, report | cache/audit state only | experimental |
| `files` | Local file audit/linking | project files | file registry/report | no delete/copy by default | experimental |
| `draft` | Draft citation audit | Markdown draft | reports/checklists | does not rewrite draft | experimental |
| `manuscript` | Manuscript citation QA | Markdown/LaTeX-ish draft | reports/tables | does not rewrite draft | experimental |
| `reading` | Reading sessions | project/paper/session | session logs/reports | explicit status updates only | experimental |
| `followups` | Follow-up actions | notes/sessions | list/export/state | completion state separate from notes | experimental |
| `import` | Local imports | CSV/BibTeX/RIS | registry/report | dry-run supported; no silent overwrite | experimental |
| `export` | Local exports | project/data | CSV/JSON/Markdown/vault/bundle | no overwrite without force | stable core; advanced experimental |
| `sync` | Sync plans and applies | source + registry | plan/report/registry | dry-run/default-safe apply | experimental |
| `integrity` | Structural checks | workspace/project | stdout/report | none unless report | experimental |
| `audit-log` | Local audit log | `.paperwb` JSONL | stdout or cleared log | clear requires `--force` | experimental |
| `backup` | Backup/restore | project | backup/restore plan | restore dry-run unless `--force` | experimental |
| `migrate` | Legacy-to-project migration | legacy data | plan/copy report | plan/dry-run first; copy-only | experimental |
| `rules` | Declarative validation | JSON rules | findings/report | read-only except report | experimental |
| `workflow` | Declarative recipes | built-in or JSON recipe | workflow report | dry-run/write gates; no shell/Python execution | experimental |
| `graph` | Evidence graph | project data | stdout/Markdown/JSON/DOT | read-only except `--out` | experimental |
| `claim-review` | Claim lifecycle review | parsed claims + sidecar | sidecar/report | explicit `mark` writes only | experimental |
| `contradictions` | Manual tension groups | parsed claims + sidecar | sidecar/report | explicit create/add writes only | experimental |
| `review-packet` | File-based collaboration | project/theme/draft/comments | packet/comments sidecar/reports | never rewrites evidence | experimental |
| `synthetic` | Stress/test fixtures | generator options | synthetic project | refuses existing without force | internal utility |

## Exit Codes

- `0`: command completed. Warnings may still indicate incomplete local data.
- `0` with printed `ERROR` findings: validation completed in non-strict review
  mode.
- `1`: release script or smoke workflow failure.
- `2`: user-facing error such as missing input, invalid option, overwrite
  refusal, missing project, unsafe path, or invalid backup.

## Stable Command Coverage Expectations

Stable command groups should have help tests, at least one happy path, common
failure-path coverage, and non-destructive/output-path coverage where relevant.
Experimental commands should at minimum have smoke tests and safety tests for
dry-run, force, or no-overwrite behavior.
