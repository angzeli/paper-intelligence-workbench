# Audit Log

v0.9 writes local audit events for safety-sensitive write workflows.

Default audit log path:

```text
.paperwb/audit_log.jsonl
```

For project workflows the log is stored under the project root, for example:

```text
projects/zis_photocatalysis/.paperwb/audit_log.jsonl
```

Show audit events:

```bash
paperwb audit-log show
paperwb audit-log show --project zis_photocatalysis --markdown
```

Clear requires explicit confirmation:

```bash
paperwb audit-log clear --project zis_photocatalysis --force
```

Audit logs are ignored by git and should not be committed. They are local operational records, not a security boundary.
