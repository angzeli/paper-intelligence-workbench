"""Small Markdown rendering helpers for internal reports."""

from __future__ import annotations

from collections.abc import Iterable, Sequence


def escape_table_cell(value: object, *, strip: bool = False) -> str:
    """Escape a value for a Markdown table cell."""
    text = "" if value is None else str(value)
    text = text.replace("|", "\\|").replace("\n", " ")
    return text.strip() if strip else text


def markdown_table(headers: Sequence[object], rows: Iterable[Sequence[object]], *, aligns: Sequence[str] | None = None) -> str:
    """Render a simple Markdown table with escaped cells."""
    header_values = [escape_table_cell(header) for header in headers]
    align_values = list(aligns or [])
    separators = [_separator_for_alignment(align_values[index] if index < len(align_values) else "") for index, _ in enumerate(header_values)]
    lines = [
        "| " + " | ".join(header_values) + " |",
        "| " + " | ".join(separators) + " |",
    ]
    for row in rows:
        cells = [escape_table_cell(cell) for cell in row]
        if len(cells) < len(header_values):
            cells.extend("" for _ in range(len(header_values) - len(cells)))
        lines.append("| " + " | ".join(cells[: len(header_values)]) + " |")
    return "\n".join(lines)


def findings_table(
    findings: Iterable[object],
    *,
    empty: str = "No findings.",
    identifier_fields: Sequence[str] = ("identifier", "paper_id", "claim_id", "theme"),
    suggestion_field: str = "suggestion",
) -> str:
    """Render common finding objects without coupling every caller to a class."""
    rows: list[list[object]] = []
    for finding in findings:
        identifier = ""
        for field in identifier_fields:
            identifier = getattr(finding, field, "") or ""
            if identifier:
                break
        rows.append(
            [
                getattr(finding, "severity", ""),
                getattr(finding, "code", ""),
                identifier,
                getattr(finding, "message", ""),
                getattr(finding, suggestion_field, ""),
            ]
        )
    if not rows:
        return empty
    return markdown_table(["Severity", "Code", "Identifier", "Message", "Suggestion"], rows)


def _separator_for_alignment(value: str) -> str:
    normalized = value.lower().strip()
    if normalized in {"right", "r", "numeric"}:
        return "---:"
    if normalized in {"center", "c"}:
        return ":---:"
    if normalized in {"left", "l"}:
        return ":---"
    return "---"
