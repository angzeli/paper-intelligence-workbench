"""Non-destructive legacy-data to project-profile migration planning."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import shutil

from .backups import BackupManifest, create_backup
from .io import write_json, write_text
from .paths import default_bibtex_path, default_notes_dir, default_registry_path, default_reports_dir, default_themes_path, project_root
from .projects import PROJECT_CONFIG, project_dir


@dataclass(slots=True)
class MigrationCopyOperation:
    source_path: str
    target_path: str
    kind: str = "file"


@dataclass(slots=True)
class MigrationPlan:
    source: str
    to_project: str
    root: str
    project_root: str
    operations: list[MigrationCopyOperation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    dry_run: bool = True
    backup_id: str = ""


def plan_legacy_migration(*, root: str | Path = ".", to_project: str) -> MigrationPlan:
    root_path = project_root(root)
    target_root = project_dir(to_project, root_path)
    operations: list[MigrationCopyOperation] = []
    warnings: list[str] = []
    conflicts: list[str] = []
    if target_root.exists() and any(target_root.iterdir()):
        conflicts.append(f"Target project already exists and is not empty: {target_root}")

    registry = default_registry_path(root_path)
    if registry.exists():
        operations.append(_op(registry, target_root / "registry.csv", root_path))
    else:
        warnings.append(f"Legacy registry not found: {registry}")

    bibtex = default_bibtex_path(root_path)
    if bibtex.exists():
        operations.append(_op(bibtex, target_root / "bibtex" / "library.bib", root_path))
    else:
        for source in sorted((root_path / "data" / "bibtex").glob("*.bib")):
            operations.append(_op(source, target_root / "bibtex" / source.name, root_path))
        if not any(operation.target_path.startswith(f"projects/{to_project}/bibtex/") for operation in operations):
            warnings.append(f"No legacy BibTeX files found under {root_path / 'data' / 'bibtex'}")

    themes = default_themes_path(root_path)
    if themes.exists():
        operations.append(_op(themes, target_root / "themes.json", root_path))
    else:
        warnings.append(f"Legacy themes file not found: {themes}")

    notes = default_notes_dir(root_path)
    if notes.exists():
        for source in sorted(path for path in notes.rglob("*") if path.is_file()):
            operations.append(_op(source, target_root / "notes" / source.relative_to(notes), root_path))
    else:
        warnings.append(f"Legacy notes folder not found: {notes}")

    reports = default_reports_dir(root_path)
    if reports.exists():
        warnings.append(f"Legacy reports detected but not copied by default: {reports}")
    config_target = target_root / PROJECT_CONFIG
    operations.append(_op_marker(config_target, root_path))
    for operation in operations:
        target = root_path / operation.target_path
        if target.exists():
            conflicts.append(f"Target path already exists: {operation.target_path}")
    return MigrationPlan(
        source="legacy",
        to_project=to_project,
        root=str(root_path),
        project_root=_rel(target_root, root_path),
        operations=operations,
        warnings=warnings,
        conflicts=conflicts,
    )


def run_legacy_migration(
    *,
    root: str | Path = ".",
    to_project: str,
    dry_run: bool = True,
    force: bool = False,
    create_backup_first: bool = True,
) -> tuple[MigrationPlan, BackupManifest | None]:
    plan = plan_legacy_migration(root=root, to_project=to_project)
    plan.dry_run = dry_run or not force
    if plan.dry_run:
        return plan, None
    if plan.conflicts:
        raise FileExistsError("; ".join(plan.conflicts))
    root_path = Path(plan.root)
    backup: BackupManifest | None = None
    if create_backup_first:
        backup, _ = create_backup(
            root=root_path,
            registry_path=default_registry_path(root_path),
            bibtex_path=default_bibtex_path(root_path),
            notes_dir=default_notes_dir(root_path),
            themes_path=default_themes_path(root_path),
            reports_dir=default_reports_dir(root_path),
            notes=f"Pre-migration backup before creating project {to_project}",
        )
        plan.backup_id = backup.backup_id
    target_root = root_path / plan.project_root
    (target_root / "bibtex").mkdir(parents=True, exist_ok=True)
    (target_root / "notes").mkdir(parents=True, exist_ok=True)
    (target_root / "papers").mkdir(parents=True, exist_ok=True)
    (target_root / "text").mkdir(parents=True, exist_ok=True)
    (target_root / "reports").mkdir(parents=True, exist_ok=True)
    for operation in plan.operations:
        target = root_path / operation.target_path
        if operation.kind == "project_config":
            write_json(
                target,
                {
                    "name": to_project,
                    "description": "Migrated from legacy data/ workflow",
                    "is_default": False,
                    "registry_path": "registry.csv",
                    "bibtex_path": "bibtex/library.bib",
                    "notes_dir": "notes",
                    "themes_path": "themes.json",
                    "reports_dir": "reports",
                },
                force=False,
            )
            continue
        source = root_path / operation.source_path
        if not source.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    plan.dry_run = False
    return plan, backup


def migration_plan_report(plan: MigrationPlan) -> str:
    lines = [
        "# Migration Plan v0.9",
        "",
        "This is a non-destructive plan. Migration copies files into a new project and preserves the legacy `data/` workflow.",
        "",
        f"Source: {plan.source}",
        f"Target project: {plan.to_project}",
        f"Project root: {plan.project_root}",
        f"Dry run: {str(plan.dry_run).lower()}",
        f"Operations: {len(plan.operations)}",
        f"Warnings: {len(plan.warnings)}",
        f"Conflicts: {len(plan.conflicts)}",
        f"Pre-migration backup: {plan.backup_id or 'not created'}",
        "",
        "## Copy Operations",
        "",
    ]
    if not plan.operations:
        lines.append("- None.")
    for operation in plan.operations:
        if operation.kind == "project_config":
            lines.append(f"- create project config `{operation.target_path}`")
        else:
            lines.append(f"- copy `{operation.source_path}` -> `{operation.target_path}`")
    if plan.warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in plan.warnings)
    if plan.conflicts:
        lines.extend(["", "## Conflicts", ""])
        lines.extend(f"- {conflict}" for conflict in plan.conflicts)
    lines.extend(
        [
            "",
            "## Safety",
            "",
            "- The legacy source files are copied, not moved.",
            "- Existing target projects are treated as conflicts.",
            "- Run with `--dry-run` first; use `--force` only after reviewing this plan.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _op(source: Path, target: Path, root: Path) -> MigrationCopyOperation:
    return MigrationCopyOperation(source_path=_rel(source, root), target_path=_rel(target, root))


def _op_marker(target: Path, root: Path) -> MigrationCopyOperation:
    return MigrationCopyOperation(source_path="", target_path=_rel(target, root), kind="project_config")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()
