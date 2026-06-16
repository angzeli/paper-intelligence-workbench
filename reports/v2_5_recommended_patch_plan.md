# v2.5 Recommended Patch Plan

## Recommended Scope

Focus v2.5 on performance, scale, incremental rebuilds, and cache hygiene for
larger local projects.

## Candidate Work

- Add simple content hashing for notes, claims, reports, and search indexes.
- Add an incremental rebuild plan/status command.
- Add cache invalidation reports.
- Add performance sanity scripts that use synthetic data only.
- Improve `.gitignore` coverage for rebuild metadata and stress outputs.
- Keep standard tests fast; put large stress runs behind explicit scripts.

## Boundaries

- Do not add heavy dependencies.
- Do not add cloud, LLM, scraping, or remote sync behavior.
- Do not optimize at the cost of clear local data flow.
- Do not commit cache state, stress-output databases, backups, audit logs, PDFs,
  or copied full text.
