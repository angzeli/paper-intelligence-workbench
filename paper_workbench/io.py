"""Small file I/O helpers used by the workbench."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_text(path: str | Path, content: str, force: bool = True) -> Path:
    target = Path(path)
    if target.exists() and not force:
        raise FileExistsError(f"{target} already exists")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def load_json(path: str | Path) -> dict:
    return json.loads(read_text(path))


def write_json(path: str | Path, data: object, force: bool = True) -> Path:
    return write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n", force=force)


def read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_csv_rows(path: str | Path, rows: Iterable[dict[str, str]], fields: list[str]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    return target
