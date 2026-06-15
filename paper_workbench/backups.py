"""Local backup snapshot and non-destructive restore planning."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil

from . import __version__
from .errors import format_error_message
from .io import load_json, write_json, write_text
from .projects import profile_config
from .schema import ProjectProfile
from .files import sha256_file


@dataclass(slots=True)
class BackupFile:
    source_path: str
    backup_path: str
    sha256: str = ""
    size_bytes: int = 0


@dataclass(slots=True)
class BackupManifest:
    backup_id: str
    created_at: str
    project: str = ""
    tool_version: str = __version__
    included_files: list[BackupFile] = field(default_factory=list)
    excluded_files: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass(slots=True)
class RestorePlan:
    backup_id: str
    project: str = ""
    files_to_restore: list[BackupFile] = field(default_factory=list)
    files_to_overwrite: list[str] = field(default_factory=list)
    missing_backup_files: list[str] = field(default_factory=list)
    target_root: str = ""
    dry_run: bool = True
    pre_restore_backup_id: str = ""


def default_backups_dir(root: str | Path = ".") -> Path:
    return Path(root) / "backups"


def _utc_id(project: str = "") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    suffix = project or "default"
    return f"{stamp}_{suffix}"


def _source_paths_for_backup(
    *,
    root: str | Path,
    registry_path: str | Path,
    bibtex_path: str | Path,
    notes_dir: str | Path,
    themes_path: str | Path,
    reports_dir: str | Path | None = None,
    profile: ProjectProfile | None = None,
    include_reports: bool = False,
) -> tuple[list[Path], list[str]]:
    sources: list[Path] = []
    excluded: list[str] = []
    for source in (Path(registry_path), Path(bibtex_path), Path(themes_path)):
        if source.exists() and source.is_file():
            sources.append(source)
    if Path(notes_dir).exists():
        sources.extend(sorted(path for path in Path(notes_dir).rglob("*") if path.is_file()))
    if profile is not None:
        config = Path(profile.root) / "project.json"
        if config.exists():
            sources.append(config)
    if include_reports and reports_dir and Path(reports_dir).exists():
        sources.extend(sorted(path for path in Path(reports_dir).rglob("*.md") if path.is_file()))
    elif reports_dir and Path(reports_dir).exists():
        excluded.append(f"{_workspace_relative(Path(reports_dir), Path(root))} (reports excluded by default)")
    for path in sorted(Path(root).glob("**/*")):
        if path.is_file() and (".paperwb" in path.parts or path.suffix.lower() in {".sqlite", ".db", ".pdf"}):
            excluded.append(_workspace_relative(path, Path(root)))
    return sources, excluded


def _workspace_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.name


def create_backup(
    *,
    root: str | Path = ".",
    registry_path: str | Path,
    bibtex_path: str | Path,
    notes_dir: str | Path,
    themes_path: str | Path,
    reports_dir: str | Path | None = None,
    profile: ProjectProfile | None = None,
    backups_dir: str | Path | None = None,
    include_reports: bool = False,
    backup_id: str = "",
    notes: str = "",
) -> tuple[BackupManifest, Path]:
    root_path = Path(root).resolve(strict=False)
    project = profile.name if profile else ""
    resolved_id = backup_id or _utc_id(project)
    base = Path(backups_dir) if backups_dir else default_backups_dir(root_path)
    target = base / resolved_id
    if target.exists():
        raise FileExistsError(f"backup already exists: {target}")
    target.mkdir(parents=True, exist_ok=False)
    sources, excluded = _source_paths_for_backup(
        root=root_path,
        registry_path=registry_path,
        bibtex_path=bibtex_path,
        notes_dir=notes_dir,
        themes_path=themes_path,
        reports_dir=reports_dir,
        profile=profile,
        include_reports=include_reports,
    )
    included: list[BackupFile] = []
    for source in sources:
        if source.suffix.lower() == ".pdf" or ".paperwb" in source.parts:
            excluded.append(str(source))
            continue
        rel = _workspace_relative(source, root_path)
        destination = target / "files" / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        included.append(
            BackupFile(
                source_path=rel,
                backup_path=destination.relative_to(target).as_posix(),
                sha256=sha256_file(destination),
                size_bytes=destination.stat().st_size,
            )
        )
    if profile is not None:
        write_json(target / "project_profile.json", profile_config(profile), force=True)
    manifest = BackupManifest(
        backup_id=resolved_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        project=project,
        included_files=included,
        excluded_files=sorted(set(excluded)),
        notes=notes,
    )
    write_json(target / "manifest.json", _manifest_to_dict(manifest), force=True)
    write_text(target / "backup_summary.md", backup_manifest_report(manifest), force=True)
    return manifest, target


def list_backups(root: str | Path = ".", *, project: str = "", backups_dir: str | Path | None = None) -> list[BackupManifest]:
    base = Path(backups_dir) if backups_dir else default_backups_dir(root)
    if not base.exists():
        return []
    manifests: list[BackupManifest] = []
    for manifest_path in sorted(base.glob("*/manifest.json")):
        manifest = load_backup_manifest(manifest_path.parent)
        if project and manifest.project != project:
            continue
        manifests.append(manifest)
    return manifests


def load_backup_manifest(backup_path: str | Path) -> BackupManifest:
    path = Path(backup_path)
    manifest_path = path / "manifest.json"
    try:
        data = load_json(manifest_path)
    except json.JSONDecodeError as exc:
        raise ValueError(
            format_error_message(
                what="Backup manifest is not valid JSON.",
                where=str(manifest_path),
                why="Restore is blocked because the tool cannot know which files belong to the backup.",
                next_step=f"Inspect or recreate the backup. Parser detail: {exc.msg}",
            )
        ) from exc
    if not isinstance(data, dict):
        raise ValueError(
            format_error_message(
                what="Backup manifest has the wrong shape.",
                where=str(manifest_path),
                why="Restore needs a JSON object with backup metadata and included files.",
                next_step="Recreate the backup or repair manifest.json manually.",
            )
        )
    return _manifest_from_dict(data)


def find_backup(root: str | Path, backup_id: str, *, backups_dir: str | Path | None = None) -> Path:
    base = Path(backups_dir) if backups_dir else default_backups_dir(root)
    target = base / backup_id
    if not (target / "manifest.json").exists():
        raise FileNotFoundError(
            format_error_message(
                what="Backup not found.",
                where=str(target),
                why="Restore and inspection commands need a local backup manifest before they can proceed.",
                next_step="Run `paperwb backup list` with the same --project/--backups-dir options, or create a backup first.",
            )
        )
    return target


def plan_restore(
    *,
    root: str | Path,
    backup_id: str,
    backups_dir: str | Path | None = None,
    project: str = "",
    dry_run: bool = True,
) -> RestorePlan:
    root_path = Path(root).resolve(strict=False)
    backup_path = find_backup(root_path, backup_id, backups_dir=backups_dir)
    manifest = load_backup_manifest(backup_path)
    if project and manifest.project and project != manifest.project:
        raise ValueError(
            format_error_message(
                what="Backup project does not match the requested project.",
                where=str(backup_path),
                why=f"Backup {backup_id} belongs to {manifest.project}, but the command requested {project}.",
                next_step="Use the matching --project value, omit --project for a default-workflow backup, or choose a different backup ID.",
            )
        )
    missing: list[str] = []
    overwrites: list[str] = []
    files: list[BackupFile] = []
    for item in manifest.included_files:
        source = backup_path / item.backup_path
        target = root_path / item.source_path
        if not source.exists():
            missing.append(item.backup_path)
            continue
        files.append(item)
        if target.exists():
            overwrites.append(item.source_path)
    return RestorePlan(
        backup_id=backup_id,
        project=manifest.project,
        files_to_restore=files,
        files_to_overwrite=overwrites,
        missing_backup_files=missing,
        target_root=str(root_path),
        dry_run=dry_run,
    )


def restore_backup(
    *,
    root: str | Path,
    backup_id: str,
    registry_path: str | Path,
    bibtex_path: str | Path,
    notes_dir: str | Path,
    themes_path: str | Path,
    reports_dir: str | Path | None = None,
    profile: ProjectProfile | None = None,
    backups_dir: str | Path | None = None,
    force: bool = False,
    create_pre_restore_backup: bool = True,
) -> RestorePlan:
    if not force:
        return plan_restore(root=root, backup_id=backup_id, backups_dir=backups_dir, project=profile.name if profile else "", dry_run=True)
    root_path = Path(root).resolve(strict=False)
    plan = plan_restore(root=root_path, backup_id=backup_id, backups_dir=backups_dir, project=profile.name if profile else "", dry_run=False)
    if plan.missing_backup_files:
        raise FileNotFoundError(
            format_error_message(
                what="Backup is missing files listed in its manifest.",
                where=str(find_backup(root_path, backup_id, backups_dir=backups_dir)),
                why="Restore is blocked because applying an incomplete backup could leave the workspace partially restored.",
                next_step=f"Inspect or recreate the backup. Missing files: {', '.join(plan.missing_backup_files)}.",
            )
        )
    pre_restore_backup_id = ""
    if create_pre_restore_backup:
        manifest, _ = create_backup(
            root=root_path,
            registry_path=registry_path,
            bibtex_path=bibtex_path,
            notes_dir=notes_dir,
            themes_path=themes_path,
            reports_dir=reports_dir,
            profile=profile,
            backups_dir=backups_dir,
            notes=f"Pre-restore backup before restoring {backup_id}",
        )
        pre_restore_backup_id = manifest.backup_id
    backup_path = find_backup(root_path, backup_id, backups_dir=backups_dir)
    for item in plan.files_to_restore:
        source = backup_path / item.backup_path
        target = root_path / item.source_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    plan.pre_restore_backup_id = pre_restore_backup_id
    return plan


def backup_manifest_report(manifest: BackupManifest) -> str:
    lines = [
        f"# Backup Manifest Demo v{__version__}",
        "",
        f"Backup ID: {manifest.backup_id}",
        f"Created at: {manifest.created_at}",
        f"Project: {manifest.project or 'default data workflow'}",
        f"Tool version: {manifest.tool_version}",
        f"Files included: {len(manifest.included_files)}",
        f"Files excluded: {len(manifest.excluded_files)}",
        f"Notes: {manifest.notes}",
        "",
        "## Included Files",
        "",
    ]
    if not manifest.included_files:
        lines.append("- None.")
    for item in manifest.included_files:
        lines.append(f"- `{item.source_path}` ({item.size_bytes} bytes, sha256 `{item.sha256[:12]}`)")
    if manifest.excluded_files:
        lines.extend(["", "## Excluded Files", ""])
        lines.extend(f"- `{item}`" for item in manifest.excluded_files[:50])
    return "\n".join(lines).rstrip() + "\n"


def restore_plan_report(plan: RestorePlan) -> str:
    lines = [
        f"# Restore Dry Run v{__version__}",
        "",
        f"Backup ID: {plan.backup_id}",
        f"Project: {plan.project or 'default data workflow'}",
        f"Target root: {_portable_path(plan.target_root)}",
        f"Dry run: {str(plan.dry_run).lower()}",
        f"Files to restore: {len(plan.files_to_restore)}",
        f"Files that would be overwritten: {len(plan.files_to_overwrite)}",
        f"Missing files inside backup: {len(plan.missing_backup_files)}",
        f"Pre-restore backup: {plan.pre_restore_backup_id or 'not created'}",
        "",
        "## Files To Restore",
        "",
    ]
    if not plan.files_to_restore:
        lines.append("- None.")
    for item in plan.files_to_restore:
        marker = "overwrite" if item.source_path in plan.files_to_overwrite else "create"
        lines.append(f"- `{item.source_path}` ({marker})")
    if plan.missing_backup_files:
        lines.extend(["", "## Missing Backup Files", ""])
        lines.extend(f"- `{item}`" for item in plan.missing_backup_files)
    return "\n".join(lines).rstrip() + "\n"


def _manifest_to_dict(manifest: BackupManifest) -> dict[str, object]:
    return {
        "backup_id": manifest.backup_id,
        "created_at": manifest.created_at,
        "project": manifest.project,
        "tool_version": manifest.tool_version,
        "included_files": [
            {
                "source_path": item.source_path,
                "backup_path": item.backup_path,
                "sha256": item.sha256,
                "size_bytes": item.size_bytes,
            }
            for item in manifest.included_files
        ],
        "excluded_files": manifest.excluded_files,
        "notes": manifest.notes,
    }


def _manifest_from_dict(data: dict) -> BackupManifest:
    return BackupManifest(
        backup_id=str(data.get("backup_id", "")),
        created_at=str(data.get("created_at", "")),
        project=str(data.get("project", "")),
        tool_version=str(data.get("tool_version", "")) or __version__,
        included_files=[BackupFile(**item) for item in data.get("included_files", [])],
        excluded_files=list(data.get("excluded_files", [])),
        notes=str(data.get("notes", "")),
    )


def _portable_path(value: str | Path) -> str:
    path = Path(value)
    try:
        return path.resolve(strict=False).relative_to(Path.cwd().resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()
