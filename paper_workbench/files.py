"""Local file scanning, linking, and audit helpers."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
import hashlib
from pathlib import Path
import re

from .io import read_csv_rows, write_csv_rows
from .registry import load_registry, save_registry
from .schema import LocalFileRecord, Paper


LOCAL_FILE_FIELDS = [
    "paper_id",
    "file_id",
    "relative_path",
    "file_type",
    "size_bytes",
    "sha256",
    "added_date",
    "linked_registry_status",
    "notes",
    "text_sidecar_path",
    "extracted_metadata_status",
]
SUPPORTED_FILE_TYPES = {"pdf", "txt", "md", "bib", "ris", "csv"}
SCAN_DIRS = ("papers", "text", "notes", "bibtex")
DEFAULT_WORKSPACE_SCAN_DIRS = ("data/papers", "data/text", "data/notes", "data/bibtex")
LARGE_FILE_BYTES = 50 * 1024 * 1024


@dataclass(slots=True)
class FileScanResult:
    root: str
    file_registry_path: str
    records: list[LocalFileRecord] = field(default_factory=list)
    missing_registry_files: list[str] = field(default_factory=list)
    duplicate_registry_paths: dict[str, list[str]] = field(default_factory=dict)
    file_registry_missing_files: list[str] = field(default_factory=list)
    file_registry_unscanned_records: list[LocalFileRecord] = field(default_factory=list)
    file_registry_hash_mismatches: list[str] = field(default_factory=list)
    duplicate_hashes: dict[str, list[LocalFileRecord]] = field(default_factory=dict)
    unsupported_files: list[str] = field(default_factory=list)
    unlinked_files: list[LocalFileRecord] = field(default_factory=list)
    sidecars: list[LocalFileRecord] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def default_file_registry_path(root: str | Path = ".", *, project: bool = False) -> Path:
    base = Path(root)
    return base / "files.csv" if project else base / "data" / "registries" / "local_files.csv"


def file_type_for_path(path: str | Path) -> str:
    suffix = Path(path).suffix.lower().lstrip(".")
    return suffix if suffix in SUPPORTED_FILE_TYPES else ""


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_path(path: str | Path, root: str | Path) -> str:
    target = Path(path).expanduser()
    root_path = Path(root).expanduser()
    if not target.is_absolute():
        target = (Path.cwd() / target).resolve()
    root_resolved = root_path.resolve()
    try:
        return target.resolve().relative_to(root_resolved).as_posix()
    except ValueError:
        return target.as_posix()


def resolve_relative(path: str | Path, root: str | Path) -> Path:
    target = Path(path).expanduser()
    if target.is_absolute():
        return target
    return Path(root) / target


def resolve_input_file(path: str | Path, root: str | Path) -> Path:
    target = Path(path).expanduser()
    if target.is_absolute():
        return target
    root_candidate = Path(root) / target
    if root_candidate.exists():
        return root_candidate
    return target


def load_file_registry(path: str | Path) -> list[LocalFileRecord]:
    target = Path(path)
    if not target.exists():
        return []
    records: list[LocalFileRecord] = []
    for row in read_csv_rows(target):
        records.append(
            LocalFileRecord(
                paper_id=(row.get("paper_id") or "").strip(),
                file_id=(row.get("file_id") or "").strip(),
                relative_path=(row.get("relative_path") or "").strip(),
                file_type=(row.get("file_type") or "").strip(),
                size_bytes=int(row.get("size_bytes") or 0),
                sha256=(row.get("sha256") or "").strip(),
                added_date=(row.get("added_date") or "").strip(),
                linked_registry_status=(row.get("linked_registry_status") or "").strip(),
                notes=(row.get("notes") or "").strip(),
                text_sidecar_path=(row.get("text_sidecar_path") or "").strip(),
                extracted_metadata_status=(row.get("extracted_metadata_status") or "").strip() or "not_attempted",
            )
        )
    return records


def save_file_registry(records: list[LocalFileRecord], path: str | Path, *, force: bool = True) -> Path:
    rows = []
    for record in records:
        rows.append(
            {
                "paper_id": record.paper_id,
                "file_id": record.file_id,
                "relative_path": record.relative_path,
                "file_type": record.file_type,
                "size_bytes": str(record.size_bytes),
                "sha256": record.sha256,
                "added_date": record.added_date,
                "linked_registry_status": record.linked_registry_status,
                "notes": record.notes,
                "text_sidecar_path": record.text_sidecar_path,
                "extracted_metadata_status": record.extracted_metadata_status,
            }
        )
    return write_csv_rows(path, rows, LOCAL_FILE_FIELDS, force=force)


def _snapshot_metadata_files(paths: list[str | Path]) -> dict[Path, bytes | None]:
    snapshots: dict[Path, bytes | None] = {}
    for raw_path in paths:
        path = Path(raw_path)
        snapshots[path] = path.read_bytes() if path.exists() else None
    return snapshots


def _restore_metadata_files(snapshots: dict[Path, bytes | None]) -> None:
    for path, content in snapshots.items():
        if content is None:
            if path.exists():
                path.unlink()
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def merge_file_registry_records(scanned: list[LocalFileRecord], existing: list[LocalFileRecord]) -> list[LocalFileRecord]:
    """Merge a fresh scan with existing user-maintained file-registry rows."""
    existing_by_key = {(record.paper_id, record.relative_path): record for record in existing}
    merged: list[LocalFileRecord] = []
    seen: set[tuple[str, str]] = set()
    for record in scanned:
        key = (record.paper_id, record.relative_path)
        previous = existing_by_key.get(key)
        if previous:
            record.notes = previous.notes or record.notes
            record.added_date = previous.added_date or record.added_date
            record.text_sidecar_path = previous.text_sidecar_path or record.text_sidecar_path
            if previous.extracted_metadata_status and previous.extracted_metadata_status != "not_attempted":
                record.extracted_metadata_status = previous.extracted_metadata_status
        merged.append(record)
        seen.add(key)
    for record in existing:
        key = (record.paper_id, record.relative_path)
        if key not in seen:
            merged.append(record)
    return merged


def _paper_path_map(papers: list[Paper], root: str | Path) -> dict[str, list[str]]:
    linked: dict[str, list[str]] = defaultdict(list)
    for paper in papers:
        if not paper.local_pdf_path:
            continue
        linked[relative_path(resolve_relative(paper.local_pdf_path, root), root)].append(paper.paper_id)
    return dict(linked)


def _paper_id_from_filename(path: Path, paper_ids: set[str]) -> str:
    stem = path.stem
    if stem in paper_ids:
        return stem
    normalized = re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")
    for paper_id in paper_ids:
        if normalized == re.sub(r"[^a-z0-9]+", "_", paper_id.lower()).strip("_"):
            return paper_id
    return ""


def _metadata_status(file_type: str) -> str:
    if file_type == "pdf":
        return "not_extracted_optional_future_work"
    return "not_applicable"


def _record_for_file(path: Path, root: str | Path, papers: list[Paper], linked_paths: dict[str, list[str]]) -> LocalFileRecord:
    rel = relative_path(path, root)
    file_type = file_type_for_path(path)
    digest = sha256_file(path)
    paper_ids = {paper.paper_id for paper in papers}
    linked_paper_ids = linked_paths.get(rel, [])
    inferred_paper_id = ";".join(linked_paper_ids) if linked_paper_ids else _paper_id_from_filename(path, paper_ids)
    if len(linked_paper_ids) > 1:
        status = "linked_multiple_registry_paths"
    elif linked_paper_ids:
        status = "linked_registry_path"
    elif inferred_paper_id:
        status = "possible_filename_match"
    else:
        status = "unlinked"
    return LocalFileRecord(
        paper_id=inferred_paper_id,
        file_id=digest[:16],
        relative_path=rel,
        file_type=file_type,
        size_bytes=path.stat().st_size,
        sha256=digest,
        linked_registry_status=status,
        notes="top-level text sidecar" if path.parent.name == "text" and file_type == "txt" else "",
        text_sidecar_path=rel if path.parent.name == "text" and file_type == "txt" else "",
        extracted_metadata_status=_metadata_status(file_type),
    )


def scan_local_files(
    *,
    root: str | Path,
    registry_path: str | Path,
    file_registry_path: str | Path | None = None,
    scan_dirs: tuple[str, ...] = SCAN_DIRS,
    large_file_bytes: int = LARGE_FILE_BYTES,
) -> FileScanResult:
    root_path = Path(root)
    registry = Path(registry_path)
    papers = load_registry(registry) if registry.exists() else []
    resolved_file_registry = file_registry_path or default_file_registry_path(root_path, project=registry.name == "registry.csv" and registry.parent == root_path)
    linked_paths = _paper_path_map(papers, root_path)
    duplicate_registry_paths = {path: paper_ids for path, paper_ids in linked_paths.items() if len(paper_ids) > 1}
    records: list[LocalFileRecord] = []
    unsupported: list[str] = []
    warnings: list[str] = []
    for rel, paper_ids in sorted(duplicate_registry_paths.items()):
        warnings.append(f"Local file path linked to multiple papers: {rel} -> {', '.join(paper_ids)}")

    for dirname in scan_dirs:
        directory = root_path / dirname
        if not directory.exists():
            warnings.append(f"Scan folder missing: {dirname}")
            continue
        for path in sorted(item for item in directory.rglob("*") if item.is_file()):
            file_type = file_type_for_path(path)
            rel = relative_path(path, root_path)
            if not file_type:
                unsupported.append(rel)
                continue
            record = _record_for_file(path, root_path, papers, linked_paths)
            records.append(record)
            if record.size_bytes > large_file_bytes:
                warnings.append(f"Large file over {large_file_bytes} bytes: {rel}")

    missing: list[str] = []
    for paper in papers:
        if not paper.local_pdf_path:
            continue
        resolved = resolve_relative(paper.local_pdf_path, root_path)
        if not resolved.exists():
            missing.append(f"{paper.paper_id}: {paper.local_pdf_path}")

    by_hash: dict[str, list[LocalFileRecord]] = defaultdict(list)
    for record in records:
        by_hash[record.sha256].append(record)
    duplicates = {digest: grouped for digest, grouped in by_hash.items() if digest and len(grouped) > 1}
    sidecars = [record for record in records if record.file_type == "txt" and Path(record.relative_path).parent.name == "text"]
    unlinked = [record for record in records if record.linked_registry_status == "unlinked"]
    for sidecar in sidecars:
        if not sidecar.paper_id:
            warnings.append(f"Text sidecar has no matching paper_id: {sidecar.relative_path}")
    for digest, grouped in duplicates.items():
        paths = ", ".join(record.relative_path for record in grouped)
        warnings.append(f"Duplicate file hash {digest[:12]}: {paths}")

    existing_file_records = load_file_registry(resolved_file_registry)
    scanned_paths = {record.relative_path for record in records}
    file_registry_missing: list[str] = []
    file_registry_unscanned: list[LocalFileRecord] = []
    file_registry_hash_mismatches: list[str] = []
    for record in existing_file_records:
        resolved = resolve_relative(record.relative_path, root_path)
        if not resolved.exists():
            file_registry_missing.append(f"{record.paper_id or '[unlinked]'}: {record.relative_path}")
            continue
        if record.relative_path not in scanned_paths:
            file_registry_unscanned.append(record)
        if record.sha256:
            actual_hash = sha256_file(resolved)
            if actual_hash != record.sha256:
                file_registry_hash_mismatches.append(f"{record.paper_id or '[unlinked]'}: {record.relative_path}")
    if file_registry_missing:
        warnings.append(f"File registry references missing files: {len(file_registry_missing)}")
    if file_registry_unscanned:
        warnings.append(f"File registry records outside current scan folders: {len(file_registry_unscanned)}")
    if file_registry_hash_mismatches:
        warnings.append(f"File registry hash mismatches: {len(file_registry_hash_mismatches)}")

    return FileScanResult(
        root=str(root_path),
        file_registry_path=str(resolved_file_registry),
        records=records,
        missing_registry_files=missing,
        duplicate_registry_paths=duplicate_registry_paths,
        file_registry_missing_files=file_registry_missing,
        file_registry_unscanned_records=file_registry_unscanned,
        file_registry_hash_mismatches=file_registry_hash_mismatches,
        duplicate_hashes=duplicates,
        unsupported_files=unsupported,
        unlinked_files=unlinked,
        sidecars=sidecars,
        warnings=warnings,
    )


def link_file_to_paper(
    *,
    paper_id: str,
    file_path: str | Path,
    root: str | Path,
    registry_path: str | Path,
    file_registry_path: str | Path,
    force: bool = False,
    notes: str = "",
) -> LocalFileRecord:
    source = resolve_input_file(file_path, root)
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(source)
    file_type = file_type_for_path(source)
    if not file_type:
        raise ValueError(f"unsupported file type: {source}")
    papers = load_registry(registry_path)
    paper = next((item for item in papers if item.paper_id == paper_id), None)
    if paper is None:
        raise ValueError(f"unknown paper_id: {paper_id}")
    rel = relative_path(source, root)
    if file_type == "pdf" and paper.local_pdf_path and paper.local_pdf_path != rel and not force:
        raise FileExistsError(f"{paper_id} already has local_pdf_path={paper.local_pdf_path}; use --force to replace it")
    digest = sha256_file(source)
    record = LocalFileRecord(
        paper_id=paper_id,
        file_id=digest[:16],
        relative_path=rel,
        file_type=file_type,
        size_bytes=source.stat().st_size,
        sha256=digest,
        added_date=date.today().isoformat(),
        linked_registry_status="linked_file_registry",
        notes=notes,
        text_sidecar_path=rel if file_type == "txt" else "",
        extracted_metadata_status=_metadata_status(file_type),
    )
    records = [item for item in load_file_registry(file_registry_path) if not (item.paper_id == paper_id and item.relative_path == rel)]
    records.append(record)
    snapshot_paths = [file_registry_path]
    if file_type == "pdf":
        snapshot_paths.append(registry_path)
    snapshots = _snapshot_metadata_files(snapshot_paths)
    try:
        save_file_registry(records, file_registry_path, force=True)
        if file_type == "pdf":
            paper.local_pdf_path = rel
            save_registry(papers, registry_path)
    except Exception:
        _restore_metadata_files(snapshots)
        raise
    return record


def unlink_file_from_paper(
    *,
    paper_id: str,
    root: str | Path,
    registry_path: str | Path,
    file_registry_path: str | Path,
    clear_pdf: bool = True,
) -> int:
    records = load_file_registry(file_registry_path)
    kept = [record for record in records if record.paper_id != paper_id]
    removed = len(records) - len(kept)
    snapshot_paths = [file_registry_path]
    if clear_pdf and Path(registry_path).exists():
        snapshot_paths.append(registry_path)
    snapshots = _snapshot_metadata_files(snapshot_paths)
    try:
        save_file_registry(kept, file_registry_path, force=True)
        if removed and clear_pdf and Path(registry_path).exists():
            papers = load_registry(registry_path)
            changed = False
            for paper in papers:
                if paper.paper_id == paper_id and paper.local_pdf_path:
                    paper.local_pdf_path = ""
                    changed = True
            if changed:
                save_registry(papers, registry_path)
    except Exception:
        _restore_metadata_files(snapshots)
        raise
    return removed


def local_files_audit_report(result: FileScanResult) -> str:
    lines = [
        "# Local Files Audit v0.7",
        "",
        "This report audits local user-provided files. It does not download, scrape, OCR, or summarize documents.",
        "",
        f"Root: {result.root}",
        f"Files found: {len(result.records)}",
        f"Unlinked files: {len(result.unlinked_files)}",
        f"Missing registry file references: {len(result.missing_registry_files)}",
        f"Duplicate registry file paths: {len(result.duplicate_registry_paths)}",
        f"Duplicate file hashes: {len(result.duplicate_hashes)}",
        f"File registry missing files: {len(result.file_registry_missing_files)}",
        f"File registry records outside scan folders: {len(result.file_registry_unscanned_records)}",
        f"File registry hash mismatches: {len(result.file_registry_hash_mismatches)}",
        f"Text sidecars: {len(result.sidecars)}",
        f"Unsupported files: {len(result.unsupported_files)}",
        "",
        "## Files",
        "",
        "| Paper ID | Type | Size | Status | Path | SHA256 |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    if not result.records:
        lines.append("|  |  | 0 | none | No supported files found. |  |")
    for record in result.records:
        lines.append(f"| {record.paper_id or '[unlinked]'} | {record.file_type} | {record.size_bytes} | {record.linked_registry_status} | {record.relative_path} | {record.sha256[:12]} |")
    if result.duplicate_registry_paths:
        lines.extend(["", "## Duplicate Registry File Paths", ""])
        for rel, paper_ids in sorted(result.duplicate_registry_paths.items()):
            lines.append(f"- `{rel}` is linked by: {', '.join(paper_ids)}")
    if result.file_registry_missing_files or result.file_registry_unscanned_records or result.file_registry_hash_mismatches:
        lines.extend(["", "## File Registry Reconciliation", ""])
        if result.file_registry_missing_files:
            lines.append("### Missing Files Referenced By files.csv")
            lines.extend(f"- {item}" for item in result.file_registry_missing_files)
            lines.append("")
        if result.file_registry_unscanned_records:
            lines.append("### Records Outside Current Scan Folders")
            lines.extend(f"- {record.paper_id or '[unlinked]'}: {record.relative_path}" for record in result.file_registry_unscanned_records)
            lines.append("")
        if result.file_registry_hash_mismatches:
            lines.append("### Hash Mismatches")
            lines.extend(f"- {item}" for item in result.file_registry_hash_mismatches)
            lines.append("")
    if result.warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in result.warnings)
    return "\n".join(lines).rstrip() + "\n"


def duplicate_files_report(result: FileScanResult) -> str:
    lines = ["# Duplicate Files v0.7", "", f"Duplicate file hashes: {len(result.duplicate_hashes)}", ""]
    if not result.duplicate_hashes:
        lines.append("No duplicate file hashes detected.")
    for digest, records in sorted(result.duplicate_hashes.items()):
        lines.append(f"## {digest}")
        for record in records:
            lines.append(f"- {record.relative_path} ({record.paper_id or 'unlinked'})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def missing_files_report(result: FileScanResult) -> str:
    lines = [
        "# Missing Local Files v0.7",
        "",
        f"Missing registry file references: {len(result.missing_registry_files)}",
        f"File registry missing files: {len(result.file_registry_missing_files)}",
        "",
    ]
    if not result.missing_registry_files and not result.file_registry_missing_files:
        lines.append("No missing registry file references detected.")
    else:
        if result.missing_registry_files:
            lines.append("## Registry local_pdf_path References")
            lines.extend(f"- {item}" for item in result.missing_registry_files)
        if result.file_registry_missing_files:
            lines.extend(["", "## File Registry References"])
            lines.extend(f"- {item}" for item in result.file_registry_missing_files)
    return "\n".join(lines).rstrip() + "\n"


def text_sidecars_report(result: FileScanResult) -> str:
    lines = [
        "# Text Sidecars v0.7",
        "",
        "Only user-provided top-level `.txt` sidecars are audited here. Do not add copyrighted full text unless you have the right to store it locally.",
        "",
        f"Text sidecars: {len(result.sidecars)}",
        "",
        "| Paper ID | Status | Size | Path |",
        "| --- | --- | ---: | --- |",
    ]
    if not result.sidecars:
        lines.append("|  | none | 0 | No text sidecars found. |")
    for record in result.sidecars:
        lines.append(f"| {record.paper_id or '[unmatched]'} | {record.linked_registry_status} | {record.size_bytes} | {record.relative_path} |")
    return "\n".join(lines).rstrip() + "\n"
