# Failure Mode Matrix v0.10

| Area | Adversarial input | Expected result | Covered by |
| --- | --- | --- | --- |
| Registry | Missing required headers | `missing_required_column`, non-zero strict CLI, no traceback | `test_missing_registry_headers_are_actionable` |
| Registry | Duplicate paper IDs and DOI variants | Duplicate findings and no crash | `test_adversarial_registry_loads_and_reports_expected_findings` |
| Registry | Relative path escapes workspace | `path_escapes_workspace` error | `test_adversarial_registry_loads_and_reports_expected_findings` |
| BibTeX | Unclosed entry | `bibtex_parse_warning` and report generation | `test_bibtex_torture_fixture_recovers_with_warnings` |
| BibTeX | Duplicate key and DOI variants | Duplicate findings | `test_bibtex_torture_fixture_recovers_with_warnings` |
| Notes | Missing paper ID and bad status | Parse warnings, no crash | `test_malformed_note_produces_warnings_and_parseable_claim` |
| Notes | Empty claim and missing evidence | Warning and conservative claim extraction | `test_malformed_note_produces_warnings_and_parseable_claim` |
| Reports | Imperfect registry/note data | Evidence map still renders warnings/sections | `test_reports_do_not_crash_with_imperfect_notes_and_registry` |
| Import | Missing Zotero `Title` | Actionable `ValueError` before writes | `test_import_failure_paths_have_useful_errors` |
| Import | Bad generic CSV mapping | Actionable `ValueError` before writes | `test_import_failure_paths_have_useful_errors` |
| Import | RIS missing `ER` | Record recovered conservatively | `test_ris_missing_terminator_is_recovered_as_one_record` |
| Audit log | Corrupted JSONL line | Parse-warning event, later events readable | `test_corrupted_audit_log_and_backup_manifest_are_safe` |
| Backup | Corrupted manifest | Restore blocked with next step | `test_corrupted_audit_log_and_backup_manifest_are_safe` |
| Project | Escaping project paths | Integrity finding | `test_integrity_detects_broken_project_profile_paths` |
| CLI | Bad import mapping | Exit 2, no traceback | `test_cli_failure_paths_do_not_traceback` |
| CLI | Missing project | Exit 2, no traceback | `test_cli_failure_paths_do_not_traceback` |
| CLI | Missing backup | Exit 2, no traceback | `test_cli_failure_paths_do_not_traceback` |
