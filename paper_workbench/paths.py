"""Workspace path helpers."""

from __future__ import annotations

import os
from pathlib import Path


DEFAULT_DIRS = [
    "paper_workbench",
    "data/examples",
    "data/papers",
    "data/text",
    "data/notes",
    "data/bibtex",
    "data/registries",
    "data/processed",
    "projects",
    "reports",
    "docs",
    "notebooks",
    "tests",
]


def project_root(path: str | Path = ".") -> Path:
    return Path(path).expanduser().resolve()


def ensure_workspace(root: str | Path = ".") -> list[Path]:
    root_path = project_root(root)
    created: list[Path] = []
    for relative in DEFAULT_DIRS:
        directory = root_path / relative
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            created.append(directory)
    return created


def default_registry_path(root: str | Path = ".") -> Path:
    return project_root(root) / "data" / "registries" / "papers.csv"


def default_bibtex_path(root: str | Path = ".") -> Path:
    return project_root(root) / "data" / "bibtex" / "library.bib"


def default_themes_path(root: str | Path = ".") -> Path:
    return project_root(root) / "data" / "examples" / "themes.json"


def default_reports_dir(root: str | Path = ".") -> Path:
    return project_root(root) / "reports"


def default_notes_dir(root: str | Path = ".") -> Path:
    return project_root(root) / "data" / "notes"


def default_projects_dir(root: str | Path = ".") -> Path:
    return project_root(root) / "projects"


def default_processed_dir(root: str | Path = ".") -> Path:
    return project_root(root) / "data" / "processed"


def is_path_within(path: str | Path, root: str | Path) -> bool:
    """Return whether a path resolves inside a workspace root."""
    try:
        Path(path).expanduser().resolve(strict=False).relative_to(Path(root).expanduser().resolve(strict=False))
        return True
    except ValueError:
        return False


def relative_path(path: str | Path, root: str | Path) -> str:
    """Return a slash-style path relative to root when possible."""
    target = Path(path)
    try:
        return target.resolve(strict=False).relative_to(Path(root).resolve(strict=False)).as_posix()
    except ValueError:
        return target.as_posix()


def display_path(path: str | Path, *, base_path: str | Path | None = None) -> str:
    """Display a filesystem path relative to a stable base when possible."""
    if not path:
        return ""
    target = Path(path)
    base = Path(base_path) if base_path is not None else Path.cwd()
    try:
        if target.is_absolute():
            return target.relative_to(base.resolve()).as_posix()
    except ValueError:
        pass
    try:
        return Path(os.path.relpath(target, start=base)).as_posix()
    except (OSError, ValueError):
        return target.as_posix()
