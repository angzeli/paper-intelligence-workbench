"""Local audit log helpers for write-oriented workflows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Iterable


@dataclass(slots=True)
class AuditEvent:
    timestamp: str
    command: str
    action: str
    project: str = ""
    affected_paths: list[str] | None = None
    dry_run: bool = False
    success: bool = True
    warnings: list[str] | None = None
    summary: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "timestamp": self.timestamp,
            "command": self.command,
            "project": self.project,
            "action": self.action,
            "affected_paths": self.affected_paths or [],
            "dry_run": self.dry_run,
            "success": self.success,
            "warnings": self.warnings or [],
            "summary": self.summary,
        }


def default_audit_log_path(root: str | Path = ".") -> Path:
    return Path(root) / ".paperwb" / "audit_log.jsonl"


def append_audit_event(
    *,
    root: str | Path = ".",
    path: str | Path | None = None,
    command: str,
    action: str,
    project: str = "",
    affected_paths: Iterable[str | Path] = (),
    dry_run: bool = False,
    success: bool = True,
    warnings: Iterable[str] = (),
    summary: str = "",
) -> AuditEvent:
    target = Path(path) if path is not None else default_audit_log_path(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    event = AuditEvent(
        timestamp=datetime.now(timezone.utc).isoformat(),
        command=command,
        action=action,
        project=project,
        affected_paths=[str(item) for item in affected_paths],
        dry_run=dry_run,
        success=success,
        warnings=list(warnings),
        summary=summary,
    )
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
    return event


def load_audit_events(path: str | Path) -> list[dict[str, object]]:
    target = Path(path)
    if not target.exists():
        return []
    events: list[dict[str, object]] = []
    for line in target.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            events.append(
                {
                    "timestamp": "",
                    "command": "",
                    "project": "",
                    "action": "parse_error",
                    "affected_paths": [],
                    "dry_run": False,
                    "success": False,
                    "warnings": [f"Could not parse audit log line: {line[:80]}"],
                    "summary": "",
                }
            )
    return events


def clear_audit_log(path: str | Path, *, force: bool = False) -> bool:
    target = Path(path)
    if not force:
        raise PermissionError("audit-log clear requires --force")
    if target.exists():
        target.unlink()
        return True
    return False


def audit_log_markdown(events: list[dict[str, object]], *, title: str = "Audit Log") -> str:
    lines = [
        f"# {title}",
        "",
        f"Events: {len(events)}",
        "",
        "| Timestamp | Project | Action | Dry run | Success | Summary |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for event in events:
        lines.append(
            "| {timestamp} | {project} | {action} | {dry_run} | {success} | {summary} |".format(
                timestamp=_escape(event.get("timestamp", "")),
                project=_escape(event.get("project", "")),
                action=_escape(event.get("action", "")),
                dry_run=str(event.get("dry_run", False)).lower(),
                success=str(event.get("success", False)).lower(),
                summary=_escape(event.get("summary", "")),
            )
        )
    if not events:
        lines.append("|  |  | none | false | true | No audit events found. |")
    return "\n".join(lines).rstrip() + "\n"


def _escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
