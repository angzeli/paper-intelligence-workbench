from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from conftest import ROOT
from paper_workbench.dogfood import create_dogfood_project
from paper_workbench.external import add_external_workspace, external_validation_markdown, list_external_workspaces, validate_external_workspace
from paper_workbench.io import write_csv_rows
from paper_workbench.registry import REGISTRY_FIELDS
from paper_workbench.safety import FORBIDDEN_PARTS


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "paper_workbench.cli", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


def make_external_workspace(tmp_path: Path) -> tuple[Path, Path]:
    external_root = tmp_path / "external_workspace"
    create_dogfood_project("photocatalysis", "real_demo", root=external_root)
    project = external_root / "projects" / "real_demo"
    write_csv_rows(
        project / "registry.csv",
        [
            {
                "paper_id": "private_paper_1",
                "title": "Private Photocatalysis Paper",
                "authors": "Example, Ada",
                "year": "2026",
                "journal": "Private Journal",
                "doi": "10.9999/private.example",
                "url": "https://example.invalid/private",
                "local_pdf_path": "/home/example/local_refs/private_paper_1.pdf",
                "bibtex_key": "privatekey2026",
                "tags": "photocorrosion; stability",
                "reading_status": "read",
                "notes_path": "notes/private_paper_1.md",
                "user_comment": "private registry comment",
            }
        ],
        REGISTRY_FIELDS,
        force=True,
    )
    (project / "bibtex" / "library.bib").write_text(
        "@article{privatekey2026, title={Private Photocatalysis Paper}, author={Example, Ada}, year={2026}, journal={Private Journal}, doi={10.9999/private.example}}\n",
        encoding="utf-8",
    )
    (project / "notes" / "private_paper_1.md").write_text(
        """# Paper Note: Private Photocatalysis Paper

## Metadata
- Paper ID: private_paper_1
- BibTeX key: privatekey2026
- Reading status: read
- Tags: photocorrosion; stability

## Claims and evidence

### Claim 1
- Claim: Private claim text that must stay outside the repository.
- Evidence type: experimental_result
- Section / page: Results p. 4
- Quote or paraphrase: Private quote text that must be redacted.
- Confidence: medium
- Tags: photocorrosion; stability
- Strength: moderate
- Supports theme: photocorrosion-stability
""",
        encoding="utf-8",
    )
    (project / "papers").mkdir(exist_ok=True)
    (project / "papers" / "private_paper_1.pdf").write_bytes(b"%PDF-1.4\n% synthetic test placeholder\n")
    return external_root, project


def test_external_config_creation_and_listing(tmp_path: Path) -> None:
    external_root, _project = make_external_workspace(tmp_path)
    config = tmp_path / ".paperwb-local" / "workspaces.json"

    workspace = add_external_workspace("fyp_private", external_root, project="real_demo", config_path=config)
    workspaces = list_external_workspaces(config_path=config)
    payload = json.loads(config.read_text(encoding="utf-8"))

    assert workspace.name == "fyp_private"
    assert workspace.project == "real_demo"
    assert payload["schema"] == "paperwb-external-workspaces-v1"
    assert list(workspaces)[0].name == "fyp_private"
    assert "Private Photocatalysis Paper" not in config.read_text(encoding="utf-8")


def test_external_workspace_validation(tmp_path: Path) -> None:
    external_root, _project = make_external_workspace(tmp_path)
    config = tmp_path / ".paperwb-local" / "workspaces.json"
    add_external_workspace("fyp_private", external_root, project="real_demo", config_path=config)

    validation = validate_external_workspace("fyp_private", config_path=config)
    report = external_validation_markdown(validation)

    assert validation.profile is not None
    assert validation.profile.name == "real_demo"
    assert not validation.blocking_errors
    assert str(external_root) not in report
    assert "<redacted-external-workspace>" in report


def test_external_validation_show_paths_is_explicit(tmp_path: Path) -> None:
    external_root, _project = make_external_workspace(tmp_path)
    config = tmp_path / ".paperwb-local" / "workspaces.json"
    add_external_workspace("fyp_private", external_root, project="real_demo", config_path=config)

    validation = validate_external_workspace("fyp_private", config_path=config)
    safe_report = external_validation_markdown(validation)
    verbose_report = external_validation_markdown(validation, reveal_paths=True)

    assert str(external_root) not in safe_report
    assert str(external_root) in verbose_report


def test_external_missing_path_handling(tmp_path: Path) -> None:
    missing = tmp_path / "missing_workspace"
    config = tmp_path / ".paperwb-local" / "workspaces.json"

    result = run_cli("external", "add", "missing", str(missing), "--config", str(config))

    assert result.returncode != 0
    assert "existing directory" in result.stderr
    assert not config.exists()


def test_external_cli_workflows_do_not_copy_private_data_into_repo(tmp_path: Path) -> None:
    external_root, project = make_external_workspace(tmp_path)
    config = tmp_path / ".paperwb-local" / "workspaces.json"
    support_dir = tmp_path / "support_bundle"
    claims_out = project / "reports" / "external_claims.csv"
    evidence_out = project / "reports" / "external_evidence_map.md"
    citation_out = project / "reports" / "external_citation_audit.md"

    add_result = run_cli("external", "add", "fyp_private", str(external_root), "--project", "real_demo", "--config", str(config))
    list_result = run_cli("external", "list", "--config", str(config))
    validate_result = run_cli("external", "validate", "fyp_private", "--config", str(config), "--strict")
    validate_report = project / "reports" / "external_validate.md"
    validate_report_result = run_cli("external", "validate", "fyp_private", "--config", str(config), "--out", str(validate_report), "--force")
    validate_verbose_report = project / "reports" / "external_validate_verbose.md"
    validate_verbose_result = run_cli(
        "external",
        "validate",
        "fyp_private",
        "--config",
        str(config),
        "--out",
        str(validate_verbose_report),
        "--force",
        "--show-paths",
    )
    doctor_result = run_cli("external", "run", "fyp_private", "doctor", "--config", str(config))
    doctor_report = project / "reports" / "external_doctor.md"
    doctor_report_result = run_cli("external", "run", "fyp_private", "doctor", "--config", str(config), "--out", str(doctor_report), "--force")
    dashboard_result = run_cli("external", "run", "fyp_private", "dashboard", "--config", str(config))
    registry_result = run_cli("external", "run", "fyp_private", "validate-registry", "--config", str(config), "--strict")
    bib_result = run_cli("external", "run", "fyp_private", "validate-bib", "--config", str(config), "--strict")
    claims_result = run_cli("external", "run", "fyp_private", "claims", "--config", str(config), "--out", str(claims_out), "--force")
    evidence_result = run_cli("external", "run", "fyp_private", "evidence-map", "--config", str(config), "--out", str(evidence_out), "--force")
    citation_result = run_cli("external", "run", "fyp_private", "citation-audit", "--config", str(config), "--out", str(citation_out), "--force")
    support_result = run_cli("external", "run", "fyp_private", "support-bundle", "--config", str(config), "--out", str(support_dir), "--force")

    assert add_result.returncode == 0, add_result.stderr
    assert list_result.returncode == 0
    assert "fyp_private" in list_result.stdout
    assert str(external_root) not in add_result.stdout
    assert str(external_root) not in list_result.stdout
    assert validate_result.returncode == 0, validate_result.stderr
    assert str(external_root) not in validate_result.stdout
    assert validate_report_result.returncode == 0, validate_report_result.stderr
    assert str(external_root) not in validate_report_result.stdout
    assert str(external_root) not in validate_report.read_text(encoding="utf-8")
    assert "<redacted-external-workspace>" in validate_report.read_text(encoding="utf-8")
    assert validate_verbose_result.returncode == 0, validate_verbose_result.stderr
    assert str(external_root) in validate_verbose_result.stdout
    assert str(external_root) in validate_verbose_report.read_text(encoding="utf-8")
    assert doctor_result.returncode == 0, doctor_result.stderr
    assert "Workspace Health Report" in doctor_result.stdout
    assert str(external_root) not in doctor_result.stdout
    assert doctor_report_result.returncode == 0, doctor_report_result.stderr
    assert str(external_root) not in doctor_report.read_text(encoding="utf-8")
    assert dashboard_result.returncode == 0, dashboard_result.stderr
    assert "Paper Workbench Dashboard - real_demo" in dashboard_result.stdout
    assert registry_result.returncode == 0, registry_result.stderr
    assert bib_result.returncode == 0, bib_result.stderr
    assert claims_result.returncode == 0, claims_result.stderr
    assert evidence_result.returncode == 0, evidence_result.stderr
    assert citation_result.returncode == 0, citation_result.stderr
    assert support_result.returncode == 0, support_result.stderr
    for result in [claims_result, evidence_result, citation_result, support_result]:
        assert str(external_root) not in result.stdout

    assert claims_out.exists()
    assert evidence_out.exists()
    assert citation_out.exists()
    combined_support = "\n".join(path.read_text(encoding="utf-8") for path in support_dir.rglob("*") if path.is_file() and path.suffix in {".md", ".json", ".csv"})
    assert "Private Photocatalysis Paper" not in combined_support
    assert "Private claim text" not in combined_support
    assert "Private quote text" not in combined_support
    assert "/home/example/local_refs" not in combined_support
    assert not any(path.suffix.lower() == ".pdf" for path in support_dir.rglob("*") if path.is_file())
    assert "Private Photocatalysis Paper" not in config.read_text(encoding="utf-8")


def test_external_cli_remove_and_backup(tmp_path: Path) -> None:
    external_root, _project = make_external_workspace(tmp_path)
    config = tmp_path / ".paperwb-local" / "workspaces.json"
    add_external_workspace("fyp_private", external_root, project="real_demo", config_path=config)

    backup_result = run_cli("external", "run", "fyp_private", "backup", "--config", str(config), "--notes", "test backup")
    remove_result = run_cli("external", "remove", "fyp_private", "--config", str(config))
    list_result = run_cli("external", "list", "--config", str(config))

    assert backup_result.returncode == 0, backup_result.stderr
    assert "Created backup" in backup_result.stdout
    assert str(external_root) not in backup_result.stdout
    assert not any(path.suffix.lower() == ".pdf" for path in (external_root / "projects" / "real_demo" / "backups").rglob("*") if path.is_file())
    assert remove_result.returncode == 0, remove_result.stderr
    assert "Removed external workspace" in remove_result.stdout
    assert list_result.returncode == 0
    assert "No external workspaces registered" in list_result.stdout


def test_local_only_config_is_ignored_and_forbidden_if_tracked() -> None:
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    assert ".paperwb-local/" in ignore
    assert ".paperwb-local" in FORBIDDEN_PARTS
