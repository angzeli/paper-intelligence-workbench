# Golden Reports

v0.3 adds golden Markdown snapshots for representative stress reports. These tests are meant to catch accidental report-format or report-order changes.

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

## Running

```bash
python -m pytest tests/test_golden_reports.py
```

The snapshots are generated from the checked-in `stress_zis_photocatalysis` project.

## Updating Intentionally

Only update golden snapshots when report behavior intentionally changes. Before updating, inspect the diff and confirm it reflects a desired user-facing change.

Avoid snapshot content that depends on:

- absolute paths
- timestamps
- random ordering
- local machine details

The v0.3 snapshot helper normalizes the repository root path before comparison.

