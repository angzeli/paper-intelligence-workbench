# Error Message Guide

v0.10 error messages should answer four questions:

1. What happened?
2. Where did it happen?
3. Why does it matter?
4. What can the user do next?

Use `paper_workbench.errors.format_error_message` for common CLI errors where practical.

Example:

```text
Generic CSV mapping references missing source columns.
Where: data/import.csv
Why it matters: The importer cannot safely map fields that are not present in the CSV header.
Next step: Fix the mapping or CSV header. Missing columns: Publication Year.
```

## Guidelines

- Do not expose Python tracebacks for expected user-input failures.
- Do not say "invalid" without naming the file, field, or record.
- Prefer warnings when the parser can recover conservatively.
- Use errors when continuing would silently corrupt, overwrite, or mis-map user data.
- Suggested actions should be local and concrete.
