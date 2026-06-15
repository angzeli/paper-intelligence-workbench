# Workflow Runner

The v2.3 workflow runner lets a project run repeatable local checks from a
named recipe instead of many individual commands.

Recipes are declarative JSON. They select from built-in step types only; they
do not run shell commands, import Python plugins, use cloud services, or call
LLM APIs.

## Common Commands

```bash
paperwb workflow list
paperwb workflow show daily_check
paperwb workflow run daily_check --project zis_photocatalysis --dry-run
paperwb workflow run pre_writing_check --project zis_photocatalysis --theme photocorrosion --force
paperwb workflow run pre_backup_check --project zis_photocatalysis --run-writes --force
paperwb workflow validate projects/zis_photocatalysis/workflows/daily_check.json --strict
```

## Recipe Locations

Built-in recipes are shipped with the package. Project-specific recipes can be
stored under:

```text
projects/<project>/workflows/*.json
```

Relative step outputs in project recipes are resolved from the project root.
For example, `reports/workflow_daily_check_dashboard.md` writes inside the
selected project's `reports/` folder.

## Dry-run And Force

- `--dry-run` plans steps and writes only the workflow run report.
- `--run-writes` explicitly opts into step writes for recipes that default to
  dry-run.
- Normal runs may write configured report/export outputs.
- Existing outputs are refused unless `--force` is supplied.
- Backup creation is available as a built-in step, but dry-run is the safe
  default for backup-oriented recipes.

## Interpretation Boundary

Workflow reports summarize local command results. They do not verify scientific
truth, fabricate claims, fabricate citations, scrape papers, or rewrite drafts.
