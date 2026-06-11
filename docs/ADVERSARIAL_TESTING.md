# Adversarial Testing

v0.10 adds a synthetic adversarial fixture library under `tests/fixtures/adversarial/`.

The fixtures intentionally include malformed, incomplete, duplicated, and unsafe local data. They are used to verify that Paper Intelligence Workbench fails safely, emits useful warnings, and avoids destructive behavior.

## Fixture Areas

- `registries/`: malformed CSV rows, missing headers, duplicate IDs, DOI variants, invalid years, invalid statuses, path escapes.
- `bibtex/`: nested braces, quoted fields, duplicate keys, DOI variants, incomplete entries, unsupported types, unclosed entries.
- `notes/`: missing metadata, missing paper IDs, malformed claim headings, invalid evidence types, invalid strengths, missing confidence, missing evidence locations.
- `imports/`: missing Zotero columns, bad generic CSV mappings, RIS records without `ER`.
- `projects/`: broken project profile paths and orphan notes.
- `sidecars/`: unmatched synthetic text sidecars.
- `expected/`: representative warning codes.

## Test Intent

Adversarial tests prioritize:

- no Python tracebacks for common bad input
- clear error messages with next steps
- conservative warnings instead of guessed fixes
- report generation on imperfect data
- non-destructive restore and migration behavior

All fixtures are synthetic. Do not replace them with real paper metadata, copyrighted PDFs, or copied paper full text.
