# Rule Engine

v1.5 adds a local rule engine for project-specific validation policies.

Rules are declarative JSON records. They can inspect registry rows, BibTeX
entries, notes, claims, themes, manuscript audits, project profiles, and
workspace-level checks. They cannot execute Python code, call cloud services, or
modify user data.

## Basic Workflow

```bash
paperwb rules list --project zis_photocatalysis --builtins
paperwb rules validate-config --project zis_photocatalysis --strict
paperwb rules run --project zis_photocatalysis
paperwb rules report --project zis_photocatalysis --out reports/rule_report_v1_5.md --force
paperwb rules explain zis.theme.photocorrosion.min_papers --project zis_photocatalysis
```

Project-specific rules live at:

```text
projects/PROJECT_NAME/rules.json
```

You can also pass an explicit file:

```bash
paperwb rules run --rules-file path/to/rules.json
```

## Boundary

The rule engine audits local completeness and consistency. It does not decide
whether a scientific claim is true, rewrite notes or drafts, or repair metadata.

