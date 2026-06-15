# Test Matrix v2

| Area | Representative tests |
| --- | --- |
| Registry | `tests/test_registry.py`, `tests/test_v0_2_validation.py` |
| BibTeX | `tests/test_bibtex.py` |
| Notes and claims | `tests/test_notes_claims.py`, `tests/test_parser_edge_fixtures.py` |
| Tags, search, reports, audit | `tests/test_tags_search_reports_audit.py` |
| Project profiles, doctor, exports | `tests/test_projects_doctor_exports.py` |
| Import/export | `tests/test_import_export_v0_4.py` |
| Indexed search | `tests/test_index_v0_5.py` |
| Authoring | `tests/test_authoring_workbench.py` |
| Local files | `tests/test_local_files_v0_7.py` |
| Integrity, backup, migration | `tests/test_integrity_backup_migration_v0_9.py` |
| Adversarial fixtures | `tests/test_adversarial_v0_10.py` |
| Draft audit | `tests/test_drafts_v1_1.py` |
| Reading sessions | `tests/test_reading_v1_2.py` |
| Sync | `tests/test_sync_v1_3.py` |
| Manuscript QA | `tests/test_manuscript_v1_4.py` |
| Rules | `tests/test_rules_v1_5.py` |
| Dashboard | `tests/test_dashboard_v1_6.py` |
| Templates | `tests/test_templates_v1_7.py` |
| Dogfooding onboarding | `tests/test_dogfood_v2_0.py` |
| Evidence graph | `tests/test_evidence_graph_v2_1.py` |
| Release contracts and hygiene | `tests/test_v1_0_rc_command_contracts.py`, `tests/test_v2_release_candidate.py`, `tests/test_release_engineering_v0_8.py` |

Run:

```bash
python -m pytest -q
python scripts/smoke_cli_workflow.py --quick
python scripts/check_notebooks.py
python scripts/data_safety_audit.py --strict
```
