from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

from conftest import ROOT, ZIS_PROJECT
from paper_workbench.bibtex import parse_bibtex_file
from paper_workbench.claims import collect_claims, collect_notes
from paper_workbench.registry import load_registry
from paper_workbench.review_packets import (
    COMMENT_FIELDS,
    ReviewItem,
    build_review_items,
    build_review_response,
    create_review_packet,
    import_reviewer_comments,
    load_reviewer_comments,
    response_to_review_report,
    review_followups_report,
    reviewer_comments_report,
)
from paper_workbench.tags import load_themes


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    return subprocess.run(
        [sys.executable, "-m", "paper_workbench.cli", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
        env=env,
    )


def _zis_inputs():
    papers = load_registry(ZIS_PROJECT / "registry.csv")
    notes = collect_notes(ZIS_PROJECT / "notes")
    claims = collect_claims(ZIS_PROJECT / "notes")
    entries = parse_bibtex_file(ZIS_PROJECT / "bibtex" / "library.bib")
    themes = load_themes(ZIS_PROJECT / "themes.json")
    return papers, notes, claims, entries, themes


def _write_comment_row(path: Path, *, item_id: str = "claim:zis_stability_2024:c1", item_type: str = "claim") -> None:
    row = {
        "comment_id": "review_1",
        "item_id": item_id,
        "item_type": item_type,
        "reviewer": "Synthetic Reviewer",
        "status": "needs_reread",
        "comment": "Please verify this evidence location before draft use.",
        "recommendation": "Add page or section evidence.",
        "requires_reread": "true",
        "requires_citation_check": "false",
        "weak_evidence": "true",
        "created_at": "2026-06-16T00:00:00+00:00",
    }
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COMMENT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerow(row)


def test_review_packet_creation_writes_manifest_and_comment_template(tmp_path: Path) -> None:
    papers, notes, claims, entries, themes = _zis_inputs()

    packet = create_review_packet(
        project="zis_photocatalysis",
        output_dir=tmp_path / "packet",
        papers=papers,
        notes=notes,
        claims=claims,
        entries=entries,
        themes=themes,
        theme="photocorrosion",
    )

    packet_dir = tmp_path / "packet"
    assert packet.packet_id.startswith("review_zis_photocatalysis_photocorrosion")
    assert (packet_dir / "overview.md").exists()
    assert (packet_dir / "comments.csv").exists()
    assert (packet_dir / "manifest.json").exists()
    assert (packet_dir / "evidence_matrix.md").exists()
    manifest = json.loads((packet_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["includes_pdfs"] is False
    assert any(item["item_type"] == "claim" for item in manifest["items"])
    assert "comments.csv" in manifest["files"]


def test_comment_import_dry_run_validates_without_writing(tmp_path: Path) -> None:
    papers, notes, claims, entries, themes = _zis_inputs()
    items, _warnings = build_review_items(papers, notes, claims, themes, entries, theme="photocorrosion")
    comments_csv = tmp_path / "comments.csv"
    sidecar = tmp_path / "reviewer_comments.json"
    _write_comment_row(comments_csv)

    result = import_reviewer_comments(
        comments_csv,
        project="zis_photocatalysis",
        output_path=sidecar,
        known_items=items,
        dry_run=True,
    )

    assert not result.errors
    assert len(result.comments) == 1
    assert not sidecar.exists()


def test_comment_import_rejects_unknown_item_and_invalid_rows(tmp_path: Path) -> None:
    comments_csv = tmp_path / "bad_comments.csv"
    _write_comment_row(comments_csv, item_id="claim:unknown", item_type="claim")

    result = import_reviewer_comments(
        comments_csv,
        project="demo",
        output_path=tmp_path / "reviewer_comments.json",
        known_items=[ReviewItem(item_id="claim:known", item_type="claim", label="Known claim")],
        dry_run=True,
    )

    assert result.errors
    assert "unknown review item" in result.errors[0]

    invalid_csv = tmp_path / "invalid_comments.csv"
    invalid_csv.write_text("item_id,item_type,comment\nclaim:x,not_a_type,hello\n", encoding="utf-8")
    invalid = import_reviewer_comments(invalid_csv, project="demo", output_path=tmp_path / "comments.json", dry_run=True)

    assert invalid.errors
    assert "Missing required comment field" in invalid.errors[0]


def test_comment_import_writes_sidecar_without_overwriting_claims(tmp_path: Path) -> None:
    papers, notes, claims, entries, themes = _zis_inputs()
    before = {claim.claim_id: claim.claim_text for claim in claims}
    items, _warnings = build_review_items(papers, notes, claims, themes, entries, theme="photocorrosion")
    comments_csv = tmp_path / "comments.csv"
    sidecar = tmp_path / "reviewer_comments.json"
    _write_comment_row(comments_csv)

    result = import_reviewer_comments(
        comments_csv,
        project="zis_photocatalysis",
        output_path=sidecar,
        known_items=items,
        dry_run=False,
        force=True,
    )

    after = {claim.claim_id: claim.claim_text for claim in claims}
    assert not result.errors
    assert before == after
    loaded = load_reviewer_comments(sidecar)
    assert loaded[0].comment_id == "review_1"


def test_response_and_followup_reports_from_comments(tmp_path: Path) -> None:
    comments_csv = tmp_path / "comments.csv"
    sidecar = tmp_path / "reviewer_comments.json"
    _write_comment_row(comments_csv)
    import_reviewer_comments(comments_csv, project="demo", output_path=sidecar, dry_run=False, force=True)
    comments = load_reviewer_comments(sidecar)
    response = build_review_response(comments, project="demo")

    comments_report = reviewer_comments_report(comments, project="demo")
    response_report = response_to_review_report(response)
    followups_report = review_followups_report(response)

    assert "Reviewer Comments" in comments_report
    assert "Response to Review" in response_report
    assert "Comments requiring reread: 1" in response_report
    assert "Reread local evidence" in followups_report


def test_review_packet_cli_smoke(tmp_path: Path) -> None:
    packet_dir = tmp_path / "packet"
    comments_csv = tmp_path / "review_comments.csv"
    sidecar = tmp_path / "reviewer_comments.json"
    import_report = tmp_path / "import_report.md"
    response_report = tmp_path / "response.md"
    followups_report = tmp_path / "followups.md"

    help_result = run_cli("review-packet", "--help")
    create = run_cli(
        "review-packet",
        "create",
        "--project",
        "zis_photocatalysis",
        "--theme",
        "photocorrosion",
        "--out",
        str(packet_dir),
    )
    _write_comment_row(comments_csv)
    dry_run = run_cli(
        "review-packet",
        "import-comments",
        str(comments_csv),
        "--project",
        "zis_photocatalysis",
        "--theme",
        "photocorrosion",
        "--comments-store",
        str(sidecar),
        "--dry-run",
    )
    assert not sidecar.exists()
    write = run_cli(
        "review-packet",
        "import-comments",
        str(comments_csv),
        "--project",
        "zis_photocatalysis",
        "--theme",
        "photocorrosion",
        "--comments-store",
        str(sidecar),
        "--force",
        "--out",
        str(import_report),
        "--force-report",
    )
    response = run_cli(
        "review-packet",
        "response",
        "--project",
        "zis_photocatalysis",
        "--theme",
        "photocorrosion",
        "--comments-store",
        str(sidecar),
        "--out",
        str(response_report),
        "--force",
    )
    followups = run_cli(
        "review-packet",
        "followups",
        "--project",
        "zis_photocatalysis",
        "--theme",
        "photocorrosion",
        "--comments-store",
        str(sidecar),
        "--out",
        str(followups_report),
        "--force",
    )

    assert help_result.returncode == 0
    assert "{create,import-comments,comments,response,followups}" in help_result.stdout
    assert create.returncode == 0, create.stderr
    assert (packet_dir / "manifest.json").exists()
    assert dry_run.returncode == 0, dry_run.stderr
    assert "Dry run: `true`" in dry_run.stdout
    assert write.returncode == 0, write.stderr
    assert sidecar.exists()
    assert response.returncode == 0, response.stderr
    assert followups.returncode == 0, followups.stderr
    assert "Response to Review" in response_report.read_text(encoding="utf-8")
