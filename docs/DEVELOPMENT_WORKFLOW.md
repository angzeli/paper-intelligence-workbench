# Development Workflow

Use this workflow for local changes.

## Setup

```bash
python -m pip install -e ".[dev]"
```

The package has no runtime dependencies. Development extras add pytest, build,
setuptools, ruff, and mypy for local quality checks. `setuptools` is included
because the release gate runs the distribution build without build isolation.

## Before Editing

```bash
git status --short --branch --ignored
python -m paper_workbench.cli --help
```

Read `AGENTS.md` before changing safety-sensitive workflows.

## During Development

- Keep changes small and reviewable.
- Preserve stable CLI behavior unless fixing a documented bug.
- Use synthetic fixtures only.
- Do not commit PDFs, cache databases, audit logs, backups, private notes, or
  private dogfood outputs.
- Add focused tests for behavior changes.

## Before Final Response

Run the relevant targeted checks, then run the release gate when quality,
release, CI, or public CLI behavior changes:

```bash
python scripts/run_quality_gate.py release
```

In a bootstrap environment without optional tools, this command can be used only
as a diagnostic preview:

```bash
python scripts/run_quality_gate.py local-diagnostic
```

CI and release validation should not skip missing tools.
