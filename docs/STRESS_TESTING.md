# Stress Testing

v0.3 stress testing proves that the workbench can process a 100-paper local review workspace without adding cloud services, LLM APIs, publisher scraping, databases, or PDF assets.

## Standard Stress Checks

```bash
python -m pytest tests/test_synthetic_stress.py tests/test_cli_stress.py tests/test_golden_reports.py
python scripts/performance_sanity.py --force
```

## Representative CLI Workflow

```bash
paperwb project list
paperwb project validate stress_zis_photocatalysis
paperwb doctor --project stress_zis_photocatalysis --out reports/stress_workspace_health_v0_3.md --force
paperwb validate-registry projects/stress_zis_photocatalysis/registry.csv
paperwb validate-bib projects/stress_zis_photocatalysis/bibtex/library.bib --registry projects/stress_zis_photocatalysis/registry.csv
paperwb claims --project stress_zis_photocatalysis --output reports/stress_claims_v0_3.csv
paperwb report evidence-map --project stress_zis_photocatalysis --out reports/stress_evidence_map_v0_3.md --force
paperwb report citation-audit --project stress_zis_photocatalysis --out reports/stress_citation_audit_v0_3.md --force
paperwb report section-outline --project stress_zis_photocatalysis --theme photocorrosion --out reports/photocorrosion_section_outline_v0_3.md --force
paperwb export claims-json --project stress_zis_photocatalysis --out reports/stress_claims_v0_3.json --force
paperwb search photocorrosion --project stress_zis_photocatalysis
```

## Interpreting Findings

Stress projects intentionally contain validation findings. A successful stress run means the tool reports the problems clearly and reproducibly; it does not mean the generated data is clean.

## Performance Sanity

`scripts/performance_sanity.py` records durations for generation, parsing, validation, audit, doctor, and report construction. It is not a strict benchmark and should not be used as a flaky timing gate.

