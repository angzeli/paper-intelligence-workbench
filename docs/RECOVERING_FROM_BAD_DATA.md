# Recovering From Bad Data

Paper Intelligence Workbench is designed to help recover from imperfect local data without rewriting it silently.

## Registry Problems

Run:

```bash
paperwb validate-registry data/registries/papers.csv
paperwb integrity check --project PROJECT
```

Fix missing required columns, duplicate paper IDs, invalid reading statuses, DOI variants, and paths that escape the workspace before running imports or migrations.

## BibTeX Problems

Run:

```bash
paperwb validate-bib data/bibtex/library.bib --registry data/registries/papers.csv
```

Parse warnings mean the parser recovered but the entry needs manual review. Do not rely on imported metadata until the entry is locally verified.

## Note Problems

Malformed note blocks should produce parse warnings rather than crashes. Check for missing paper IDs, missing evidence locations, unsupported evidence types, invalid strengths, and claims with empty text.

## Import Problems

Use dry-run first:

```bash
paperwb import zotero-csv input.csv --dry-run
paperwb import csv input.csv --mapping mapping.json --dry-run
```

Fix mapping files and source headers before using force or fill-missing options.

## Backup and Restore Problems

If a backup manifest is corrupt, restore is blocked. Recreate the backup or inspect `manifest.json` manually. Restore never deletes unrelated files.

## Migration Problems

Migration should be planned before it is run:

```bash
paperwb migrate plan --from legacy --to-project migrated_review
paperwb migrate run --from legacy --to-project migrated_review --dry-run
```

Existing target projects are conflicts. Choose a new project name or inspect the target before proceeding.
