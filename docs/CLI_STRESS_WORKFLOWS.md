# CLI Stress Workflows

These commands exercise the v0.3 stress workspace through the public CLI.

## Generate a Temporary Stress Project

```bash
paperwb synthetic generate --project stress_cli_demo --papers 50 --claims 120 --themes 6 --domain ml
```

Use `--force` only when replacing a known synthetic fixture.

## Validate a Checked-in Stress Project

```bash
paperwb project validate stress_zis_photocatalysis
paperwb doctor --project stress_zis_photocatalysis
paperwb validate-registry projects/stress_zis_photocatalysis/registry.csv
paperwb validate-bib projects/stress_zis_photocatalysis/bibtex/library.bib --registry projects/stress_zis_photocatalysis/registry.csv
```

## Extract and Export

```bash
paperwb claims --project stress_zis_photocatalysis --output scratch/stress_claims_v0_3.csv
paperwb export claims-json --project stress_zis_photocatalysis --out scratch/stress_claims_v0_3.json --force
paperwb export reading-list --project stress_zis_photocatalysis --tag photocorrosion --out scratch/stress_reading_list_photocorrosion_v0_3.md --force
```

## Generate Reports

```bash
paperwb report inventory --project stress_zis_photocatalysis --out scratch/stress_inventory_v0_3.md --force
paperwb report reading-status --project stress_zis_photocatalysis --out scratch/stress_reading_status_v0_3.md --force
paperwb report bibtex-audit --project stress_zis_photocatalysis --out scratch/stress_bibtex_audit_v0_3.md --force
paperwb report citation-audit --project stress_zis_photocatalysis --out scratch/stress_citation_audit_v0_3.md --force
paperwb report evidence-map --project stress_zis_photocatalysis --out scratch/stress_evidence_map_v0_3.md --force
paperwb report theme-dashboard --project stress_zis_photocatalysis --out scratch/stress_theme_dashboard_v0_3.md --force
paperwb report workspace-health --project stress_zis_photocatalysis --out scratch/stress_workspace_health_v0_3.md --force
```

## Search

```bash
paperwb search photocorrosion --project stress_zis_photocatalysis
paperwb search "Synthetic claim 37" --project stress_zis_photocatalysis --claims --exact
paperwb search "Local Review Conditions" --project stress_zis_photocatalysis --notes --exact
```
