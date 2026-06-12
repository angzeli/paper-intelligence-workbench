# Final Release Verdict v2.0rc

## Verdict

Ready for local dogfooding as `2.0.0rc1`.

The repository is coherent enough for a small real literature-review project
after one final maintainer review of the release diff. It is not yet a promise
that every experimental command group is API-stable.

## Blockers

- None found during v2.0rc validation.

## High-Priority Issues

- None found during v2.0rc validation.

## Medium-Priority Issues

- Historical reports are numerous and include older validation contexts. Keep
  them for auditability in this repository, but consider archiving or trimming
  them before presenting a public release branch.
- Experimental interfaces should stay clearly labelled until dogfooding proves
  their shape.

## Stable Features

See `docs/STABLE_SURFACE_V2.md`.

## Experimental Features

See `docs/EXPERIMENTAL_FEATURES_V2.md`.

## Deprecated Features

No CLI command groups are deprecated in v2.0rc.

## Before Tagging

- Full tests passed: 244 tests.
- Smoke workflow passed: 14 steps.
- Notebook validation passed: 8 notebooks.
- Data-safety audit passed: 0 errors and 8 warnings.
- Clean external-user simulation passed.
- No tag should be created until explicitly requested.

## Stable Dogfooding Scope

Use v2.0rc first for registry/BibTeX validation, structured notes, claim
extraction, core reports, project templates, dashboard summaries, backup
planning, and manuscript/draft audit on synthetic or user-owned local data.

## Do Not Expand Before Tagging

- Do not add cloud, LLM, scraping, or PDF-download behavior.
- Do not broaden manuscript/draft matching into semantic claims.
- Do not stabilize sync/index/cache formats prematurely.
- Do not add new major command groups before `v2.0.0rc1` is tagged.

## Recommended Next Step

Perform a final maintainer diff review, confirm no unsafe generated files are
staged, then tag `v2.0.0rc1` only if explicitly approved.
