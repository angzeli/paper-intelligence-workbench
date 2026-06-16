"""Sanitized local diagnostic exports and support bundles."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys

from . import __version__
from .bibtex import parse_bibtex_file, validate_bibtex
from .claims import CLAIM_FIELDS, collect_notes, portable_note_path
from .doctor import workspace_health
from .integrity import check_workspace_integrity
from .io import write_csv_rows, write_json, write_text
from .markdown import findings_table, markdown_table
from .paths import default_bibtex_path, default_notes_dir, default_registry_path, default_reports_dir, default_themes_path, display_path
from .projects import resolve_project_profile
from .registry import REGISTRY_FIELDS, display_authors, load_registry, paper_to_row, validate_registry, validate_registry_headers
from .safety import ABSOLUTE_PATH_PATTERNS, SECRET_PATTERNS
from .schema import Claim, Paper, PaperNote, ProjectProfile, ProjectTheme, ValidationFinding, dataclass_to_plain
from .tags import format_tags, load_themes


BUNDLE_FILES = [
    "manifest.json",
    "environment.md",
    "cli_inventory.md",
    "project_structure.md",
    "validation_summary.md",
    "report_inventory.md",
    "schema_summary.md",
    "data_safety_summary.md",
    "command_reproduction.md",
    "sanitized_registry_sample.csv",
    "sanitized_claims_sample.csv",
    "sanitized_findings.json",
    "README_SUPPORT_BUNDLE.md",
]

FORBIDDEN_BUNDLE_SUFFIXES = {".pdf", ".sqlite", ".sqlite3", ".db", ".zip", ".tar", ".gz"}
FORBIDDEN_BUNDLE_PARTS = {".paperwb", "backups", "__pycache__", ".pytest_cache", ".idea"}
REDACTED_TEXT = "<redacted>"


@dataclass(slots=True)
class RedactionRule:
    pattern: str
    replacement: str
    description: str = ""


@dataclass(slots=True)
class SupportFinding:
    severity: str
    code: str
    message: str
    path: str = ""
    suggested_action: str = ""


@dataclass(slots=True)
class ReproductionHint:
    title: str
    command: str
    notes: str = ""


@dataclass(slots=True)
class DiagnosticSummary:
    version: str
    project: str
    root: str
    generated_at: str
    counts: dict[str, int] = field(default_factory=dict)
    findings: list[SupportFinding] = field(default_factory=list)


@dataclass(slots=True)
class SanitizedProjectSnapshot:
    project: str
    root: str
    registry_sample: list[dict[str, str]] = field(default_factory=list)
    claims_sample: list[dict[str, str]] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def warnings_as_findings(self) -> list[SupportFinding]:
        return [SupportFinding("warning", "support_bundle_warning", warning) for warning in self.warnings]


@dataclass(slots=True)
class SupportBundle:
    project: str
    out_dir: str
    safe: bool
    verbose_local_only: bool
    manifest: dict[str, object]
    files_written: list[str] = field(default_factory=list)
    findings: list[SupportFinding] = field(default_factory=list)


@dataclass(slots=True)
class _ProjectData:
    project: str
    root: Path
    registry_path: Path
    bibtex_path: Path
    notes_dir: Path
    themes_path: Path
    reports_dir: Path
    profile: ProjectProfile | None = None
    papers: list[Paper] = field(default_factory=list)
    notes: list[PaperNote] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    entries: list[object] = field(default_factory=list)
    themes: list[ProjectTheme] = field(default_factory=list)
    findings: list[SupportFinding] = field(default_factory=list)


def default_support_bundle_dir(project: str = "workspace", *, root: str | Path = ".") -> Path:
    label = project or "workspace"
    return Path(root) / "support_bundles" / f"{label}_support_bundle"


def redact_path(value: str | Path, *, preserve_name: bool = True) -> str:
    text = str(value or "")
    if not text:
        return ""
    path = Path(text).expanduser()
    if not path.is_absolute():
        return path.as_posix()
    name = path.name if preserve_name and path.name else "path"
    return f"<redacted-path>/{name}"


def redact_text(value: object, *, placeholder: str = REDACTED_TEXT) -> str:
    text = "" if value is None else str(value)
    if not text:
        return ""
    redacted = text
    for pattern in ABSOLUTE_PATH_PATTERNS:
        redacted = pattern.sub("<redacted-path>", redacted)
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("<redacted-secret>", redacted)
    return redacted if redacted != text else placeholder


def support_doctor_markdown(project: str = "", *, root: str | Path = ".") -> str:
    data = _load_project_data(project, root=root)
    summary = _diagnostic_summary(data)
    return _diagnostic_report(summary, data)


def redaction_preview_markdown(project: str = "", *, root: str | Path = ".", verbose_local_only: bool = False, sample_limit: int = 5) -> str:
    data = _load_project_data(project, root=root)
    snapshot = _sanitized_snapshot(data, safe=not verbose_local_only, verbose_local_only=verbose_local_only, sample_limit=sample_limit)
    warning = _verbose_warning() if verbose_local_only else "Safe mode is active: titles, authors, DOI/URL values, local PDF paths, note bodies, claims, quotes, and user comments are redacted."
    lines = [
        "# Support Bundle Redaction Preview",
        "",
        warning,
        "",
        f"Project: {snapshot.project}",
        f"Root: {redact_path(snapshot.root)}",
        "",
        "## Counts Preserved",
        "",
        markdown_table(["Item", "Count"], sorted(snapshot.counts.items()), aligns=["", "right"]),
        "",
        "## Registry Sample Shape",
        "",
        _sample_table(snapshot.registry_sample, ["paper_id", "title", "authors", "year", "doi", "local_pdf_path", "bibtex_key", "reading_status"]),
        "",
        "## Claims Sample Shape",
        "",
        _sample_table(snapshot.claims_sample, ["claim_id", "paper_id", "claim_text", "evidence_type", "section", "page", "quote_or_paraphrase", "strength"]),
        "",
        "## Redaction Rules",
        "",
    ]
    for rule in default_redaction_rules():
        lines.append(f"- `{rule.pattern}` -> `{rule.replacement}`: {rule.description}")
    return "\n".join(lines).rstrip() + "\n"


def reproduction_markdown(project: str = "", *, root: str | Path = ".") -> str:
    data = _load_project_data(project, root=root)
    hints = _reproduction_hints(data)
    lines = [
        "# Support Reproduction Commands",
        "",
        "These commands reproduce safe local diagnostics without copying PDFs, cache databases, backups, audit logs, notes, or drafts.",
        "",
    ]
    for hint in hints:
        lines.extend([f"## {hint.title}", "", f"```bash\n{hint.command}\n```", ""])
        if hint.notes:
            lines.extend([hint.notes, ""])
    return "\n".join(lines).rstrip() + "\n"


def create_support_bundle(
    *,
    project: str = "",
    root: str | Path = ".",
    out_dir: str | Path | None = None,
    safe: bool = True,
    verbose_local_only: bool = False,
    force: bool = False,
    sample_limit: int = 20,
) -> SupportBundle:
    data = _load_project_data(project, root=root)
    destination = Path(out_dir) if out_dir is not None else default_support_bundle_dir(data.project, root=root)
    _prepare_bundle_dir(destination, force=force)
    snapshot = _sanitized_snapshot(data, safe=safe, verbose_local_only=verbose_local_only, sample_limit=sample_limit)
    summary = _diagnostic_summary(data)
    findings = summary.findings + snapshot.warnings_as_findings()
    manifest = _bundle_manifest(data, destination, snapshot, safe=safe, verbose_local_only=verbose_local_only)

    files: dict[str, str] = {
        "environment.md": _environment_markdown(data, safe=safe, verbose_local_only=verbose_local_only),
        "cli_inventory.md": _cli_inventory_markdown(),
        "project_structure.md": _project_structure_markdown(data, safe=safe),
        "validation_summary.md": _diagnostic_report(summary, data),
        "report_inventory.md": _report_inventory_markdown(data, safe=safe),
        "schema_summary.md": _schema_summary_markdown(data),
        "data_safety_summary.md": _bundle_data_safety_markdown(data, destination, safe=safe, verbose_local_only=verbose_local_only),
        "command_reproduction.md": reproduction_markdown(data.project, root=root),
        "README_SUPPORT_BUNDLE.md": _bundle_readme(data, safe=safe, verbose_local_only=verbose_local_only),
    }
    written: list[str] = []
    for relative, content in files.items():
        write_text(destination / relative, content, force=True)
        written.append(relative)
    write_json(destination / "manifest.json", manifest, force=True)
    written.insert(0, "manifest.json")
    write_csv_rows(destination / "sanitized_registry_sample.csv", snapshot.registry_sample, REGISTRY_FIELDS, force=True)
    written.append("sanitized_registry_sample.csv")
    write_csv_rows(destination / "sanitized_claims_sample.csv", snapshot.claims_sample, CLAIM_FIELDS, force=True)
    written.append("sanitized_claims_sample.csv")
    write_json(destination / "sanitized_findings.json", [dataclass_to_plain(finding) for finding in findings], force=True)
    written.append("sanitized_findings.json")
    _assert_no_forbidden_bundle_outputs(destination)
    return SupportBundle(
        project=data.project,
        out_dir=str(destination),
        safe=safe,
        verbose_local_only=verbose_local_only,
        manifest=manifest,
        files_written=written,
        findings=findings,
    )


def support_bundle_markdown(bundle: SupportBundle) -> str:
    lines = [
        "# Support Bundle Demo",
        "",
        f"Project: {bundle.project}",
        f"Output directory: `{bundle.out_dir}`",
        f"Safe mode: {str(bundle.safe).lower()}",
        f"Verbose local-only mode: {str(bundle.verbose_local_only).lower()}",
        f"Files written: {len(bundle.files_written)}",
        f"Findings: {len(bundle.findings)}",
        "",
        "## Files",
        "",
    ]
    for file_name in bundle.files_written:
        lines.append(f"- `{file_name}`")
    lines.extend(
        [
            "",
            "## Privacy Boundary",
            "",
            "- The bundle is generated from local project state.",
            "- It does not copy PDFs, cache databases, backup archives, audit logs, notes, or drafts.",
            "- Safe mode redacts paper titles, authors, DOI/URL values, BibTeX keys, note bodies, claim text, quotes, local PDF paths, and user comments.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def default_redaction_rules() -> list[RedactionRule]:
    return [
        RedactionRule("absolute local paths", "<redacted-path>", "Home-directory and temporary filesystem paths are replaced."),
        RedactionRule("local_pdf_path", "<redacted-local-pdf-path>", "PDF references are never exported as usable paths."),
        RedactionRule("note bodies", "<redacted-note-body>", "Structured note prose is summarized by counts only."),
        RedactionRule("claim_text", "<redacted-claim-text>", "Claim text is redacted in safe mode."),
        RedactionRule("quote_or_paraphrase", "<redacted-quote-or-paraphrase>", "Quotes/paraphrases are redacted by default."),
        RedactionRule("secret/token patterns", "<redacted-secret>", "Known secret-like strings are replaced."),
    ]


def _load_project_data(project: str = "", *, root: str | Path = ".") -> _ProjectData:
    profile = resolve_project_profile(project or None, root=root)
    if profile:
        root_path = Path(profile.root)
        registry_path = Path(profile.registry_path)
        bibtex_path = Path(profile.bibtex_path)
        notes_dir = Path(profile.notes_dir)
        themes_path = Path(profile.themes_path)
        reports_dir = Path(profile.reports_dir)
        project_id = profile.name
    else:
        root_path = Path(root).expanduser().resolve(strict=False)
        registry_path = default_registry_path(root_path)
        bibtex_path = default_bibtex_path(root_path)
        notes_dir = default_notes_dir(root_path)
        themes_path = default_themes_path(root_path)
        reports_dir = default_reports_dir(root_path)
        project_id = project or "default"

    data = _ProjectData(
        project=project_id,
        root=root_path,
        registry_path=registry_path,
        bibtex_path=bibtex_path,
        notes_dir=notes_dir,
        themes_path=themes_path,
        reports_dir=reports_dir,
        profile=profile,
    )
    try:
        if registry_path.exists():
            data.papers = load_registry(registry_path)
        else:
            data.findings.append(SupportFinding("warning", "missing_registry", f"Registry file not found: {registry_path}", redact_path(registry_path), "Create or import a registry before sharing diagnostics."))
    except Exception as exc:  # noqa: BLE001 - diagnostic exports should keep going with findings
        data.findings.append(SupportFinding("error", "registry_load_failed", str(exc), redact_path(registry_path)))
    try:
        if bibtex_path.exists():
            data.entries = parse_bibtex_file(bibtex_path)
        else:
            data.findings.append(SupportFinding("warning", "missing_bibtex", f"BibTeX file not found: {bibtex_path}", redact_path(bibtex_path), "Add a BibTeX file before citation diagnostics."))
    except Exception as exc:  # noqa: BLE001
        data.findings.append(SupportFinding("error", "bibtex_load_failed", str(exc), redact_path(bibtex_path)))
    try:
        if notes_dir.exists():
            data.notes = collect_notes(notes_dir)
            data.claims = [claim for note in data.notes for claim in note.claims]
        else:
            data.findings.append(SupportFinding("warning", "missing_notes_dir", f"Notes directory not found: {notes_dir}", redact_path(notes_dir)))
    except Exception as exc:  # noqa: BLE001
        data.findings.append(SupportFinding("error", "notes_load_failed", str(exc), redact_path(notes_dir)))
    try:
        if themes_path.exists():
            data.themes = load_themes(themes_path)
    except Exception as exc:  # noqa: BLE001
        data.findings.append(SupportFinding("warning", "themes_load_failed", str(exc), redact_path(themes_path)))
    return data


def _diagnostic_summary(data: _ProjectData) -> DiagnosticSummary:
    findings = list(data.findings)
    try:
        registry_findings = validate_registry_headers(data.registry_path) if data.registry_path.exists() else []
        registry_findings += validate_registry(data.papers, root=data.root, claims=data.claims) if data.papers else []
        findings.extend(_convert_validation_findings(registry_findings, default_path=data.registry_path))
    except Exception as exc:  # noqa: BLE001
        findings.append(SupportFinding("error", "registry_validation_failed", str(exc), redact_path(data.registry_path)))
    try:
        if data.entries or data.papers:
            findings.extend(_convert_validation_findings(validate_bibtex(data.entries, data.papers), default_path=data.bibtex_path))
    except Exception as exc:  # noqa: BLE001
        findings.append(SupportFinding("error", "bibtex_validation_failed", str(exc), redact_path(data.bibtex_path)))
    try:
        health = workspace_health(
            root=data.root,
            registry_path=data.registry_path,
            bibtex_path=data.bibtex_path,
            notes_dir=data.notes_dir,
            themes_path=data.themes_path,
            reports_dir=data.reports_dir,
            profile=data.profile,
        )
        findings.extend(_convert_validation_findings(health, default_path=data.root))
    except Exception as exc:  # noqa: BLE001
        findings.append(SupportFinding("warning", "workspace_health_failed", str(exc), redact_path(data.root)))
    try:
        integrity = check_workspace_integrity(
            root=Path("."),
            registry_path=data.registry_path,
            bibtex_path=data.bibtex_path,
            notes_dir=data.notes_dir,
            themes_path=data.themes_path,
            reports_dir=data.reports_dir,
            profile=data.profile,
        )
        findings.extend(_convert_validation_findings(integrity.findings, default_path=data.root))
    except Exception as exc:  # noqa: BLE001
        findings.append(SupportFinding("warning", "integrity_check_failed", str(exc), redact_path(data.root)))
    return DiagnosticSummary(
        version=__version__,
        project=data.project,
        root=redact_path(data.root),
        generated_at=datetime.now(timezone.utc).isoformat(),
        counts=_counts(data),
        findings=_redact_support_finding_identifiers(_dedupe_support_findings(findings), data),
    )


def _convert_validation_findings(findings: list[ValidationFinding], *, default_path: str | Path) -> list[SupportFinding]:
    result: list[SupportFinding] = []
    for finding in findings:
        path = getattr(finding, "source", "") or getattr(finding, "identifier", "") or str(default_path)
        result.append(
            SupportFinding(
                severity=finding.severity,
                code=finding.code,
                message=redact_text(finding.message, placeholder=finding.message),
                path=redact_path(path),
                suggested_action=getattr(finding, "suggestion", ""),
            )
        )
    return result


def _sanitized_snapshot(data: _ProjectData, *, safe: bool, verbose_local_only: bool, sample_limit: int) -> SanitizedProjectSnapshot:
    paper_ids = {paper.paper_id: f"paper_{index:03d}" for index, paper in enumerate(data.papers, start=1)}
    registry_sample = [
        _sanitize_paper_row(paper, index=index, paper_ids=paper_ids, safe=safe, verbose_local_only=verbose_local_only)
        for index, paper in enumerate(data.papers[:sample_limit], start=1)
    ]
    claims_sample = [
        _sanitize_claim_row(claim, index=index, paper_ids=paper_ids, safe=safe, verbose_local_only=verbose_local_only, root=data.root)
        for index, claim in enumerate(data.claims[:sample_limit], start=1)
    ]
    warnings = []
    if verbose_local_only:
        warnings.append(_verbose_warning())
    return SanitizedProjectSnapshot(
        project=data.project,
        root=redact_path(data.root),
        registry_sample=registry_sample,
        claims_sample=claims_sample,
        counts=_counts(data),
        warnings=warnings,
    )


def _sanitize_paper_row(paper: Paper, *, index: int, paper_ids: dict[str, str], safe: bool, verbose_local_only: bool) -> dict[str, str]:
    row = paper_to_row(paper)
    if safe and not verbose_local_only:
        row.update(
            {
                "paper_id": paper_ids.get(paper.paper_id, f"paper_{index:03d}"),
                "title": f"<redacted-title-{index:03d}>",
                "authors": "<redacted-authors>",
                "journal": "<redacted-journal>" if paper.journal else "",
                "doi": "<redacted-doi>" if paper.doi else "",
                "url": "<redacted-url>" if paper.url else "",
                "local_pdf_path": "<redacted-local-pdf-path>" if paper.local_pdf_path else "",
                "bibtex_key": f"<redacted-bibtex-key-{index:03d}>" if paper.bibtex_key else "",
                "notes_path": redact_path(paper.notes_path) if paper.notes_path else "",
                "user_comment": "<redacted-user-comment>" if paper.user_comment else "",
            }
        )
    else:
        row["authors"] = display_authors(paper.authors)
        row["local_pdf_path"] = "<redacted-local-pdf-path>" if paper.local_pdf_path else ""
        row["notes_path"] = redact_path(paper.notes_path) if paper.notes_path else ""
        row["user_comment"] = "<redacted-user-comment>" if paper.user_comment else ""
    return {field: row.get(field, "") for field in REGISTRY_FIELDS}


def _sanitize_claim_row(claim: Claim, *, index: int, paper_ids: dict[str, str], safe: bool, verbose_local_only: bool, root: str | Path) -> dict[str, str]:
    if safe and not verbose_local_only:
        claim_id = f"claim_{index:03d}"
        paper_id = paper_ids.get(claim.paper_id, "<redacted-paper-id>")
        claim_text = "<redacted-claim-text>"
    else:
        claim_id = claim.claim_id
        paper_id = claim.paper_id
        claim_text = redact_text(claim.claim_text, placeholder=claim.claim_text)
    row = {
        "claim_id": claim_id,
        "paper_id": paper_id,
        "claim_text": claim_text,
        "evidence_type": claim.evidence_type,
        "section": claim.section,
        "page": claim.page,
        "confidence": claim.confidence,
        "tags": format_tags(claim.tags),
        "quote_or_paraphrase": "<redacted-quote-or-paraphrase>" if claim.quote_or_paraphrase else "",
        "user_comment": "<redacted-user-comment>" if claim.user_comment else "",
        "supports_theme": claim.supports_theme,
        "strength": claim.strength,
        "note_file": redact_path(portable_note_path(claim.note_file, root=root)) if claim.note_file else "",
    }
    return {field: row.get(field, "") for field in CLAIM_FIELDS}


def _counts(data: _ProjectData) -> dict[str, int]:
    report_count = len(list(data.reports_dir.glob("*.md"))) if data.reports_dir.exists() else 0
    return {
        "papers": len(data.papers),
        "bibtex_entries": len(data.entries),
        "notes": len(data.notes),
        "claims": len(data.claims),
        "themes": len(data.themes),
        "reports": report_count,
    }


def _diagnostic_report(summary: DiagnosticSummary, data: _ProjectData) -> str:
    severity_counts = Counter(finding.severity for finding in summary.findings)
    lines = [
        f"# Support Doctor Report v{summary.version}",
        "",
        "This diagnostic report is sanitized by default. It summarizes local structure and validation findings without copying notes, drafts, PDFs, cache databases, audit logs, or backup archives.",
        "",
        f"Project: {summary.project}",
        f"Root: {summary.root}",
        f"Registry: {redact_path(data.registry_path)}",
        f"BibTeX: {redact_path(data.bibtex_path)}",
        f"Notes dir: {redact_path(data.notes_dir)}",
        f"Themes: {redact_path(data.themes_path)}",
        f"Reports dir: {redact_path(data.reports_dir)}",
        "",
        "## Counts",
        "",
        markdown_table(["Item", "Count"], sorted(summary.counts.items()), aligns=["", "right"]),
        "",
        "## Finding Summary",
        "",
        markdown_table(["Severity", "Count"], sorted(severity_counts.items()), aligns=["", "right"]),
        "",
        "## Findings",
        "",
        _support_findings_table(summary.findings),
    ]
    return "\n".join(lines).rstrip() + "\n"


def _environment_markdown(data: _ProjectData, *, safe: bool, verbose_local_only: bool) -> str:
    lines = [
        "# Environment",
        "",
        f"Package version: {__version__}",
        f"Python: {platform.python_version()}",
        f"Executable: {redact_path(sys.executable)}",
        f"Platform: {platform.system()} {platform.release()}",
        f"Project: {data.project}",
        f"Safe mode: {str(safe).lower()}",
        f"Verbose local-only mode: {str(verbose_local_only).lower()}",
    ]
    if verbose_local_only:
        lines.extend(["", _verbose_warning()])
    return "\n".join(lines).rstrip() + "\n"


def _cli_inventory_markdown() -> str:
    groups = [
        "init",
        "project",
        "template",
        "dogfood",
        "support",
        "validate-registry",
        "validate-bib",
        "add-paper",
        "list",
        "note-template",
        "claims",
        "report",
        "dashboard",
        "doctor",
        "integrity",
        "backup",
        "workflow",
        "sync",
        "index",
        "rebuild",
        "files",
        "draft",
        "manuscript",
        "reading",
        "followups",
        "graph",
        "rules",
        "claim-review",
        "contradictions",
        "review-packet",
        "import",
        "export",
        "migrate",
        "synthetic",
    ]
    return "\n".join(["# CLI Inventory", "", "Run `paperwb --help` for exact flags in this installation.", "", *[f"- `paperwb {group}`" for group in groups]]) + "\n"


def _project_structure_markdown(data: _ProjectData, *, safe: bool) -> str:
    rows: list[tuple[str, int]] = []
    redacted_count = 0
    for directory in [data.root, data.registry_path.parent, data.bibtex_path.parent, data.notes_dir, data.themes_path.parent, data.reports_dir]:
        if directory.exists() and directory.is_dir():
            files = [path for path in directory.iterdir() if path.is_file()]
            rows.append((redact_path(directory) if safe else display_path(directory), len(files)))
            redacted_count += sum(1 for path in files if _is_forbidden_source_path(path))
    ext_counts: Counter[str] = Counter()
    if data.root.exists():
        for path in data.root.rglob("*"):
            if path.is_file():
                if _is_forbidden_source_path(path):
                    redacted_count += 1
                    continue
                ext_counts[path.suffix.lower() or "[no suffix]"] += 1
    lines = [
        "# Project Structure Summary",
        "",
        "This summary reports counts and schema-relevant paths only. It does not include raw note or draft bodies.",
        "",
        "## Directory Counts",
        "",
        markdown_table(["Directory", "Files"], rows, aligns=["", "right"]) if rows else "No expected project directories found.",
        "",
        "## Extension Counts",
        "",
        markdown_table(["Suffix", "Files"], sorted(ext_counts.items()), aligns=["", "right"]) if ext_counts else "No non-forbidden files found.",
        "",
        f"Forbidden/private files intentionally excluded from detail: {redacted_count}",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _report_inventory_markdown(data: _ProjectData, *, safe: bool) -> str:
    rows = []
    if data.reports_dir.exists():
        for path in sorted(data.reports_dir.glob("*.md")):
            rows.append([path.name, path.stat().st_size])
    lines = [
        "# Report Inventory",
        "",
        f"Reports directory: {redact_path(data.reports_dir) if safe else display_path(data.reports_dir)}",
        "",
        markdown_table(["Report", "Bytes"], rows, aligns=["", "right"]) if rows else "No Markdown reports found.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _schema_summary_markdown(data: _ProjectData) -> str:
    return "\n".join(
        [
            "# Schema Summary",
            "",
            "## Registry CSV Fields",
            "",
            ", ".join(f"`{field}`" for field in REGISTRY_FIELDS),
            "",
            "## Claim CSV Fields",
            "",
            ", ".join(f"`{field}`" for field in CLAIM_FIELDS),
            "",
            "## Project Profile Paths",
            "",
            f"- Registry: `{redact_path(data.registry_path)}`",
            f"- BibTeX: `{redact_path(data.bibtex_path)}`",
            f"- Notes: `{redact_path(data.notes_dir)}`",
            f"- Themes: `{redact_path(data.themes_path)}`",
            f"- Reports: `{redact_path(data.reports_dir)}`",
            "",
            "## Privacy Boundary",
            "",
            "Schema summaries preserve column names and counts, not private prose or copied source documents.",
        ]
    ).rstrip() + "\n"


def _bundle_data_safety_markdown(data: _ProjectData, destination: Path, *, safe: bool, verbose_local_only: bool) -> str:
    forbidden_outputs = _forbidden_bundle_outputs(destination)
    lines = [
        "# Support Bundle Data Safety Summary",
        "",
        f"Safe mode: {str(safe).lower()}",
        f"Verbose local-only mode: {str(verbose_local_only).lower()}",
        f"Source project: {data.project}",
        f"Bundle directory: {redact_path(destination)}",
        "",
        "## Exclusions",
        "",
        "- PDFs and other binary paper files are not copied.",
        "- Cache databases under `.paperwb/` are not copied.",
        "- Backup archives are not copied.",
        "- Audit logs are summarized only by command reproduction guidance; raw audit logs are not copied.",
        "- Full notes, drafts, private comments, quotes, and paraphrases are not copied in safe mode.",
        "",
        "## Bundle Output Check",
        "",
        f"Forbidden output files detected: {len(forbidden_outputs)}",
    ]
    for path in forbidden_outputs:
        lines.append(f"- `{path}`")
    if not forbidden_outputs:
        lines.append("- None.")
    return "\n".join(lines).rstrip() + "\n"


def _bundle_readme(data: _ProjectData, *, safe: bool, verbose_local_only: bool) -> str:
    return "\n".join(
        [
            "# README Support Bundle",
            "",
            "This folder was generated by `paperwb support bundle`.",
            "",
            "It is intended for local debugging and safe issue reproduction. The default safe mode redacts private project content and never copies PDFs, cache databases, backups, audit logs, full notes, or full drafts.",
            "",
            f"Project: {data.project}",
            f"Safe mode: {str(safe).lower()}",
            f"Verbose local-only mode: {str(verbose_local_only).lower()}",
            "",
            "Start with:",
            "",
            "- `manifest.json` for generated file inventory.",
            "- `validation_summary.md` for validation and health findings.",
            "- `data_safety_summary.md` for what was intentionally excluded.",
            "- `command_reproduction.md` for local reproduction commands.",
            "",
            "Do not treat sanitized samples as real scientific metadata or evidence.",
        ]
    ).rstrip() + "\n"


def _reproduction_hints(data: _ProjectData) -> list[ReproductionHint]:
    project_flag = f" --project {data.project}" if data.profile else ""
    if data.profile:
        validate_registry_cmd = f"paperwb validate-registry {display_path(data.registry_path)} --strict"
        validate_bib_cmd = f"paperwb validate-bib {display_path(data.bibtex_path)} --registry {display_path(data.registry_path)} --strict"
    else:
        validate_registry_cmd = "paperwb validate-registry data/registries/papers.csv --strict"
        validate_bib_cmd = "paperwb validate-bib data/bibtex/library.bib --registry data/registries/papers.csv --strict"
    return [
        ReproductionHint("Import Package", "python -c \"import paper_workbench; print(paper_workbench.__version__)\""),
        ReproductionHint("CLI Help", "paperwb --help"),
        ReproductionHint("Validate Registry", validate_registry_cmd),
        ReproductionHint("Validate BibTeX", validate_bib_cmd),
        ReproductionHint("Run Doctor", f"paperwb doctor{project_flag}"),
        ReproductionHint("Run Integrity Check", f"paperwb integrity check{project_flag}"),
        ReproductionHint("Run Dashboard", f"paperwb dashboard{project_flag} --no-audit-log"),
        ReproductionHint("Generate Sanitized Support Bundle", f"paperwb support bundle{project_flag} --safe --out support_bundles/{data.project}_support_bundle"),
    ]


def _bundle_manifest(data: _ProjectData, destination: Path, snapshot: SanitizedProjectSnapshot, *, safe: bool, verbose_local_only: bool) -> dict[str, object]:
    return {
        "bundle_schema": "paperwb.support_bundle.v1",
        "package_version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": data.project,
        "out_dir": redact_path(destination),
        "safe": safe,
        "verbose_local_only": verbose_local_only,
        "files": BUNDLE_FILES,
        "counts": snapshot.counts,
        "privacy_boundary": {
            "copies_pdfs": False,
            "copies_cache_databases": False,
            "copies_backup_archives": False,
            "copies_audit_logs": False,
            "copies_full_notes": False,
            "copies_full_drafts": False,
        },
    }


def _prepare_bundle_dir(destination: Path, *, force: bool) -> None:
    if destination.exists() and not destination.is_dir():
        raise NotADirectoryError(f"{destination} exists and is not a directory")
    if destination.exists() and not force:
        existing = [path for path in destination.iterdir() if path.name not in {".DS_Store"}]
        if existing:
            raise FileExistsError(f"{destination} already exists and is not empty; pass --force to rewrite known bundle files")
    destination.mkdir(parents=True, exist_ok=True)


def _assert_no_forbidden_bundle_outputs(destination: Path) -> None:
    forbidden = _forbidden_bundle_outputs(destination)
    if forbidden:
        raise ValueError(f"support bundle contains forbidden files: {', '.join(forbidden)}")


def _forbidden_bundle_outputs(destination: Path) -> list[str]:
    forbidden: list[str] = []
    if not destination.exists():
        return forbidden
    for path in destination.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in FORBIDDEN_BUNDLE_SUFFIXES or any(part in FORBIDDEN_BUNDLE_PARTS for part in path.parts):
            forbidden.append(path.relative_to(destination).as_posix())
    return forbidden


def _is_forbidden_source_path(path: Path) -> bool:
    return path.suffix.lower() in FORBIDDEN_BUNDLE_SUFFIXES or any(part in FORBIDDEN_BUNDLE_PARTS for part in path.parts)


def _sample_table(rows: list[dict[str, str]], fields: list[str]) -> str:
    if not rows:
        return "No sample rows available."
    return markdown_table(fields, [[row.get(field, "") for field in fields] for row in rows])


def _support_findings_table(findings: list[SupportFinding]) -> str:
    return findings_table(findings, empty="No diagnostic findings detected.", identifier_fields=("path",), suggestion_field="suggested_action")


def _dedupe_support_findings(findings: list[SupportFinding]) -> list[SupportFinding]:
    seen: set[tuple[str, str, str, str]] = set()
    deduped: list[SupportFinding] = []
    for finding in findings:
        key = (finding.severity, finding.code, finding.message, finding.path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(finding)
    return deduped


def _redact_support_finding_identifiers(findings: list[SupportFinding], data: _ProjectData) -> list[SupportFinding]:
    replacements: dict[str, str] = {}
    for index, paper in enumerate(data.papers, start=1):
        if paper.paper_id:
            replacements[paper.paper_id] = f"paper_{index:03d}"
        if paper.bibtex_key:
            replacements[paper.bibtex_key] = f"bibtex_key_{index:03d}"
        if paper.title:
            replacements[paper.title] = f"<redacted-title-{index:03d}>"
    for index, claim in enumerate(data.claims, start=1):
        if claim.claim_id:
            replacements[claim.claim_id] = f"claim_{index:03d}"
        if claim.claim_text:
            replacements[claim.claim_text] = "<redacted-claim-text>"
        if claim.quote_or_paraphrase:
            replacements[claim.quote_or_paraphrase] = "<redacted-quote-or-paraphrase>"
    redacted: list[SupportFinding] = []
    for finding in findings:
        redacted.append(
            SupportFinding(
                severity=finding.severity,
                code=finding.code,
                message=_replace_known_values(finding.message, replacements),
                path=_replace_known_values(finding.path, replacements),
                suggested_action=_replace_known_values(finding.suggested_action, replacements),
            )
        )
    return redacted


def _replace_known_values(value: str, replacements: dict[str, str]) -> str:
    result = value
    for original, replacement in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        if original:
            result = result.replace(original, replacement)
    return result


def _verbose_warning() -> str:
    return "Verbose local-only mode is active. Do not share this bundle externally until you inspect it; it may include paper titles, authors, DOI/URL values, BibTeX keys, and claim text."
