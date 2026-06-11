# CLI Failure Modes

v0.10 adds regression tests for expected CLI failure paths.

## Expected Behavior

Commands should:

- return a non-zero status for unsafe or unrecoverable input
- avoid Python tracebacks for expected user mistakes
- explain the failing file, field, or project
- include a suggested next step where practical
- avoid writing partial outputs when preflight checks fail

## Representative Failure Paths

| Command | Failure | Expected behavior |
| --- | --- | --- |
| `validate-registry` | missing required header | Prints `missing_required_column` and a next step. |
| `import csv` | bad mapping target | Exits 2 with a registry-field explanation. |
| `import csv` | mapped source column missing | Exits 2 before writing registry data. |
| `import zotero-csv` | missing `Title` column | Exits 2 with a Zotero export hint. |
| `project validate` | missing project | Exits 2 without traceback. |
| `backup restore` | missing backup | Exits 2 without modifying files. |
| `backup restore` | corrupt manifest | Exits 2 and blocks restore. |

Use adversarial fixtures when adding new parser or write-operation behavior.
