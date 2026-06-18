# v3.4 Recommended Patch Plan

## Recommended Focus

Keep v3.4 focused on tightening the quality baseline after real dogfooding.

## Suggested Work

1. Install and run ruff locally in the normal development environment.
2. Expand ruff rules only after measuring current findings.
3. Add a README quickstart transcript test.
4. Add a strict warning or explicit `--allow-empty` behavior for empty review packets.
5. Split selected CLI helper paths only where command-contract tests already exist.
6. Start package-wide typing one module at a time, beginning with low-dependency modules.

## Not Recommended

- Do not add another major product subsystem.
- Do not run broad autoformatting across the repository without a dedicated review.
- Do not make package-wide mypy a release blocker until the baseline is reduced.
