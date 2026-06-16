# Deprecated Features v3

v3 does not deprecate any public CLI command group outright.

## Secondary Or Legacy Paths

- Legacy top-level `data/` examples remain supported for compatibility and
  tests, but new real work should use project profiles under `projects/`.
- Lowercase docs such as `docs/getting-started.md` and `docs/cli-reference.md`
  remain historical site-source pages. Prefer the v3 docs for release-candidate
  orientation.
- Generated historical reports remain in `reports/` for traceability. They are
  not current release guidance unless listed in `reports/index.md` as current.

## Deprecated Behavior Policy

Before removing or changing stable behavior, maintainers should:

1. Document the change in `CHANGELOG.md`.
2. Add a migration note or compatibility note.
3. Keep a non-destructive migration plan where local files are involved.
4. Add command-contract tests for the new behavior.

## Not Planned

- Cloud sync.
- LLM summarization.
- Publisher scraping.
- Automatic claim verification.
- Arbitrary executable plugins.
- Web app UI.
