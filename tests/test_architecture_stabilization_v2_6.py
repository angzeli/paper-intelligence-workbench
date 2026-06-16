from __future__ import annotations

from pathlib import Path

from conftest import ROOT
from paper_workbench.integrity import IntegrityResult, workspace_integrity_report
from paper_workbench.markdown import escape_table_cell, findings_table, markdown_table
from paper_workbench.paths import display_path, is_path_within, relative_path
from paper_workbench.reporting import bibtex_audit_report
from paper_workbench.schema import ValidationFinding, make_validation_finding


def test_markdown_helpers_escape_cells_and_render_tables() -> None:
    assert escape_table_cell("alpha|beta\nnext") == "alpha\\|beta next"
    assert markdown_table(["Name", "Count"], [["a|b", 2]], aligns=["", "right"]) == (
        "| Name | Count |\n"
        "| --- | ---: |\n"
        "| a\\|b | 2 |"
    )


def test_findings_table_matches_existing_report_finding_shape() -> None:
    finding = ValidationFinding(
        severity="warning",
        code="pipe_value",
        identifier="paper|1",
        message="Message with | and\nnewline.",
        suggestion="Fix | manually.",
    )

    expected_row = "| warning | pipe_value | paper\\|1 | Message with \\| and newline. | Fix \\| manually. |"

    assert expected_row in findings_table([finding])
    assert expected_row in bibtex_audit_report([], [finding])


def test_integrity_report_uses_shared_finding_table() -> None:
    finding = make_validation_finding(
        "warning",
        "needs_review",
        "Message with | table character.",
        identifier="clean|demo",
        suggestion="Review | locally.",
    )
    result = IntegrityResult(root=str(ROOT), project="clean_demo", findings=[finding], checked_paths=[ROOT / "projects" / "clean_demo"])

    report = workspace_integrity_report(result)

    assert "| warning | needs_review | clean\\|demo | Message with \\| table character. | Review \\| locally. |" in report


def test_path_helpers_preserve_relative_display_contract(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    note = root / "notes" / "paper.md"
    note.parent.mkdir(parents=True)
    note.write_text("# Synthetic note\n", encoding="utf-8")
    outside = tmp_path / "outside.md"

    assert is_path_within(note, root)
    assert not is_path_within(outside, root)
    assert relative_path(note, root) == "notes/paper.md"
    assert display_path(note, base_path=root) == "notes/paper.md"
