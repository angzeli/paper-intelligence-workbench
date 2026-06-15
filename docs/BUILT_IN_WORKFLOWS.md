# Built-in Workflows

v2.3 includes these built-in workflow recipes:

| Recipe | Safety | Purpose |
| --- | --- | --- |
| `daily_check` | writes reports | Validate registry/BibTeX, run workspace health, rules, and dashboard. |
| `weekly_review` | writes reports | Refresh claims and core weekly evidence reports. |
| `pre_writing_check` | writes reports | Refresh evidence, citation, missing-evidence, and optional writing-packet checks. |
| `pre_manuscript_check` | writes reports | Run validation, citation audit, and manuscript QA when a draft path is supplied. |
| `pre_backup_check` | dry-run by default; backup only with `--run-writes` | Run validation and integrity before optional local backup creation. |
| `external_user_demo` | writes reports | Exercise the safe synthetic demo workflow. |
| `release_candidate_check` | read-only or cache | Run representative validation, diagnostics, rules, dashboard, and optional index rebuild. |

Inspect a recipe before running it:

```bash
paperwb workflow show daily_check
```

Run a dry-run first when a recipe includes backup, cache, or multi-report
outputs:

```bash
paperwb workflow run pre_backup_check --project zis_photocatalysis --dry-run
paperwb workflow run pre_backup_check --project zis_photocatalysis --run-writes --force
```
