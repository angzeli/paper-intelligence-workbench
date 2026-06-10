"""Validate repository notebooks without optional notebook dependencies."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


ABSOLUTE_PATH_PATTERNS = [
    re.compile(r"/Users/"),
    re.compile(r"/private/"),
    re.compile(r"file://"),
    re.compile(r"[A-Za-z]:\\\\"),
]


def _source_text(cell: dict) -> str:
    source = cell.get("source", "")
    if isinstance(source, list):
        return "".join(str(part) for part in source)
    return str(source)


def validate_notebook(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON: {exc}"]
    if data.get("nbformat") != 4:
        errors.append(f"{path}: expected nbformat 4")
    cells = data.get("cells")
    if not isinstance(cells, list) or not cells:
        errors.append(f"{path}: expected a non-empty cells list")
        return errors
    for index, cell in enumerate(cells, start=1):
        cell_type = cell.get("cell_type")
        if cell_type not in {"markdown", "code", "raw"}:
            errors.append(f"{path}: cell {index} has invalid cell_type {cell_type!r}")
        if "source" not in cell:
            errors.append(f"{path}: cell {index} is missing source")
        source = _source_text(cell)
        for pattern in ABSOLUTE_PATH_PATTERNS:
            if pattern.search(source):
                errors.append(f"{path}: cell {index} contains an absolute-path pattern: {pattern.pattern}")
    return errors


def execute_notebook(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    namespace = {"__name__": "__notebook__"}
    errors: list[str] = []
    for index, cell in enumerate(data.get("cells", []), start=1):
        if cell.get("cell_type") != "code":
            continue
        source = _source_text(cell).strip()
        if not source:
            continue
        try:
            exec(compile(source, f"{path}:cell-{index}", "exec"), namespace)
        except Exception as exc:  # noqa: BLE001 - report notebook execution failures.
            errors.append(f"{path}: cell {index} failed during execution: {exc}")
            break
    return errors


def notebook_paths(args: argparse.Namespace) -> list[Path]:
    if args.paths:
        return [Path(value) for value in args.paths]
    return sorted(Path("notebooks").glob("*.ipynb"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate notebook JSON and optional top-to-bottom execution.")
    parser.add_argument("paths", nargs="*", help="Notebook paths. Defaults to notebooks/*.ipynb.")
    parser.add_argument("--execute", action="store_true", help="Execute code cells with the standard Python runtime.")
    args = parser.parse_args(argv)

    errors: list[str] = []
    paths = notebook_paths(args)
    if not paths:
        errors.append("No notebooks found.")
    for path in paths:
        errors.extend(validate_notebook(path))
        if args.execute:
            errors.extend(execute_notebook(path))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Validated {len(paths)} notebook(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
