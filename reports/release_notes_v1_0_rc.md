# Release Notes v1.0-rc

Paper Intelligence Workbench v1.0-rc is a local release-candidate hardening
pass. It is not published, tagged, or pushed by this work.

## Added

- API surface inventory in `docs/API_SURFACE.md`.
- CLI surface inventory in `docs/CLI_SURFACE.md`.
- Command-contract documentation in `docs/COMMAND_CONTRACTS.md`.
- Command-contract tests for help output, safe report overwrite behavior,
  dry-run import behavior, failure-path error quality, and RC scripts.
- `scripts/clean_room_install_check.py` for a current-environment release
  workflow check with documented fresh-venv commands.
- v1.0-rc reports for current-environment checks, external-user simulation, data
  safety, known limitations, release notes, and post-v1.0 planning.

## Updated

- Documentation index, CLI reference, installation docs, report gallery,
  roadmap, README, AGENTS guidance, and changelog.
- CI now runs the current-environment release check in quick mode, verifies the
  installed `paperwb` console script, builds source/wheel distributions, and
  tests Python 3.10, 3.11, and 3.12.
- Data-safety report generation can use a release-specific title while
  preserving the v0.10 default.
- Package metadata is aligned to the release-candidate version `1.0.0rc1`.
- `paperwb claims --output` and `paperwb validate-registry --json` now refuse
  existing files unless `--force` is explicit.

## Boundaries Confirmed

- Local-first only.
- No cloud APIs.
- No LLM APIs.
- No publisher scraping.
- No copyrighted PDFs or full-text examples.
- No claim, citation, quote, summary, or final-prose fabrication.
- Evidence and citation reports audit completeness, not scientific truth.

## Compatibility

- Existing CLI commands are preserved.
- The legacy `data/` workflow remains supported.
- Project profiles under `projects/` remain supported.
- The package version is `1.0.0rc1`; final v1.0.0 tagging remains a separate
  maintainer action.
