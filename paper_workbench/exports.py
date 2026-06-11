"""Local import/export helpers."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import re
import shutil

from .claims import claim_to_row, save_claims_csv
from .io import write_csv_rows, write_json, write_text
from .paths import display_path
from .registry import REGISTRY_FIELDS, filter_papers, parse_boolish, paper_to_row, save_registry, save_registry_json
from .schema import Claim, Paper, PaperNote, ProjectTheme, dataclass_to_plain
from .tags import format_tags, normalize_theme_id, parse_tags, theme_by_tag, themes_for_tags


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


def export_claims_csv(claims: list[Claim], out: str | Path, force: bool = True, *, root: str | Path | None = None) -> Path:
    return save_claims_csv(claims, out, force=force, root=root)


def export_claims_json(claims: list[Claim], out: str | Path, force: bool = True) -> Path:
    return write_json(out, [_relativize_note_file(dataclass_to_plain(claim)) for claim in claims], force=force)


def _filtered_reading_list(
    papers: list[Paper],
    *,
    tag: str = "",
    status: str = "",
    theme: str = "",
    themes: list[ProjectTheme] | None = None,
    included: bool | None = None,
    excluded: bool = False,
    high_priority: bool = False,
    missing_notes: bool = False,
    notes: list[PaperNote] | None = None,
) -> list[Paper]:
    filtered = filter_papers(papers, tag=tag, status=status)
    if theme and themes:
        wanted = normalize_theme_id(theme)
        filtered = [
            paper
            for paper in filtered
            if any(item.theme_id == wanted or item.name.lower() == theme.strip().lower() for item in themes_for_tags(paper.tags, themes))
        ]
    if included is not None:
        filtered = [paper for paper in filtered if parse_boolish(paper.included_in_lit_review) is included]
    if excluded:
        filtered = [paper for paper in filtered if parse_boolish(paper.included_in_lit_review) is False]
    if high_priority:
        filtered = [
            paper
            for paper in filtered
            if str(paper.priority).lower() in {"high", "critical"} or str(paper.reading_priority).lower() in {"high", "critical"}
        ]
    if missing_notes:
        note_ids = {note.paper_id for note in notes or [] if note.paper_id}
        filtered = [paper for paper in filtered if paper.paper_id not in note_ids]
    return filtered


def reading_list_markdown(
    papers: list[Paper],
    *,
    tag: str = "",
    status: str = "",
    theme: str = "",
    themes: list[ProjectTheme] | None = None,
    included: bool | None = None,
    excluded: bool = False,
    high_priority: bool = False,
    missing_notes: bool = False,
    notes: list[PaperNote] | None = None,
) -> str:
    filtered = _filtered_reading_list(
        papers,
        tag=tag,
        status=status,
        theme=theme,
        themes=themes,
        included=included,
        excluded=excluded,
        high_priority=high_priority,
        missing_notes=missing_notes,
        notes=notes,
    )
    title = "Reading List"
    if tag:
        title += f": {tag}"
    if status:
        title += f" ({status})"
    if theme:
        title += f" [theme: {theme}]"
    if included is True:
        title += " [included]"
    if excluded:
        title += " [excluded]"
    if high_priority:
        title += " [high priority]"
    if missing_notes:
        title += " [missing notes]"
    lines = [f"# {title}", "", f"Papers: {len(filtered)}", ""]
    for paper in filtered:
        citation = f" [{paper.bibtex_key}]" if paper.bibtex_key else " [missing BibTeX key]"
        lines.append(f"- {paper.paper_id}: {paper.title} ({paper.year}, {paper.reading_status}){citation}")
        if excluded and paper.exclude_reason:
            lines.append(f"  - Exclude reason: {paper.exclude_reason}")
    return "\n".join(lines).rstrip() + "\n"


def export_reading_list(
    papers: list[Paper],
    out: str | Path,
    *,
    tag: str = "",
    status: str = "",
    theme: str = "",
    themes: list[ProjectTheme] | None = None,
    included: bool | None = None,
    excluded: bool = False,
    high_priority: bool = False,
    missing_notes: bool = False,
    notes: list[PaperNote] | None = None,
    output_format: str = "markdown",
    force: bool = True,
) -> Path:
    filtered = _filtered_reading_list(
        papers,
        tag=tag,
        status=status,
        theme=theme,
        themes=themes,
        included=included,
        excluded=excluded,
        high_priority=high_priority,
        missing_notes=missing_notes,
        notes=notes,
    )
    if output_format == "csv":
        return write_csv_rows(out, (paper_to_row(paper) for paper in filtered), REGISTRY_FIELDS, force=force)
    return write_text(
        out,
        reading_list_markdown(
            papers,
            tag=tag,
            status=status,
            theme=theme,
            themes=themes,
            included=included,
            excluded=excluded,
            high_priority=high_priority,
            missing_notes=missing_notes,
            notes=notes,
        ),
        force=force,
    )


def export_theme_claims(claims: list[Claim], out: str | Path, *, theme: str, force: bool = True) -> Path:
    wanted = normalize_theme_id(theme)
    selected = [
        claim
        for claim in claims
        if wanted == normalize_theme_id(claim.supports_theme)
        or wanted in claim.tags
    ]
    return write_json(out, [_relativize_note_file(claim_to_row(claim)) for claim in selected], force=force)


def save_registry_no_overwrite(papers: list[Paper], out: str | Path) -> Path:
    from .registry import REGISTRY_FIELDS, paper_to_row
    from .io import write_csv_rows

    return write_csv_rows(out, (paper_to_row(paper) for paper in papers), REGISTRY_FIELDS, force=False)


def _write_registry_json_no_overwrite(papers: list[Paper], out: str | Path) -> Path:
    return write_json(out, [dataclass_to_plain(paper) for paper in papers], force=False)


def _safe_name(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return safe.strip("_") or "untitled"


def _ensure_export_dir(path: str | Path, *, force: bool) -> Path:
    target = Path(path)
    if target.exists() and any(target.iterdir()):
        raise FileExistsError(f"{target} already exists and is not empty; choose an empty output directory")
    target.mkdir(parents=True, exist_ok=True)
    return target


def export_obsidian_vault(
    papers: list[Paper],
    notes: list[PaperNote],
    claims: list[Claim],
    themes: list[ProjectTheme],
    out: str | Path,
    *,
    force: bool = False,
) -> Path:
    vault = _ensure_export_dir(out, force=force)
    papers_dir = vault / "papers"
    papers_dir.mkdir(parents=True, exist_ok=True)
    claims_by_paper: dict[str, list[Claim]] = {}
    for claim in claims:
        claims_by_paper.setdefault(claim.paper_id, []).append(claim)
    theme_map = theme_by_tag(themes)
    status_counts = Counter(paper.reading_status for paper in papers)
    tag_counts = Counter(tag for paper in papers for tag in parse_tags(paper.tags))
    for paper in papers:
        paper_themes = themes_for_tags(paper.tags, themes)
        lines = [
            f"# {paper.title or paper.paper_id}",
            "",
            "## Metadata",
            "",
            f"- Paper ID: {paper.paper_id}",
            f"- Year: {paper.year}",
            f"- Authors: {'; '.join(author.display() for author in paper.authors)}",
            f"- Journal: {paper.journal}",
            f"- DOI: {paper.doi}",
            f"- URL: {paper.url}",
            f"- BibTeX key: {paper.bibtex_key}",
            f"- Reading status: {paper.reading_status}",
            f"- Tags: {format_tags(paper.tags)}",
            f"- Themes: {', '.join(f'[{theme.name}](../themes.md#{_safe_anchor(theme.name)})' for theme in paper_themes) if paper_themes else ''}",
            "",
            "## Claims",
            "",
        ]
        paper_claims = claims_by_paper.get(paper.paper_id, [])
        if paper_claims:
            for claim in paper_claims:
                evidence = claim.section or claim.page or "missing evidence location"
                lines.extend(
                    [
                        f"### {claim.claim_id}",
                        "",
                        f"- Claim: {claim.claim_text}",
                        f"- Evidence type: {claim.evidence_type}",
                        f"- Evidence location: {evidence}",
                        f"- Confidence: {claim.confidence}",
                        f"- Strength: {claim.strength}",
                        f"- Tags: {format_tags(claim.tags)}",
                        f"- Supports theme: {claim.supports_theme}",
                        "",
                    ]
                )
        else:
            lines.append("- No parsed claims.")
        write_text(papers_dir / f"{_safe_name(paper.paper_id)}.md", "\n".join(lines).rstrip() + "\n", force=force)
    write_text(vault / "index.md", _obsidian_index(papers, status_counts), force=force)
    write_text(vault / "tags.md", _counter_page("Tag Index", tag_counts), force=force)
    write_text(vault / "themes.md", _themes_page(papers, claims, themes, theme_map), force=force)
    write_text(vault / "reading_status.md", _counter_page("Reading Status Index", status_counts), force=force)
    write_text(vault / "claims.md", _claims_page(claims), force=force)
    write_text(vault / "missing_evidence.md", _missing_evidence_page(claims), force=force)
    write_text(vault / "export_summary.md", obsidian_export_summary(papers, notes, claims, themes, vault), force=force)
    return vault


def _safe_anchor(value: str) -> str:
    return re.sub(r"[^a-z0-9 -]", "", value.lower()).replace(" ", "-")


def _obsidian_index(papers: list[Paper], status_counts: Counter[str]) -> str:
    lines = ["# Paper Workbench Vault Index", "", f"Papers: {len(papers)}", "", "## Reading Status", ""]
    for status, count in sorted(status_counts.items()):
        lines.append(f"- {status}: {count}")
    lines.extend(["", "## Papers", ""])
    for paper in papers:
        lines.append(f"- [{paper.paper_id}](papers/{_safe_name(paper.paper_id)}.md): {paper.title}")
    return "\n".join(lines).rstrip() + "\n"


def _counter_page(title: str, counts: Counter[str]) -> str:
    lines = [f"# {title}", "", "| Value | Count |", "| --- | ---: |"]
    for value, count in sorted(counts.items()):
        lines.append(f"| {value} | {count} |")
    return "\n".join(lines).rstrip() + "\n"


def _themes_page(papers: list[Paper], claims: list[Claim], themes: list[ProjectTheme], theme_map) -> str:
    lines = ["# Theme Index", ""]
    for theme in themes:
        theme_papers = [paper for paper in papers if any(theme_map.get(tag) and theme_map[tag].theme_id == theme.theme_id for tag in parse_tags(paper.tags))]
        theme_claims = [
            claim
            for claim in claims
            if theme.theme_id == normalize_theme_id(claim.supports_theme)
            or any(theme_map.get(tag) and theme_map[tag].theme_id == theme.theme_id for tag in parse_tags(claim.tags))
        ]
        lines.extend([f"## {theme.name}", "", f"- Papers: {len(theme_papers)}", f"- Claims: {len(theme_claims)}", ""])
        for paper in theme_papers:
            lines.append(f"- [{paper.paper_id}](papers/{_safe_name(paper.paper_id)}.md)")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _claims_page(claims: list[Claim]) -> str:
    lines = ["# Claims Index", ""]
    for claim in claims:
        lines.append(f"- **{claim.claim_id}** ({claim.strength}): {claim.claim_text}")
    if not claims:
        lines.append("- No parsed claims.")
    return "\n".join(lines).rstrip() + "\n"


def _missing_evidence_page(claims: list[Claim]) -> str:
    missing = [claim for claim in claims if not (claim.section or claim.page)]
    lines = ["# Missing Evidence", "", f"Claims missing evidence locations: {len(missing)}", ""]
    for claim in missing:
        lines.append(f"- {claim.claim_id}: {claim.claim_text}")
    return "\n".join(lines).rstrip() + "\n"


def obsidian_export_summary(papers: list[Paper], notes: list[PaperNote], claims: list[Claim], themes: list[ProjectTheme], out: str | Path) -> str:
    return (
        "# Obsidian Export Summary v0.4\n\n"
        f"- Output vault: {out}\n"
        f"- Papers exported: {len(papers)}\n"
        f"- Parsed notes: {len(notes)}\n"
        f"- Claims exported: {len(claims)}\n"
        f"- Themes exported: {len(themes)}\n"
        "- PDFs included: false\n"
    )


def export_bundle(
    *,
    registry_path: str | Path,
    bibtex_path: str | Path,
    notes_dir: str | Path,
    themes_path: str | Path,
    reports_dir: str | Path,
    text_dir: str | Path | None = None,
    out: str | Path,
    project: str = "",
    include_pdfs: bool = False,
    papers: list[Paper] | None = None,
    root: str | Path = ".",
    force: bool = False,
) -> Path:
    bundle = _ensure_export_dir(out, force=force)
    data_dir = bundle / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for source, relative in [
        (Path(registry_path), "registry.csv"),
        (Path(bibtex_path), "library.bib"),
        (Path(themes_path), "themes.json"),
    ]:
        if source.exists():
            target = data_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            copied.append(str(target.relative_to(bundle)))
    if Path(notes_dir).exists():
        _copy_tree_contents(Path(notes_dir), data_dir / "notes", copied, bundle)
    sidecars_copied: list[str] = []
    resolved_text_dir = _bundle_text_dir(text_dir=text_dir, notes_dir=notes_dir, root=root)
    if resolved_text_dir.exists():
        _copy_text_sidecars(resolved_text_dir, data_dir / "text", copied, sidecars_copied, bundle)
    if Path(reports_dir).exists():
        _copy_tree_contents(Path(reports_dir), bundle / "reports", copied, bundle)
    pdfs_copied: list[str] = []
    if include_pdfs and papers:
        pdf_dir = data_dir / "papers"
        for paper in papers:
            if not paper.local_pdf_path:
                continue
            source = Path(paper.local_pdf_path)
            if not source.is_absolute():
                source = Path(root) / source
            if source.exists() and source.is_file():
                pdf_dir.mkdir(parents=True, exist_ok=True)
                target = pdf_dir / source.name
                shutil.copy2(source, target)
                pdfs_copied.append(str(target.relative_to(bundle)))
    from . import __version__

    manifest = {
        "project": project,
        "export_timestamp": datetime.now(timezone.utc).isoformat(),
        "tool_version": __version__,
        "include_pdfs": include_pdfs,
        "pdfs_copied": pdfs_copied,
        "text_sidecars_copied": sorted(sidecars_copied),
        "files_copied": sorted(copied),
    }
    write_json(bundle / "manifest.json", manifest, force=True)
    write_text(bundle / "bundle_summary.md", bundle_export_summary(manifest, bundle), force=True)
    return bundle


def _bundle_text_dir(*, text_dir: str | Path | None, notes_dir: str | Path, root: str | Path) -> Path:
    if text_dir is not None:
        return Path(text_dir)
    sibling_text_dir = Path(notes_dir).parent / "text"
    if sibling_text_dir.exists():
        return sibling_text_dir
    return Path(root) / "data" / "text"


def _copy_text_sidecars(source_dir: Path, target_dir: Path, copied: list[str], sidecars_copied: list[str], bundle: Path) -> None:
    for source in sorted(path for path in source_dir.rglob("*.txt") if path.is_file()):
        if any(part.startswith(".") for part in source.relative_to(source_dir).parts):
            continue
        target = target_dir / source.relative_to(source_dir)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        relative = str(target.relative_to(bundle))
        copied.append(relative)
        sidecars_copied.append(relative)


def _copy_tree_contents(source_dir: Path, target_dir: Path, copied: list[str], bundle: Path) -> None:
    for source in sorted(path for path in source_dir.rglob("*") if path.is_file()):
        target = target_dir / source.relative_to(source_dir)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(str(target.relative_to(bundle)))


def bundle_export_summary(manifest: dict, out: str | Path) -> str:
    return (
        "# Backup Bundle Export Summary v0.4\n\n"
        f"- Output bundle: {out}\n"
        f"- Project: {manifest.get('project') or 'default data workflow'}\n"
        f"- Tool version: {manifest.get('tool_version')}\n"
        f"- Include PDFs: {str(manifest.get('include_pdfs')).lower()}\n"
        f"- Files copied: {len(manifest.get('files_copied', []))}\n"
        f"- Text sidecars copied: {len(manifest.get('text_sidecars_copied', []))}\n"
        f"- PDFs copied: {len(manifest.get('pdfs_copied', []))}\n"
    )


def project_summary_markdown(papers: list[Paper], claims: list[Claim], themes: list[ProjectTheme]) -> str:
    status_counts = Counter(paper.reading_status for paper in papers)
    lines = [
        "# Project Summary Export",
        "",
        f"- Papers: {len(papers)}",
        f"- Claims: {len(claims)}",
        f"- Themes: {len(themes)}",
        "",
        "## Reading Status",
        "",
        "| Status | Papers |",
        "| --- | ---: |",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"| {status} | {count} |")
    return "\n".join(lines).rstrip() + "\n"


def export_project_summary(papers: list[Paper], claims: list[Claim], themes: list[ProjectTheme], out: str | Path, *, force: bool = True) -> Path:
    return write_text(out, project_summary_markdown(papers, claims, themes), force=force)


def _display_path(path: Path, *, base: Path | None = None) -> str:
    return display_path(path, base_path=base)


def _report_version(path: Path) -> tuple[int, int] | None:
    match = re.search(r"(?:^|_)v(\d+)_(\d+)", path.stem)
    return (int(match.group(1)), int(match.group(2))) if match else None


def _format_report_version(version: tuple[int, int]) -> str:
    return f"v{version[0]}.{version[1]}"


def _latest_release_version(reports: list[Path]) -> tuple[int, int] | None:
    versions = [
        version
        for report in reports
        if "recommended_patch_plan" not in report.name
        for version in [_report_version(report)]
        if version is not None
    ]
    return max(versions) if versions else None


CURRENT_UNVERSIONED_REPORTS_BY_RELEASE: dict[tuple[int, int], set[str]] = {
    (1, 7): {
        "template_finance_overview.md",
        "template_ml_methods_overview.md",
        "template_photocatalysis_overview.md",
    },
}


def _is_current_unversioned_report(report: Path, latest_release: tuple[int, int] | None) -> bool:
    if latest_release is None:
        return False
    return report.name in CURRENT_UNVERSIONED_REPORTS_BY_RELEASE.get(latest_release, set())


def report_index_markdown(reports_dir: str | Path, *, output_path: str | Path | None = None) -> str:
    root = Path(reports_dir)
    reports = sorted(
        path
        for path in root.glob("*.md")
        if path.is_file() and not re.fullmatch(r"hostile_review_v0_\d+\.md", path.name)
    )
    link_base = Path(output_path).parent if output_path is not None else root
    latest_release = _latest_release_version(reports)
    current: list[Path] = []
    next_plans: list[Path] = []
    historical: list[Path] = []
    legacy: list[Path] = []
    for report in reports:
        version = _report_version(report)
        if (
            report.name == "hostile_review_latest.md"
            or _is_current_unversioned_report(report, latest_release)
            or (latest_release is not None and version == latest_release and "recommended_patch_plan" not in report.name)
        ):
            current.append(report)
        elif latest_release is not None and "recommended_patch_plan" in report.name and version is not None and version > latest_release:
            next_plans.append(report)
        elif version is not None:
            historical.append(report)
        else:
            legacy.append(report)

    lines = [
        "# Report Index",
        "",
        f"Reports directory: {_display_path(root, base=link_base)}",
        "",
        f"Markdown reports indexed: {len(reports)}",
        "",
        "Versioned hostile-review drafts are omitted from this index; `hostile_review_latest.md` is the canonical current review.",
    ]
    sections = [
        (f"Current {_format_report_version(latest_release)} Release Reports" if latest_release is not None else "Current Reports", current),
        ("Next Patch Plan", next_plans),
        ("Historical Versioned Reports", historical),
        ("Legacy Unversioned Reports", legacy),
    ]
    for heading, grouped_reports in sections:
        if not grouped_reports:
            continue
        lines.extend(["", f"## {heading}", ""])
        for report in grouped_reports:
            lines.append(f"- [{report.name}]({_display_path(report, base=link_base)})")
    return "\n".join(lines).rstrip() + "\n"


def export_report_index(reports_dir: str | Path, out: str | Path, *, force: bool = True) -> Path:
    return write_text(out, report_index_markdown(reports_dir, output_path=out), force=force)
