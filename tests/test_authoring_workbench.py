from __future__ import annotations

import json
import subprocess
import sys

from conftest import ZIS_PROJECT
from paper_workbench.authoring import (
    build_claim_bank,
    build_citation_bank,
    build_evidence_matrix,
    build_paragraph_plan,
    build_subsection_readiness,
    claim_bank_report,
    citation_bank_report,
    evidence_matrix_report,
    paragraph_plan_report,
    subsection_readiness_report,
    writing_packet_report,
)
from paper_workbench.bibtex import parse_bibtex_file
from paper_workbench.claims import collect_notes
from paper_workbench.registry import load_registry
from paper_workbench.tags import load_themes


def run_cli(*args: str):
    return subprocess.run([sys.executable, "-m", "paper_workbench.cli", *args], check=False, text=True, capture_output=True)


def load_zis_inputs():
    papers = load_registry(ZIS_PROJECT / "registry.csv")
    notes = collect_notes(ZIS_PROJECT / "notes")
    claims = [claim for note in notes for claim in note.claims]
    entries = parse_bibtex_file(ZIS_PROJECT / "bibtex" / "library.bib")
    themes = load_themes(ZIS_PROJECT / "themes.json")
    return papers, notes, claims, entries, themes


def test_evidence_matrix_uses_only_tracked_claims_and_citations():
    papers, notes, claims, _entries, themes = load_zis_inputs()
    matrix = build_evidence_matrix("charge separation", papers, claims, themes, notes, project="zis_photocatalysis")
    assert matrix.theme == "charge-separation"
    assert len(matrix.rows) == 1
    assert matrix.rows[0].claim_id == "zis_charge_2025:c1"
    assert matrix.rows[0].bibtex_key == "zisCharge2025"
    report = evidence_matrix_report(matrix)
    assert "does not validate scientific truth" in report
    assert "The synthetic ZIS benchmark records stronger charge transfer" in report


def test_claim_bank_and_citation_bank_flag_weak_review_statement_claims():
    papers, notes, claims, entries, themes = load_zis_inputs()
    bank = build_claim_bank("photocorrosion", claims, themes, project="zis_photocatalysis")
    assert [claim.claim_id for claim in bank.weak_claims] == ["zis_stability_2024:c1"]
    assert [claim.claim_id for claim in bank.missing_evidence_claims] == ["zis_stability_2024:c1"]
    assert "Claims Not Ready for Confident Use" in claim_bank_report(bank)

    citations = build_citation_bank("photocorrosion", papers, claims, themes, notes, entries, project="zis_photocatalysis")
    assert citations.groups["not yet usable"]
    citation_report = citation_bank_report(citations, claims)
    assert "missing location" not in citation_report
    assert "zisStability2024" in citation_report


def test_paragraph_plan_and_readiness_preserve_writing_boundary():
    papers, notes, claims, entries, themes = load_zis_inputs()
    plan = build_paragraph_plan("photocorrosion", papers, claims, themes, notes, project="zis_photocatalysis")
    rendered_plan = paragraph_plan_report(plan)
    assert "not polished final prose" in rendered_plan
    assert "Gap leading to the next subsection" in rendered_plan

    readiness = build_subsection_readiness("photocorrosion", papers, notes, claims, entries, themes, project="zis_photocatalysis")
    rendered_readiness = subsection_readiness_report(readiness)
    assert readiness.status in {"needs_targeted_follow_up", "not_ready"}
    assert "not a truth score" in rendered_readiness
    assert "missing evidence locations" in rendered_readiness


def test_writing_packet_combines_authoring_reports_without_polished_prose():
    papers, notes, claims, entries, themes = load_zis_inputs()
    packet = writing_packet_report("charge separation", papers, notes, claims, entries, themes, project="zis_photocatalysis")
    assert "Literature Review Writing Packet" in packet
    assert "does not fabricate claims" in packet
    assert "## Evidence Matrix" in packet
    assert "## Citation Bank" in packet
    assert "## Subsection Readiness" in packet
    assert "Synthetic ZIS Charge Transfer Benchmark" in packet


def test_cli_authoring_reports_and_matrix_exports(tmp_path):
    matrix_md = tmp_path / "matrix.md"
    matrix_csv = tmp_path / "matrix.csv"
    matrix_json = tmp_path / "matrix.json"
    matrix = run_cli(
        "report",
        "evidence-matrix",
        "--project",
        "zis_photocatalysis",
        "--theme",
        "charge separation",
        "--out",
        str(matrix_md),
        "--csv-out",
        str(matrix_csv),
        "--json-out",
        str(matrix_json),
        "--force",
    )
    assert matrix.returncode == 0, matrix.stderr
    assert matrix_md.exists()
    assert matrix_csv.exists()
    exported = json.loads(matrix_json.read_text(encoding="utf-8"))
    assert exported["rows"][0]["claim_id"] == "zis_charge_2025:c1"

    for report_type in ("claim-bank", "citation-bank", "paragraph-plan", "subsection-readiness"):
        out = tmp_path / f"{report_type}.md"
        result = run_cli("report", report_type, "--project", "zis_photocatalysis", "--theme", "photocorrosion", "--out", str(out), "--force")
        assert result.returncode == 0, result.stderr
        assert out.exists()

    packet = tmp_path / "packet.md"
    result = run_cli("writing-packet", "--project", "zis_photocatalysis", "--theme", "photocorrosion", "--out", str(packet), "--force")
    assert result.returncode == 0, result.stderr
    assert "Writing Packet" in packet.read_text(encoding="utf-8")


def test_cli_evidence_matrix_preflights_multi_output_paths(tmp_path):
    matrix_md = tmp_path / "matrix.md"
    matrix_csv = tmp_path / "matrix.csv"
    matrix_json = tmp_path / "matrix.json"
    matrix_csv.write_text("existing csv\n", encoding="utf-8")

    result = run_cli(
        "report",
        "evidence-matrix",
        "--project",
        "zis_photocatalysis",
        "--theme",
        "charge separation",
        "--out",
        str(matrix_md),
        "--csv-out",
        str(matrix_csv),
        "--json-out",
        str(matrix_json),
    )

    assert result.returncode == 2
    assert f"{matrix_csv} already exists" in result.stderr
    assert not matrix_md.exists()
    assert matrix_csv.read_text(encoding="utf-8") == "existing csv\n"
    assert not matrix_json.exists()


def test_cli_authoring_reports_require_known_theme(tmp_path):
    out = tmp_path / "missing.md"
    result = run_cli("report", "claim-bank", "--project", "zis_photocatalysis", "--theme", "unknown", "--out", str(out))
    assert result.returncode == 2
    assert "Unknown theme" in result.stderr
    assert not out.exists()


def test_authoring_reports_have_stable_strong_weak_and_missing_evidence_sections():
    papers, notes, claims, entries, themes = load_zis_inputs()

    strong_matrix = evidence_matrix_report(
        build_evidence_matrix("charge separation", papers, claims, themes, notes, project="zis_photocatalysis")
    )
    assert "# Evidence Matrix: charge-separation" in strong_matrix
    assert "Claims: 1" in strong_matrix
    assert "zis_charge_2025:c1" in strong_matrix
    assert "| experimental_result | strong | high | Results p. 3 |" in strong_matrix

    weak_bank = claim_bank_report(build_claim_bank("photocorrosion", claims, themes, project="zis_photocatalysis"))
    assert "## Weak or Speculative Claims" in weak_bank
    assert "zis_stability_2024:c1" in weak_bank
    assert "review_statement" in weak_bank
    assert "## Claims Missing Evidence Location" in weak_bank

    missing_readiness = subsection_readiness_report(
        build_subsection_readiness("photocorrosion", papers, notes, claims, entries, themes, project="zis_photocatalysis")
    )
    assert "Status: needs_targeted_follow_up" in missing_readiness
    assert "+0/10: 1 claim(s) missing evidence locations" in missing_readiness
    assert "Score: 50/100" in missing_readiness
