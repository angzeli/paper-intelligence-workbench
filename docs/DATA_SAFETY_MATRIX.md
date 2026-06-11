# Data Safety Matrix

| Risk | Control | Automated check | Manual review |
| --- | --- | --- | --- |
| Copyrighted PDFs committed | `.gitignore` blocks `*.pdf`; data uses synthetic placeholders | `scripts/data_safety_audit.py`, CI hygiene scan | Confirm no PDFs are staged |
| Copied paper full text committed | Example sidecars are synthetic and small | data-safety sidecar size warning | Review text sidecars before release |
| Cloud or LLM dependency added | Runtime dependency list is empty | dependency and source review | Check new imports and docs |
| Publisher scraping added | No scraper modules or network workflow | source search in hostile reviews | Review new importers carefully |
| Secrets committed | Secret-pattern scan | data-safety audit | Inspect warnings before release |
| Cache DB committed | `.paperwb/`, `.sqlite`, `.db` ignored | CI hygiene scan | Check `git status --ignored` |
| Absolute machine paths in docs/reports | New docs use relative `scratch/` outputs | data-safety warnings | Historical reports may need curation |
| User notes overwritten | Note template requires explicit force | CLI tests | Review new write commands |
| Registry metadata overwritten | Imports fill blanks only; local-file writes merge records | import/local-file tests | Review force behavior |
| Generated prose mistaken for user writing | Authoring docs state planning-aid boundary | authoring tests | Review report wording |
