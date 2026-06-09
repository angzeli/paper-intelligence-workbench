"""Project-profile support for multi-review workspaces."""

from __future__ import annotations

from pathlib import Path
import re

from .io import load_json, write_json
from .paths import default_projects_dir, project_root
from .registry import create_empty_registry
from .schema import ProjectProfile


PROJECT_CONFIG = "project.json"
PROJECT_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def validate_project_name(name: str) -> str:
    value = name.strip()
    if not PROJECT_NAME_RE.fullmatch(value):
        raise ValueError("project names must use letters, numbers, underscores, or hyphens")
    return value


def project_dir(name: str, root: str | Path = ".") -> Path:
    return default_projects_dir(root) / validate_project_name(name)


def _profile_from_root(project_path: Path, data: dict | None = None) -> ProjectProfile:
    config = data or {}
    name = config.get("name", project_path.name)
    registry_path = project_path / config.get("registry_path", "registry.csv")
    bibtex_path = project_path / config.get("bibtex_path", "bibtex/library.bib")
    notes_dir = project_path / config.get("notes_dir", "notes")
    themes_path = project_path / config.get("themes_path", "themes.json")
    reports_dir = project_path / config.get("reports_dir", "reports")
    return ProjectProfile(
        name=name,
        root=str(project_path),
        registry_path=str(registry_path),
        bibtex_path=str(bibtex_path),
        notes_dir=str(notes_dir),
        themes_path=str(themes_path),
        reports_dir=str(reports_dir),
        description=config.get("description", ""),
        is_default=bool(config.get("is_default", False)),
    )


def profile_config(profile: ProjectProfile) -> dict[str, object]:
    root = Path(profile.root)
    return {
        "name": profile.name,
        "description": profile.description,
        "is_default": profile.is_default,
        "registry_path": str(Path(profile.registry_path).relative_to(root)),
        "bibtex_path": str(Path(profile.bibtex_path).relative_to(root)),
        "notes_dir": str(Path(profile.notes_dir).relative_to(root)),
        "themes_path": str(Path(profile.themes_path).relative_to(root)),
        "reports_dir": str(Path(profile.reports_dir).relative_to(root)),
    }


def create_project_profile(
    name: str,
    root: str | Path = ".",
    *,
    description: str = "",
    force: bool = False,
) -> ProjectProfile:
    project_path = project_dir(name, root)
    if project_path.exists() and not force and (project_path / PROJECT_CONFIG).exists():
        raise FileExistsError(f"project {name!r} already exists")
    (project_path / "notes").mkdir(parents=True, exist_ok=True)
    (project_path / "bibtex").mkdir(parents=True, exist_ok=True)
    (project_path / "reports").mkdir(parents=True, exist_ok=True)
    profile = _profile_from_root(project_path, {"name": validate_project_name(name), "description": description})
    create_empty_registry(profile.registry_path)
    bibtex = Path(profile.bibtex_path)
    if not bibtex.exists():
        bibtex.write_text("", encoding="utf-8")
    themes = Path(profile.themes_path)
    if not themes.exists():
        themes.write_text('{"themes": []}\n', encoding="utf-8")
    write_json(project_path / PROJECT_CONFIG, profile_config(profile))
    return profile


def load_project_profile(name: str, root: str | Path = ".") -> ProjectProfile:
    project_path = project_dir(name, root)
    config_path = project_path / PROJECT_CONFIG
    if not config_path.exists():
        if project_path.exists():
            return _profile_from_root(project_path)
        raise FileNotFoundError(f"project profile not found: {name}")
    return _profile_from_root(project_path, load_json(config_path))


def list_project_profiles(root: str | Path = ".") -> list[ProjectProfile]:
    projects_root = default_projects_dir(root)
    if not projects_root.exists():
        return []
    profiles: list[ProjectProfile] = []
    for path in sorted(projects_root.iterdir()):
        if not path.is_dir():
            continue
        config_path = path / PROJECT_CONFIG
        if config_path.exists():
            profiles.append(_profile_from_root(path, load_json(config_path)))
        else:
            profiles.append(_profile_from_root(path))
    return profiles


def default_project_profile(root: str | Path = ".") -> ProjectProfile | None:
    profiles = list_project_profiles(root)
    for profile in profiles:
        if profile.is_default:
            return profile
    return profiles[0] if profiles else None


def resolve_project_profile(name: str | None, root: str | Path = ".") -> ProjectProfile | None:
    if name:
        return load_project_profile(name, root)
    return None


def profile_summary(profile: ProjectProfile) -> str:
    return (
        f"{profile.name}\tregistry={profile.registry_path}\t"
        f"notes={profile.notes_dir}\treports={profile.reports_dir}"
    )
