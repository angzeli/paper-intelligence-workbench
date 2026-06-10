"""Local import/export helpers."""

from __future__ import annotations

from pathlib import Path

from .claims import claim_to_row, save_claims_csv
from .io import write_json, write_text
from .registry import filter_papers, save_registry, save_registry_json
from .schema import Claim, Paper, dataclass_to_plain


def _relativize_note_file(row: dict) -> dict:
    note_file = row.get("note_file", "")
    if note_file:
        path = Path(note_file)
        if path.is_absolute():
            try:
                row["note_file"] = str(path.relative_to(Path.cwd()))
            except ValueError:
                row["note_file"] = path.name
    return row


def export_registry_csv(papers: list[Paper], out: str | Path, force: bool = True) -> Path:
    return save_registry(papers, out) if force else save_registry_no_overwrite(papers, out)


def export_registry_json(papers: list[Paper], out: str | Path, force: bool = True) -> Path:
    return save_registry_json(papers, out) if force else _write_registry_json_no_overwrite(papers, out)


def export_claims_csv(claims: list[Claim], out: str | Path, force: bool = True) -> Path:
    return save_claims_csv(claims, out, force=force)


def export_claims_json(claims: list[Claim], out: str | Path, force: bool = True) -> Path:
    return write_json(out, [_relativize_note_file(dataclass_to_plain(claim)) for claim in claims], force=force)


def reading_list_markdown(papers: list[Paper], *, tag: str = "", status: str = "") -> str:
    filtered = filter_papers(papers, tag=tag, status=status)
    title = "Reading List"
    if tag:
        title += f": {tag}"
    if status:
        title += f" ({status})"
    lines = [f"# {title}", "", f"Papers: {len(filtered)}", ""]
    for paper in filtered:
        citation = f" [{paper.bibtex_key}]" if paper.bibtex_key else " [missing BibTeX key]"
        lines.append(f"- {paper.paper_id}: {paper.title} ({paper.year}, {paper.reading_status}){citation}")
    return "\n".join(lines).rstrip() + "\n"


def export_reading_list(papers: list[Paper], out: str | Path, *, tag: str = "", status: str = "", force: bool = True) -> Path:
    return write_text(out, reading_list_markdown(papers, tag=tag, status=status), force=force)


def export_theme_claims(claims: list[Claim], out: str | Path, *, theme: str, force: bool = True) -> Path:
    wanted = theme.strip().lower().replace(" ", "-").replace("_", "-")
    selected = [
        claim
        for claim in claims
        if wanted == claim.supports_theme.strip().lower().replace(" ", "-").replace("_", "-")
        or wanted in claim.tags
    ]
    return write_json(out, [_relativize_note_file(claim_to_row(claim)) for claim in selected], force=force)


def save_registry_no_overwrite(papers: list[Paper], out: str | Path) -> Path:
    from .registry import REGISTRY_FIELDS, paper_to_row
    from .io import write_csv_rows

    return write_csv_rows(out, (paper_to_row(paper) for paper in papers), REGISTRY_FIELDS, force=False)


def _write_registry_json_no_overwrite(papers: list[Paper], out: str | Path) -> Path:
    return write_json(out, [dataclass_to_plain(paper) for paper in papers], force=False)
