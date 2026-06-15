# Command Contracts v2

This page freezes the v2.0 command expectations for external dogfooding. It
documents command behavior, not internal implementation details.

## Global Contract

- `paperwb --help` must work after editable install.
- `python -m paper_workbench.cli --help` must also work from the repository root.
  It is not the recommended form inside initialized workspaces because a local
  workspace `paper_workbench/` data folder can shadow the installed package.
- Commands must remain local-first and must not require cloud APIs, LLM APIs,
  publisher scraping, secrets, copyrighted PDFs, or copied paper full text.
- Normal bad input should return a user-facing error, not a Python traceback.
- Report, export, note-template, backup, migration, and sync outputs must not
  overwrite user files without explicit force flags.
- Validation and audit commands default to review mode: they print findings and
  complete successfully unless the command itself fails. Use `--strict` in CI or
  release checks when error-level findings should return non-zero.

## Command Map

| Command group | Purpose | Inputs | Outputs | Write behavior | Status | Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| `init` | Create folders | optional `--root` | workspace dirs | creates missing dirs only | stable | command-contract, smoke |
| `project` | Profiles | project name | `projects/<name>` files | non-destructive init/validate | stable | project tests |
| `template` | Empty scaffolds | template id, project | project scaffold | refuses existing target | stable | template tests |
| `dogfood` | Real-project onboarding | template id, project, optional local paths | empty scaffold or planning report | refuses existing target; plan-from-files is read-only unless `--out` | stable | dogfood tests |
| `validate-registry` | Registry audit | CSV | findings, optional JSON/report | read-only unless output path | stable | registry tests |
| `validate-bib` | BibTeX audit | `.bib`, optional registry | findings/report | read-only unless report | stable | BibTeX tests |
| `add-paper` | Append row | CLI metadata | registry CSV | appends only selected registry | stable | CLI tests |
| `list` | Registry listing | registry/project | stdout table | read-only | stable | CLI tests |
| `note-template` | Note template | paper id, registry/project | Markdown note | no overwrite without force | stable | note tests |
| `claims` | Claim extraction | notes dir | stdout/CSV/Markdown | output only | stable | note/claim tests |
| `search` | Search | query, local files | stdout/Markdown | read-only unless `--out` | stable; indexed experimental | search/index tests |
| `index` | SQLite cache | project/local files | `.paperwb/index.sqlite` | rebuildable cache only | experimental | index tests |
| `files` | Local file audit | project files | scan/audit reports | no delete/move/copy by default | experimental | local-file tests |
| `report` | Markdown reports | registry/BibTeX/notes/themes | Markdown | no overwrite without force | stable core, experimental authoring | report tests |
| `writing-packet` | Writing planning | project/theme | Markdown packet | output only | experimental | authoring tests |
| `checklist` | Theme checklist | project/theme | stdout/Markdown | output only | stable | report tests |
| `draft` | Draft audit | Markdown draft | reports/checklists | does not rewrite draft | experimental | draft tests |
| `manuscript` | Manuscript QA | Markdown/LaTeX-ish draft | QA/context/trace reports | does not rewrite draft | experimental | manuscript tests |
| `reading` | Reading sessions | project/paper/session | session logs/reports | explicit status updates only | experimental | reading tests |
| `followups` | Follow-up actions | notes/sessions | list/export/state | completion state separate from notes | experimental | reading tests |
| `import` | Local imports | CSV/BibTeX/RIS | registry/report | dry-run supported; no silent overwrite | experimental | import tests |
| `export` | Local exports | project/data | CSV/JSON/Markdown/vault/bundle | no overwrite without force | stable core, experimental bundle/vault | import/export tests |
| `sync` | Sync plans | source + registry | plan/report | plan first; apply dry-run by default | experimental | sync tests |
| `doctor` | Workspace health | workspace/project | findings/report | read-only unless report | stable | doctor tests |
| `integrity` | Structural checks | workspace/project | findings/report | read-only unless report | experimental | integrity tests |
| `audit-log` | Audit log | `.paperwb` JSONL | stdout | clear requires force | experimental | integrity tests |
| `backup` | Snapshots/restore | project | backup/restore plan | restore dry-run unless force | experimental | backup tests |
| `migrate` | Legacy-to-project | legacy data | plan/copy report | plan/dry-run first; copy-only | experimental | migration tests |
| `rules` | Declarative checks | JSON rules | findings/report | read-only except report | experimental | rule tests |
| `dashboard` | Summary | project/workspace | stdout/Markdown | read-only except `--out` | stable | dashboard tests |
| `synthetic` | Fixtures | generator options | synthetic project | refuses existing without force | internal/test utility | synthetic tests |

## Exit Codes

- `0`: command completed. Warnings may still indicate incomplete local data.
- `0` with printed `ERROR` findings: validation completed in non-strict review
  mode. Re-run with `--strict` when error-level findings should fail a script.
- `1`: release script or smoke workflow failure.
- `2`: user-facing error such as missing input, invalid option, overwrite
  refusal, missing project, unsafe path, or invalid backup.
