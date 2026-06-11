# Golden Reports

Golden and stable report regression tests catch accidental report-format, report-order, and report-section changes.

## Location

Snapshots live under:

```text
tests/golden/stress_zis_photocatalysis/
```

Current snapshots cover:

- inventory
- reading status
- BibTeX audit
- citation audit
- evidence map
- theme dashboard
- weak claims
- missing evidence
- workspace health
- section outline

v0.6 authoring reports are covered by stable section/count assertions rather than full-file snapshots. These assertions pin representative strong-claim, weak-claim, and missing-evidence cases without making the tests brittle to harmless wording changes.

## Running

```bash
python -m pytest tests/test_golden_reports.py
```

The snapshots are generated from the checked-in `stress_zis_photocatalysis` project.

## Updating Intentionally

Only update golden snapshots or stable authoring assertions when report behavior intentionally changes. Before updating, inspect the diff and confirm it reflects a desired user-facing change.

Avoid snapshot content that depends on:

- absolute paths
- timestamps
- random ordering
- local machine details

The snapshot helper normalizes the repository root path before comparison.
