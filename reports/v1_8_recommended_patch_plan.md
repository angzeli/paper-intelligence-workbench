# v1.8 Recommended Patch Plan

## High Priority

- Add non-destructive template diff planning for existing projects.
- Add user-defined local template JSON support with schema validation.
- Add tests that verify template-generated projects remain compatible with
  doctor, dashboard, rules, and report commands as the CLI evolves.

## Medium Priority

- Add optional template customization prompts or config files without making
  creation interactive by default.
- Add dashboard filters for theme, tag, status, and priority.
- Add CSV/JSON export for template rule inventories.

## Low Priority

- Add a notebook for project-template onboarding only if it can stay short and
  portable.
- Add template examples for additional disciplines after real use reveals
  repeated patterns.

## Explicitly Not Worth Doing Yet

- Do not add cloud template registries.
- Do not add templates containing real paper metadata.
- Do not add investment recommendations to finance workflows.
- Do not add auto-migration of user projects from templates.
