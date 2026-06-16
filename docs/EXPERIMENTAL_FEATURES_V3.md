# Experimental Features v3

These workflows are useful for local dogfooding but are not API-frozen in
v3. They should stay conservative, local, and explicit.

| Area | Commands | Why experimental |
| --- | --- | --- |
| Indexed search | `index`, `search --indexed` | SQLite cache format is rebuildable and may change. |
| Local file registry | `files` | File path policies and sidecar audits need more real-use feedback. |
| Import/export advanced flows | `import`, advanced `export` outputs | Mapping rules and vault/bundle outputs may evolve. |
| Sync and conflict planning | `sync` | `apply` is safe and dry-run-first, but reconciliation policy is not frozen. |
| Backup/restore/migration | `backup`, `migrate`, `audit-log`, `integrity` | Read-only checks are safer; forced writes remain safety-sensitive. |
| Draft and manuscript QA | `draft`, `manuscript` | Matching is heuristic and must not be treated as scientific certainty. |
| Reading sessions | `reading`, `followups` | Session sidecars and follow-up state may evolve. |
| Rule engine | `rules` | Declarative rule schema is safe but not complete enough to freeze. |
| Evidence graph | `graph` | Graph JSON/DOT exports are derived views and may change. |
| Claim lifecycle | `claim-review`, `contradictions` | Sidecar schemas are review metadata, not stable claim data. |
| Workflow runner | `workflow` | Recipe schemas are declarative and safe, but still dogfooding. |
| Review packets | `review-packet` | Packet and imported-comment schemas are local collaboration experiments. |
| Incremental rebuilds | `rebuild` | Cache metadata is ignored state and may change. |
| Synthetic generators | `synthetic` | Test/stress utility, not a user-facing stable workflow. |

## Rules For Experimental Workflows

- Prefer `--dry-run` where available.
- Write reports to `scratch/` or project `reports/` first.
- Do not use experimental outputs as machine-stable APIs.
- Keep user data untouched unless a command explicitly documents the write.
- Treat heuristic warnings as prompts for manual review, not truth judgments.
