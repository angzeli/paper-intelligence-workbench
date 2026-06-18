"""Validate Markdown docs links and command examples without external tools."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import shlex
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DOC_PATHS = [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
ABSOLUTE_PATH_RE = re.compile(r"(/Users/|/private/|file://|[A-Za-z]:\\)")
PAPERWB_RE = re.compile(r"^\s*paperwb(?:\s+(.+))?$")


def _markdown_links(text: str) -> list[str]:
    links: list[str] = []
    for raw in LINK_RE.findall(text):
        target = raw.strip()
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        links.append(target.split("#", 1)[0])
    return links


def check_links(paths: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for link in _markdown_links(text):
            target = (path.parent / link).resolve()
            try:
                target.relative_to(ROOT)
            except ValueError:
                errors.append(f"{path.relative_to(ROOT)}: link escapes repository: {link}")
                continue
            if not target.exists():
                errors.append(f"{path.relative_to(ROOT)}: missing link target: {link}")
    return errors


def check_absolute_paths(paths: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if ABSOLUTE_PATH_RE.search(text):
            errors.append(f"{path.relative_to(ROOT)}: contains raw absolute-path pattern")
    return errors


def _paperwb_commands() -> set[str]:
    completed = subprocess.run(
        [sys.executable, "-m", "paper_workbench.cli", "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout)
    match = re.search(r"\{([^}]+)\}", completed.stdout)
    if not match:
        raise RuntimeError("could not parse paperwb command list")
    return {item.strip() for item in match.group(1).split(",") if item.strip()}


def _paperwb_example_commands(text: str) -> list[str]:
    commands: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("paperwb"):
            continue
        try:
            parts = shlex.split(stripped.rstrip("\\"))
        except ValueError:
            continue
        if len(parts) < 2 or parts[0] != "paperwb" or parts[1].startswith("-"):
            continue
        command = parts[1]
        if command.isupper() or "/" in command:
            continue
        commands.append(command)
    return commands


def check_paperwb_examples(paths: list[Path]) -> list[str]:
    commands = _paperwb_commands()
    errors: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for command in _paperwb_example_commands(text):
            if command not in commands:
                errors.append(f"{path.relative_to(ROOT)}: unknown paperwb command in example: {command}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check Markdown docs links, path hygiene, and paperwb command examples.")
    parser.add_argument("paths", nargs="*", help="Optional Markdown files to check. Defaults to README.md and docs/**/*.md.")
    args = parser.parse_args(argv)

    paths = [Path(path) for path in args.paths] if args.paths else DOC_PATHS
    paths = [path if path.is_absolute() else ROOT / path for path in paths]
    errors: list[str] = []
    errors.extend(check_links(paths))
    errors.extend(check_absolute_paths(paths))
    errors.extend(check_paperwb_examples(paths))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Checked {len(paths)} Markdown doc file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
