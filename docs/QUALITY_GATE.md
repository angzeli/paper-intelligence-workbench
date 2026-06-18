# Quality Gate

v3.3 introduces a single local quality-gate runner:

```bash
python scripts/run_quality_gate.py --list
python scripts/run_quality_gate.py release
python scripts/run_quality_gate.py local-diagnostic
```

The release target is declarative. It runs only local commands and does not use
cloud services, LLM APIs, publisher scraping, or arbitrary shell snippets.

## Targets

| Target | Purpose |
| --- | --- |
| `tests` | Full pytest suite. |
| `lint` | Ruff lint check. v3.3 starts with Pyflakes-style correctness rules to avoid broad style churn. |
| `format-check` | Ruff format check for the quality-gate script introduced in v3.3. |
| `type-check` | Mypy over release/quality scripts. Package-wide typing remains future work. |
| `smoke` | Non-destructive CLI smoke workflow on synthetic data. |
| `notebooks` | Notebook JSON, title, and absolute-path validation. |
| `data-safety` | Repository data-safety audit for private paths, PDFs, caches, and unsafe artifacts. |
| `build` | Source and wheel distribution build using local build requirements without build isolation. |
| `release` | Runs the full ordered gate: lint, format-check, type-check, tests, smoke, notebooks, data-safety, build. |
| `local-diagnostic` | Runs the same ordered steps as `release`, but skips missing optional tool-backed steps and marks the report as diagnostic only. |

## Missing Tools

Development installs should use:

```bash
python -m pip install -e ".[dev]"
```

If a local bootstrap environment does not have optional tools installed, a
developer can inspect the gate without failing on missing tools:

```bash
python scripts/run_quality_gate.py local-diagnostic --out scratch/quality_gate.md
```

Do not use diagnostic output for CI or release readiness. The `release` target
does not allow missing tools to be skipped.
