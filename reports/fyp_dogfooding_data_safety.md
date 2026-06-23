# FYP Dogfooding Data-safety Check

Date: 2026-06-23

This report summarizes data-safety checks for the FYP ZnIn2S4 dogfooding branch.

## Verdict

No private dogfooding data is intended for commit.

The committed project scaffold is empty or placeholder-only. The full workflow
simulation was run in a temporary synthetic workspace and is summarized in
`reports/fyp_dogfooding_simulation.md` without private paths or real metadata.

## Checked Boundaries

- No PDFs are added to the project scaffold.
- No copied paper full text is added.
- No real BibTeX metadata is committed.
- No real citation shortlist is committed.
- No real paper claims are committed.
- No private external workspace path is committed.
- `.paperwb/` audit logs remain ignored.
- `scratch/`, cache directories, build artifacts, backup archives, and SQLite
  indexes remain ignored.
- Support bundles are generated in safe mode by default and are not committed.

## Committed Scaffold Contents

- Empty `registry.csv` with headers only.
- Empty `bibtex/library.bib`.
- Empty project folders preserved with `.gitkeep` markers.
- Photocatalysis theme pack and rule examples.
- Project-local onboarding files and checklists.
- `fyp_lit_review_workflow.md` describing the manual first-use loop.

## Temporary Simulation Contents

The simulation used synthetic placeholders only:

- one placeholder registry row
- one placeholder BibTeX entry
- one placeholder structured note
- one placeholder extracted claim
- one placeholder draft paragraph

These files were not copied into the repository.

## Commands Used For Safety Checks

- `find <synthetic_temp_workspace> -type f -name '*.pdf' -o -name '*.db' -o -name '*.sqlite' -o -name '*.zip' -o -name '*.tar' -o -name '*.gz'`
- `grep -R "<private_fyp_reference_path>" -n projects docs reports paper_workbench tests README.md AGENTS.md`
- `python scripts/data_safety_audit.py --out scratch/fyp_dogfood_data_safety_raw.md --strict`
- `git status --short --branch --ignored`

## Notes

The private FYP reference folder and BibTeX file can be used later as read-only
inputs to a local planning command, but outputs that include real filenames,
BibTeX keys, metadata, or private absolute paths should stay untracked unless
manually sanitized.
