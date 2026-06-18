# Private Dogfooding

Private dogfooding means using Paper Intelligence Workbench on a real local
literature-review workspace without putting private data in this repository.

Use this mode for real FYP, finance-reading, ML-methods, or generic projects
once the synthetic examples are understood.

## Recommended Layout

Keep the real workspace outside the repository:

```text
<external_workspace>/
└── projects/
    └── fyp_zis_real/
        ├── registry.csv
        ├── bibtex/library.bib
        ├── notes/
        ├── reports/
        ├── drafts/
        └── project.json
```

Register it locally:

```bash
paperwb external add fyp_zis_real <external_workspace> --project fyp_zis_real
paperwb external validate fyp_zis_real --strict
```

The registration is stored in `.paperwb-local/workspaces.json`, which is
ignored by Git. It may contain private absolute paths, so it must stay local.

## Safe Daily Commands

```bash
paperwb external run fyp_zis_real doctor
paperwb external run fyp_zis_real dashboard
paperwb external run fyp_zis_real validate-registry --strict
paperwb external run fyp_zis_real validate-bib --strict
paperwb external run fyp_zis_real evidence-map
paperwb external run fyp_zis_real citation-audit
paperwb external run fyp_zis_real support-bundle
```

Report outputs default to the external workspace when the selected workflow
writes files. You can pass `--out <external_workspace>/...` explicitly when you
need a specific destination.

External validation reports and run summaries redact private local paths by
default, even when written with `--out`. Use `--show-paths` only for private
local debugging, and do not commit outputs generated with that flag.

## Safety Boundary

- The adapter stores pointers, not copied papers.
- It does not copy PDFs, notes, drafts, or BibTeX into the repository.
- External validation and run summaries redact private paths by default.
- Support bundles remain redacted by default.
- Backups created through external mode live under the external project root.
- Do not stage `.paperwb-local/`.
