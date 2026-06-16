"""Backward-compatibility inspection for historical workspace shapes."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

from . import __version__
from .io import read_text
from .markdown import findings_table, markdown_table
from .notes import parse_note_file
from .paths import default_bibtex_path, default_notes_dir, default_registry_path, default_themes_path, display_path, is_path_within, relative_path
from .projects import PROJECT_CONFIG
from .registry import REGISTRY_FIELDS, REQUIRED_REGISTRY_HEADERS
from .schema import ValidationFinding, make_validation_finding


PROJECT_PATH_FIELDS = ("registry_path", "bibtex_path", "notes_dir", "themes_path", "reports_dir")


@dataclass(slots=True)
class RegistrySchemaObservation:
    path: str
    headers: list[str] = field(default_factory=list)
    missing_required: list[str] = field(default_factory=list)
    extra_columns: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ProjectObservation:
    path: str
    has_project_json: bool = False
    configured_paths: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class CompatibilityInspection:
    root: str
    workspace_type: str
    approximate_version: str
    supported: bool
    inspectable: bool
    migration_needed: bool
    migratable: bool
    requires_backup: bool
    requires_manual_review: bool
    findings: list[ValidationFinding] = field(default_factory=list)
    registry_observations: list[RegistrySchemaObservation] = field(default_factory=list)
    project_observations: list[ProjectObservation] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationFinding]:
        return [finding for finding in self.findings if finding.severity == "error"]

    @property
    def warnings(self) -> list[ValidationFinding]:
        return [finding for finding in self.findings if finding.severity == "warning"]

    @property
    def infos(self) -> list[ValidationFinding]:
        return [finding for finding in self.findings if finding.severity == "info"]


@dataclass(slots=True)
class CompatibilityMatrixRow:
    source_workspace: str
    supported: str
    inspectable: str
    migratable: str
    requires_backup: str
    requires_manual_review: str
    tests: str
    limitations: str


def inspect_workspace(path: str | Path, *, to_project: str = "migrated_review") -> CompatibilityInspection:
    root = Path(path).expanduser().resolve(strict=False)
    findings: list[ValidationFinding] = []
    registry_observations: list[RegistrySchemaObservation] = []
    project_observations: list[ProjectObservation] = []

    if not root.exists():
        findings.append(
            _finding(
                "error",
                "workspace_missing",
                f"Workspace path does not exist: {root}",
                root,
                "Choose an existing workspace or historical fixture path.",
            )
        )
        return CompatibilityInspection(
            root=str(root),
            workspace_type="missing",
            approximate_version="unknown",
            supported=False,
            inspectable=False,
            migration_needed=False,
            migratable=False,
            requires_backup=False,
            requires_manual_review=True,
            findings=findings,
            recommended_actions=["Create or choose an existing local workspace before running migration checks."],
        )

    legacy_files = _legacy_files(root)
    project_roots = _project_roots(root)
    has_legacy = (root / "data").exists() and any(path.exists() for path in legacy_files.values())
    has_projects = bool(project_roots)
    workspace_type = _workspace_type(has_legacy, has_projects, root)
    approximate_version = _approximate_version(root, has_legacy, project_roots)

    if has_legacy:
        _inspect_legacy(root, legacy_files, findings, registry_observations)
    for project_root in project_roots:
        project_observations.append(_inspect_project(project_root, root, findings, registry_observations))

    if not has_legacy and not has_projects:
        findings.append(
            _finding(
                "error",
                "unsupported_workspace_shape",
                f"No legacy data/ workflow or project-profile workspace detected under {root}",
                root,
                "Run `paperwb init`, choose a workspace root, or inspect a project folder directly.",
            )
        )

    migration_needed = has_legacy
    requires_backup = migration_needed
    if has_legacy and project_roots:
        findings.append(
            _finding(
                "warning",
                "partial_migration_workspace",
                "Legacy data/ files and project profiles both exist; migration needs manual target review.",
                root,
                "Inspect existing projects before choosing a migration target.",
            )
        )
    target = root / "projects" / to_project
    if has_legacy and target.exists() and any(target.iterdir()):
        findings.append(
            _finding(
                "error",
                "migration_target_conflict",
                f"Default migration target already exists and is not empty: {relative_path(target, root)}",
                target,
                "Choose a new --to-project name or inspect the existing project before migration.",
            )
        )

    has_error = any(finding.severity == "error" for finding in findings)
    has_path_escape = any(finding.code == "project_profile_path_escape" for finding in findings)
    supported = workspace_type != "unknown_workspace" and not any(finding.code == "unsupported_workspace_shape" for finding in findings)
    inspectable = workspace_type != "missing"
    migratable = bool(has_legacy and not has_path_escape and not any(finding.code == "migration_target_conflict" for finding in findings))
    requires_manual_review = has_error or any(
        finding.code in {"extra_registry_columns", "partial_migration_workspace", "unsafe_local_pdf_path", "note_parse_warning"} for finding in findings
    )
    return CompatibilityInspection(
        root=str(root),
        workspace_type=workspace_type,
        approximate_version=approximate_version,
        supported=supported,
        inspectable=inspectable,
        migration_needed=migration_needed,
        migratable=migratable,
        requires_backup=requires_backup,
        requires_manual_review=requires_manual_review,
        findings=_dedupe_findings(findings),
        registry_observations=registry_observations,
        project_observations=project_observations,
        recommended_actions=_recommended_actions(migration_needed, migratable, requires_manual_review, has_error),
    )


def compatibility_terminal_summary(inspection: CompatibilityInspection) -> str:
    lines = [
        f"Workspace: {display_path(inspection.root)}",
        f"Detected type: {inspection.workspace_type}",
        f"Approximate version: {inspection.approximate_version}",
        f"Supported: {_yes_no(inspection.supported)}",
        f"Inspectable: {_yes_no(inspection.inspectable)}",
        f"Migration needed: {_yes_no(inspection.migration_needed)}",
        f"Migratable: {_yes_no(inspection.migratable)}",
        f"Requires backup: {_yes_no(inspection.requires_backup)}",
        f"Manual review: {_yes_no(inspection.requires_manual_review)}",
        f"Findings: {len(inspection.errors)} error(s), {len(inspection.warnings)} warning(s), {len(inspection.infos)} info",
    ]
    if inspection.findings:
        lines.append("")
        for finding in inspection.findings:
            identifier = f" [{finding.identifier}]" if finding.identifier else ""
            lines.append(f"{finding.severity.upper()} {finding.code}{identifier}: {finding.message}")
    return "\n".join(lines).rstrip() + "\n"


def compatibility_report(inspection: CompatibilityInspection) -> str:
    lines = [
        f"# Compatibility Inspection Report v{__version__}",
        "",
        "This report inspects historical or malformed local workspaces. It does not modify files.",
        "",
        f"Root: `{display_path(inspection.root)}`",
        f"Workspace type: `{inspection.workspace_type}`",
        f"Approximate version: `{inspection.approximate_version}`",
        f"Supported: `{_yes_no(inspection.supported)}`",
        f"Inspectable: `{_yes_no(inspection.inspectable)}`",
        f"Migration needed: `{_yes_no(inspection.migration_needed)}`",
        f"Migratable: `{_yes_no(inspection.migratable)}`",
        f"Requires backup: `{_yes_no(inspection.requires_backup)}`",
        f"Requires manual review: `{_yes_no(inspection.requires_manual_review)}`",
        "",
        "## Registry Schema Observations",
        "",
        _registry_table(inspection.registry_observations),
        "",
        "## Project Observations",
        "",
        _project_table(inspection.project_observations),
        "",
        "## Findings",
        "",
        findings_table(inspection.findings, empty="No compatibility findings detected."),
        "",
        "## Recommended Actions",
        "",
    ]
    if inspection.recommended_actions:
        lines.extend(f"- {action}" for action in inspection.recommended_actions)
    else:
        lines.append("- No follow-up action is required.")
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            "- Compatibility inspection is read-only.",
            "- Migration should be dry-run first and should copy, not move, legacy files.",
            "- Extra registry columns are reported so migrations can preserve the raw CSV rather than rewriting user fields.",
            "- Real workspaces should be backed up before any forced migration.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def compatibility_matrix_rows() -> list[CompatibilityMatrixRow]:
    return [
        CompatibilityMatrixRow("legacy data/ workflow", "yes", "yes", "yes, to project profile", "yes", "if malformed or partially migrated", "tests/test_compatibility_v3_2.py", "Reports and caches are not copied by default."),
        CompatibilityMatrixRow("early project profile without project.json", "yes", "yes", "not needed", "no", "if required files are missing", "tests/test_compatibility_v3_2.py", "Loaded through project-root defaults."),
        CompatibilityMatrixRow("pre-v2 registry schema", "yes", "yes", "copy-preserved", "yes for migration", "if extra or missing columns exist", "tests/test_compatibility_v3_2.py", "Current loaders ignore unknown columns; migration copies raw CSV."),
        CompatibilityMatrixRow("v2.0rc dogfood workspace", "yes", "yes", "not needed", "no", "no, unless user data is incomplete", "tests/test_compatibility_v3_2.py", "Empty scaffolds are valid and should explain missing data clearly."),
        CompatibilityMatrixRow("v3.0rc project workspace", "yes", "yes", "not needed", "no", "no for clean projects", "tests/test_compatibility_v3_2.py", "Advanced sidecars remain experimental."),
        CompatibilityMatrixRow("malformed missing registry", "partial", "yes", "no", "n/a", "yes", "tests/test_compatibility_v3_2.py", "User must create or recover a registry first."),
        CompatibilityMatrixRow("malformed broken notes", "partial", "yes", "not until repaired", "yes if migrating", "yes", "tests/test_compatibility_v3_2.py", "Notes are reported with parser warnings; claims are not invented."),
        CompatibilityMatrixRow("partial migration conflict", "partial", "yes", "blocked until target chosen", "yes", "yes", "tests/test_compatibility_v3_2.py", "Existing project targets are never overwritten silently."),
        CompatibilityMatrixRow("workspace with extra registry columns", "yes", "yes", "copy-preserved", "yes for migration", "yes", "tests/test_compatibility_v3_2.py", "Extra columns are not interpreted but should be preserved by copy-based migration."),
    ]


def compatibility_matrix_markdown() -> str:
    rows = compatibility_matrix_rows()
    return (
        f"# Compatibility Matrix v{__version__}\n\n"
        "This matrix documents which historical local workspace shapes are inspectable, migratable, or require manual review.\n\n"
        + markdown_table(
            ["Source workspace", "Supported", "Inspectable", "Migratable", "Requires backup", "Manual review", "Tests", "Limitations"],
            [
                [
                    row.source_workspace,
                    row.supported,
                    row.inspectable,
                    row.migratable,
                    row.requires_backup,
                    row.requires_manual_review,
                    row.tests,
                    row.limitations,
                ]
                for row in rows
            ],
        )
        + "\n\n## Policy\n\n"
        "- Inspect before migrating.\n"
        "- Dry-run before forced migration.\n"
        "- Preserve extra user columns by copying raw registries where possible.\n"
        "- Never overwrite existing project targets without an explicit future safety-reviewed force workflow.\n"
    )


def _inspect_legacy(
    root: Path,
    legacy_files: dict[str, Path],
    findings: list[ValidationFinding],
    registry_observations: list[RegistrySchemaObservation],
) -> None:
    registry = legacy_files["registry"]
    if registry.exists():
        registry_observations.append(_inspect_registry(registry, root, findings))
    else:
        findings.append(_finding("error", "legacy_registry_missing", f"Legacy registry is missing: {relative_path(registry, root)}", registry, "Restore or create data/registries/papers.csv before migration."))
    for key, code in (("bibtex", "legacy_bibtex_missing"), ("notes", "legacy_notes_missing"), ("themes", "legacy_themes_missing")):
        path = legacy_files[key]
        if not path.exists():
            findings.append(_finding("warning", code, f"Legacy {key} path is missing: {relative_path(path, root)}", path, "Migration can still be planned, but the migrated project will be incomplete."))
    notes = legacy_files["notes"]
    if notes.exists():
        _inspect_notes(notes, root, findings)


def _inspect_project(
    project_root: Path,
    workspace_root: Path,
    findings: list[ValidationFinding],
    registry_observations: list[RegistrySchemaObservation],
) -> ProjectObservation:
    config_path = project_root / PROJECT_CONFIG
    config: dict[str, object] = {}
    has_config = config_path.exists()
    if has_config:
        try:
            config = json.loads(read_text(config_path))
        except json.JSONDecodeError as exc:
            findings.append(_finding("error", "project_config_invalid_json", f"project.json is not valid JSON: {exc}", config_path, "Repair project.json before migration or validation."))
    configured_paths: dict[str, str] = {}
    for key in PROJECT_PATH_FIELDS:
        value = str(config.get(key, _default_project_value(key)))
        configured_paths[key] = value
        resolved = Path(value) if Path(value).is_absolute() else project_root / value
        if not is_path_within(resolved, project_root):
            findings.append(_finding("error", "project_profile_path_escape", f"{key} escapes project root: {value}", resolved, "Keep project profile paths inside the project folder."))
    registry = project_root / configured_paths["registry_path"]
    bibtex = project_root / configured_paths["bibtex_path"]
    notes = project_root / configured_paths["notes_dir"]
    themes = project_root / configured_paths["themes_path"]
    required = ((registry, "project_registry_missing"), (bibtex, "project_bibtex_missing"), (notes, "project_notes_missing"), (themes, "project_themes_missing"))
    for path, code in required:
        if not path.exists():
            severity = "error" if code == "project_registry_missing" else "warning"
            findings.append(_finding(severity, code, f"Project path is missing: {relative_path(path, workspace_root)}", path, "Recover the file or adjust project.json."))
    if registry.exists():
        registry_observations.append(_inspect_registry(registry, workspace_root, findings))
    if notes.exists():
        _inspect_notes(notes, workspace_root, findings)
    return ProjectObservation(path=relative_path(project_root, workspace_root), has_project_json=has_config, configured_paths=configured_paths)


def _inspect_registry(path: Path, root: Path, findings: list[ValidationFinding]) -> RegistrySchemaObservation:
    headers = _csv_headers(path)
    missing = sorted(REQUIRED_REGISTRY_HEADERS - set(headers))
    extra = [header for header in headers if header and header not in REGISTRY_FIELDS]
    observation = RegistrySchemaObservation(path=relative_path(path, root), headers=headers, missing_required=missing, extra_columns=extra)
    if missing:
        findings.append(_finding("error", "registry_missing_required_columns", f"Registry missing required columns: {', '.join(missing)}", path, "Add required registry headers before loading or migrating."))
    if extra:
        findings.append(_finding("info", "extra_registry_columns", f"Registry has extra user columns: {', '.join(extra)}", path, "Copy-based migration preserves the raw CSV; avoid rewriting this registry through schema-normalizing commands until reviewed."))
    for row_number, row in enumerate(_csv_rows(path), start=2):
        local_pdf = (row.get("local_pdf_path") or "").strip()
        if _unsafe_path_reference(local_pdf):
            findings.append(_finding("warning", "unsafe_local_pdf_path", f"Registry row {row_number} has an unsafe or absolute local_pdf_path.", path, "Keep local file paths relative where possible and do not commit PDFs."))
    return observation


def _inspect_notes(notes_dir: Path, root: Path, findings: list[ValidationFinding]) -> None:
    for note_path in sorted(notes_dir.rglob("*.md")):
        try:
            note = parse_note_file(note_path)
        except UnicodeDecodeError as exc:
            findings.append(_finding("error", "note_decode_error", f"Could not read note as UTF-8: {exc}", note_path, "Convert the note to UTF-8 before migration."))
            continue
        for warning in note.warnings:
            findings.append(_finding("warning", "note_parse_warning", f"{relative_path(note_path, root)}: {warning}", note_path, "Repair the structured note before relying on extracted claims."))


def _legacy_files(root: Path) -> dict[str, Path]:
    registry = default_registry_path(root)
    if not registry.exists():
        registry = _first_existing(root / "data" / "registries", "*.csv", registry)
    bibtex = default_bibtex_path(root)
    if not bibtex.exists():
        bibtex = _first_existing(root / "data" / "bibtex", "*.bib", bibtex)
    return {
        "registry": registry,
        "bibtex": bibtex,
        "notes": default_notes_dir(root),
        "themes": default_themes_path(root),
    }


def _first_existing(directory: Path, pattern: str, fallback: Path) -> Path:
    if directory.exists():
        for path in sorted(directory.glob(pattern)):
            if path.is_file():
                return path
    return fallback


def _project_roots(root: Path) -> list[Path]:
    roots: list[Path] = []
    if (root / PROJECT_CONFIG).exists() or (root / "registry.csv").exists():
        roots.append(root)
    projects = root / "projects"
    if projects.exists():
        roots.extend(path for path in sorted(projects.iterdir()) if path.is_dir())
    return roots


def _workspace_type(has_legacy: bool, has_projects: bool, root: Path) -> str:
    if has_legacy and has_projects:
        return "partial_migration_workspace"
    if has_legacy:
        return "legacy_data_workflow"
    if has_projects:
        return "project_profile_workspace"
    if (root / "data").exists() or (root / "projects").exists():
        return "malformed_workspace"
    return "unknown_workspace"


def _approximate_version(root: Path, has_legacy: bool, project_roots: list[Path]) -> str:
    if has_legacy and not project_roots:
        return "v0.1-v0.9 legacy data workflow"
    if any(not (project / PROJECT_CONFIG).exists() for project in project_roots):
        return "v0.2 early project-profile workflow"
    if any((project / "project_onboarding.md").exists() or (project / "first_week_plan.md").exists() for project in project_roots):
        return "v2.0 dogfooding workspace"
    if any((project / "workflows").exists() or (project / "rules.json").exists() for project in project_roots):
        return "v3.0rc-or-newer project workspace"
    if project_roots:
        return "v1-v3 project-profile workflow"
    return "unknown"


def _default_project_value(key: str) -> str:
    return {
        "registry_path": "registry.csv",
        "bibtex_path": "bibtex/library.bib",
        "notes_dir": "notes",
        "themes_path": "themes.json",
        "reports_dir": "reports",
    }[key]


def _csv_headers(path: Path) -> list[str]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            return [header.strip() for header in next(csv.reader(handle), [])]
    except OSError:
        return []


def _csv_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    except OSError:
        return []


def _unsafe_path_reference(value: str) -> bool:
    if not value:
        return False
    path = Path(value)
    return path.is_absolute() or ".." in path.parts


def _registry_table(observations: list[RegistrySchemaObservation]) -> str:
    if not observations:
        return "No registry files detected."
    return markdown_table(
        ["Path", "Headers", "Missing required", "Extra columns"],
        [
            [
                observation.path,
                ", ".join(observation.headers) or "(none)",
                ", ".join(observation.missing_required) or "none",
                ", ".join(observation.extra_columns) or "none",
            ]
            for observation in observations
        ],
    )


def _project_table(observations: list[ProjectObservation]) -> str:
    if not observations:
        return "No project profiles detected."
    return markdown_table(
        ["Project path", "project.json", "Registry", "BibTeX", "Notes", "Themes", "Reports"],
        [
            [
                observation.path,
                _yes_no(observation.has_project_json),
                observation.configured_paths.get("registry_path", ""),
                observation.configured_paths.get("bibtex_path", ""),
                observation.configured_paths.get("notes_dir", ""),
                observation.configured_paths.get("themes_path", ""),
                observation.configured_paths.get("reports_dir", ""),
            ]
            for observation in observations
        ],
    )


def _recommended_actions(migration_needed: bool, migratable: bool, requires_manual_review: bool, has_error: bool) -> list[str]:
    if has_error:
        return ["Fix error-level findings before running forced migration.", "Use `paperwb compatibility report` after repairs to confirm the workspace shape."]
    if migration_needed and migratable:
        return ["Run `paperwb migrate run --dry-run` and inspect the migration plan.", "Create or confirm a backup before any forced migration."]
    if requires_manual_review:
        return ["Review warnings and info findings before using this workspace for real writing."]
    return ["Proceed with normal validation commands such as `paperwb doctor`, `paperwb validate-registry`, and `paperwb validate-bib`."]


def _finding(severity: str, code: str, message: str, identifier: str | Path, suggestion: str = "") -> ValidationFinding:
    shown = display_path(identifier) if isinstance(identifier, Path) else str(identifier)
    return make_validation_finding(severity, code, message, identifier=shown, suggestion=suggestion)


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


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"
