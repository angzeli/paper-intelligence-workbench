# First Real Dogfooding Plan v3.0rc2

## Purpose

Use Paper Intelligence Workbench on the first real literature-review project without committing private data, real PDFs, copied full text, or unverified metadata.

## Recommended Workspace Pattern

Keep the real workspace outside this repository:

```text
<external_workspace>/
└── projects/
    └── fyp_zis_real/
        ├── registry.csv
        ├── bibtex/library.bib
        ├── notes/
        ├── drafts/
        ├── reports/
        └── project.json
```

Register a local pointer:

```bash
paperwb external add fyp_zis_real <external_workspace> --project fyp_zis_real
paperwb external validate fyp_zis_real --strict
```

The pointer lives in ignored `.paperwb-local/workspaces.json`.

## First Week Workflow

1. Create or validate the external project layout.
2. Add a small starter set of real paper metadata manually.
3. Add BibTeX entries from the user’s own reference manager export.
4. Validate registry and BibTeX:

```bash
paperwb external run fyp_zis_real validate-registry --strict
paperwb external run fyp_zis_real validate-bib --strict
```

5. Generate note templates for the first papers.
6. Read papers manually and write structured notes.
7. Extract claims from those notes:

```bash
paperwb external run fyp_zis_real claims
```

8. Generate evidence and citation checks:

```bash
paperwb external run fyp_zis_real evidence-map
paperwb external run fyp_zis_real citation-audit
paperwb external run fyp_zis_real dashboard
```

9. Create a backup before major imports, sync applies, migrations, or note reorganizations:

```bash
paperwb external run fyp_zis_real backup --notes "Before major metadata update"
```

10. Generate a support bundle only when debugging:

```bash
paperwb external run fyp_zis_real support-bundle
```

Support bundles and external summaries redact private paths by default.

## Manual Data Rules

- Verify metadata before adding registry rows.
- Do not let the tool invent titles, authors, DOI values, citation keys, claims, or conclusions.
- Do not commit real PDFs, full text, private notes, private drafts, or private BibTeX exports.
- Treat citation audits, manuscript QA, rules, graph analytics, and dashboards as heuristic checks.

## Stop Conditions

Stop and fix data before writing prose if:

- registry validation has errors
- BibTeX keys are missing or duplicated
- notes are missing for included papers
- claims have no evidence location
- a draft uses unknown citation keys
- a support bundle or report contains private unredacted paths

## Expected Outcome

After the first dogfooding pass, the user should know which papers are read, which claims have evidence locations, which themes are weak, which citations need cleanup, and what to read next.
