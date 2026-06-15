# CLI Surface v2

The external interface for Paper Intelligence Workbench is the `paperwb`
command. Commands are local-first, operate on user-provided files, and do not
call cloud APIs, LLM APIs, or publisher scrapers.

This page is an inventory. For the current stability policy, use
[STABLE_SURFACE_V2.md](STABLE_SURFACE_V2.md) and
[EXPERIMENTAL_FEATURES_V2.md](EXPERIMENTAL_FEATURES_V2.md). Do not assume a
command is stable unless the status below says so.

## Command Inventory

| Command | Stability | Contract |
| --- | --- | --- |
| `paperwb init` | stable | Create expected folders without overwriting existing user files |
| `paperwb validate-registry` | stable | Validate a CSV registry and optionally export JSON |
| `paperwb validate-bib` | stable | Validate local BibTeX, optionally linked to a registry |
| `paperwb add-paper` | stable | Append one manually entered registry row |
| `paperwb list` | stable | List and filter registry papers |
| `paperwb note-template` | stable | Generate a structured note without overwrite unless `--force` is used |
| `paperwb claims` | stable | Extract claims from structured Markdown notes |
| `paperwb search` | stable | Run substring search by default; indexed search only with `--indexed` |
| `paperwb report` | stable | Generate Markdown reports and refuse output overwrite unless `--force` is used |
| `paperwb writing-packet` | experimental | Generate a theme-specific writing planning packet, not final prose |
| `paperwb checklist` | stable | Generate a theme review checklist |
| `paperwb draft parse/citations/audit/checklist/evidence-matrix` | experimental | Audit Markdown drafts against local citations and tracked evidence without rewriting prose |
| `paperwb manuscript parse/citations/qa/checklist/trace-claims/context-table/evidence-matrix` | experimental | Run reviewer-style manuscript citation QA against local evidence without rewriting prose |
| `paperwb rules list/validate-config/run/report/explain` | experimental | Run declarative local validation rules without executing arbitrary code or changing user data |
| `paperwb dashboard` | stable | Show a read-only terminal dashboard and optional Markdown report with local project health and next actions |
| `paperwb reading queue/start/finish/status/review` | experimental | Manage local reading queues and session records without reading papers or fabricating notes |
| `paperwb followups list/export/done` | experimental | Collect follow-up actions from notes/sessions and track completion outside source notes |
| `paperwb doctor` | stable | Run workspace-health diagnostics |
| `paperwb project init/list/validate` | stable | Manage local project profiles under `projects/` |
| `paperwb template list/inspect/create` | stable | Create non-destructive empty project scaffolds from local templates |
| `paperwb dogfood create/status/checklist/plan-from-files` | stable | Create empty real-project onboarding scaffolds and read-only metadata-backed starter plans |
| `paperwb import zotero-csv/csv/bibtex/ris` | experimental | Import local bibliography data with dry-run and no silent field overwrite |
| `paperwb sync plan/apply/conflicts/plan-obsidian` | experimental | Plan and dry-run local sync changes before safe registry apply |
| `paperwb export` | stable core, experimental advanced exports | Export registries, claims, reading lists, Obsidian vaults, bundles, summaries, and report indexes |
| `paperwb index rebuild/status/clear` | experimental | Manage a rebuildable local SQLite search cache |
| `paperwb files scan/status/link/unlink/audit/hash/sidecars` | experimental | Inspect and link local user-provided files without deleting or scraping |
| `paperwb integrity check` | experimental | Run read-only workspace integrity checks |
| `paperwb audit-log show/clear` | experimental | Inspect or explicitly clear ignored local audit logs |
| `paperwb backup create/list/inspect/plan-restore/restore` | experimental | Create local snapshots and plan or force restores safely |
| `paperwb migrate plan/run` | experimental | Plan or copy legacy `data/` files into a new project profile without deleting originals |
| `paperwb graph build/summary/export` | experimental | Build a derived local evidence graph and export Markdown, JSON, or DOT summaries |

## Experimental Commands

The inventory above marks experimental command groups inline. See
[EXPERIMENTAL_FEATURES_V2.md](EXPERIMENTAL_FEATURES_V2.md) for rationale and
current cautions.

| Command | Reason |
| --- | --- |
| `paperwb synthetic generate` | Fixture schema and generated corpus shape may change as stress coverage evolves |

## Deprecated Commands

No command groups are deprecated in v2.

## Write Safety Contract

- Commands that write reports or exports refuse to overwrite existing files
  unless `--force` or the command-specific force flag is provided.
- Directory exports require a new or empty destination.
- Imports preserve existing non-empty registry fields unless the user asks for a
  documented fill behavior.
- Sync apply is dry-run by default. Forced sync applies create a backup by
  default, refuse high-risk or stale plans, and do not overwrite non-empty
  registry fields or auto-merge notes.
- Rule commands are read-only except for optional Markdown report outputs, and
  rule files are declarative JSON only.
- `paperwb dashboard` is read-only except for optional `--out` report writes;
  use `--no-audit-log` when generating deterministic release-facing reports.
- Restore and migration workflows default to planning or dry-run behavior unless
  `--force` is passed.
- `paperwb reading start` preserves existing notes by default and requires
  `--force-note` to overwrite a note template.
- Follow-up completion state is stored separately from source notes.
- File workflows do not delete, move, copy, download, OCR, or summarize user
  documents.
- Project-profile commands keep `data/` workflow compatibility.
- Template creation refuses existing project paths and creates empty scaffolds
  only; templates must not include real paper metadata, claims, PDFs, or copied
  paper text.
- Dogfood scaffolds remain empty until users add verified metadata; file plans
  compare filenames with BibTeX keys and do not copy PDFs, read PDF text, or
  write registry rows.

## Command Exit Contract

- `0`: command completed. Warnings may still be printed for incomplete local
  data.
- `1`: release or smoke script failure, usually one or more subcommands failed.
- `2`: user-facing command error such as missing input, output overwrite
  refusal, invalid project, invalid backup, or unsafe option combination.

Common errors should include what happened, where possible where it happened,
why it matters, and a next step. Python tracebacks are not expected for normal
user input errors.

## Interpretation Boundary

Reports and authoring commands organize user-entered local evidence. They do not
judge scientific truth, invent claims, invent citations, fabricate quotes, or
write polished final prose.

Draft and manuscript commands use transparent local heuristics. They flag
possible support gaps for manual checking; they do not certify whether a
paragraph is true.
