# Release Readiness v3.1

## Verdict

Ready for local dogfooding.

## Features Added

- `paperwb support bundle`
- `paperwb support doctor`
- `paperwb support redact-preview`
- `paperwb support reproduce`
- Safe support-bundle redaction helpers.
- Sanitized registry and claim sample exports.
- Support bundle manifest, environment, CLI inventory, project structure,
  validation summary, report inventory, schema summary, data-safety summary,
  and reproduction-command outputs.

## Privacy Assessment

Safe mode does not copy PDFs, cache databases, backup archives, raw audit logs,
full notes, full drafts, or private comments. It redacts local paths, local PDF
paths, paper metadata, claim text, quotes, and user comments in diagnostic
samples.

## Commands Checked

- `paperwb support --help`
- `paperwb support bundle --project clean_demo`
- `paperwb support doctor --project clean_demo`
- `paperwb support redact-preview --project clean_demo`
- `paperwb support reproduce --project clean_demo`

## Tests Run

- `pytest tests/test_support_bundle_v3_1.py`
- `pytest tests/test_support_bundle_v3_1.py tests/test_v3_release_candidate.py tests/test_v2_release_candidate.py tests/test_release_hygiene.py tests/test_release_engineering_v0_8.py`
- `pytest`
- `python scripts/data_safety_audit.py --out <tmp>/data_safety_v3_1.md --strict`

Full suite result: 319 passed.

Data-safety audit result: 0 errors, 0 warnings.

## Known Limitations

- Redaction is pattern-based and conservative, not a formal privacy proof.
- Verbose local-only mode is intentionally less redacted and must be inspected
  before sharing.
- Support bundles summarize diagnostics; they do not reproduce every workflow
  failure automatically.

## Recommended v3.2 Scope

Keep v3.2 focused on real-project dogfooding feedback: improve any confusing
diagnostic fields, add targeted redaction rules from observed cases, and avoid
large feature expansion.
