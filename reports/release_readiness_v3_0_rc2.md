# Release Readiness v3.0rc2

## Scope

v3.0rc2 is a public-release cleanup and dogfooding-readiness label layered on top of package metadata `3.5`. It is not a package-version rollback.

## Cleanup Performed

- Simplified the public README.
- Clarified the docs landing page.
- Added generated-report policy documentation.
- Added artifact inventory and report archive plan.
- Added first real dogfooding plan.
- Added final public-push readiness verdict.

## Artifact Status

- No tracked PDFs, cache databases, backup archives, raw audit logs, `.paperwb/`, `.paperwb-local/`, `.DS_Store`, build outputs, or egg-info artifacts should be committed.
- Ignored local artifacts are present in the working tree and should remain ignored.
- The root reports directory is large but documented; no deletion was performed.

## Validation To Run

- `python -m pytest -q`
- `python scripts/check_docs.py`
- `python scripts/validate_notebooks.py`
- `python scripts/data_safety_audit.py --out scratch/data_safety.md --strict`
- `python scripts/run_quality_gate.py local-diagnostic --out scratch/quality_gate.md`
- stable CLI smoke commands
- external workspace redaction smoke commands

## Known Limitations

- The working tree had pre-existing tracked modifications in code, tests, and one notebook before this cleanup task. Resolve those before tagging or public release.
- Strict release quality gate requires development tooling such as Ruff and build support to be installed.
- Reports should be archived in a future dedicated cleanup after confirming docs and tests do not depend on current paths.
- Experimental command schemas are not frozen.

## Verdict

**Ready for private dogfooding only from this worktree.**

Public push as an experimental repository is reasonable only after the pre-existing tracked modifications are reviewed, committed, or intentionally discarded, and after a final clean-clone data-safety audit.
