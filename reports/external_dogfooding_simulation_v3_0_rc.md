# External Dogfooding Simulation v3.0rc

Simulated user: technically comfortable undergraduate or early-stage researcher
starting with synthetic data and an empty real-project scaffold.

## Scope

The simulation used public-facing docs, CLI help, bundled synthetic examples,
and a disposable temporary workspace. No PDFs, real metadata, real full text,
cloud APIs, LLM APIs, or publisher scraping were used.

## Commands Checked

- `python -c "import paper_workbench; print(paper_workbench.__version__)"`
- `paperwb --help`
- `paperwb dogfood --help`
- `paperwb dogfood create photocatalysis --project v3_demo --root <temporary dogfood root>`
- `paperwb dogfood status --project v3_demo --root <temporary dogfood root>`
- `paperwb dogfood checklist --project v3_demo --root <temporary dogfood root>`
- `paperwb validate-registry <temporary dogfood project>/registry.csv --strict`
- `paperwb validate-bib <temporary dogfood project>/bibtex/library.bib --registry <temporary dogfood project>/registry.csv --strict`
- `paperwb add-paper --project v3_demo ...`
- `paperwb note-template v3_seed --project v3_demo`
- `paperwb list --project v3_demo`
- `paperwb validate-registry projects/clean_demo/registry.csv --strict`
- `paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry projects/clean_demo/registry.csv --strict`
- `paperwb claims projects/clean_demo/notes --output <temporary output>`
- `paperwb report evidence-map --project clean_demo --out <temporary output> --force`
- `paperwb report citation-audit --project clean_demo --out <temporary output> --force`
- `paperwb writing-packet --project clean_demo --theme clean-validation --out <temporary output> --force`
- `paperwb dashboard --project clean_demo --no-audit-log`
- `paperwb doctor --project clean_demo`
- `paperwb integrity check --project clean_demo`
- `paperwb backup create --project v3_demo`
- `paperwb workflow list`
- `paperwb workflow run release_candidate_check --project clean_demo --dry-run --out <temporary output> --force`

## Results

- Package import reported `3.0.0rc1`.
- CLI help loaded and pointed to v3 docs.
- Empty dogfooding project creation succeeded and refused no user data.
- Empty registry and empty BibTeX validated cleanly.
- Empty project status clearly reported no papers, BibTeX, notes, or claims and
  suggested the next safe command.
- A synthetic manual paper row was added in the temporary workspace, note
  template generation worked, and registry validation still passed.
- Bundled `clean_demo` validated with zero registry, BibTeX, doctor, and
  integrity findings.
- Claims, evidence-map, citation-audit, writing-packet, dashboard, and backup
  smoke checks completed.
- The release-candidate workflow dry-run initially exposed a stale internal
  keyword argument in the search-index step. The bug was fixed and the dry-run
  then completed with zero errors and zero warnings.

## Release Blockers Found

- Fixed: workflow runner `search_index_rebuild` called `build_index_records`
  with a stale `root` keyword. This only affected workflow recipes that include
  an index step.

## Verdict

Ready for local dogfooding as v3.0rc after the workflow runner compatibility
fix, subject to full pytest, notebook validation, data-safety audit, and final
git hygiene checks.
