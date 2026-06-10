# Report Regression Testing

Reports are user-facing artifacts. v0.3 treats report stability as part of the test surface.

## Test Types

- Golden snapshot tests compare full normalized Markdown output for stress reports.
- Scale-visibility assertions check important counts such as paper, BibTeX, and missing-evidence totals.
- CLI stress tests generate reports through the public command interface.

## Why Sorting Matters

Reports must avoid nondeterministic ordering from Python sets or filesystem iteration. When report content is derived from sets, sort identifiers before rendering.

## When Tests Fail

If a golden report test fails:

1. Inspect the diff.
2. Decide whether the change is intentional.
3. If intentional, regenerate the snapshot from the deterministic stress project.
4. Update documentation when the user-facing report behavior changed.

Do not update snapshots to hide a regression.

