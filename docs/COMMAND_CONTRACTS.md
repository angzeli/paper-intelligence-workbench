# Command Contracts v1.5

This page defines the v1.5 behavior expected by tests and external
users. The contract is intentionally practical: it describes command behavior,
not internal implementation details.

## Global Contract

- `paperwb --help` must work after editable install and through
  `python -m paper_workbench.cli --help`.
- Commands must remain local-first and must not require network access,
  secrets, cloud services, LLM APIs, publisher scraping, or copyrighted example
  files.
- Normal bad inputs should return a user-facing error without a Python
  traceback.
- Generated files should be reproducible from local inputs.
- Existing reports, exports, note templates, and audit outputs must not be
  overwritten without an explicit force flag.

## Major Command Coverage

| Command | Help covered | Happy path | Failure path | Non-destructive check |
| --- | --- | --- | --- | --- |
| `init` | yes | temp workspace init | existing files preserved | folder creation only |
| `project` | yes | list and validate synthetic projects | missing project | no legacy data mutation |
| `validate-registry` | yes | example registry | missing/malformed registry | JSON export refuses overwrite without `--force` |
| `validate-bib` | yes | example BibTeX | broken/missing BibTeX | report preflight |
| `import` | yes | dry-run Zotero/generic/BibTeX/RIS | bad mapping/missing columns | registry unchanged on dry-run |
| `sync` | yes | plan/apply dry-run/conflicts/Obsidian plan | high-risk conflict or overwrite refusal | dry-run by default; no note auto-merge |
| `add-paper` | yes | synthetic row append in temp tests | invalid reading status | appends only to selected registry |
| `list` | yes | filtered example listings | missing registry | read-only |
| `note-template` | yes | temp note output | missing paper or overwrite refusal | no overwrite without `--force` |
| `claims` | yes | example notes to temp CSV | missing notes path or malformed notes | output CSV refuses overwrite without `--force`; note files preserved |
| `search` | yes | substring and indexed examples | missing index with `--indexed` | read-only unless `--out` |
| `index` | yes | temp SQLite index rebuild/status | stale or missing index | cache is rebuildable and ignored |
| `files` | yes | scan/audit/hash sidecars | missing files or overwrite refusal | no delete/move/copy |
| `report` | yes | inventory/evidence/citation/authoring reports | missing theme, invalid `report all --out`, or overwrite refusal | no overwrite without `--force`; `report all` preflights every output before writing |
| `writing-packet` | yes | synthetic theme packet | unknown theme | planning aid only |
| `draft` | yes | parse/audit/checklist synthetic drafts | unknown citations or overwrite refusal | no draft rewrite; reports only |
| `manuscript` | yes | parse/qa/context/trace synthetic manuscripts | unknown citations or overwrite refusal | no manuscript rewrite; reports only |
| `rules` | yes | list/validate/run/report synthetic project rules | invalid config or overwrite refusal | no user data mutation; JSON rules only |
| `reading` | yes | temp queue/start/finish/status/review | invalid status or missing session | existing notes preserved unless `--force-note` |
| `followups` | yes | list/export/done temp actions | missing state path tolerated | source notes preserved; completion state stored separately |
| `doctor` | yes | workspace-health report | missing inputs | read-only unless `--out` |
| `integrity` | yes | project integrity check | unsafe path/missing project | read-only unless `--out` |
| `audit-log` | yes | show ignored logs | clear without force | clear requires `--force` |
| `backup` | yes | create/list/inspect/plan restore | missing/corrupt backup | restore dry-run unless `--force` |
| `migrate` | yes | legacy migration plan/dry-run | target conflicts | copies only, never deletes legacy data |
| `export` | yes | temp CSV/JSON/Markdown outputs | overwrite refusal | no overwrite without `--force` |
| `synthetic` | yes | generated temp stress project | existing target without force | restricted to named synthetic output |

## Report And Authoring Boundary

Authoring commands generate outlines, matrices, banks, paragraph plans,
readiness checks, and writing packets. They must not produce polished literature
review prose as if it were user-authored, and they must not infer claims from
papers without user-entered notes.

Draft and manuscript commands audit manuscript text and emit reports, matrices,
tables, and checklists. They must not rewrite the user draft or invent missing
citations.

## Test Mapping

Representative contract tests live in:

- `tests/test_cli.py`
- `tests/test_cli_stress.py`
- `tests/test_import_export_v0_4.py`
- `tests/test_index_v0_5.py`
- `tests/test_authoring_workbench.py`
- `tests/test_local_files_v0_7.py`
- `tests/test_integrity_backup_migration_v0_9.py`
- `tests/test_adversarial_v0_10.py`
- `tests/test_v1_0_rc_command_contracts.py`
- `tests/test_drafts_v1_1.py`
- `tests/test_reading_v1_2.py`
- `tests/test_sync_v1_3.py`
- `tests/test_manuscript_v1_4.py`
- `tests/test_rules_v1_5.py`

Release scripts used by the contract:

- `scripts/smoke_cli_workflow.py`
- `scripts/check_notebooks.py`
- `scripts/validate_notebooks.py`
- `scripts/data_safety_audit.py`
- `scripts/clean_room_install_check.py`
