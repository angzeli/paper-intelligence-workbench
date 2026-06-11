"""Workspace integrity checks for local project safety."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import subprocess

from .bibtex import parse_bibtex_file, validate_bibtex
from .claims import collect_notes
from .doctor import workspace_health
from .files import default_file_registry_path, scan_local_files
from .paths import default_bibtex_path, default_notes_dir, default_registry_path, default_reports_dir, default_themes_path
from .projects import list_project_profiles
from .registry import load_registry, validate_registry
from .schema import ProjectProfile, ValidationFinding
from .tags import load_themes


@dataclass(slots=True)
class IntegrityResult:
    root: str
    project: str = ""
    findings: list[ValidationFinding] = field(default_factory=list)
    checked_paths: list[str] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationFinding]:
        return [finding for finding in self.findings if finding.severity == "error"]

    @property
    def warnings(self) -> list[ValidationFinding]:
        return [finding for finding in self.findings if finding.severity == "warning"]


def _finding(severity: str, code: str, message: str, identifier: str = "", suggestion: str = "") -> ValidationFinding:
    return ValidationFinding(severity=severity, code=code, message=message, identifier=identifier, suggestion=suggestion)


def is_path_within(path: str | Path, root: str | Path) -> bool:
    try:
        Path(path).expanduser().resolve(strict=False).relative_to(Path(root).expanduser().resolve(strict=False))
        return True
    except ValueError:
        return False


def _display(path: Path, root: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def _tracked_files(root: Path) -> list[str]:
    try:
        result = subprocess.run(["git", "ls-files"], cwd=root, text=True, capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def check_workspace_integrity(
    *,
    root: str | Path = ".",
    registry_path: str | Path | None = None,
    bibtex_path: str | Path | None = None,
    notes_dir: str | Path | None = None,
    themes_path: str | Path | None = None,
    reports_dir: str | Path | None = None,
    profile: ProjectProfile | None = None,
) -> IntegrityResult:
    root_path = Path(root).expanduser().resolve(strict=False)
    registry = Path(registry_path or default_registry_path(root_path))
    bibtex = Path(bibtex_path or default_bibtex_path(root_path))
    notes = Path(notes_dir or default_notes_dir(root_path))
    themes = Path(themes_path or default_themes_path(root_path))
    reports = Path(reports_dir or default_reports_dir(root_path))
    project = profile.name if profile else ""
    checked = [str(path) for path in (registry, bibtex, notes, themes, reports)]
    findings: list[ValidationFinding] = []

    for path in (registry, bibtex, notes, themes, reports):
        if path.is_absolute() and not is_path_within(path, root_path):
            findings.append(
                _finding(
                    "error",
                    "path_escapes_workspace",
                    f"Configured path escapes the selected workspace root: {path}",
                    str(path),
                    "Use project-relative or workspace-relative paths.",
                )
            )

    if profile is None:
        expected = [root_path / "data", root_path / "data" / "registries", root_path / "data" / "bibtex", root_path / "data" / "notes", root_path / "reports"]
    else:
        project_root = Path(profile.root)
        expected = [project_root, Path(profile.notes_dir), Path(profile.bibtex_path).parent, Path(profile.reports_dir)]
        if not is_path_within(project_root, root_path):
            findings.append(
                _finding(
                    "error",
                    "project_root_escapes_workspace",
                    f"Project root escapes workspace: {project_root}",
                    profile.name,
                    "Move the project under projects/ or fix project.json.",
                )
            )
    for directory in expected:
        if not directory.exists():
            findings.append(_finding("warning", "missing_expected_folder", f"Expected folder is missing: {directory}", str(directory)))

    findings.extend(
        workspace_health(
            root=Path(profile.root) if profile else root_path,
            registry_path=registry,
            bibtex_path=bibtex,
            notes_dir=notes,
            themes_path=themes,
            reports_dir=reports,
            profile=profile,
        )
    )

    papers = []
    parsed_notes = []
    claims = []
    entries = []
    theme_defs = []
    if registry.exists():
        papers = load_registry(registry)
    if notes.exists():
        parsed_notes = collect_notes(notes)
        claims = [claim for note in parsed_notes for claim in note.claims]
    if bibtex.exists():
        entries = parse_bibtex_file(bibtex)
    if themes.exists():
        theme_defs = load_themes(themes)
    if papers:
        findings.extend(validate_registry(papers, root=Path(profile.root) if profile else root_path, claims=claims))
    if entries or papers:
        findings.extend(validate_bibtex(entries, papers))

    registry_ids = {paper.paper_id for paper in papers}
    for note in parsed_notes:
        if note.paper_id and note.paper_id not in registry_ids:
            findings.append(
                _finding(
                    "warning",
                    "integrity_note_unknown_paper",
                    f"Note references paper_id not present in registry: {note.paper_id}",
                    note.paper_id,
                    "Add a registry row or correct the note metadata.",
                )
            )

    scan_root = Path(profile.root) if profile else root_path
    file_registry = default_file_registry_path(scan_root, project=profile is not None)
    file_scan = scan_local_files(root=scan_root, registry_path=registry, file_registry_path=file_registry)
    checked.append(str(file_registry))
    for warning in file_scan.warnings:
        findings.append(_finding("warning", "local_file_warning", warning, suggestion="Run `paperwb files audit` for details."))

    for tracked in _tracked_files(root_path):
        path = Path(tracked)
        if ".paperwb" in path.parts or path.suffix.lower() in {".sqlite", ".db"}:
            findings.append(
                _finding(
                    "error",
                    "tracked_cache_file",
                    f"Tracked cache or database file should not be committed: {tracked}",
                    tracked,
                    "Remove it from git and keep cache files ignored.",
                )
            )
        if path.suffix.lower() == ".pdf" and ("data" in path.parts or "projects" in path.parts):
            findings.append(
                _finding(
                    "error",
                    "tracked_pdf",
                    f"Tracked PDF detected in repository data: {tracked}",
                    tracked,
                    "Remove real PDFs from the repository; keep only local user-owned files ignored or outside git.",
                )
            )

    for project_profile in list_project_profiles(root_path):
        for configured in (
            project_profile.registry_path,
            project_profile.bibtex_path,
            project_profile.notes_dir,
            project_profile.themes_path,
            project_profile.reports_dir,
        ):
            if not is_path_within(configured, project_profile.root):
                findings.append(
                    _finding(
                        "error",
                        "project_profile_path_escape",
                        f"{project_profile.name} path escapes its project root: {configured}",
                        project_profile.name,
                        "Keep project paths inside the project folder.",
                    )
                )

    return IntegrityResult(root=str(root_path), project=project, findings=_dedupe_findings(findings), checked_paths=checked)


def workspace_integrity_report(result: IntegrityResult) -> str:
    lines = [
        "# Workspace Integrity Report v0.9",
        "",
        "This report checks local workspace consistency. It does not modify files.",
        "",
        f"Root: {_portable_path(result.root)}",
        f"Project: {result.project or 'default data workflow'}",
        f"Errors: {len(result.errors)}",
        f"Warnings: {len(result.warnings)}",
        f"Checked paths: {len(result.checked_paths)}",
        "",
        "## Checked Paths",
        "",
    ]
    for path in result.checked_paths:
        lines.append(f"- `{_portable_path(path)}`")
    lines.extend(["", "## Findings", ""])
    if not result.findings:
        lines.append("No integrity findings detected.")
    else:
        lines.extend(["| Severity | Code | Identifier | Message | Suggestion |", "| --- | --- | --- | --- | --- |"])
        for finding in result.findings:
            lines.append(
                f"| {finding.severity} | {finding.code} | {_escape(finding.identifier)} | {_escape(finding.message)} | {_escape(finding.suggestion)} |"
            )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This is a completeness and path-safety audit, not a scientific truth audit.",
            "- It does not download, scrape, parse PDFs, or inspect ignored private files.",
            "- Warnings should be reviewed before migration, restore, or external release.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _escape(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _portable_path(value: str | Path) -> str:
    path = Path(value)
    try:
        return path.resolve(strict=False).relative_to(Path.cwd().resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def _dedupe_findings(findings: list[ValidationFinding]) -> list[ValidationFinding]:
    seen: set[tuple[str, str, str, str]] = set()
    result: list[ValidationFinding] = []
    for finding in findings:
        key = (finding.severity, finding.code, finding.identifier, finding.message)
        if key in seen:
            continue
        seen.add(key)
        result.append(finding)
    return result
