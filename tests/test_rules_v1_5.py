from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys

from paper_workbench.bibtex import parse_bibtex_file
from paper_workbench.claims import collect_notes
from paper_workbench.registry import load_registry
from paper_workbench.rules import (
    RuleContext,
    load_rule_set,
    maybe_audit_manuscript,
    rule_report,
    run_rule_set,
    validate_rule_set,
)
from paper_workbench.schema import LocalFileRecord
from paper_workbench.tags import load_themes

from conftest import FINANCE_PROJECT, ROOT, ZIS_PROJECT


def _context(project: Path, name: str) -> RuleContext:
    notes = collect_notes(project / "notes")
    return RuleContext(
        project=name,
        root=str(project),
        registry_path=str(project / "registry.csv"),
        bibtex_path=str(project / "bibtex" / "library.bib"),
        notes_dir=str(project / "notes"),
        themes_path=str(project / "themes.json"),
        reports_dir=str(project / "reports"),
        papers=load_registry(project / "registry.csv"),
        bibtex_entries=parse_bibtex_file(project / "bibtex" / "library.bib"),
        notes=notes,
        claims=[claim for note in notes for claim in note.claims],
        themes=load_themes(project / "themes.json"),
    )


def _write_rules(path: Path, rules: list[dict]) -> Path:
    path.write_text(json.dumps({"version": "1.5", "rules": rules}, indent=2), encoding="utf-8")
    return path


def test_rule_schema_loading_and_validation() -> None:
    rule_set = load_rule_set(ZIS_PROJECT / "rules.json")
    findings = validate_rule_set(rule_set)
    assert not findings
    assert {rule.rule_id for rule in rule_set.rules} >= {
        "zis.theme.photocorrosion.min_papers",
        "zis.manuscript.no_unknown_citations",
    }


def test_invalid_rule_config_reports_errors(tmp_path: Path) -> None:
    path = _write_rules(
        tmp_path / "bad_rules.json",
        [
            {
                "rule_id": "bad.target",
                "target": "registry",
                "severity": "urgent",
                "condition": {"type": "required_field"},
            }
        ],
    )

    findings = validate_rule_set(load_rule_set(path))

    assert {finding.rule_id for finding in findings} >= {
        "config.invalid_severity",
        "config.missing_condition_field",
    }


def test_invalid_numeric_rule_config_reports_errors(tmp_path: Path) -> None:
    path = _write_rules(
        tmp_path / "bad_numeric_rules.json",
        [
            {
                "rule_id": "bad.min_count",
                "target": "claim",
                "severity": "warning",
                "condition": {"type": "min_count", "min": "many"},
            },
            {
                "rule_id": "bad.max_count",
                "target": "claim",
                "severity": "warning",
                "condition": {"type": "max_count", "max": []},
            },
            {
                "rule_id": "bad.theme_min_papers",
                "target": "theme",
                "severity": "warning",
                "condition": {"type": "theme_min_papers", "theme": "photocorrosion", "min_papers": "three"},
            },
            {
                "rule_id": "bad.theme_min_strong_claims",
                "target": "theme",
                "severity": "warning",
                "condition": {"type": "theme_min_strong_claims", "theme": "photocorrosion", "min_strong_claims": False},
            },
        ],
    )

    rule_set = load_rule_set(path)
    findings = validate_rule_set(rule_set)
    result = run_rule_set(rule_set, _context(ZIS_PROJECT, "zis_photocatalysis"), include_builtins=False)

    invalid_integer_findings = [finding for finding in findings if finding.rule_id == "config.invalid_integer"]
    assert len(invalid_integer_findings) == 4
    assert result.findings == findings
    assert all("must be an integer" in finding.message for finding in invalid_integer_findings)


def test_invalid_numeric_rule_config_cli_does_not_crash(tmp_path: Path) -> None:
    path = _write_rules(
        tmp_path / "bad_numeric_rules.json",
        [
            {
                "rule_id": "bad.theme_min_papers",
                "target": "theme",
                "severity": "warning",
                "condition": {"type": "theme_min_papers", "theme": "photocorrosion", "min_papers": "three"},
            }
        ],
    )

    validate = subprocess.run(
        [
            sys.executable,
            "-m",
            "paper_workbench.cli",
            "rules",
            "validate-config",
            str(path),
            "--strict",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "paper_workbench.cli",
            "rules",
            "run",
            "--project",
            "zis_photocatalysis",
            "--rules-file",
            str(path),
            "--no-builtins",
            "--strict",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert validate.returncode == 1
    assert run.returncode == 1
    assert "config.invalid_integer" in validate.stdout
    assert "condition.min_papers must be an integer" in validate.stdout
    assert "config.invalid_integer" in run.stdout
    assert "invalid literal" not in run.stderr


def test_where_equals_json_boolean_matches_registry_string_values(tmp_path: Path) -> None:
    path = _write_rules(
        tmp_path / "bool_filter_rules.json",
        [
            {
                "rule_id": "included.need_pdf",
                "target": "registry",
                "severity": "warning",
                "condition": {
                    "type": "required_field",
                    "field": "local_pdf_path",
                    "where_field": "included_in_lit_review",
                    "where_equals": True,
                },
            }
        ],
    )

    result = run_rule_set(load_rule_set(path), _context(ZIS_PROJECT, "zis_photocatalysis"), include_builtins=False)

    assert [finding.identifier for finding in result.findings] == ["zis_charge_2025", "zis_stability_2024"]


def test_required_field_allowed_values_and_regex_rules(tmp_path: Path) -> None:
    path = _write_rules(
        tmp_path / "rules.json",
        [
            {
                "rule_id": "registry.requires_url",
                "target": "registry",
                "severity": "warning",
                "condition": {"type": "required_field", "field": "url"},
            },
            {
                "rule_id": "registry.status.allowed",
                "target": "registry",
                "severity": "error",
                "condition": {"type": "allowed_values", "field": "reading_status", "values": ["unread"]},
                "message": "{identifier} has status {value}.",
            },
            {
                "rule_id": "registry.synthetic_doi",
                "target": "registry",
                "severity": "warning",
                "condition": {"type": "regex_match", "field": "doi", "pattern": "^10\\.0000/"},
            },
        ],
    )

    result = run_rule_set(load_rule_set(path), _context(ZIS_PROJECT, "zis_photocatalysis"), include_builtins=False)

    assert {finding.rule_id for finding in result.findings} == {"registry.status.allowed"}
    assert all(finding.severity == "error" for finding in result.findings)


def test_theme_and_claim_threshold_rules_on_zis_project() -> None:
    result = run_rule_set(
        load_rule_set(ZIS_PROJECT / "rules.json"),
        _context(ZIS_PROJECT, "zis_photocatalysis"),
        include_builtins=False,
    )

    by_id = {finding.rule_id: finding for finding in result.findings}
    assert "zis.theme.photocorrosion.min_papers" in by_id
    assert "zis.theme.photocorrosion.strong_claims" in by_id
    assert "zis.claim.strong_claims_need_location" not in by_id


def test_count_and_contains_tag_rules(tmp_path: Path) -> None:
    path = _write_rules(
        tmp_path / "rules.json",
        [
            {
                "rule_id": "claims.min_count",
                "target": "claim",
                "severity": "warning",
                "condition": {"type": "min_count", "min": 3},
                "message": "Only {count} claims found; expected {minimum}.",
            },
            {
                "rule_id": "claims.max_count",
                "target": "claim",
                "severity": "warning",
                "condition": {"type": "max_count", "max": 1},
                "message": "{count} claims found; maximum is {maximum}.",
            },
            {
                "rule_id": "papers.must_have_tag",
                "target": "registry",
                "severity": "warning",
                "condition": {"type": "contains_tag", "tag": "must-review"},
            },
        ],
    )

    result = run_rule_set(load_rule_set(path), _context(ZIS_PROJECT, "zis_photocatalysis"), include_builtins=False)

    assert {finding.rule_id for finding in result.findings} == {
        "claims.min_count",
        "claims.max_count",
        "papers.must_have_tag",
    }
    assert len([finding for finding in result.findings if finding.rule_id == "papers.must_have_tag"]) == 2


def test_missing_note_and_citation_key_rules(tmp_path: Path) -> None:
    context = _context(ZIS_PROJECT, "zis_photocatalysis")
    context.notes = []
    context.papers[0] = replace(context.papers[0], notes_path="", bibtex_key="")
    path = _write_rules(
        tmp_path / "rules.json",
        [
            {
                "rule_id": "read_papers.need_notes",
                "target": "registry",
                "severity": "warning",
                "condition": {"type": "missing_note_for_status", "statuses": ["deeply_read"]},
            },
            {
                "rule_id": "papers.need_citation_key",
                "target": "registry",
                "severity": "warning",
                "condition": {"type": "citation_key_required"},
            },
        ],
    )

    result = run_rule_set(load_rule_set(path), context, include_builtins=False)

    assert {finding.rule_id for finding in result.findings} == {
        "read_papers.need_notes",
        "papers.need_citation_key",
    }


def test_claim_strength_and_evidence_type_rules(tmp_path: Path) -> None:
    path = _write_rules(
        tmp_path / "rules.json",
        [
            {
                "rule_id": "photocorrosion.minimum_strength",
                "target": "claim",
                "severity": "warning",
                "condition": {
                    "type": "claim_strength_threshold",
                    "theme": "photocorrosion",
                    "min_strength": "moderate",
                },
            },
            {
                "rule_id": "photocorrosion.primary_evidence",
                "target": "claim",
                "severity": "warning",
                "condition": {
                    "type": "evidence_type_required",
                    "theme": "photocorrosion",
                    "evidence_types": ["experimental_result", "theory_or_mechanism"],
                },
            },
        ],
    )

    result = run_rule_set(load_rule_set(path), _context(ZIS_PROJECT, "zis_photocatalysis"), include_builtins=False)

    assert {finding.rule_id for finding in result.findings} == {
        "photocorrosion.minimum_strength",
        "photocorrosion.primary_evidence",
    }


def test_file_target_rules(tmp_path: Path) -> None:
    context = _context(ZIS_PROJECT, "zis_photocatalysis")
    context.files = [LocalFileRecord(paper_id="zis_charge_2025", relative_path="papers/zis_charge_2025.pdf")]
    path = _write_rules(
        tmp_path / "rules.json",
        [
            {
                "rule_id": "files.need_hash",
                "target": "file",
                "severity": "warning",
                "condition": {"type": "required_field", "field": "sha256"},
            }
        ],
    )

    result = run_rule_set(load_rule_set(path), context, include_builtins=False)

    assert len(result.findings) == 1
    assert result.findings[0].rule_id == "files.need_hash"
    assert result.findings[0].target == "file"


def test_finance_project_specific_rules_pass() -> None:
    result = run_rule_set(
        load_rule_set(FINANCE_PROJECT / "rules.json"),
        _context(FINANCE_PROJECT, "finance_reading"),
        include_builtins=False,
    )

    assert result.findings == []


def test_manuscript_unknown_citation_rule(tmp_path: Path) -> None:
    context = _context(ZIS_PROJECT, "zis_photocatalysis")
    context.manuscript_audit = maybe_audit_manuscript(ROOT / "drafts" / "synthetic_unknown_citations.md", context)
    path = _write_rules(
        tmp_path / "rules.json",
        [
            {
                "rule_id": "manuscript.no_unknown",
                "target": "manuscript",
                "severity": "error",
                "condition": {"type": "manuscript_no_unknown_citations"},
                "message": "Unknown citation {citation_key} in {paragraph_id}.",
            }
        ],
    )

    result = run_rule_set(load_rule_set(path), context, include_builtins=False)

    unknown_findings = [finding for finding in result.findings if finding.rule_id == "manuscript.no_unknown"]
    assert len(unknown_findings) == 2
    assert {finding.identifier for finding in unknown_findings} == {"unknownSynthetic2027", "anotherMissing2028"}
    assert any(finding.severity == "error" for finding in result.findings)


def test_rule_report_generation() -> None:
    result = run_rule_set(
        load_rule_set(ZIS_PROJECT / "rules.json"),
        _context(ZIS_PROJECT, "zis_photocatalysis"),
        include_builtins=False,
    )
    report = rule_report(result)

    assert "# Rule Report v1.5" in report
    assert "zis.theme.photocorrosion.min_papers" in report
    assert "Configured rule findings: 2" in report


def test_rule_config_does_not_execute_arbitrary_code(tmp_path: Path) -> None:
    marker = tmp_path / "executed.txt"
    path = _write_rules(
        tmp_path / "unsafe.json",
        [
            {
                "rule_id": "unsafe.expression",
                "target": "workspace",
                "severity": "error",
                "condition": {
                    "type": "python_expression",
                    "expression": f"__import__('pathlib').Path({str(marker)!r}).write_text('bad')",
                },
            }
        ],
    )

    findings = validate_rule_set(load_rule_set(path))

    assert any(finding.rule_id == "config.invalid_condition_type" for finding in findings)
    assert not marker.exists()


def test_rules_cli_smoke(tmp_path: Path) -> None:
    report = tmp_path / "rule_report.md"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "paper_workbench.cli",
            "rules",
            "report",
            "--project",
            "zis_photocatalysis",
            "--no-builtins",
            "--out",
            str(report),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    assert "Wrote" in result.stdout
    assert "zis.theme.photocorrosion.min_papers" in report.read_text(encoding="utf-8")
