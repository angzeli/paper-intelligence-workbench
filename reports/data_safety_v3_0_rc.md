# Data Safety Audit v3.0.0rc1

This audit checks tracked and unignored repository files. It does not inspect ignored user caches, local PDFs, or ignored private files.

Root: .
Repository files checked: 746
Errors: 0
Warnings: 0

## Summary By Code

| Code | Count |
| --- | ---: |
| none | 0 |

## Findings

No tracked data-safety findings detected.

## Interpretation

- Errors should block release until fixed.
- Warnings identify release-hygiene risks, including historical reports that may contain machine-local paths.
- The audit does not prove that user-supplied text is copyright-safe; examples must remain synthetic and reviewable.
