# Command Reference

Use `paperwb --help` and `paperwb COMMAND --help` as the authoritative CLI
reference. This page groups the current command surface by expected stability.

## Stable Starting Points

| Command | Purpose |
| --- | --- |
| `paperwb init` | Create missing local workspace folders. |
| `paperwb project` | Manage project profiles. |
| `paperwb template` | Create empty or synthetic project scaffolds. |
| `paperwb dogfood` | Create empty real-project onboarding scaffolds and file plans. |
| `paperwb validate-registry` | Validate registry CSV files. |
| `paperwb validate-bib` | Validate BibTeX files and registry linkage. |
| `paperwb add-paper` | Append one explicit user-provided registry row. |
| `paperwb list` | List registry rows with local filters. |
| `paperwb note-template` | Generate structured note templates. |
| `paperwb claims` | Extract user-entered claims from structured notes. |
| `paperwb report` | Generate stable core Markdown reports. |
| `paperwb checklist` | Generate theme review checklists. |
| `paperwb doctor` | Run read-only workspace diagnostics. |
| `paperwb dashboard` | Show read-only project health and next actions. |
| `paperwb support` | Create sanitized diagnostics and support bundles. |
| `paperwb compatibility` | Inspect historical workspace layouts and migration readiness. |

## Experimental Or Safety-Sensitive Groups

Use these with project-local synthetic data first, and prefer `--dry-run` where
available:

- `paperwb workflow`
- `paperwb review-packet`
- `paperwb import`
- `paperwb sync`
- `paperwb search --indexed`
- `paperwb index`
- `paperwb rebuild`
- `paperwb files`
- `paperwb draft`
- `paperwb manuscript`
- `paperwb reading`
- `paperwb followups`
- `paperwb graph`
- `paperwb rules`
- `paperwb backup`
- `paperwb migrate`
- `paperwb audit-log`
- `paperwb claim-review`
- `paperwb contradictions`

## Common Flags

| Flag | Meaning |
| --- | --- |
| `--project` | Use `projects/<project>/` paths. |
| `--root` | Use a different workspace root where supported. |
| `--strict` | Return non-zero on error-level validation findings. |
| `--out` | Write a report or export to a path. |
| `--force` | Overwrite an existing output where supported. |
| `--dry-run` | Plan or preview without applying writes where supported. |
| `--no-audit-log` | Avoid writing audit-log events for read-only shared output where supported. |

## Exact Reference Files

- [CLI Reference v3](../CLI_REFERENCE_V3.md)
- [Command Contracts v3](../COMMAND_CONTRACTS_V3.md)
- [Stable Surface v3](../STABLE_SURFACE_V3.md)
- [Experimental Features v3](../EXPERIMENTAL_FEATURES_V3.md)
