"""Non-destructive sync planning and conflict reporting."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field as dataclass_field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .claims import collect_notes
from .importers import import_bibtex, import_generic_csv, import_ris, import_zotero_csv
from .io import load_json, write_json
from .registry import REGISTRY_FIELDS, display_authors, normalize_doi, normalize_title, paper_from_row, paper_to_row, save_registry
from .schema import Paper, PaperNote, dataclass_to_plain
from .tags import format_tags, parse_tags


SYNC_SOURCE_TYPES = {"zotero-csv", "bibtex", "generic-csv", "ris"}
UPDATE_FIELDS = ["title", "authors", "year", "journal", "doi", "url", "bibtex_key", "tags", "source_type"]
IDENTITY_FIELDS = {"title", "doi", "bibtex_key"}


@dataclass(slots=True)
class SyncSource:
    source_type: str
    path: str
    label: str = ""


@dataclass(slots=True)
class SyncTarget:
    target_type: str
    path: str
    project: str = ""


@dataclass(slots=True)
class SyncConflict:
    conflict_id: str
    conflict_type: str
    source: str
    target: str
    paper_id: str = ""
    field: str = ""
    registry_value: str = ""
    source_value: str = ""
    risk_level: str = "medium"
    reason: str = ""
    suggested_action: str = ""


@dataclass(slots=True)
class SyncAction:
    action_id: str
    action_type: str
    source: str
    target: str
    paper_id: str = ""
    field: str = ""
    old_value: str = ""
    new_value: str = ""
    risk_level: str = "low"
    requires_force: bool = False
    reason: str = ""
    paper: dict[str, str] = dataclass_field(default_factory=dict)


@dataclass(slots=True)
class SyncPlan:
    plan_id: str
    project: str
    source: SyncSource
    target: SyncTarget
    generated_at: str
    actions: list[SyncAction] = dataclass_field(default_factory=list)
    conflicts: list[SyncConflict] = dataclass_field(default_factory=list)
    warnings: list[str] = dataclass_field(default_factory=list)
    dry_run: bool = True


@dataclass(slots=True)
class SyncApplyResult:
    plan_id: str
    dry_run: bool = True
    applied_actions: list[str] = dataclass_field(default_factory=list)
    skipped_actions: list[str] = dataclass_field(default_factory=list)
    warnings: list[str] = dataclass_field(default_factory=list)
    backup_id: str = ""
    registry_path: str = ""


def load_source_papers(source_path: str | Path, source_type: str, *, project: str = "", mapping_path: str | Path | None = None) -> tuple[list[Paper], list[str]]:
    """Load import source data as registry-compatible Paper objects without writing."""

    source = Path(source_path)
    imported: list[Paper] = []
    warnings: list[str] = []
    if source_type == "zotero-csv":
        result = import_zotero_csv(source, imported, registry_path="", project=project, dry_run=True)
    elif source_type == "bibtex":
        result = import_bibtex(source, imported, registry_path="", project=project, dry_run=True)
    elif source_type == "generic-csv":
        if not mapping_path:
            raise ValueError("generic-csv sync planning requires --mapping")
        result = import_generic_csv(source, mapping_path, imported, registry_path="", project=project, dry_run=True)
    elif source_type == "ris":
        result = import_ris(source, imported, registry_path="", project=project, dry_run=True)
    else:
        raise ValueError(f"unsupported sync source type: {source_type}")
    warnings.extend(f"{finding.code}: {finding.message}" for finding in result.warnings)
    return result.registry_papers, warnings


def build_registry_sync_plan(
    *,
    existing_papers: list[Paper],
    source_papers: list[Paper],
    source: SyncSource,
    target: SyncTarget,
    project: str = "",
    warnings: Iterable[str] = (),
    now: datetime | None = None,
) -> SyncPlan:
    generated = now or datetime.now(timezone.utc)
    plan = SyncPlan(
        plan_id=_plan_id(source, target, generated),
        project=project,
        source=source,
        target=target,
        generated_at=generated.isoformat(),
        warnings=list(warnings),
    )
    action_counter = 1
    conflict_counter = 1
    for incoming in source_papers:
        matches = _matches(incoming, existing_papers)
        if len(matches) > 1:
            plan.conflicts.append(
                _conflict(
                    conflict_counter,
                    "ambiguous_match",
                    source,
                    target,
                    incoming.paper_id,
                    "",
                    "",
                    "",
                    "high",
                    f"Imported record matches multiple registry papers: {', '.join(sorted(p.paper_id for p in matches))}.",
                    "Review DOI, title, and BibTeX key manually before applying sync.",
                )
            )
            conflict_counter += 1
            continue
        if not matches:
            plan.actions.append(
                SyncAction(
                    action_id=f"A{action_counter:04d}",
                    action_type="create_paper",
                    source=source.path,
                    target=target.path,
                    paper_id=incoming.paper_id,
                    risk_level="low",
                    requires_force=True,
                    reason="Imported record does not match an existing registry row by paper_id, DOI, title, or BibTeX key.",
                    paper=paper_to_row(incoming),
                )
            )
            action_counter += 1
            continue
        existing = matches[0]
        before_actions = len(plan.actions)
        before_conflicts = len(plan.conflicts)
        new_conflicts = _identifier_conflicts(existing, incoming, source, target, conflict_counter)
        plan.conflicts.extend(new_conflicts)
        conflict_counter += len(new_conflicts)
        for field_name in UPDATE_FIELDS:
            current = _field_value(existing, field_name)
            incoming_value = _field_value(incoming, field_name)
            if _blank(incoming_value) or _same_field(field_name, current, incoming_value):
                continue
            if _blank(current):
                plan.actions.append(
                    SyncAction(
                        action_id=f"A{action_counter:04d}",
                        action_type="fill_blank_field",
                        source=source.path,
                        target=target.path,
                        paper_id=existing.paper_id,
                        field=field_name,
                        old_value=current,
                        new_value=incoming_value,
                        risk_level="low",
                        requires_force=False,
                        reason=f"Registry field {field_name} is blank and import source has a value.",
                    )
                )
                action_counter += 1
            elif field_name == "tags":
                plan.conflicts.append(
                    _conflict(
                        conflict_counter,
                        "tag_mismatch",
                        source,
                        target,
                        existing.paper_id,
                        field_name,
                        current,
                        incoming_value,
                        "medium",
                        "Registry tags differ from imported tags.",
                        "Review tags manually; the sync planner does not merge tag vocabularies automatically.",
                    )
                )
                conflict_counter += 1
            elif field_name not in IDENTITY_FIELDS:
                plan.conflicts.append(
                    _conflict(
                        conflict_counter,
                        "registry_field_differs_from_import",
                        source,
                        target,
                        existing.paper_id,
                        field_name,
                        current,
                        incoming_value,
                        "medium",
                        f"Registry field {field_name} differs from imported metadata.",
                        "Preserve the registry value unless you explicitly decide the import source is more accurate.",
                    )
                )
                conflict_counter += 1
        if before_actions == len(plan.actions) and before_conflicts == len(plan.conflicts):
            plan.actions.append(
                SyncAction(
                    action_id=f"A{action_counter:04d}",
                    action_type="skip_unchanged",
                    source=source.path,
                    target=target.path,
                    paper_id=existing.paper_id,
                    risk_level="low",
                    requires_force=False,
                    reason="Imported record already matches the current registry for supported sync fields.",
                )
            )
            action_counter += 1
    return plan


def build_note_sync_plan(
    *,
    local_notes_dir: str | Path,
    exported_notes_dir: str | Path,
    source: SyncSource,
    target: SyncTarget,
    project: str = "",
    now: datetime | None = None,
) -> SyncPlan:
    generated = now or datetime.now(timezone.utc)
    plan = SyncPlan(
        plan_id=_plan_id(source, target, generated),
        project=project,
        source=source,
        target=target,
        generated_at=generated.isoformat(),
    )
    local = _notes_by_id(local_notes_dir)
    exported = _notes_by_id(exported_notes_dir)
    conflict_counter = 1
    for paper_id in sorted(set(local) | set(exported)):
        local_note = local.get(paper_id)
        exported_note = exported.get(paper_id)
        if local_note is None:
            plan.conflicts.append(
                _conflict(conflict_counter, "note_exists_in_export_not_local", source, target, paper_id, "note_file", "", exported_note.source_path if exported_note else "", "medium", "An exported note exists without a matching local structured note.", "Review manually before copying into local notes.")
            )
            conflict_counter += 1
            continue
        if exported_note is None:
            plan.conflicts.append(
                _conflict(conflict_counter, "note_exists_locally_not_in_export", source, target, paper_id, "note_file", local_note.source_path, "", "low", "A local note is not present in the exported notes directory.", "This may be expected if the export is partial; regenerate the export if needed.")
            )
            conflict_counter += 1
            continue
        for field_name, local_value, exported_value in _note_comparisons(local_note, exported_note):
            if local_value != exported_value:
                plan.conflicts.append(
                    _conflict(
                        conflict_counter,
                        "local_note_differs_from_exported_note",
                        source,
                        target,
                        paper_id,
                        field_name,
                        local_value,
                        exported_value,
                        "medium",
                        f"Local note {field_name} differs from exported note.",
                        "Review both Markdown files manually; v1.3 does not auto-merge note content.",
                    )
                )
                conflict_counter += 1
    if not plan.conflicts:
        plan.actions.append(
            SyncAction(
                action_id="A0001",
                action_type="skip_unchanged",
                source=source.path,
                target=target.path,
                risk_level="low",
                reason="No parseable note differences were detected.",
            )
        )
    return plan


def build_obsidian_roundtrip_plan(
    *,
    local_notes_dir: str | Path,
    vault: str | Path,
    project: str = "",
    now: datetime | None = None,
) -> SyncPlan:
    vault_path = Path(vault)
    papers_dir = vault_path / "papers"
    source = SyncSource(source_type="obsidian-vault", path=str(vault_path), label="Obsidian export")
    target = SyncTarget(target_type="notes", path=str(local_notes_dir), project=project)
    plan = build_note_sync_plan(local_notes_dir=local_notes_dir, exported_notes_dir=papers_dir, source=source, target=target, project=project, now=now)
    if not papers_dir.exists():
        plan.warnings.append(f"Obsidian vault papers directory not found: {papers_dir}")
    return plan


def apply_registry_sync_plan(
    plan: SyncPlan,
    existing_papers: list[Paper],
    *,
    dry_run: bool = True,
    force: bool = False,
) -> tuple[list[Paper], SyncApplyResult]:
    result = SyncApplyResult(plan_id=plan.plan_id, dry_run=dry_run, registry_path=plan.target.path)
    high_risk = [conflict for conflict in plan.conflicts if conflict.risk_level == "high"]
    if high_risk and not force and not dry_run:
        raise PermissionError("sync apply refused high-risk conflicts without --force")
    if high_risk and dry_run:
        result.warnings.append(f"Plan contains {len(high_risk)} high-risk conflict(s); a real apply would require --force.")
    working = [paper_from_row(paper_to_row(paper)) for paper in existing_papers]
    by_id = {paper.paper_id: paper for paper in working}
    for action in plan.actions:
        if action.action_type == "skip_unchanged":
            result.skipped_actions.append(action.action_id)
            continue
        if action.action_type == "create_paper":
            if action.paper_id in by_id:
                result.skipped_actions.append(action.action_id)
                result.warnings.append(f"{action.action_id}: paper {action.paper_id} already exists; skipped create.")
                continue
            if not dry_run:
                paper = paper_from_row(action.paper)
                working.append(paper)
                by_id[paper.paper_id] = paper
            result.applied_actions.append(action.action_id)
            continue
        if action.action_type == "fill_blank_field":
            target = by_id.get(action.paper_id)
            if target is None:
                result.skipped_actions.append(action.action_id)
                result.warnings.append(f"{action.action_id}: target paper {action.paper_id} is missing; skipped field fill.")
                continue
            current = _field_value(target, action.field)
            if not _blank(current):
                result.skipped_actions.append(action.action_id)
                result.warnings.append(f"{action.action_id}: field {action.field} on {action.paper_id} is no longer blank; skipped.")
                continue
            if not dry_run:
                _set_field_value(target, action.field, action.new_value)
            result.applied_actions.append(action.action_id)
            continue
        result.skipped_actions.append(action.action_id)
        result.warnings.append(f"{action.action_id}: unsupported action type {action.action_type}; skipped.")
    return working, result


def save_sync_plan_json(plan: SyncPlan, path: str | Path, *, force: bool = True) -> Path:
    return write_json(path, sync_plan_to_dict(plan), force=force)


def load_sync_plan_json(path: str | Path) -> SyncPlan:
    data = load_json(path)
    return sync_plan_from_dict(data)


def write_registry_apply_result(papers: list[Paper], registry_path: str | Path) -> Path:
    return save_registry(papers, registry_path)


def sync_plan_report(plan: SyncPlan) -> str:
    action_counts = Counter(action.action_type for action in plan.actions)
    conflict_counts = Counter(conflict.conflict_type for conflict in plan.conflicts)
    lines = [
        "# Sync Plan",
        "",
        f"- Plan ID: {plan.plan_id}",
        f"- Project: {plan.project or 'default'}",
        f"- Source: {plan.source.source_type} ({plan.source.path})",
        f"- Target: {plan.target.target_type} ({plan.target.path})",
        f"- Dry run: {str(plan.dry_run).lower()}",
        f"- Actions: {len(plan.actions)}",
        f"- Conflicts: {len(plan.conflicts)}",
        "",
        "## Action Summary",
        "",
    ]
    if action_counts:
        for name, count in sorted(action_counts.items()):
            lines.append(f"- {name}: {count}")
    else:
        lines.append("- None.")
    lines.extend(["", "## Conflict Summary", ""])
    if conflict_counts:
        for name, count in sorted(conflict_counts.items()):
            lines.append(f"- {name}: {count}")
    else:
        lines.append("- None.")
    lines.extend(["", "## Actions", "", "| Action ID | Type | Paper ID | Field | Risk | Requires force | Reason |", "| --- | --- | --- | --- | --- | --- | --- |"])
    for action in plan.actions:
        lines.append(
            f"| {_esc(action.action_id)} | {_esc(action.action_type)} | {_esc(action.paper_id)} | {_esc(action.field)} | {_esc(action.risk_level)} | {str(action.requires_force).lower()} | {_esc(action.reason)} |"
        )
    if not plan.actions:
        lines.append("|  | none |  |  |  | false | No actions planned. |")
    lines.extend(["", "## Conflicts", "", conflict_table(plan.conflicts)])
    if plan.warnings:
        lines.extend(["", "## Warnings", ""])
        for warning in plan.warnings:
            lines.append(f"- {_esc(warning)}")
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            "This plan is local and non-destructive until applied. v1.3 does not auto-merge note conflicts or overwrite non-empty registry fields.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def conflict_report(plan: SyncPlan) -> str:
    lines = [
        "# Sync Conflicts",
        "",
        f"Plan ID: {plan.plan_id}",
        f"Conflicts: {len(plan.conflicts)}",
        "",
        conflict_table(plan.conflicts),
        "",
        "## Recommended Review",
        "",
        "- Resolve high-risk identifier conflicts before applying registry sync.",
        "- Compare note conflicts manually; v1.3 does not auto-merge note text.",
        "- Regenerate a new sync plan after manual edits.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def sync_apply_report(plan: SyncPlan, result: SyncApplyResult) -> str:
    lines = [
        "# Sync Apply Report",
        "",
        f"- Plan ID: {plan.plan_id}",
        f"- Dry run: {str(result.dry_run).lower()}",
        f"- Registry path: {result.registry_path}",
        f"- Backup ID: {result.backup_id or 'none'}",
        f"- Applied actions: {len(result.applied_actions)}",
        f"- Skipped actions: {len(result.skipped_actions)}",
        "",
        "## Applied Actions",
        "",
    ]
    lines.extend(f"- {action_id}" for action_id in result.applied_actions) if result.applied_actions else lines.append("- None.")
    lines.extend(["", "## Skipped Actions", ""])
    lines.extend(f"- {action_id}" for action_id in result.skipped_actions) if result.skipped_actions else lines.append("- None.")
    if result.warnings:
        lines.extend(["", "## Warnings", ""])
        for warning in result.warnings:
            lines.append(f"- {_esc(warning)}")
    return "\n".join(lines).rstrip() + "\n"


def conflict_table(conflicts: list[SyncConflict]) -> str:
    lines = ["| Conflict ID | Type | Paper ID | Field | Risk | Registry value | Source value | Suggested action |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for conflict in conflicts:
        lines.append(
            f"| {_esc(conflict.conflict_id)} | {_esc(conflict.conflict_type)} | {_esc(conflict.paper_id)} | {_esc(conflict.field)} | {_esc(conflict.risk_level)} | {_esc(conflict.registry_value)} | {_esc(conflict.source_value)} | {_esc(conflict.suggested_action)} |"
        )
    if not conflicts:
        lines.append("|  | none |  |  |  |  |  | No conflicts detected. |")
    return "\n".join(lines)


def sync_plan_to_dict(plan: SyncPlan) -> dict[str, object]:
    return dataclass_to_plain(plan)


def sync_plan_from_dict(data: dict[str, object]) -> SyncPlan:
    source_data = data.get("source", {})
    target_data = data.get("target", {})
    return SyncPlan(
        plan_id=str(data.get("plan_id", "")),
        project=str(data.get("project", "")),
        source=SyncSource(**source_data),
        target=SyncTarget(**target_data),
        generated_at=str(data.get("generated_at", "")),
        actions=[SyncAction(**item) for item in data.get("actions", [])],
        conflicts=[SyncConflict(**item) for item in data.get("conflicts", [])],
        warnings=[str(item) for item in data.get("warnings", [])],
        dry_run=bool(data.get("dry_run", True)),
    )


def _plan_id(source: SyncSource, target: SyncTarget, generated: datetime) -> str:
    stamp = generated.strftime("%Y%m%dT%H%M%SZ")
    source_label = Path(source.path).stem.replace(" ", "_") or source.source_type
    target_label = Path(target.path).stem.replace(" ", "_") or target.target_type
    return f"sync_{source.source_type.replace('-', '_')}_{source_label}_to_{target_label}_{stamp}"


def _matches(incoming: Paper, existing_papers: list[Paper]) -> list[Paper]:
    matches: dict[str, Paper] = {}
    incoming_doi = normalize_doi(incoming.doi)
    incoming_title = normalize_title(incoming.title)
    incoming_key = incoming.bibtex_key.strip()
    for paper in existing_papers:
        if incoming.paper_id and paper.paper_id == incoming.paper_id:
            matches[paper.paper_id] = paper
        if incoming_doi and normalize_doi(paper.doi) == incoming_doi:
            matches[paper.paper_id] = paper
        if incoming_title and normalize_title(paper.title) == incoming_title:
            matches[paper.paper_id] = paper
        if incoming_key and paper.bibtex_key.strip() == incoming_key:
            matches[paper.paper_id] = paper
    return list(matches.values())


def _identifier_conflicts(existing: Paper, incoming: Paper, source: SyncSource, target: SyncTarget, start: int) -> list[SyncConflict]:
    conflicts: list[SyncConflict] = []
    counter = start
    same_doi = normalize_doi(existing.doi) and normalize_doi(existing.doi) == normalize_doi(incoming.doi)
    same_title = normalize_title(existing.title) and normalize_title(existing.title) == normalize_title(incoming.title)
    same_key = existing.bibtex_key and existing.bibtex_key == incoming.bibtex_key
    if same_doi and incoming.title and existing.title and not same_title:
        conflicts.append(_conflict(counter, "same_doi_different_title", source, target, existing.paper_id, "title", existing.title, incoming.title, "high", "The same DOI is associated with different titles.", "Verify whether one title is abbreviated, stale, or incorrect before applying."))
        counter += 1
    if same_title and incoming.doi and existing.doi and normalize_doi(existing.doi) != normalize_doi(incoming.doi):
        conflicts.append(_conflict(counter, "same_title_different_doi", source, target, existing.paper_id, "doi", existing.doi, incoming.doi, "high", "The same normalized title is associated with different DOIs.", "Resolve DOI manually; do not guess."))
        counter += 1
    if same_key and incoming.doi and existing.doi and normalize_doi(existing.doi) != normalize_doi(incoming.doi):
        conflicts.append(_conflict(counter, "same_bibtex_key_different_doi", source, target, existing.paper_id, "bibtex_key", existing.doi, incoming.doi, "high", "The same BibTeX key points to different DOI values.", "Review BibTeX key ownership before applying."))
    return conflicts


def _conflict(index: int, conflict_type: str, source: SyncSource, target: SyncTarget, paper_id: str, field_name: str, registry_value: str, source_value: str, risk_level: str, reason: str, suggested_action: str) -> SyncConflict:
    return SyncConflict(
        conflict_id=f"C{index:04d}",
        conflict_type=conflict_type,
        source=source.path,
        target=target.path,
        paper_id=paper_id,
        field=field_name,
        registry_value=registry_value,
        source_value=source_value,
        risk_level=risk_level,
        reason=reason,
        suggested_action=suggested_action,
    )


def _field_value(paper: Paper, field_name: str) -> str:
    if field_name == "authors":
        return display_authors(paper.authors)
    if field_name == "tags":
        return format_tags(paper.tags)
    return str(getattr(paper, field_name, "") or "")


def _set_field_value(paper: Paper, field_name: str, value: str) -> None:
    if field_name == "tags":
        paper.tags = parse_tags(value)
    elif field_name == "authors":
        from .registry import parse_authors

        paper.authors = parse_authors(value)
    else:
        setattr(paper, field_name, value)


def _same_field(field_name: str, left: str, right: str) -> bool:
    if field_name == "doi":
        return normalize_doi(left) == normalize_doi(right)
    if field_name == "title":
        return normalize_title(left) == normalize_title(right)
    if field_name == "tags":
        return set(parse_tags(left)) == set(parse_tags(right))
    return (left or "").strip() == (right or "").strip()


def _blank(value: str) -> bool:
    return not str(value or "").strip()


def _notes_by_id(path: str | Path) -> dict[str, PaperNote]:
    target = Path(path)
    if not target.exists():
        return {}
    notes = collect_notes(target)
    return {note.paper_id: note for note in notes if note.paper_id}


def _note_comparisons(local: PaperNote, exported: PaperNote) -> list[tuple[str, str, str]]:
    return [
        ("citation_key", local.citation_key, exported.citation_key),
        ("reading_status", local.reading_status, exported.reading_status),
        ("tags", format_tags(local.tags), format_tags(exported.tags)),
        ("claim_count", str(len(local.claims)), str(len(exported.claims))),
        ("claim_texts", " || ".join(claim.claim_text for claim in local.claims), " || ".join(claim.claim_text for claim in exported.claims)),
        ("follow_up_actions", " || ".join(local.follow_up_actions), " || ".join(exported.follow_up_actions)),
        ("personal_reading_notes", local.personal_reading_notes.strip(), exported.personal_reading_notes.strip()),
    ]


def _esc(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ").strip()
