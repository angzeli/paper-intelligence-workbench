from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from conftest import ROOT
from paper_workbench.registry import load_registry
from paper_workbench.rules import load_rule_set, validate_rule_set
from paper_workbench.tags import load_themes
from paper_workbench.templates import create_project_from_template, get_template, inspect_template, list_templates


def run_cli(*args: str):
    return subprocess.run([sys.executable, "-m", "paper_workbench.cli", *args], cwd=ROOT, check=False, text=True, capture_output=True)


def test_template_listing_and_inspection() -> None:
    template_ids = {template.template_id for template in list_templates()}

    assert template_ids == {"finance", "generic", "ml-methods", "photocatalysis"}
    assert len(get_template("photocatalysis").themes) == 10
    assert "Photocatalysis Literature Review" in inspect_template("photocatalysis")
    assert "does not provide investment advice" in inspect_template("finance")


def test_template_create_generates_project_structure(tmp_path: Path) -> None:
    result = create_project_from_template("photocatalysis", "demo_photo", root=tmp_path)
    project = tmp_path / "projects" / "demo_photo"

    assert result.profile.name == "demo_photo"
    assert (project / "project.json").exists()
    assert (project / "registry.csv").exists()
    assert (project / "themes.json").exists()
    assert (project / "rules.json").exists()
    assert (project / "templates" / "NOTE_TEMPLATE.md").exists()
    assert (project / "registry_schema.md").exists()
    assert (project / "report_checklist.md").exists()
    assert (project / "manuscript_qa_checklist.md").exists()
    assert (project / "dashboard_expectations.md").exists()
    assert (project / "reading_queue_config.json").exists()

    assert load_registry(project / "registry.csv") == []
    themes = load_themes(project / "themes.json")
    assert len(themes) == 10
    assert {theme.theme_id for theme in themes} >= {"photocorrosion", "charge-separation", "co2-reduction"}
    rule_set = load_rule_set(project / "rules.json")
    assert not validate_rule_set(rule_set)
    assert any(rule.rule_id == "template.strong_claims_need_evidence_location" for rule in rule_set.rules)


def test_template_create_is_non_destructive(tmp_path: Path) -> None:
    create_project_from_template("generic", "demo_review", root=tmp_path)

    try:
        create_project_from_template("generic", "demo_review", root=tmp_path)
    except FileExistsError as exc:
        assert "project path already exists" in str(exc)
    else:
        raise AssertionError("template creation should refuse an existing project")


def test_template_cli_smoke_create_and_refuse_duplicate(tmp_path: Path) -> None:
    root = tmp_path / "workspace"

    listed = run_cli("template", "list")
    inspected = run_cli("template", "inspect", "ml-methods")
    created = run_cli("template", "create", "ml-methods", "--project", "demo_ml", "--root", str(root))
    duplicate = run_cli("template", "create", "ml-methods", "--project", "demo_ml", "--root", str(root))

    assert listed.returncode == 0
    assert "photocatalysis" in listed.stdout
    assert inspected.returncode == 0
    assert "ML Methods Reading" in inspected.stdout
    assert created.returncode == 0
    assert "Created project demo_ml from template ml-methods" in created.stdout
    assert duplicate.returncode == 2
    assert "project path already exists" in duplicate.stderr
