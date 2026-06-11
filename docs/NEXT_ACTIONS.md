# Next Actions

The v1.6 dashboard includes a transparent next-action list. Actions are local
workflow suggestions generated from existing validation findings and project
state.

Each action includes:

- action ID
- project
- priority
- reason
- command suggestion
- related paper, claim, rule, or workspace item

Priorities are simple and deterministic:

- `critical`: workspace-health errors
- `high`: rule errors, missing evidence locations, included papers without notes, and BibTeX errors
- `medium`: weak claims, theme/citation warnings, manuscript QA warnings, and open follow-ups
- `low`: reading queue suggestions and maintenance reminders

Example:

```bash
paperwb dashboard --project zis_photocatalysis --view next-actions
```

Export to Markdown:

```bash
paperwb dashboard --project zis_photocatalysis --view next-actions --out reports/next_actions_v1_6.md --force
```

Next actions are advisory. The tool does not run the suggested commands
automatically and does not edit notes, registries, drafts, or BibTeX files.

