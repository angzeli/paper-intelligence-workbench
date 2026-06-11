# Adversarial Test Summary v0.10

## Summary

v0.10 adds a synthetic adversarial fixture library and regression tests for malformed local inputs. The goal is safe failure behavior, not broader feature expansion.

## Fixture Library

Fixtures added under `tests/fixtures/adversarial/`:

- `registries/`: malformed registry rows and missing headers.
- `bibtex/`: duplicate keys, DOI variants, nested braces, unsupported types, incomplete entries, and unclosed entries.
- `notes/`: missing metadata, malformed claim blocks, invalid evidence type/strength/status, missing confidence, and missing evidence locations.
- `imports/`: missing Zotero fields, bad generic mapping, missing mapped source columns, and RIS without `ER`.
- `projects/`: project profile with escaping paths and orphan notes.
- `sidecars/`: unmatched synthetic text sidecar.
- `expected/`: representative warning/error codes.

## Tests Added

`tests/test_adversarial_v0_10.py` covers:

- registry validation on malformed CSV rows
- missing registry headers
- BibTeX parse recovery and warning reports
- malformed note parsing
- report generation with imperfect data
- import failure-path error messages
- RIS recovery without `ER`
- corrupted audit log lines
- corrupted backup manifests
- broken project profile paths
- CLI failure paths without tracebacks

## Safety Outcome

The suite verifies that common malformed inputs produce warnings or actionable errors rather than destructive writes or Python tracebacks.
