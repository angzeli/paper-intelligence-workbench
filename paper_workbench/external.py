"""Local-only external workspace registration and safe workflow adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import re

from .audit import citation_audit
from .backups import BackupManifest, create_backup
from .bibtex import parse_bibtex_file, validate_bibtex
from .claims import collect_notes, save_claims_csv
from .dashboard import build_dashboard, dashboard_markdown, dashboard_terminal
from .doctor import workspace_health
from .io import load_json, write_json, write_text
from .markdown import findings_table
from .paths import display_path, is_path_within
from .projects import PROJECT_CONFIG, load_project_profile, validate_project_name
from .registry import load_registry, validate_registry, validate_registry_headers
from .reporting import citation_audit_report, evidence_map_report, workspace_health_report
from .schema import ProjectProfile, ValidationFinding, make_validation_finding
from .support import create_support_bundle
from .tags import load_themes


EXTERNAL_CONFIG_SCHEMA = "paperwb-external-workspaces-v1"
DEFAULT_LOCAL_CONFIG = ".paperwb-local/workspaces.json"
REDACTED_EXTERNAL_PATH = "<redacted-external-workspace>"
GENERAL_ABSOLUTE_PATH_RE = re.compile(r"(?<![:\w>])/(?:[^\s`|,\")]+/)*[^\s`|,\")]+")
ALLOWED_EXTERNAL_RUNS = {
    "doctor",
    "dashboard",
    "validate-registry",
    "validate-bib",
    "claims",
    "evidence-map",
    "citation-audit",
    "support-bundle",
    "backup",
}


@dataclass(slots=True)
class ExternalWorkspace:
    name: str
    path: str
    project: str = ""
    description: str = ""
    added_at: str = ""


@dataclass(slots=True)
class ExternalWorkspaceConfig:
    config_path: Path
    workspaces: dict[str, ExternalWorkspace] = field(default_factory=dict)


@dataclass(slots=True)
class ExternalValidation:
    workspace: ExternalWorkspace
    workspace_root: Path
    profile: ProjectProfile | None
    findings: list[ValidationFinding] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationFinding]:
        return [finding for finding in self.findings if finding.severity == "error"]

    @property
    def warnings(self) -> list[ValidationFinding]:
        return [finding for finding in self.findings if finding.severity == "warning"]

    @property
    def blocking_errors(self) -> list[ValidationFinding]:
        return [finding for finding in self.errors if finding.code in {"external_workspace_missing", "external_project_missing"}]


@dataclass(slots=True)
class ExternalRunResult:
    workspace: ExternalWorkspace
    command: str
    content: str = ""
    outputs: list[Path] = field(default_factory=list)
    findings: list[ValidationFinding] = field(default_factory=list)
    backup: BackupManifest | None = None


def default_external_config_path(root: str | Path = ".") -> Path:
    return Path(root) / DEFAULT_LOCAL_CONFIG


def load_external_config(config_path: str | Path | None = None, *, root: str | Path = ".") -> ExternalWorkspaceConfig:
    target = Path(config_path) if config_path else default_external_config_path(root)
    if not target.exists():
        return ExternalWorkspaceConfig(config_path=target)
    data = load_json(target)
    if not isinstance(data, dict):
        raise ValueError(f"External workspace config must be a JSON object: {target}")
    workspaces: dict[str, ExternalWorkspace] = {}
    raw_workspaces = data.get("workspaces", {})
    if not isinstance(raw_workspaces, dict):
        raise ValueError(f"External workspace config has invalid `workspaces`: {target}")
    for name, value in raw_workspaces.items():
        if not isinstance(value, dict):
            raise ValueError(f"External workspace entry {name!r} must be a JSON object")
        workspace = ExternalWorkspace(
            name=validate_project_name(str(value.get("name") or name)),
            path=str(value.get("path", "")),
            project=str(value.get("project", "")).strip(),
            description=str(value.get("description", "")).strip(),
            added_at=str(value.get("added_at", "")).strip(),
        )
        if not workspace.path:
            raise ValueError(f"External workspace entry {name!r} is missing `path`")
        workspaces[workspace.name] = workspace
    return ExternalWorkspaceConfig(config_path=target, workspaces=workspaces)


def save_external_config(config: ExternalWorkspaceConfig) -> Path:
    payload = {
        "schema": EXTERNAL_CONFIG_SCHEMA,
        "workspaces": {name: _workspace_to_dict(workspace) for name, workspace in sorted(config.workspaces.items())},
    }
    return write_json(config.config_path, payload, force=True)


def add_external_workspace(
    name: str,
    path: str | Path,
    *,
    project: str = "",
    description: str = "",
    config_path: str | Path | None = None,
    root: str | Path = ".",
    force: bool = False,
) -> ExternalWorkspace:
    config = load_external_config(config_path, root=root)
    workspace_name = validate_project_name(name)
    if workspace_name in config.workspaces and not force:
        raise FileExistsError(f"external workspace {workspace_name!r} already exists; use --force to update it")
    target = Path(path).expanduser().resolve(strict=False)
    if not target.exists() or not target.is_dir():
        raise FileNotFoundError(f"external workspace path must be an existing directory: {target}")
    project_name = validate_project_name(project or workspace_name)
    workspace = ExternalWorkspace(
        name=workspace_name,
        path=str(target),
        project=project_name,
        description=description.strip(),
        added_at=datetime.now(timezone.utc).isoformat(),
    )
    config.workspaces[workspace_name] = workspace
    save_external_config(config)
    return workspace


def remove_external_workspace(name: str, *, config_path: str | Path | None = None, root: str | Path = ".") -> ExternalWorkspace:
    config = load_external_config(config_path, root=root)
    workspace_name = validate_project_name(name)
    try:
        removed = config.workspaces.pop(workspace_name)
    except KeyError as exc:
        raise KeyError(f"external workspace {workspace_name!r} is not registered") from exc
    save_external_config(config)
    return removed


def list_external_workspaces(*, config_path: str | Path | None = None, root: str | Path = ".") -> list[ExternalWorkspace]:
    return list(load_external_config(config_path, root=root).workspaces.values())


def get_external_workspace(name: str, *, config_path: str | Path | None = None, root: str | Path = ".") -> ExternalWorkspace:
    config = load_external_config(config_path, root=root)
    workspace_name = validate_project_name(name)
    try:
        return config.workspaces[workspace_name]
    except KeyError as exc:
        raise KeyError(f"external workspace {workspace_name!r} is not registered") from exc


def validate_external_workspace(
    name: str,
    *,
    config_path: str | Path | None = None,
    root: str | Path = ".",
) -> ExternalValidation:
    workspace = get_external_workspace(name, config_path=config_path, root=root)
    return inspect_external_workspace(workspace, repo_root=root)


def inspect_external_workspace(workspace: ExternalWorkspace, *, repo_root: str | Path = ".") -> ExternalValidation:
    workspace_root = Path(workspace.path).expanduser().resolve(strict=False)
    findings: list[ValidationFinding] = []
    profile: ProjectProfile | None = None
    if not workspace_root.exists() or not workspace_root.is_dir():
        findings.append(
            make_validation_finding(
                "error",
                "external_workspace_missing",
                f"External workspace path does not exist or is not a directory: {workspace_root}",
                source=str(workspace_root),
                suggestion="Update the local-only registration with `paperwb external add NAME PATH --force` or remove it.",
            )
        )
        return ExternalValidation(workspace=workspace, workspace_root=workspace_root, profile=None, findings=findings)
    repo = Path(repo_root).resolve(strict=False)
    if is_path_within(workspace_root, repo):
        findings.append(
            make_validation_finding(
                "warning",
                "external_workspace_inside_repo",
                "External workspace path is inside the repository; keep private data out of tracked files.",
                source=str(workspace_root),
                suggestion="Prefer a workspace outside the repository for real private dogfooding.",
            )
        )
    try:
        profile = load_project_profile(workspace.project, root=workspace_root)
    except FileNotFoundError:
        profile_path = workspace_root / "projects" / workspace.project / PROJECT_CONFIG
        findings.append(
            make_validation_finding(
                "error",
                "external_project_missing",
                f"Registered project {workspace.project!r} was not found under the external workspace.",
                source=str(profile_path),
                suggestion="Create a project in the external root or re-register with the correct --project value.",
            )
        )
        return ExternalValidation(workspace=workspace, workspace_root=workspace_root, profile=None, findings=findings)
    findings.extend(
        workspace_health(
            root=profile.root,
            registry_path=profile.registry_path,
            bibtex_path=profile.bibtex_path,
            notes_dir=profile.notes_dir,
            themes_path=profile.themes_path,
            reports_dir=profile.reports_dir,
            profile=profile,
        )
    )
    return ExternalValidation(workspace=workspace, workspace_root=workspace_root, profile=profile, findings=findings)


def external_validation_markdown(validation: ExternalValidation, *, reveal_paths: bool = False) -> str:
    workspace = validation.workspace
    lines = [
        "# External Workspace Validation",
        "",
        "This validation uses a local-only workspace registration. It does not copy private data into the repository.",
        "Private paths are redacted by default; use `--show-paths` only for local debugging.",
        "",
        f"Name: {workspace.name}",
        f"Project: {workspace.project}",
        f"Path: `{_redact_external_text(workspace.path, validation, reveal_paths=reveal_paths)}`",
        f"Profile loaded: {str(validation.profile is not None).lower()}",
        f"Errors: {len(validation.errors)}",
        f"Warnings: {len(validation.warnings)}",
        "",
        "## Findings",
        "",
        findings_table(_redact_findings(validation.findings, validation, reveal_paths=reveal_paths)),
    ]
    return "\n".join(lines).rstrip() + "\n"


def external_workspace_summary(workspace: ExternalWorkspace, *, base_path: str | Path = ".", reveal_paths: bool = False) -> str:
    path_display = display_path(workspace.path, base_path=base_path) if reveal_paths else REDACTED_EXTERNAL_PATH
    return f"{workspace.name}\tproject={workspace.project}\tpath={path_display}"


def redact_external_output(text: str | Path, validation: ExternalValidation, *, reveal_paths: bool = False) -> str:
    """Redact path-like text for external workspace terminal/report output."""
    return _redact_external_text(str(text), validation, reveal_paths=reveal_paths)


def run_external_workflow(
    name: str,
    command: str,
    *,
    config_path: str | Path | None = None,
    root: str | Path = ".",
    out: str | Path | None = None,
    force: bool = False,
    notes: str = "",
    reveal_paths: bool = False,
) -> ExternalRunResult:
    if command not in ALLOWED_EXTERNAL_RUNS:
        allowed = ", ".join(sorted(ALLOWED_EXTERNAL_RUNS))
        raise ValueError(f"unsupported external run command {command!r}; allowed commands: {allowed}")
    validation = validate_external_workspace(name, config_path=config_path, root=root)
    if validation.blocking_errors:
        return ExternalRunResult(
            workspace=validation.workspace,
            command=command,
            content=findings_table(_redact_findings(validation.findings, validation, reveal_paths=reveal_paths)) + "\n",
            findings=validation.findings,
        )
    if validation.profile is None:
        return ExternalRunResult(
            workspace=validation.workspace,
            command=command,
            content=findings_table(_redact_findings(validation.findings, validation, reveal_paths=reveal_paths)) + "\n",
            findings=validation.findings,
        )
    profile = validation.profile
    papers = load_registry(profile.registry_path) if Path(profile.registry_path).exists() else []
    entries = parse_bibtex_file(profile.bibtex_path) if Path(profile.bibtex_path).exists() else []
    notes_data = collect_notes(profile.notes_dir) if Path(profile.notes_dir).exists() else []
    claims = [claim for note_data in notes_data for claim in note_data.claims]
    themes = load_themes(profile.themes_path) if Path(profile.themes_path).exists() else []
    outputs: list[Path] = []
    result_findings = list(validation.findings)
    default_reports_dir = Path(profile.reports_dir)

    if command == "doctor":
        content = workspace_health_report(validation.findings)
    elif command == "dashboard":
        dashboard = build_dashboard(
            project=profile.name,
            root=profile.root,
            papers=papers,
            notes=notes_data,
            claims=claims,
            bibtex_entries=entries,
            themes=themes,
            health_findings=validation.findings,
            project_profiles=[],
            report_paths=sorted(Path(profile.reports_dir).glob("*.md")) if Path(profile.reports_dir).exists() else [],
        )
        prefix = (
            f"External workspace: {validation.workspace.name}\n"
            "Private data stays in the registered external path. For adapter workflows, use `paperwb external run ...`.\n\n"
        )
        content = prefix + (dashboard_markdown(dashboard) if out else dashboard_terminal(dashboard))
    elif command == "validate-registry":
        result_findings = validate_registry_headers(profile.registry_path) + validate_registry(papers, root=profile.root, claims=claims)
        content = findings_table(result_findings) + "\n"
    elif command == "validate-bib":
        result_findings = validate_bibtex(entries, papers)
        content = findings_table(result_findings) + "\n"
    elif command == "claims":
        target = Path(out) if out else default_reports_dir / "external_claims.csv"
        outputs.append(save_claims_csv(claims, target, force=force, root=profile.root))
        content = f"Wrote {_redact_external_text(str(outputs[-1]), validation, reveal_paths=reveal_paths)}\nClaims: {len(claims)}\n"
    elif command == "evidence-map":
        target = Path(out) if out else default_reports_dir / "external_evidence_map.md"
        outputs.append(write_text(target, evidence_map_report(papers, claims, themes, notes_data), force=force))
        content = f"Wrote {_redact_external_text(str(outputs[-1]), validation, reveal_paths=reveal_paths)}\n"
    elif command == "citation-audit":
        target = Path(out) if out else default_reports_dir / "external_citation_audit.md"
        findings = citation_audit(papers, notes_data, claims, entries, themes, root=profile.root)
        outputs.append(write_text(target, citation_audit_report(findings), force=force))
        content = f"Wrote {_redact_external_text(str(outputs[-1]), validation, reveal_paths=reveal_paths)}\nFindings: {len(findings)}\n"
    elif command == "support-bundle":
        bundle = create_support_bundle(project=profile.name, root=validation.workspace_root, out_dir=out or None, force=force)
        content = (
            f"Wrote support bundle to {_redact_external_text(str(bundle.out_dir), validation, reveal_paths=reveal_paths)}\n"
            f"Project: {bundle.project}\n"
            f"Safe mode: {str(bundle.safe).lower()}\n"
            f"Files: {len(bundle.files_written)}\n"
        )
        outputs.append(Path(bundle.out_dir))
    elif command == "backup":
        manifest, backup_path = create_backup(
            root=profile.root,
            registry_path=profile.registry_path,
            bibtex_path=profile.bibtex_path,
            notes_dir=profile.notes_dir,
            themes_path=profile.themes_path,
            reports_dir=profile.reports_dir,
            profile=profile,
            include_reports=False,
            notes=notes,
        )
        content = f"Created backup {manifest.backup_id}\nPath: {_redact_external_text(str(backup_path), validation, reveal_paths=reveal_paths)}\nFiles: {len(manifest.included_files)}\n"
        outputs.append(backup_path)
        return ExternalRunResult(workspace=validation.workspace, command=command, content=content, outputs=outputs, findings=validation.findings, backup=manifest)
    else:  # pragma: no cover - guarded above
        raise AssertionError(command)

    content = _redact_external_text(content, validation, reveal_paths=reveal_paths)
    if out and command not in {"claims", "evidence-map", "citation-audit", "support-bundle"}:
        target = write_text(out, content, force=force)
        outputs.append(target)
        content = f"Wrote {_redact_external_text(str(target), validation, reveal_paths=reveal_paths)}\n"
    return ExternalRunResult(
        workspace=validation.workspace,
        command=command,
        content=content,
        outputs=outputs,
        findings=result_findings,
    )


def _redact_findings(findings: list[ValidationFinding], validation: ExternalValidation, *, reveal_paths: bool = False) -> list[ValidationFinding]:
    if reveal_paths:
        return findings
    return [
        ValidationFinding(
            severity=finding.severity,
            code=finding.code,
            message=_redact_external_text(finding.message, validation, reveal_paths=False),
            source=_redact_external_text(finding.source, validation, reveal_paths=False),
            identifier=_redact_external_text(finding.identifier, validation, reveal_paths=False),
            suggestion=_redact_external_text(finding.suggestion, validation, reveal_paths=False),
        )
        for finding in findings
    ]


def _redact_external_text(text: str, validation: ExternalValidation, *, reveal_paths: bool = False) -> str:
    if reveal_paths:
        return text
    redacted = text
    path_values = [validation.workspace.path, str(validation.workspace_root)]
    if validation.profile is not None:
        path_values.extend(
            [
                str(validation.profile.root),
                str(validation.profile.registry_path),
                str(validation.profile.bibtex_path),
                str(validation.profile.notes_dir),
                str(validation.profile.themes_path),
                str(validation.profile.reports_dir),
            ]
        )
    for value in sorted({path for path in path_values if path}, key=len, reverse=True):
        redacted = redacted.replace(value, REDACTED_EXTERNAL_PATH)
    return GENERAL_ABSOLUTE_PATH_RE.sub(REDACTED_EXTERNAL_PATH, redacted)


def _workspace_to_dict(workspace: ExternalWorkspace) -> dict[str, str]:
    return {
        "name": workspace.name,
        "path": workspace.path,
        "project": workspace.project,
        "description": workspace.description,
        "added_at": workspace.added_at,
    }
