# Private External Workspace

Use an external workspace for real FYP dogfooding. The workspace should live
outside this repository and should be registered through the ignored local
config file `.paperwb-local/workspaces.json`.

Example layout:

```text
<external_workspace>/
└── projects/
    └── fyp_zis_lit_review/
        ├── registry.csv
        ├── bibtex/library.bib
        ├── notes/
        ├── drafts/
        ├── reports/
        ├── reading_sessions/
        └── project.json
```

Create the external scaffold:

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review --root <external_workspace>
```

Register it locally from the repository root:

```bash
paperwb external add fyp_zis_real <external_workspace> --project fyp_zis_lit_review
paperwb external validate fyp_zis_real --strict
```

The registration stores a local path only. Do not commit
`.paperwb-local/workspaces.json`.

## Safe External Commands

```bash
paperwb external run fyp_zis_real validate-registry --strict
paperwb external run fyp_zis_real validate-bib --strict
paperwb external run fyp_zis_real doctor
paperwb external run fyp_zis_real dashboard
paperwb external run fyp_zis_real evidence-map
paperwb external run fyp_zis_real citation-audit
paperwb external run fyp_zis_real support-bundle
```

External outputs stay in the external workspace unless an explicit `--out` is
provided. Support bundles redact by default.

## Boundary

- Do not copy PDFs into this repository.
- Do not commit private notes, drafts, BibTeX exports, or external reports.
- Do not use `--show-paths` for reports that might be shared.
- Do not treat any generated report as scientific truth.
