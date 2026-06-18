# Release Readiness v3.5

## Features Added

- Local-only external workspace registry.
- `paperwb external ...` CLI group.
- Private dogfooding documentation.
- `.paperwb-local/` ignore and data-safety protection.
- Tests for external workspace registration, validation, bounded runs, support
  redaction, backup safety, and missing paths.

## Commands Checked

```bash
paperwb external --help
paperwb external add
paperwb external list
paperwb external validate
paperwb external run
paperwb external remove
```

Representative external workflows are covered by tests using temporary
synthetic external workspaces.

## Data-safety Assessment

The v3.5 adapter is pointer-based. It writes ignored local config and runs
existing local workflows against the registered path. It does not copy private
workspace files into the repository. Support bundles remain safe by default.

## Known Limitations

- Strict release validation still requires development tooling to be installed
  locally or in CI.
- `paper_workbench/cli.py` remains large.
- External mode does not support arbitrary command forwarding.
- External workspaces currently need project-profile layout compatibility.

## Verdict

Ready for local dogfooding as a v3.5 patch after full test and smoke
validation.

