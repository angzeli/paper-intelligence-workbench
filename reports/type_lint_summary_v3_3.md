# Type and Lint Summary v3.3

## Tool Choice

- Ruff is selected for linting and format checks because it is lightweight and
  fast.
- Mypy is selected for type-checking release/quality scripts only.
- Package-wide type checking is not enabled in v3.3 because the current package
  baseline has many legacy typing errors and fixing them would require broad
  refactors.

## Ruff Scope

Ruff is configured with narrow `F` rules first. This catches undefined names and
similar correctness issues without triggering broad style churn across the
large existing codebase.

Format-check starts with `scripts/run_quality_gate.py`, the new script added in
this patch.

## Mypy Scope

Mypy checks files under `scripts/` with followed imports skipped, so release
script typing can improve without making package-wide typing a release blocker.

Current local result:

```text
Success: no issues found in 8 source files
```

## Deferred Work

- Expand ruff rule coverage after dogfooding.
- Format more files only when the team is ready for style churn.
- Reduce package-wide mypy errors module by module.
- Keep build validation local-first by avoiding isolated network dependency
  installation.
