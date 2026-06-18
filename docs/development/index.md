# Development

Use this page for local development and release validation.

## Setup

```bash
python -m pip install -e ".[dev]"
python scripts/run_quality_gate.py --list
```

## Required Checks

For ordinary code and docs changes:

```bash
python -m pytest -q
python scripts/check_docs.py
paperwb --help
```

For release, CI, quality tooling, or public CLI changes:

```bash
python scripts/run_quality_gate.py release
```

If your bootstrap environment is missing development tools, use diagnostic mode
only:

```bash
python scripts/run_quality_gate.py local-diagnostic
```

Diagnostic output is not a strict release-gate pass.

## Maintainer References

- [Quality Gate](../QUALITY_GATE.md)
- [CI](../CI.md)
- [Release Validation](../RELEASE_VALIDATION.md)
- [Contributing](../CONTRIBUTING.md)
- [Maintainer Guide](../MAINTAINER_GUIDE.md)
- [Internal Architecture](../INTERNAL_ARCHITECTURE.md)
- [Public vs Internal API](../PUBLIC_VS_INTERNAL_API.md)
