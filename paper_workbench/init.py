"""Project initialization workflow."""

from __future__ import annotations

from pathlib import Path

from .paths import ensure_workspace
from .registry import create_empty_registry


def init_workspace(root: str | Path = ".", create_registry: bool = True) -> list[Path]:
    """Create the expected workspace folders without overwriting user files."""
    created = ensure_workspace(root)
    if create_registry:
        create_empty_registry(Path(root) / "data" / "registries" / "papers.csv")
    return created
