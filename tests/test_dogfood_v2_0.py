from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from conftest import ROOT
from paper_workbench.dogfood import FYP_PHOTOCATALYSIS_THEMES, build_file_plan, create_dogfood_project, dogfood_checklist, dogfood_status
from paper_workbench.registry import load_registry
from paper_workbench.tags import load_themes


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "paper_workbench.cli", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


def test_dogfood_create_photocatalysis_project_structure(tmp_path: Path) -> None:
    result = create_dogfood_project("photocatalysis", "fyp_zis_lit_review", root=tmp_path)
    project = tmp_path / "projects" / "fyp_zis_lit_review"

    assert result.profile.name == "fyp_zis_lit_review"
    for relative in (
        "project.json",
        "registry.csv",
        "themes.json",
        "rules.json",
        "README.md",
        "project_onboarding.md",
        "first_week_plan.md",
        "evidence_tracking_checklist.md",
        "fyp_lit_review_workflow.md",
        "templates/NOTE_TEMPLATE.md",
    ):
        assert (project / relative).exists(), relative
    for dirname in ("notes", "bibtex", "reports", "drafts", "reading_sessions"):
        assert (project / dirname).is_dir(), dirname

    assert load_registry(project / "registry.csv") == []
    theme_ids = {theme.theme_id for theme in load_themes(project / "themes.json")}
    assert len(theme_ids) == len(FYP_PHOTOCATALYSIS_THEMES)
    assert {
        "precursor-derived-thin-films",
        "znin2s4-photocatalysis",
        "znin2s4-structure-phases",
        "xanthate-derived-thin-films",
        "photocorrosion-stability",
    } <= theme_ids
    assert not list(project.rglob("*.pdf"))


def test_dogfood_create_refuses_existing_project(tmp_path: Path) -> None:
    create_dogfood_project("generic", "my_review", root=tmp_path)

    try:
        create_dogfood_project("generic", "my_review", root=tmp_path)
    except FileExistsError as exc:
        assert "project path already exists" in str(exc)
    else:
        raise AssertionError("dogfood creation should refuse an existing project path")


def test_dogfood_status_is_empty_project_friendly(tmp_path: Path) -> None:
    create_dogfood_project("photocatalysis", "fyp_review", root=tmp_path)

    content = dogfood_status("fyp_review", root=tmp_path)

    assert "No papers yet" in content
    assert "No BibTeX entries yet" in content
    assert "No notes yet" in content
    assert "No claims yet" in content
    assert "Next step" in content

    checklist = dogfood_checklist("fyp_review", root=tmp_path)
    assert "Template: `photocatalysis`" in checklist

    create_dogfood_project("finance", "finance_review", root=tmp_path)
    assert "Template: `finance`" in dogfood_checklist("finance_review", root=tmp_path)


def test_plan_from_files_uses_only_filename_and_bibtex_key_matches(tmp_path: Path) -> None:
    references = tmp_path / "references"
    references.mkdir()
    for filename in (
        "001_syntheticalpha2024demo.pdf",
        "002_syntheticbeta2025demo.pdf",
        "003_syntheticgamma2026demo_esi.pdf",
        "004_unmatchedpaper.pdf",
    ):
        (references / filename).write_bytes(b"%PDF-1.4\n% synthetic placeholder\n")
    bibtex = tmp_path / "library.bib"
    bibtex.write_text(
        """@article{syntheticalpha2024demo, title={Synthetic Alpha}, author={Example, Ada}, year={2024}}
@article{syntheticbeta2025demo, title={Synthetic Beta}, author={Example, Ben}, year={2025}}
@article{unlinked2026demo, title={Synthetic Unlinked}, author={Example, Cai}, year={2026}}
""",
        encoding="utf-8",
    )

    plan = build_file_plan("photocatalysis", "demo_project", references, bibtex, limit=15)

    assert plan.pdf_count == 4
    assert plan.supplement_count == 1
    assert plan.bibtex_key_count == 3
    assert plan.selected == [
        ("001_syntheticalpha2024demo.pdf", "syntheticalpha2024demo"),
        ("002_syntheticbeta2025demo.pdf", "syntheticbeta2025demo"),
    ]
    assert "004_unmatchedpaper.pdf" in plan.unmatched_pdfs
    assert "unlinked2026demo" in plan.unmatched_bibtex_keys


def test_dogfood_cli_smoke_create_status_and_plan(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    references = tmp_path / "references"
    references.mkdir()
    (references / "001_syntheticpaper2024demo.pdf").write_bytes(b"%PDF-1.4\n% synthetic placeholder\n")
    bibtex = tmp_path / "library.bib"
    bibtex.write_text("@article{syntheticpaper2024demo, title={Synthetic}, author={Example, Ada}, year={2024}}\n", encoding="utf-8")

    help_result = run_cli("dogfood", "--help")
    created = run_cli("dogfood", "create", "photocatalysis", "--project", "demo_fyp", "--root", str(root))
    duplicate = run_cli("dogfood", "create", "photocatalysis", "--project", "demo_fyp", "--root", str(root))
    status = run_cli("dogfood", "status", "--project", "demo_fyp", "--root", str(root))
    plan = run_cli(
        "dogfood",
        "plan-from-files",
        "photocatalysis",
        "--project",
        "demo_fyp",
        "--references-dir",
        str(references),
        "--bibtex",
        str(bibtex),
    )

    assert help_result.returncode == 0
    assert "plan-from-files" in help_result.stdout
    assert created.returncode == 0, created.stderr
    assert "Created dogfood project demo_fyp" in created.stdout
    assert duplicate.returncode == 2
    assert "project path already exists" in duplicate.stderr
    assert status.returncode == 0
    assert "No papers yet" in status.stdout
    assert plan.returncode == 0
    assert "syntheticpaper2024demo" in plan.stdout


def test_v2_dogfood_docs_use_v2_0_label() -> None:
    checked = [
        ROOT / "reports" / "release_readiness_v2_0.md",
        ROOT / "reports" / "dogfooding_project_template_v2_0.md",
        ROOT / "reports" / "real_project_onboarding_v2_0.md",
        ROOT / "docs" / "REAL_PROJECT_ONBOARDING.md",
        ROOT / "docs" / "FYP_DOGFOODING_WORKFLOW.md",
    ]
    for path in checked:
        content = path.read_text(encoding="utf-8")
        assert "v2.0.0" not in content
        assert "2.0.0" not in content
