# External User Simulation Final

Date: 2026-06-11

## Scope

This simulation treated the repository as a brand-new external checkout. The initial inspection and workflow tests were run from a clean tracked-file copy under `/private/tmp/paperwb_external_user_sim` before modifying the real repository.

Covered workflows:

- README installation and quickstart
- `paperwb --help` / module-form CLI help
- `paperwb init`
- example registry and BibTeX validation
- note template generation
- claim extraction
- inventory, BibTeX audit, evidence map, citation audit, doctor, and section-outline reports
- project profile list/init/validate
- Zotero CSV dry-run import
- Obsidian vault export
- local SQLite index rebuild/status/search
- notebook JSON validation and notebook execution
- clean-checkout test behavior

## Environment

- Source copy: `git archive HEAD` exported to `/private/tmp/paperwb_external_user_sim`
- Python workflow: isolated venv plus module-form CLI fallback
- Network: restricted/offline for Python package installation
- Notebook runtime: system Jupyter was available outside the isolated venv

## Results

| Area | Result | Notes |
| --- | --- | --- |
| README install command | Blocked in restricted network | `python -m pip install -e ".[test]"` tried to fetch `setuptools>=69` for build isolation and failed without network. |
| Offline/no-install CLI | Passed | `python -m paper_workbench.cli --help` worked from the checkout. |
| `paperwb --help` entry point | Blocked by install failure | The `paperwb` script was not created because editable install failed. |
| `paperwb init` equivalent | Passed | Module-form command initialized the workspace and created missing `data/papers`. |
| Registry validation | Passed with expected findings | Synthetic duplicate DOI/title and missing BibTeX-key findings were reported. |
| BibTeX validation | Passed with expected findings | Synthetic duplicate DOI, missing author/journal, invalid year, and unlinked-entry findings were reported. |
| Note template generation | Passed | Generated a note template to a temporary output path without touching checked-in notes. |
| Claim extraction | Passed | Extracted 3 claims from `data/notes`. |
| Evidence map | Passed | Generated a Markdown evidence map from synthetic example data. |
| Citation audit | Passed | Generated a Markdown citation-audit report from synthetic example data. |
| Project profiles | Passed | Listed profiles, validated `zis_photocatalysis`, and initialized `external_demo_review` in the temporary copy. |
| Zotero CSV dry-run import | Passed | Wrote an import report in the temporary project and did not modify the real repo. |
| Obsidian export | Passed | Exported expected vault files to a temporary output directory. |
| Indexed search | Passed | Rebuilt project index, checked status, and searched `corrosion` against `photocorrosion` records. |
| Notebook JSON validation | Passed | `scripts/validate_notebooks.py` validated 5 notebooks. |
| Notebook execution | Passed | Notebooks 01, 02, 04, 05, and 06 executed to `/private/tmp` via system Jupyter. |
| Full pytest from first external copy | Failed before fix | Golden `workspace_health.md` was sensitive to untracked local stress `reports/` directories. |
| Clean staged checkout after fix | Passed targeted tests | `tests/test_golden_reports.py` and `tests/test_synthetic_stress.py` passed from an exported staged tree. |

## Blockers Found

### 1. Installation Documentation Was Incomplete for Offline/Restricted Environments

The documented editable install command is normal for online users, but in this restricted simulation it failed because pip build isolation could not fetch `setuptools>=69`. The package itself has no runtime dependencies and the module-form CLI works from source, so this is a documentation blocker rather than a code/runtime blocker.

Fix applied:

- Updated README installation guidance to explain the offline/restricted fallback.
- Updated the external quickstart to clarify that `python -m paper_workbench.cli ...` works from the repository root when editable install cannot fetch build dependencies.

### 2. Clean Checkouts Did Not Reproduce Stress Report Fixture Directories

The real working tree had local `projects/stress_*/reports/` directories, but those empty directories were not tracked. A clean archive checkout missed them, causing the golden workspace-health report to change and `tests/test_golden_reports.py` to fail.

Fix applied:

- Added tracked placeholders under each stress project `reports/` directory.
- Added a stress fixture-layout test asserting checked-in stress project report directories exist.

## Commands Run

Representative external workflow commands:

```bash
python -m pip install -e ".[test]"
python -m paper_workbench.cli --help
python -m paper_workbench.cli init
python -m paper_workbench.cli validate-registry data/registries/example_papers.csv
python -m paper_workbench.cli validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv
python -m paper_workbench.cli note-template synth_charge_2024 --registry data/registries/example_papers.csv --output /private/tmp/paperwb_external_user_sim/generated_note.md
python -m paper_workbench.cli claims data/notes --output /private/tmp/paperwb_external_user_sim/example_claims.csv
python -m paper_workbench.cli report evidence-map --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out /private/tmp/paperwb_external_user_sim/evidence_map.md --force
python -m paper_workbench.cli report citation-audit --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out /private/tmp/paperwb_external_user_sim/citation_audit.md --force
python -m paper_workbench.cli project list
python -m paper_workbench.cli project validate zis_photocatalysis
python -m paper_workbench.cli project init external_demo_review
python -m paper_workbench.cli import zotero-csv data/examples/zotero_export.csv --project zis_photocatalysis --dry-run --force
python -m paper_workbench.cli export obsidian --project zis_photocatalysis --out /private/tmp/paperwb_external_user_sim/obsidian_zis
python -m paper_workbench.cli index rebuild --project zis_photocatalysis --include-text
python -m paper_workbench.cli index status --project zis_photocatalysis --include-text --check-files
python -m paper_workbench.cli search corrosion --project zis_photocatalysis --indexed
python scripts/validate_notebooks.py
jupyter nbconvert --to notebook --execute notebooks/01_registry_and_bibtex_workflow.ipynb --output /private/tmp/paperwb_external_user_sim/executed_01_registry_and_bibtex_workflow.ipynb --ExecutePreprocessor.timeout=300
```

Additional notebooks 02, 04, 05, and 06 were executed the same way.

## Validation After Fixes

- `python -m pytest tests/test_synthetic_stress.py tests/test_golden_reports.py -q` passed in the working repository.
- `python -m pytest tests/test_golden_reports.py tests/test_synthetic_stress.py -q` passed from a clean staged-tree export.
- `python -m pytest -q` passed in the working repository.
- `python scripts/validate_notebooks.py` passed in the working repository.
- Representative final CLI smoke checks passed for help, registry validation, project listing, citation-audit report generation, Zotero CSV dry-run import, Obsidian export, index rebuild/status, and indexed search.

## Remaining Non-Blockers

- A fully isolated offline venv still cannot run `paperwb` as an installed console script unless Python build dependencies are already available locally.
- The README's default `paperwb` commands assume successful install; the module-form fallback is now documented for restricted environments.
- Zotero dry-run import still writes an import report; this is known behavior and was not treated as a blocker in this simulation.

## Verdict

After the documentation and fixture-layout fixes, a new external user can use the workbench from source with the module-form CLI, validate synthetic data, generate notes and reports, use project profiles, import/export local data, rebuild the local search index, and run notebooks when Jupyter is available.
