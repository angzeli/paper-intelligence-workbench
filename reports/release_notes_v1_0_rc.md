# Release Notes v1.0-rc

Paper Intelligence Workbench v1.0-rc is a local release-candidate hardening
pass. It is not published, tagged, or pushed by this work.

## Added

- API surface inventory in `docs/API_SURFACE.md`.
- CLI surface inventory in `docs/CLI_SURFACE.md`.
- Command-contract documentation in `docs/COMMAND_CONTRACTS.md`.
- Command-contract tests for help output, safe report overwrite behavior,
  dry-run import behavior, failure-path error quality, and RC scripts.
- `scripts/clean_room_install_check.py` for a current-environment clean-room
  workflow check.
- v1.0-rc reports for clean-room install checks, external-user simulation, data
  safety, known limitations, release notes, and post-v1.0 planning.

## Updated

- Documentation index, CLI reference, installation docs, report gallery,
  roadmap, README, AGENTS guidance, and changelog.
- CI now runs the clean-room check in quick mode.
- Data-safety report generation can use a release-specific title while
  preserving the v0.10 default.

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
- The package version remains `0.10.0` until an explicit version bump/tag step is
  requested.
