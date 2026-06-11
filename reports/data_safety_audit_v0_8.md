# Data Safety Audit v0.8

This audit checks tracked and unignored repository files. It does not inspect ignored user caches, local PDFs, or ignored private files.

Root: .
Repository files checked: 402
Errors: 0
Warnings: 12

## Summary By Code

| Code | Count |
| --- | ---: |
| absolute_local_path | 12 |

## Findings

- **warning absolute_local_path** `reports/external_user_simulation_final.md`: Text contains local absolute-path pattern `/private/[^\s`|,\"]+`.
- **warning absolute_local_path** `reports/hostile_review_latest.md`: Text contains local absolute-path pattern `/private/[^\s`|,\"]+`.
- **warning absolute_local_path** `reports/hostile_review_v0_4.md`: Text contains local absolute-path pattern `/Users/[^\s`|,\"]+`.
- **warning absolute_local_path** `reports/hostile_review_v0_5.md`: Text contains local absolute-path pattern `/Users/[^\s`|,\"]+`.
- **warning absolute_local_path** `reports/import_bibtex_v0_4.md`: Text contains local absolute-path pattern `/Users/[^\s`|,\"]+`.
- **warning absolute_local_path** `reports/import_generic_csv_v0_4.md`: Text contains local absolute-path pattern `/Users/[^\s`|,\"]+`.
- **warning absolute_local_path** `reports/import_ris_v0_4.md`: Text contains local absolute-path pattern `/Users/[^\s`|,\"]+`.
- **warning absolute_local_path** `reports/import_zotero_csv_v0_4.md`: Text contains local absolute-path pattern `/Users/[^\s`|,\"]+`.
- **warning absolute_local_path** `reports/release_readiness_v0_3.md`: Text contains local absolute-path pattern `/private/[^\s`|,\"]+`.
- **warning absolute_local_path** `reports/release_readiness_v0_6.md`: Text contains local absolute-path pattern `/private/[^\s`|,\"]+`.
- **warning absolute_local_path** `reports/stress_claims_v0_3.csv`: Text contains local absolute-path pattern `/Users/[^\s`|,\"]+`.
- **warning absolute_local_path** `reports/stress_workspace_health_v0_3.md`: Text contains local absolute-path pattern `/Users/[^\s`|,\"]+`.

## Interpretation

- Errors should block release until fixed.
- Warnings identify release-hygiene risks, including historical reports that may contain machine-local paths.
- The audit does not prove that user-supplied text is copyright-safe; examples must remain synthetic and reviewable.
