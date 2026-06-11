# Built-in Rule Adapters

The v1.5 rule report can include existing workbench checks as built-in adapter
findings. These preserve existing validation behavior and make the rule report a
single audit surface.

Built-in adapters:

- `builtin.registry`: registry validation findings
- `builtin.citation_audit`: citation-audit findings
- `builtin.evidence_map`: theme paper and claim coverage thresholds
- `builtin.workspace_health`: workspace-health diagnostics
- `builtin.manuscript`: manuscript QA findings when a draft is supplied

List them locally:

```bash
paperwb rules list --project zis_photocatalysis --builtins
```

Run only configured custom rules:

```bash
paperwb rules run --project zis_photocatalysis --no-builtins
```

Built-in adapters are report-only in this context. They do not replace the
existing commands such as `validate-registry`, `validate-bib`, `doctor`,
`report citation-audit`, or `manuscript qa`.

