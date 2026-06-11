"""Workspace path helpers."""

from __future__ import annotations

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
