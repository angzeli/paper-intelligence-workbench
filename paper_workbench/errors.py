"""Shared error and warning taxonomy for user-facing diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ErrorCategory:
    code: str
    severity: str
    source: str
    suggested_action: str


ERROR_TAXONOMY: dict[str, ErrorCategory] = {
    "missing_required_column": ErrorCategory(
        code="missing_required_column",
        severity="error",
        source="registry/import",
        suggested_action="Check the CSV header row and use the documented registry schema.",
    ),
    "malformed_csv": ErrorCategory(
        code="malformed_csv",
        severity="error",
        source="registry/import",
        suggested_action="Open the CSV locally, fix the row/header structure, and retry.",
    ),
    "bad_mapping": ErrorCategory(
        code="bad_mapping",
        severity="error",
        source="import",
        suggested_action="Fix the JSON mapping so every target is a registry field and every source column exists.",
    ),
    "bibtex_parse_warning": ErrorCategory(
        code="bibtex_parse_warning",
        severity="warning",
        source="bibtex",
        suggested_action="Review the surrounding BibTeX manually; the parser is conservative.",
    ),
    "note_parse_warning": ErrorCategory(
        code="note_parse_warning",
        severity="warning",
        source="notes",
        suggested_action="Review the note against the structured note format.",
    ),
    "corrupt_backup_manifest": ErrorCategory(
        code="corrupt_backup_manifest",
        severity="error",
        source="backup",
        suggested_action="Inspect or recreate the backup; restore is blocked until manifest JSON is valid.",
    ),
    "audit_log_parse_warning": ErrorCategory(
        code="audit_log_parse_warning",
        severity="warning",
        source="audit-log",
        suggested_action="Review the malformed audit log line; later valid events remain readable.",
    ),
    "unsafe_destructive_action": ErrorCategory(
        code="unsafe_destructive_action",
        severity="error",
        source="safe-write",
        suggested_action="Rerun with an explicit dry-run or force flag after reviewing the plan.",
    ),
    "path_escapes_workspace": ErrorCategory(
        code="path_escapes_workspace",
        severity="error",
        source="integrity",
        suggested_action="Use project-relative or workspace-relative paths.",
    ),
}


def describe_error(code: str) -> ErrorCategory | None:
    return ERROR_TAXONOMY.get(code)


def _display_where(value: str) -> str:
    text = value.strip()
    if not text:
        return text
    path = Path(text)
    if not path.is_absolute():
        return text
    try:
        return path.resolve(strict=False).relative_to(Path.cwd().resolve(strict=False)).as_posix()
    except ValueError:
        return text


def format_error_message(
    *,
    what: str,
    where: str = "",
    why: str = "",
    next_step: str = "",
) -> str:
    """Build a concise CLI/report error with the expected quality fields."""
    parts = [what.strip()]
    if where:
        parts.append(f"Where: {_display_where(where)}")
    if why:
        parts.append(f"Why it matters: {why.strip()}")
    if next_step:
        parts.append(f"Next step: {next_step.strip()}")
    return " ".join(part for part in parts if part)
