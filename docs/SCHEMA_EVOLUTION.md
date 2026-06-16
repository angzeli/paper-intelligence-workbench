# Schema Evolution

Paper Intelligence Workbench has evolved from a small legacy `data/` workflow
to project profiles with structured notes, claims, evidence maps, support
bundles, and compatibility diagnostics.

## Registry Evolution

- Early registries only required `paper_id`, `title`, `authors`, and `year`.
- Later versions added BibTeX keys, local file paths, reading status, priority,
  project, source type, relevance, inclusion, and comments.
- Extra user columns are allowed in local CSV files. Core loaders ignore unknown
  fields, while copy-based migration preserves the raw CSV.

## Note Evolution

- Structured Markdown notes remain the stable source of user-entered claims.
- Unknown or malformed note fields should create warnings, not invented claims.

## Project Evolution

- Early project folders may omit `project.json`; default project paths are still
  inspectable.
- Current project profiles should keep registry, BibTeX, notes, themes, reports,
  and optional sidecars inside the project root.

