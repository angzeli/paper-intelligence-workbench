# Report Regression Testing

Reports are user-facing artifacts. Report stability is part of the test surface.

## Test Types

- Golden snapshot tests compare full normalized Markdown output for stress reports.
- Scale-visibility assertions check important counts such as paper, BibTeX, and missing-evidence totals.
- Stable authoring assertions check v0.6 writing-workbench sections and counts for strong, weak, and missing-evidence cases.
- CLI stress tests generate reports through the public command interface.

## Why Sorting Matters

Reports must avoid nondeterministic ordering from Python sets or filesystem iteration. When report content is derived from sets, sort identifiers before rendering.

## When Tests Fail

If a golden or stable report test fails:

1. Inspect the diff.
2. Decide whether the change is intentional.
3. If intentional, regenerate the snapshot from the deterministic stress project or update the stable assertion with the new expected user-facing behavior.
4. Update documentation when the user-facing report behavior changed.

Do not update snapshots to hide a regression.
