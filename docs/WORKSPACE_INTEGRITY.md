# Workspace Integrity

v0.9 adds a local integrity check for workspace consistency before risky operations such as migration or restore.

```bash
paperwb integrity check --project zis_photocatalysis --out reports/workspace_integrity_v0_9.md --force
```

The check is read-only. It reports missing folders, missing registry/BibTeX/theme inputs, notes that reference unknown paper IDs, path containment problems, local-file warnings, tracked cache databases, and tracked PDFs in repository data.

The integrity score is not a scientific-quality score. It only checks whether local files, registry rows, notes, claims, and project paths are internally consistent enough to work with safely.

## Strict Mode

```bash
paperwb integrity check --project zis_photocatalysis --strict
```

`--strict` returns non-zero when integrity errors are found. Warnings remain review prompts.

## Safety Boundary

- The command does not modify input data.
- It does not inspect ignored private files.
- It does not parse PDFs or full text.
- It does not infer missing metadata.
