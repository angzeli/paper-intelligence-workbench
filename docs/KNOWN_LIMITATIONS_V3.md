# Known Limitations v3

v3 is dogfoodable, but not a fully automated research assistant.

## Evidence And Writing

- The tool tracks evidence completeness, not scientific truth.
- Claims are only as good as user-written structured notes.
- Manuscript and draft matching is heuristic keyword/citation overlap.
- Generated writing packets are planning aids, not final prose.

## Data And Imports

- Imports are conservative and may require manual mapping review.
- Sync apply is experimental and should be run dry-run first.
- PDF metadata is advisory and should not be trusted as paper metadata.
- Real PDFs and full text are intentionally excluded from examples.

## Scale

- Incremental rebuilds and indexed search are useful but experimental.
- Hundreds of papers are a realistic local target; very large projects need
  periodic report cleanup and cache hygiene.

## Architecture

- `paper_workbench/cli.py` remains large.
- Several advanced modules still own local report rendering.
- Historical docs and reports are noisy because the repo preserves release
  evidence from the v0-v2 cycle.
