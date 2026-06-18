# Local-only Config

Paper Intelligence Workbench uses `.paperwb-local/` for private local pointers
that should never be committed.

The v3.5 external-workspace registry is:

```text
.paperwb-local/workspaces.json
```

Example shape:

```json
{
  "schema": "paperwb-external-workspaces-v1",
  "workspaces": {
    "fyp_zis_real": {
      "name": "fyp_zis_real",
      "path": "<external_workspace>",
      "project": "fyp_zis_real",
      "description": "",
      "added_at": "2026-06-18T00:00:00+00:00"
    }
  }
}
```

This file may contain private local paths. `.gitignore` excludes
`.paperwb-local/`, and the data-safety audit treats it as a forbidden tracked
artifact if it is ever staged.

