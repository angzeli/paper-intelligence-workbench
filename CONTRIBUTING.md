# Contributing

Paper Intelligence Workbench is a local-first research workflow tool. Contributions should preserve user-owned notes, registries, and local files.

## Development Setup

```bash
python -m pip install -e ".[dev]"
python scripts/run_quality_gate.py --list
```

The package intentionally has no runtime dependencies. Add dependencies only when they remove meaningful complexity and keep optional tooling separated under `project.optional-dependencies`.

## Safety Rules

- Do not add copyrighted PDFs or copied paper full text.
- Do not fabricate real paper metadata, claims, quotes, or conclusions.
- Do not scrape publishers, call cloud APIs, or use LLM APIs.
- Do not overwrite user notes or registry metadata without explicit force behavior.
- Keep SQLite indexes and generated caches out of git.
- Keep generated examples synthetic and clearly labelled.

## Tests

Add or update tests for parser behavior, validation rules, CLI workflows, reports, importers, exporters, local-file handling, search/indexing, and release scripts. Prefer small synthetic fixtures.

## Documentation

Update docs when public CLI behavior changes. Documentation examples should use synthetic data and avoid machine-specific absolute paths.

## Release Checks

Before a release-ready patch, run:

```bash
python scripts/run_quality_gate.py release
```

Do not push from an automated agent unless explicitly asked.
