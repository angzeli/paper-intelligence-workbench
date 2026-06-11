from __future__ import annotations

import subprocess
import sys

from conftest import EXAMPLE_REGISTRY
from paper_workbench.files import (
    duplicate_files_report,
    link_file_to_paper,
    load_file_registry,
    local_files_audit_report,
    missing_files_report,
    save_file_registry,
    scan_local_files,
    sha256_file,
    text_sidecars_report,
    unlink_file_from_paper,
)
from paper_workbench.registry import load_registry, save_registry
from paper_workbench.schema import Author, Paper


def run_cli(*args: str):
    return subprocess.run([sys.executable, "-m", "paper_workbench.cli", *args], check=False, text=True, capture_output=True)


def make_file_workspace(tmp_path):
    root = tmp_path / "project"
    for dirname in ("papers", "text", "notes", "bibtex", "reports"):
        (root / dirname).mkdir(parents=True)
    registry = root / "registry.csv"
    save_registry(
        [
            Paper(
                paper_id="paper_alpha",
                title="Synthetic Alpha Local File Paper",
                authors=[Author(given="Ada", family="Alpha", raw_name="Ada Alpha")],
                year="2026",
                local_pdf_path="papers/missing_alpha.pdf",
                notes_path="notes/paper_alpha.md",
            ),
            Paper(
                paper_id="paper_beta",
                title="Synthetic Beta Local File Paper",
                authors=[Author(given="Ben", family="Beta", raw_name="Ben Beta")],
                year="2025",
            ),
        ],
        registry,
    )
    (root / "papers" / "paper_alpha.pdf").write_bytes(b"%PDF-1.4 synthetic local placeholder\n")
    (root / "papers" / "paper_alpha_copy.pdf").write_bytes(b"%PDF-1.4 synthetic local placeholder\n")
    (root / "text" / "paper_alpha.txt").write_text("Synthetic sidecar text about local evidence.\n", encoding="utf-8")
    (root / "text" / "orphan_sidecar.txt").write_text("Synthetic orphan sidecar.\n", encoding="utf-8")
    (root / "notes" / "paper_alpha.md").write_text("# Synthetic note\n", encoding="utf-8")
    (root / "bibtex" / "library.bib").write_text("@misc{alpha,title={Synthetic}}\n", encoding="utf-8")
    (root / "papers" / "unsupported.tmp").write_text("ignore\n", encoding="utf-8")
    return root, registry, root / "files.csv"


def test_scan_local_files_detects_sidecars_duplicates_missing_and_unsupported(tmp_path):
    root, registry, files_csv = make_file_workspace(tmp_path)

    result = scan_local_files(root=root, registry_path=registry, file_registry_path=files_csv)

    assert len(result.records) == 6
    assert any(record.relative_path == "text/paper_alpha.txt" and record.paper_id == "paper_alpha" for record in result.sidecars)
    assert any(record.relative_path == "text/orphan_sidecar.txt" and not record.paper_id for record in result.sidecars)
    assert result.missing_registry_files == ["paper_alpha: papers/missing_alpha.pdf"]
    assert result.unsupported_files == ["papers/unsupported.tmp"]
    assert len(result.duplicate_hashes) == 1
    assert any("Text sidecar has no matching paper_id" in warning for warning in result.warnings)


def test_file_registry_save_load_and_reports(tmp_path):
    root, registry, files_csv = make_file_workspace(tmp_path)
    result = scan_local_files(root=root, registry_path=registry, file_registry_path=files_csv)

    save_file_registry(result.records, files_csv)
    loaded = load_file_registry(files_csv)

    assert len(loaded) == len(result.records)
    assert loaded[0].sha256
    assert "Local Files Audit v0.7" in local_files_audit_report(result)
    assert "Duplicate Files v0.7" in duplicate_files_report(result)
    assert "paper_alpha: papers/missing_alpha.pdf" in missing_files_report(result)
    assert "Text Sidecars v0.7" in text_sidecars_report(result)


def test_link_and_unlink_file_preserve_files_and_store_relative_paths(tmp_path):
    root, registry, files_csv = make_file_workspace(tmp_path)
    linked_pdf = root / "papers" / "paper_beta.pdf"
    linked_pdf.write_bytes(b"%PDF-1.4 beta synthetic placeholder\n")

    record = link_file_to_paper(
        paper_id="paper_beta",
        file_path="papers/paper_beta.pdf",
        root=root,
        registry_path=registry,
        file_registry_path=files_csv,
    )

    assert record.relative_path == "papers/paper_beta.pdf"
    assert linked_pdf.exists()
    assert load_registry(registry)[1].local_pdf_path == "papers/paper_beta.pdf"
    assert load_file_registry(files_csv)[0].paper_id == "paper_beta"

    removed = unlink_file_from_paper(paper_id="paper_beta", root=root, registry_path=registry, file_registry_path=files_csv)

    assert removed == 1
    assert linked_pdf.exists()
    assert load_registry(registry)[1].local_pdf_path == ""
    assert load_file_registry(files_csv) == []


def test_link_refuses_to_overwrite_existing_pdf_path_without_force(tmp_path):
    root, registry, files_csv = make_file_workspace(tmp_path)
    replacement = root / "papers" / "replacement.pdf"
    replacement.write_bytes(b"%PDF replacement\n")
    papers = load_registry(registry)
    papers[1].local_pdf_path = "papers/existing.pdf"
    save_registry(papers, registry)

    result = run_cli(
        "files",
        "link",
        "paper_beta",
        str(replacement),
        "--registry",
        str(registry),
        "--file-registry",
        str(files_csv),
    )

    assert result.returncode == 2
    assert "already has local_pdf_path" in result.stderr
    assert not files_csv.exists()
    assert load_registry(registry)[1].local_pdf_path == "papers/existing.pdf"


def test_cli_files_scan_status_audit_hash_and_sidecars(tmp_path):
    root, registry, files_csv = make_file_workspace(tmp_path)
    reports_dir = root / "reports"

    scan = run_cli("files", "scan", "--registry", str(registry), "--file-registry", str(files_csv), "--scan-dir", str(root / "text"), "--write-registry")
    assert scan.returncode == 0, scan.stderr
    assert files_csv.exists()
    assert "paper_alpha" in scan.stdout

    status = run_cli("files", "status", "--registry", str(registry), "--file-registry", str(files_csv), "--scan-dir", str(root / "text"))
    assert status.returncode == 0
    assert "Text sidecars: 2" in status.stdout

    sidecars = run_cli("files", "sidecars", "--registry", str(registry), "--scan-dir", str(root / "text"))
    assert sidecars.returncode == 0
    assert "orphan_sidecar" in sidecars.stdout

    audit = run_cli("files", "audit", "--registry", str(registry), "--scan-dir", str(root / "text"), "--reports-dir", str(reports_dir), "--force")
    assert audit.returncode == 0, audit.stderr
    assert (reports_dir / "local_files_audit_v0_7.md").exists()
    assert (reports_dir / "text_sidecars_v0_7.md").exists()

    hashed = run_cli("files", "hash", str(root / "text" / "paper_alpha.txt"))
    assert hashed.returncode == 0
    assert sha256_file(root / "text" / "paper_alpha.txt") in hashed.stdout


def test_cli_files_scan_default_workspace_uses_data_folders():
    result = run_cli("files", "scan", "--registry", str(EXAMPLE_REGISTRY))

    assert result.returncode == 0
    assert "data/text/synth_charge_2024.txt" in result.stdout


def test_no_pdf_examples_are_tracked():
    result = subprocess.run(["git", "ls-files", "*.pdf"], check=True, text=True, capture_output=True)
    assert result.stdout.strip() == ""
