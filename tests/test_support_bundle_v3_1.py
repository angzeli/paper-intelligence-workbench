from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from conftest import ROOT
from paper_workbench.dogfood import create_dogfood_project
from paper_workbench.io import write_csv_rows
from paper_workbench.registry import REGISTRY_FIELDS
from paper_workbench.support import create_support_bundle, redact_path, redaction_preview_markdown, support_doctor_markdown


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "paper_workbench.cli", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


def make_private_project(tmp_path: Path) -> Path:
    create_dogfood_project("photocatalysis", "support_demo", root=tmp_path)
    project = tmp_path / "projects" / "support_demo"
    write_csv_rows(
        project / "registry.csv",
        [
            {
                "paper_id": "private_paper_1",
                "title": "Private ZnIn2S4 Photocorrosion Paper",
                "authors": "Example, Ada",
                "year": "2026",
                "journal": "Private Journal",
                "doi": "10.1234/private.example",
                "url": "https://example.invalid/private",
                "local_pdf_path": "/Users/example/private/references/private_paper_1.pdf",
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
        "@article{privatekey2026, title={Private ZnIn2S4 Photocorrosion Paper}, author={Example, Ada}, year={2026}, doi={10.1234/private.example}}\n",
        encoding="utf-8",
    )
    (project / "notes" / "private_paper_1.md").write_text(
        """# Paper Note: Private ZnIn2S4 Photocorrosion Paper

## Metadata
- Paper ID: private_paper_1
- BibTeX key: privatekey2026
- DOI: 10.1234/private.example
- Year: 2026
- Journal: Private Journal
- Tags: photocorrosion; stability
- Reading status: read

## One-sentence summary

This private note body should not appear in the support bundle.

## Claims and evidence

### Claim 1
- Claim: Secret photocorrosion claim text that must be redacted.
- Evidence type: experimental_result
- Section / page: Results section p. 7
- Quote or paraphrase: Private quote text that must be redacted.
- Confidence: medium
- Tags: photocorrosion; stability
- User comment: private claim comment
- Strength: moderate
- Supports theme: photocorrosion-stability

## Personal reading notes

These private personal reading notes must not be exported.
""",
        encoding="utf-8",
    )
    (project / "papers").mkdir(exist_ok=True)
    (project / "papers" / "private_paper_1.pdf").write_bytes(b"%PDF-1.4\n% synthetic placeholder only\n")
    (project / ".paperwb").mkdir(exist_ok=True)
    (project / ".paperwb" / "index.sqlite").write_bytes(b"not really sqlite")
    (project / ".paperwb" / "audit.log").write_text("private audit log\n", encoding="utf-8")
    (project / "backups").mkdir(exist_ok=True)
    (project / "backups" / "backup.zip").write_bytes(b"not really zip")
    return project


def test_redact_path_replaces_absolute_user_paths() -> None:
    redacted = redact_path("/Users/example/private/references/private_paper_1.pdf")

    assert "/Users/example" not in redacted
    assert redacted == "<redacted-path>/private_paper_1.pdf"


def test_support_bundle_safe_default_redacts_private_content(tmp_path: Path) -> None:
    make_private_project(tmp_path)
    out_dir = tmp_path / "support_bundle"

    bundle = create_support_bundle(project="support_demo", root=tmp_path, out_dir=out_dir)

    assert bundle.safe is True
    assert (out_dir / "manifest.json").exists()
    assert (out_dir / "sanitized_registry_sample.csv").exists()
    assert (out_dir / "sanitized_claims_sample.csv").exists()
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["privacy_boundary"]["copies_pdfs"] is False

    combined_text = "\n".join(path.read_text(encoding="utf-8") for path in out_dir.rglob("*") if path.is_file() and path.suffix in {".md", ".json", ".csv"})
    assert "Private ZnIn2S4 Photocorrosion Paper" not in combined_text
    assert "Secret photocorrosion claim text" not in combined_text
    assert "Private quote text" not in combined_text
    assert "private registry comment" not in combined_text
    assert "/Users/example/private" not in combined_text
    assert "<redacted-title-001>" in combined_text
    assert "<redacted-claim-text>" in combined_text
    assert "<redacted-local-pdf-path>" in combined_text


def test_support_bundle_does_not_include_forbidden_artifacts(tmp_path: Path) -> None:
    make_private_project(tmp_path)
    out_dir = tmp_path / "support_bundle"

    create_support_bundle(project="support_demo", root=tmp_path, out_dir=out_dir)

    outputs = [path.relative_to(out_dir).as_posix() for path in out_dir.rglob("*") if path.is_file()]
    assert not any(path.endswith(".pdf") for path in outputs)
    assert not any(path.endswith(".sqlite") or path.endswith(".db") for path in outputs)
    assert not any("backup" in path.lower() for path in outputs)
    assert not any("audit.log" in path for path in outputs)


def test_support_verbose_local_only_warns(tmp_path: Path) -> None:
    make_private_project(tmp_path)

    preview = redaction_preview_markdown("support_demo", root=tmp_path, verbose_local_only=True)

    assert "Verbose local-only mode is active" in preview
    assert "Private ZnIn2S4 Photocorrosion Paper" in preview


def test_support_doctor_is_sanitized(tmp_path: Path) -> None:
    make_private_project(tmp_path)

    report = support_doctor_markdown("support_demo", root=tmp_path)

    assert "Support Doctor Report" in report
    assert "Private ZnIn2S4 Photocorrosion Paper" not in report
    assert "/Users/example/private" not in report


def test_support_cli_smoke_bundle_preview_and_reproduce(tmp_path: Path) -> None:
    make_private_project(tmp_path)
    out_dir = tmp_path / "support_bundle"
    preview = tmp_path / "preview.md"
    reproduce = tmp_path / "reproduce.md"

    help_result = run_cli("support", "--help")
    bundle = run_cli("support", "bundle", "--project", "support_demo", "--root", str(tmp_path), "--out", str(out_dir))
    preview_result = run_cli("support", "redact-preview", "--project", "support_demo", "--root", str(tmp_path), "--out", str(preview), "--force")
    reproduce_result = run_cli("support", "reproduce", "--project", "support_demo", "--root", str(tmp_path), "--out", str(reproduce), "--force")

    assert help_result.returncode == 0
    assert "bundle" in help_result.stdout
    assert bundle.returncode == 0, bundle.stderr
    assert "Wrote support bundle" in bundle.stdout
    assert preview_result.returncode == 0, preview_result.stderr
    assert reproduce_result.returncode == 0, reproduce_result.stderr
    assert preview.exists()
    assert reproduce.exists()


def test_support_cli_rejects_conflicting_redaction_modes_without_writing(tmp_path: Path) -> None:
    make_private_project(tmp_path)
    out_dir = tmp_path / "conflicting_support_bundle"

    result = run_cli(
        "support",
        "bundle",
        "--project",
        "support_demo",
        "--root",
        str(tmp_path),
        "--safe",
        "--verbose-local-only",
        "--out",
        str(out_dir),
    )

    assert result.returncode == 2
    assert "--safe" in result.stderr
    assert "--verbose-local-only" in result.stderr
    assert not out_dir.exists()
