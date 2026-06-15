# Data Safety Audit v2.2

This audit checks tracked and unignored repository files. It does not inspect ignored user caches, local PDFs, or ignored private files.

Root: .
Repository files checked: 653
Errors: 0
Warnings: 7

## Summary By Code

| Code | Count |
| --- | ---: |
| absolute_local_path | 7 |

## Findings

- **warning absolute_local_path** `reports/hostile_review_v0_4.md`: Text contains local absolute-path pattern `/Users/[^\s`|,\"]+`.
- **warning absolute_local_path** `reports/hostile_review_v0_5.md`: Text contains local absolute-path pattern `/Users/[^\s`|,\"]+`.
- **warning absolute_local_path** `reports/release_readiness_v0_3.md`: Text contains local absolute-path pattern `/private/[^\s`|,\"]+`.
- **warning absolute_local_path** `reports/release_readiness_v0_6.md`: Text contains local absolute-path pattern `/private/[^\s`|,\"]+`.
- **warning absolute_local_path** `tests/test_integrity_backup_migration_v0_9.py`: Text contains local absolute-path pattern `/private/[^\s`|,\"]+`.
- **warning absolute_local_path** `tests/test_release_hygiene.py`: Text contains local absolute-path pattern `/private/[^\s`|,\"]+`.
- **warning absolute_local_path** `tests/test_v2_release_candidate.py`: Text contains local absolute-path pattern `/private/[^\s`|,\"]+`.

## Interpretation

- Errors should block release until fixed.
- Warnings identify release-hygiene risks, including historical reports that may contain machine-local paths.
- The audit does not prove that user-supplied text is copyright-safe; examples must remain synthetic and reviewable.
