# Experimental Features v2

These features are usable for local dogfooding but may change in behavior,
output shape, or internal file format before a future stable release.

| Feature | Commands | Why experimental |
| --- | --- | --- |
| SQLite indexed search | `index`, `search --indexed` | Cache schema is rebuildable and may change. |
| Text sidecar indexing | `index rebuild --include-text`, `search --text` | Sidecars are user-provided and search ranking is simple lexical matching. |
| Import workflows | `import zotero-csv/csv/bibtex/ris` | Column mappings and enrichment policies may need real-world tuning. |
| Export round-trips | `export obsidian`, `sync plan-obsidian` | Markdown round-trip conflict detection is conservative. |
| Sync apply | `sync apply` | Safe registry creates/fill-missing behavior is supported, but conflict policy is intentionally narrow. |
| Reading sessions | `reading`, `followups` | Session log format may evolve as real workflows are dogfooded. |
| Draft/manuscript QA | `draft`, `manuscript` | Evidence matching is heuristic lexical matching, not semantic verification. |
| Authoring workbench | `writing-packet`, authoring reports | Planning aid format may change; reports must not be treated as final prose. |
| Local file ingestion | `files` | File registry and PDF metadata hooks are advisory and local-only. |
| Backup/restore/migration | `backup`, `migrate`, `integrity`, `audit-log` | Dry-run planning is the supported safe path; forced restore/migration needs cautious dogfooding. |
| Rule engine | `rules` | Declarative rule types are stable enough to test, but additional rule types may refine schema. |
| Synthetic corpus generator | `synthetic generate` | Fixture shape may change to improve stress coverage. |

Experimental does not mean unsafe by default. These commands remain local-first,
avoid cloud/LLM APIs, and should refuse destructive behavior unless explicit
force flags are used.

