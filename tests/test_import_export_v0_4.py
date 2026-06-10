from __future__ import annotations

import json
import subprocess
import sys

import pytest

from paper_workbench.claims import collect_claims, collect_notes
from paper_workbench.exports import export_bundle, export_obsidian_vault, export_reading_list
from paper_workbench.importers import import_bibtex, import_generic_csv, import_report, import_ris, import_zotero_csv
from paper_workbench.registry import create_empty_registry, load_registry, save_registry, validate_registry
from paper_workbench.tags import load_themes

from conftest import (
    EXAMPLE_GENERIC_CSV,
    EXAMPLE_GENERIC_MAPPING,
    EXAMPLE_IMPORT_BIBTEX,
    EXAMPLE_RIS,
    EXAMPLE_ZOTERO_CSV,
    ROOT,
    ZIS_PROJECT,
)


def run_cli(*args: str):
    return subprocess.run([sys.executable, "-m", "paper_workbench.cli", *args], check=False, text=True, capture_output=True)


def test_zotero_csv_import_reports_duplicates_and_unmapped_fields(tmp_path):
    registry = tmp_path / "papers.csv"
    create_empty_registry(registry)
    papers = load_registry(registry)
    result = import_zotero_csv(EXAMPLE_ZOTERO_CSV, papers, registry_path=registry, project="import_demo")
    save_registry(result.registry_papers, registry)
    codes = {warning.code for warning in result.warnings}
    assert result.imported == 3
    assert result.skipped == 2
    assert "duplicate_record" in codes
    assert "missing_title" in codes
    assert "missing_author" in codes
    assert "Extra Local Column" in result.unmapped_fields
    assert "Rows read: 5" in import_report(result)
    assert len(load_registry(registry)) == 3


def test_zotero_csv_dry_run_does_not_modify_registry(tmp_path):
    registry = tmp_path / "papers.csv"
    create_empty_registry(registry)
    papers = load_registry(registry)
    result = import_zotero_csv(EXAMPLE_ZOTERO_CSV, papers, registry_path=registry, dry_run=True)
    assert result.imported == 3
    assert len(papers) == 0
    assert len(load_registry(registry)) == 0


def test_generic_csv_import_with_mapping(tmp_path):
    registry = tmp_path / "papers.csv"
    create_empty_registry(registry)
    papers = load_registry(registry)
    result = import_generic_csv(EXAMPLE_GENERIC_CSV, EXAMPLE_GENERIC_MAPPING, papers, registry_path=registry, project="finance_reading")
    assert result.imported == 2
    assert result.skipped == 1
    imported = result.registry_papers
    assert imported[0].project == "finance_reading"
    assert "finance-valuation" in imported[0].tags
    assert any(warning.code == "duplicate_record" for warning in result.warnings)


def test_generic_csv_mapping_rejects_unknown_registry_field(tmp_path):
    mapping = tmp_path / "bad_mapping.json"
    mapping.write_text('{"Paper Title": "not_a_registry_field"}\n', encoding="utf-8")
    with pytest.raises(ValueError):
        import_generic_csv(EXAMPLE_GENERIC_CSV, mapping, [], registry_path=tmp_path / "papers.csv")


def test_bibtex_import_and_fill_missing(tmp_path):
    registry = tmp_path / "papers.csv"
    create_empty_registry(registry)
    papers = load_registry(registry)
    result = import_bibtex(EXAMPLE_IMPORT_BIBTEX, papers, registry_path=registry, project="ml_methods")
    assert result.imported == 2
    assert result.skipped == 1
    assert any(paper.bibtex_key == "SyntheticImport2026Charge" for paper in result.registry_papers)

    existing = result.registry_papers[:1]
    existing[0].bibtex_key = ""
    fill_result = import_bibtex(EXAMPLE_IMPORT_BIBTEX, existing, registry_path=registry, fill_missing=True)
    assert fill_result.updated == 1
    assert fill_result.registry_papers[0].bibtex_key == "SyntheticImport2026Charge"


def test_ris_import_conservative_parser(tmp_path):
    registry = tmp_path / "papers.csv"
    create_empty_registry(registry)
    result = import_ris(EXAMPLE_RIS, load_registry(registry), registry_path=registry, project="zis_photocatalysis")
    assert result.imported == 2
    assert "N1" in result.unmapped_fields
    assert any(warning.code == "unmapped_field" for warning in result.warnings)


def test_import_roundtrip_registry_json_validation(tmp_path):
    registry = tmp_path / "papers.csv"
    create_empty_registry(registry)
    papers = load_registry(registry)
    zotero = import_zotero_csv(EXAMPLE_ZOTERO_CSV, papers, registry_path=registry, project="roundtrip")
    save_registry(zotero.registry_papers, registry)
    imported = load_registry(registry)
    findings = validate_registry(imported, root=tmp_path)
    assert imported
    assert any(finding.code == "missing_authors" for finding in findings)


def test_obsidian_export_generates_expected_files(tmp_path):
    papers = load_registry(ZIS_PROJECT / "registry.csv")
    notes = collect_notes(ZIS_PROJECT / "notes")
    claims = collect_claims(ZIS_PROJECT / "notes")
    themes = load_themes(ZIS_PROJECT / "themes.json")
    vault = export_obsidian_vault(papers, notes, claims, themes, tmp_path / "vault")
    assert (vault / "index.md").exists()
    assert (vault / "tags.md").exists()
    assert (vault / "themes.md").exists()
    assert (vault / "claims.md").exists()
    assert (vault / "missing_evidence.md").exists()
    assert (vault / "papers" / "zis_charge_2025.md").exists()


def test_bundle_export_contains_manifest_without_pdfs_by_default(tmp_path):
    papers = load_registry(ZIS_PROJECT / "registry.csv")
    bundle = export_bundle(
        registry_path=ZIS_PROJECT / "registry.csv",
        bibtex_path=ZIS_PROJECT / "bibtex" / "library.bib",
        notes_dir=ZIS_PROJECT / "notes",
        themes_path=ZIS_PROJECT / "themes.json",
        reports_dir=ZIS_PROJECT / "reports",
        out=tmp_path / "bundle",
        project="zis_photocatalysis",
        papers=papers,
    )
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["include_pdfs"] is False
    assert (bundle / "data" / "registry.csv").exists()
    assert (bundle / "data" / "notes" / "zis_charge_2025.md").exists()


def test_reading_list_theme_and_csv_exports(tmp_path):
    papers = load_registry(ZIS_PROJECT / "registry.csv")
    themes = load_themes(ZIS_PROJECT / "themes.json")
    markdown = export_reading_list(papers, tmp_path / "theme.md", theme="photocorrosion", themes=themes)
    assert "zis_stability_2024" in markdown.read_text(encoding="utf-8")
    csv_path = export_reading_list(papers, tmp_path / "included.csv", included=True, output_format="csv")
    assert "paper_id,title" in csv_path.read_text(encoding="utf-8")


def test_cli_import_and_export_smoke(tmp_path):
    registry = tmp_path / "papers.csv"
    reports = tmp_path / "reports"
    zotero = run_cli(
        "import",
        "zotero-csv",
        str(EXAMPLE_ZOTERO_CSV),
        "--registry",
        str(registry),
        "--reports-dir",
        str(reports),
        "--force",
    )
    assert zotero.returncode == 0, zotero.stderr
    assert registry.exists()
    assert (reports / "import_zotero_csv.md").exists()

    dry_run = run_cli(
        "import",
        "bibtex",
        str(EXAMPLE_IMPORT_BIBTEX),
        "--registry",
        str(registry),
        "--reports-dir",
        str(reports),
        "--dry-run",
        "--force",
    )
    assert dry_run.returncode == 0, dry_run.stderr
    assert "dry-run: True" in dry_run.stdout

    vault = tmp_path / "vault"
    obsidian = run_cli("export", "obsidian", "--registry", str(registry), "--out", str(vault), "--force")
    assert obsidian.returncode == 0, obsidian.stderr
    assert (vault / "index.md").exists()

    bundle = tmp_path / "bundle"
    bundle_result = run_cli("export", "bundle", "--registry", str(registry), "--reports-dir", str(reports), "--out", str(bundle), "--force")
    assert bundle_result.returncode == 0, bundle_result.stderr
    assert (bundle / "manifest.json").exists()
