from __future__ import annotations

import subprocess
import sys

from conftest import EXAMPLE_REGISTRY, ROOT
from paper_workbench import __version__


def run_cli(*args: str):
    return subprocess.run([sys.executable, "-m", "paper_workbench.cli", *args], cwd=ROOT, check=False, text=True, capture_output=True)


def run_script(*args: str):
    return subprocess.run([sys.executable, *args], cwd=ROOT, check=False, text=True, capture_output=True)


def test_major_cli_help_contracts_are_available():
    commands = [
        (("--help",), "Local-first academic paper registry"),
        (("init", "--help"), "--root"),
        (("project", "--help"), "{init,list,validate}"),
        (("project", "init", "--help"), "--description"),
        (("validate-registry", "--help"), "--force"),
        (("validate-bib", "--help"), "--registry"),
        (("claims", "--help"), "--force"),
        (("import", "--help"), "{zotero-csv,csv,bibtex,ris}"),
        (("import", "csv", "--help"), "--mapping"),
        (("sync", "--help"), "{plan,apply,conflicts,plan-obsidian}"),
        (("sync", "plan", "--help"), "--source-type"),
        (("export", "--help"), "{registry-csv,registry-json"),
        (("index", "--help"), "{rebuild,status,clear}"),
        (("files", "--help"), "{scan,status,link"),
        (("report", "--help"), "evidence-matrix"),
        (("writing-packet", "--help"), "--theme"),
        (("draft", "--help"), "{parse,citations,audit,checklist,evidence-matrix}"),
        (("reading", "--help"), "{queue,start,finish,status,review}"),
        (("followups", "--help"), "{list,export,done}"),
        (("doctor", "--help"), "--strict"),
        (("integrity", "--help"), "{check}"),
        (("audit-log", "--help"), "{show,clear}"),
        (("backup", "--help"), "{create,list,inspect"),
        (("migrate", "--help"), "{plan,run}"),
        (("graph", "--help"), "{build,summary,export}"),
        (("workflow", "--help"), "{list,show,run,validate}"),
        (("review-packet", "--help"), "{create,import-comments,comments,response,followups}"),
        (("synthetic", "--help"), "{generate}"),
    ]

    for args, expected in commands:
        result = run_cli(*args)
        assert result.returncode == 0, (args, result.stderr)
        assert expected in result.stdout, args
        assert "Traceback" not in result.stderr


def test_release_candidate_docs_describe_frozen_surfaces():
    expected = [
        "docs/API_SURFACE.md",
        "docs/CLI_SURFACE.md",
        "docs/COMMAND_CONTRACTS.md",
    ]
    for relative in expected:
        path = ROOT / relative
        assert path.exists(), relative
        content = path.read_text(encoding="utf-8")
        assert "v1." in content or "v2" in content
        assert "local-first" in content


def test_active_docs_use_ignored_scratch_outputs_for_user_commands():
    checked_docs = [
        "README.md",
        "docs/CLI_REFERENCE.md",
        "docs/EXTERNAL_USER_QUICKSTART.md",
        "docs/WORKFLOW_EXAMPLES.md",
    ]
    for relative in checked_docs:
        content = (ROOT / relative).read_text(encoding="utf-8")
        assert "--out reports/" not in content, relative
        assert "--output reports/" not in content, relative
        assert "--reports-dir reports" not in content, relative


def test_readme_quickstart_uses_ignored_scratch_outputs():
    content = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "paperwb claims data/notes --output scratch/example_claims.csv" in content
    assert "reports/example_claims.csv" not in content
    assert "--out reports/workspace_health.md" not in content
    assert "--out reports/photocorrosion_section_outline.md" not in content


def test_command_contract_no_overwrite_and_failure_paths(tmp_path):
    out = tmp_path / "inventory.md"
    result = run_cli("report", "inventory", "--registry", str(EXAMPLE_REGISTRY), "--out", str(out))
    assert result.returncode == 0, result.stderr
    original = out.read_text(encoding="utf-8")

    refusal = run_cli("report", "inventory", "--registry", str(EXAMPLE_REGISTRY), "--out", str(out))
    assert refusal.returncode == 2
    assert out.read_text(encoding="utf-8") == original
    assert "Traceback" not in refusal.stderr

    missing_project = run_cli("project", "validate", "missing_release_candidate_project")
    assert missing_project.returncode == 2
    assert "Next step:" in missing_project.stderr
    assert str(ROOT) not in missing_project.stderr
    assert "Traceback" not in missing_project.stderr

    missing_backup = run_cli("backup", "restore", "missing-backup-id", "--dry-run", "--out", str(tmp_path / "restore.md"))
    assert missing_backup.returncode == 2
    assert "Next step:" in missing_backup.stderr
    assert "Traceback" not in missing_backup.stderr

    audit_clear = run_cli("audit-log", "clear")
    assert audit_clear.returncode == 2
    assert "--force" in audit_clear.stderr
    assert "Traceback" not in audit_clear.stderr


def test_import_dry_run_contract_does_not_modify_registry(tmp_path):
    registry = tmp_path / "papers.csv"
    registry.write_text((ROOT / "data" / "registries" / "example_papers.csv").read_text(encoding="utf-8"), encoding="utf-8")
    before = registry.read_text(encoding="utf-8")
    report = tmp_path / "zotero_import.md"

    result = run_cli(
        "import",
        "zotero-csv",
        "data/examples/zotero_export.csv",
        "--registry",
        str(registry),
        "--reports-dir",
        str(tmp_path),
        "--report",
        str(report),
        "--dry-run",
    )

    assert result.returncode == 0, result.stderr
    assert registry.read_text(encoding="utf-8") == before
    assert "dry-run: True" in result.stdout
    assert report.exists()


def test_clean_room_install_check_quick_generates_release_report(tmp_path):
    out = tmp_path / "clean_room.md"
    result = run_script("scripts/clean_room_install_check.py", "--quick", "--out", str(out))

    assert result.returncode == 0, result.stderr
    content = out.read_text(encoding="utf-8")
    assert f"Current-Environment Release Check v{__version__}" in content
    assert "Failures: 0" in content
    assert "create temp project" in content


def test_data_safety_audit_accepts_release_candidate_title(tmp_path):
    out = tmp_path / "data_safety.md"
    result = run_script(
        "scripts/data_safety_audit.py",
        "--out",
        str(out),
        "--title",
        "Data Safety Audit v1.0-rc",
        "--strict",
    )

    assert result.returncode == 0, result.stderr
    content = out.read_text(encoding="utf-8")
    assert "Data Safety Audit v1.0-rc" in content
    assert "Errors: 0" in content
