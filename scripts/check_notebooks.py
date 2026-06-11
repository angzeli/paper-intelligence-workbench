"""Static notebook checker for release engineering."""

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
    re.compile(r"[A-Za-z]:\\"),
]


def _source_text(cell: dict) -> str:
    source = cell.get("source", "")
    if isinstance(source, list):
        return "".join(str(part) for part in source)
    return str(source)


def _notebook_title(data: dict, fallback: str) -> str:
    for cell in data.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        for line in _source_text(cell).splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                return stripped.lstrip("#").strip() or fallback
    return fallback


def check_notebook(path: Path) -> tuple[str, list[str]]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return path.stem, [f"{path}: invalid JSON: {exc}"]
    title = _notebook_title(data, path.stem)
    if data.get("nbformat") != 4:
        errors.append(f"{path}: expected nbformat 4")
    cells = data.get("cells")
    if not isinstance(cells, list) or not cells:
        errors.append(f"{path}: expected a non-empty cells list")
        return title, errors
    for index, cell in enumerate(cells, start=1):
        if cell.get("cell_type") not in {"markdown", "code", "raw"}:
            errors.append(f"{path}: cell {index} has invalid cell_type {cell.get('cell_type')!r}")
        if "source" not in cell:
            errors.append(f"{path}: cell {index} is missing source")
        source = _source_text(cell)
        for pattern in ABSOLUTE_PATH_PATTERNS:
            if pattern.search(source):
                errors.append(f"{path}: cell {index} contains absolute-path pattern {pattern.pattern!r}")
    return title, errors


def notebook_paths(paths: list[str]) -> list[Path]:
    if paths:
        return [Path(path) for path in paths]
    return sorted(Path("notebooks").glob("*.ipynb"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate notebook JSON, titles, and portability without executing notebooks.")
    parser.add_argument("paths", nargs="*", help="Notebook paths. Defaults to notebooks/*.ipynb.")
    args = parser.parse_args(argv)

    paths = notebook_paths(args.paths)
    if not paths:
        print("No notebooks found.", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for path in paths:
        title, errors = check_notebook(path)
        print(f"{path}: {title}")
        all_errors.extend(errors)
    if all_errors:
        for error in all_errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Checked {len(paths)} notebook(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
