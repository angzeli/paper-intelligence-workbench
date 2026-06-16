"""Incremental rebuild planning and cache metadata.

The rebuild layer is deliberately conservative. It fingerprints local inputs and
records cache metadata so users can see what is stale before running heavier
commands. It does not rewrite reports, notes, registries, or indexes itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from . import __version__
from .index import build_index_records, default_index_path, index_status
from .io import load_json, write_json
from .paths import display_path


REBUILD_METADATA_SCHEMA = "paperwb-rebuild-metadata-v1"
REBUILD_TARGETS = (
    "claims",
    "evidence_map",
    "search_index",
    "report_outputs",
    "manuscript_qa",
    "dashboard",
)


@dataclass(slots=True)
class RebuildItem:
    target: str
    label: str
    current_hash: str
    previous_hash: str = ""
    stale: bool = False
    reason: str = ""
    source_paths: list[str] = field(default_factory=list)
    output_path: str = ""
    recommended_action: str = ""


@dataclass(slots=True)
class RebuildPlan:
    project_id: str
    root: str
    metadata_path: str
    generated_at: str
    metadata_exists: bool
    items: list[RebuildItem]
    warnings: list[str] = field(default_factory=list)

    @property
    def stale_items(self) -> list[RebuildItem]:
        return [item for item in self.items if item.stale]


@dataclass(slots=True)
class RebuildRunResult:
    project_id: str
    metadata_path: str
    refreshed_targets: list[str]
    force: bool
    plan: RebuildPlan


def default_rebuild_metadata_path(root: str | Path = ".") -> Path:
    return Path(root) / ".paperwb" / "rebuild_metadata.json"


def sha256_text(value: str) -> str:
    digest = hashlib.sha256()
    digest.update(value.encode("utf-8"))
    return digest.hexdigest()


def hash_file(path: str | Path) -> str:
    target = Path(path)
    digest = hashlib.sha256()
    with target.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iter_files(path: str | Path, *, suffixes: set[str] | None = None) -> list[Path]:
    target = Path(path)
    if not target.exists():
        return []
    if target.is_file():
        if suffixes and target.suffix.lower() not in suffixes:
            return []
        return [target]
    files: list[Path] = []
    for item in target.rglob("*"):
        if not item.is_file():
            continue
        if any(part in {".paperwb", "__pycache__", ".pytest_cache", ".ipynb_checkpoints"} for part in item.parts):
            continue
        if suffixes and item.suffix.lower() not in suffixes:
            continue
        files.append(item)
    return sorted(files, key=lambda value: value.as_posix())


def hash_path_set(paths: list[str | Path], *, root: str | Path = ".", suffixes: set[str] | None = None) -> str:
    base = Path(root)
    digest = hashlib.sha256()
    for path in paths:
        for file_path in _iter_files(path, suffixes=suffixes):
            try:
                label = file_path.resolve().relative_to(base.resolve()).as_posix()
            except ValueError:
                label = file_path.as_posix()
            digest.update(label.encode("utf-8"))
            digest.update(b"\0")
            digest.update(hash_file(file_path).encode("ascii"))
            digest.update(b"\0")
    return digest.hexdigest()


def _load_metadata(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = load_json(path)
    except (json.JSONDecodeError, OSError, ValueError):
        return {"_corrupt": True}
    return data if isinstance(data, dict) else {"_invalid": True}


def _target_metadata(metadata: dict, target: str) -> dict:
    targets = metadata.get("targets", {})
    if not isinstance(targets, dict):
        return {}
    value = targets.get(target, {})
    return value if isinstance(value, dict) else {}


def _relative_sources(paths: list[str | Path], *, root: str | Path) -> list[str]:
    base = Path(root)
    labels: list[str] = []
    for path in paths:
        target = Path(path)
        if target.exists():
            labels.append(display_path(target, base_path=base))
    return sorted(dict.fromkeys(labels))


def _mark_item(
    *,
    target: str,
    label: str,
    current_hash: str,
    metadata: dict,
    metadata_exists: bool,
    source_paths: list[str | Path],
    root: str | Path,
    output_path: str | Path,
    recommended_action: str,
    initial_reason: str = "No rebuild metadata recorded.",
) -> RebuildItem:
    previous_hash = str(_target_metadata(metadata, target).get("content_hash", ""))
    stale = False
    reason = "Inputs unchanged since the last recorded rebuild."
    if not metadata_exists:
        stale = True
        reason = initial_reason
    elif not previous_hash:
        stale = True
        reason = "No prior fingerprint exists for this target."
    elif previous_hash != current_hash:
        stale = True
        reason = "Input fingerprints changed since the last recorded rebuild."
    return RebuildItem(
        target=target,
        label=label,
        current_hash=current_hash,
        previous_hash=previous_hash,
        stale=stale,
        reason=reason,
        source_paths=_relative_sources(source_paths, root=root),
        output_path=display_path(output_path, base_path=root) if output_path else "",
        recommended_action=recommended_action,
    )


def _project_command(project_id: str, *parts: str) -> str:
    command = ["paperwb", *parts]
    if project_id != "default":
        command.extend(["--project", project_id])
    return " ".join(command)


def _command_path(path: str | Path) -> str:
    return display_path(path, base_path=Path.cwd())


def build_rebuild_plan(
    *,
    project_id: str,
    root: str | Path,
    registry_path: str | Path,
    bibtex_path: str | Path,
    notes_dir: str | Path,
    themes_path: str | Path,
    reports_dir: str | Path,
    text_dir: str | Path | None = None,
    include_text: bool = False,
    metadata_path: str | Path | None = None,
) -> RebuildPlan:
    root_path = Path(root)
    registry = Path(registry_path)
    bibtex = Path(bibtex_path)
    notes = Path(notes_dir)
    themes = Path(themes_path)
    reports = Path(reports_dir)
    text = Path(text_dir) if text_dir else root_path / "text"
    metadata_file = Path(metadata_path) if metadata_path else default_rebuild_metadata_path(root_path)
    metadata = _load_metadata(metadata_file)
    metadata_exists = metadata_file.exists() and not metadata.get("_corrupt") and not metadata.get("_invalid")
    warnings: list[str] = []
    if metadata.get("_corrupt"):
        warnings.append("Rebuild metadata could not be parsed; all rebuild targets are treated as stale.")
    if metadata.get("_invalid"):
        warnings.append("Rebuild metadata has an unexpected shape; all rebuild targets are treated as stale.")
    if metadata.get("schema") and metadata.get("schema") != REBUILD_METADATA_SCHEMA:
        warnings.append("Rebuild metadata schema differs from this release; targets may be stale.")

    core_inputs = [registry, bibtex, notes, themes]
    claims_hash = hash_path_set([notes], root=root_path, suffixes={".md"})
    evidence_hash = hash_path_set(core_inputs, root=root_path, suffixes={".csv", ".bib", ".md", ".json"})
    reports_hash = hash_path_set(core_inputs, root=root_path, suffixes={".csv", ".bib", ".md", ".json"})
    dashboard_hash = hash_path_set([registry, bibtex, notes, themes, root_path / "rules.json"], root=root_path, suffixes={".csv", ".bib", ".md", ".json"})
    draft_paths = [root_path / "drafts"]
    if root_path.name != "drafts":
        draft_paths.append(root_path.parent / "drafts")
    manuscript_hash = hash_path_set([*draft_paths, *core_inputs], root=root_path, suffixes={".md", ".csv", ".bib", ".json"})

    index_records = build_index_records(
        project_id=project_id,
        registry_path=registry,
        bibtex_path=bibtex,
        notes_dir=notes,
        themes_path=themes,
        text_dir=text,
        include_text=include_text,
    )
    index_hash = sha256_text("\n".join(f"{record.record_id}\t{record.content_hash}" for record in index_records))
    index_file = default_index_path(root_path)
    status = index_status(index_file, project_id=project_id, current_records=index_records)

    items = [
        _mark_item(
            target="claims",
            label="Claim extraction inputs",
            current_hash=claims_hash,
            metadata=metadata,
            metadata_exists=metadata_exists,
            source_paths=[notes],
            root=root_path,
            output_path=reports / "claims.csv",
            recommended_action=_project_command(project_id, "claims", "--out", _command_path(reports / "claims.csv")),
        ),
        _mark_item(
            target="evidence_map",
            label="Evidence map inputs",
            current_hash=evidence_hash,
            metadata=metadata,
            metadata_exists=metadata_exists,
            source_paths=core_inputs,
            root=root_path,
            output_path=reports / "evidence_map.md",
            recommended_action=_project_command(project_id, "report", "evidence-map", "--out", _command_path(reports / "evidence_map.md")),
        ),
        _mark_item(
            target="search_index",
            label="Search index records",
            current_hash=index_hash,
            metadata=metadata,
            metadata_exists=metadata_exists,
            source_paths=[*core_inputs, text] if include_text else core_inputs,
            root=root_path,
            output_path=index_file,
            recommended_action=_project_command(project_id, "index", "rebuild"),
            initial_reason="Search index metadata has not been recorded.",
        ),
        _mark_item(
            target="report_outputs",
            label="Core report inputs",
            current_hash=reports_hash,
            metadata=metadata,
            metadata_exists=metadata_exists,
            source_paths=core_inputs,
            root=root_path,
            output_path=reports,
            recommended_action=_project_command(project_id, "report", "all", "--reports-dir", _command_path(reports)),
        ),
        _mark_item(
            target="manuscript_qa",
            label="Draft/manuscript QA inputs",
            current_hash=manuscript_hash,
            metadata=metadata,
            metadata_exists=metadata_exists,
            source_paths=[*draft_paths, *core_inputs],
            root=root_path,
            output_path=reports / "manuscript_qa.md",
            recommended_action="Run `paperwb manuscript qa DRAFT --project PROJECT --out REPORT` for each active draft.",
        ),
        _mark_item(
            target="dashboard",
            label="Dashboard inputs",
            current_hash=dashboard_hash,
            metadata=metadata,
            metadata_exists=metadata_exists,
            source_paths=[registry, bibtex, notes, themes],
            root=root_path,
            output_path=reports / "dashboard.md",
            recommended_action=_project_command(project_id, "dashboard", "--out", _command_path(reports / "dashboard.md")),
        ),
    ]
    if not index_file.exists():
        for item in items:
            if item.target == "search_index":
                item.stale = True
                item.reason = "Search index file is missing."
    elif status.warnings:
        for item in items:
            if item.target == "search_index":
                item.stale = True
                item.reason = "; ".join(status.warnings)
    if not any(Path(path).exists() for path in draft_paths):
        for item in items:
            if item.target == "manuscript_qa" and metadata_exists and not item.previous_hash:
                item.stale = False
                item.reason = "No draft or manuscript files found."
    return RebuildPlan(
        project_id=project_id,
        root=str(root_path),
        metadata_path=str(metadata_file),
        generated_at=datetime.now(timezone.utc).isoformat(),
        metadata_exists=metadata_exists,
        items=items,
        warnings=warnings,
    )


def run_rebuild_metadata(plan: RebuildPlan, *, force: bool = False) -> RebuildRunResult:
    metadata_path = Path(plan.metadata_path)
    current = _load_metadata(metadata_path)
    if current.get("_corrupt") or current.get("_invalid"):
        current = {}
    targets = current.get("targets", {})
    if not isinstance(targets, dict):
        targets = {}
    refreshed: list[str] = []
    now = datetime.now(timezone.utc).isoformat()
    for item in plan.items:
        if force or item.stale:
            targets[item.target] = {
                "content_hash": item.current_hash,
                "updated_at": now,
                "label": item.label,
            }
            refreshed.append(item.target)
    payload = {
        "schema": REBUILD_METADATA_SCHEMA,
        "tool_version": __version__,
        "project_id": plan.project_id,
        "updated_at": now,
        "targets": targets,
    }
    write_json(metadata_path, payload)
    return RebuildRunResult(
        project_id=plan.project_id,
        metadata_path=str(metadata_path),
        refreshed_targets=refreshed,
        force=force,
        plan=plan,
    )


def rebuild_plan_markdown(plan: RebuildPlan) -> str:
    stale_count = len(plan.stale_items)
    lines = [
        f"# Incremental Rebuild Plan v{__version__}",
        "",
        f"- Project: `{plan.project_id}`",
        f"- Generated at: `{plan.generated_at}`",
        f"- Metadata path: `{display_path(plan.metadata_path, base_path=plan.root)}`",
        f"- Metadata exists: `{str(plan.metadata_exists).lower()}`",
        f"- Stale targets: {stale_count} / {len(plan.items)}",
        "",
    ]
    if plan.warnings:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in plan.warnings)
        lines.append("")
    lines.extend(
        [
            "## Target Summary",
            "",
            "| Target | Status | Reason | Output |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in plan.items:
        status = "stale" if item.stale else "current"
        lines.append(f"| `{item.target}` | {status} | {item.reason} | `{item.output_path}` |")
    lines.extend(["", "## Recommended Actions", ""])
    for item in plan.items:
        if item.stale:
            lines.append(f"- `{item.target}`: {item.recommended_action}")
    if not plan.stale_items:
        lines.append("- No rebuild actions are currently recommended.")
    lines.extend(["", "## Source Coverage", ""])
    for item in plan.items:
        sources = ", ".join(f"`{source}`" for source in item.source_paths) if item.source_paths else "No existing source paths found."
        lines.append(f"- `{item.target}`: {sources}")
    return "\n".join(lines).rstrip() + "\n"


def rebuild_status_markdown(plan: RebuildPlan) -> str:
    lines = [
        f"# Rebuild Status v{__version__}",
        "",
        f"- Project: `{plan.project_id}`",
        f"- Metadata path: `{display_path(plan.metadata_path, base_path=plan.root)}`",
        f"- Metadata exists: `{str(plan.metadata_exists).lower()}`",
        f"- Current targets: {len(plan.items) - len(plan.stale_items)}",
        f"- Stale targets: {len(plan.stale_items)}",
        "",
    ]
    if plan.stale_items:
        lines.extend(["## Stale Targets", ""])
        for item in plan.stale_items:
            lines.append(f"- `{item.target}`: {item.reason}")
    else:
        lines.extend(["## Stale Targets", "", "- None."])
    if plan.warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in plan.warnings)
    return "\n".join(lines).rstrip() + "\n"


def rebuild_run_markdown(result: RebuildRunResult) -> str:
    lines = [
        f"# Rebuild Metadata Run v{__version__}",
        "",
        f"- Project: `{result.project_id}`",
        f"- Metadata path: `{display_path(result.metadata_path, base_path=result.plan.root)}`",
        f"- Force refresh: `{str(result.force).lower()}`",
        f"- Refreshed targets: {len(result.refreshed_targets)}",
        "",
        "## Refreshed Targets",
        "",
    ]
    if result.refreshed_targets:
        lines.extend(f"- `{target}`" for target in result.refreshed_targets)
    else:
        lines.append("- None. Existing fingerprints were already current.")
    lines.extend(
        [
            "",
            "## Important Boundary",
            "",
            "This command updated rebuild metadata only. It did not rewrite notes, registry rows, BibTeX entries, reports, search indexes, or user drafts.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"
