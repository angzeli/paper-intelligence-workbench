"""Synthetic indexed-search workflow for paper-intelligence-workbench.

Run from the repository root:

    python examples/indexed_search_workflow.py

The script uses only checked-in synthetic project data and writes a local
ignored cache under .paperwb/.
"""

from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from paper_workbench.index import (
    build_index_records,
    default_index_path,
    index_status,
    index_status_markdown,
    rebuild_index,
    search_index,
    search_results_markdown,
)
from paper_workbench.io import write_text


PROJECT = "zis_photocatalysis"
PROJECT_ROOT = Path("projects") / PROJECT
INDEX_PATH = default_index_path(".")


def main() -> None:
    records = build_index_records(
        project_id=PROJECT,
        registry_path=PROJECT_ROOT / "registry.csv",
        bibtex_path=PROJECT_ROOT / "bibtex" / "library.bib",
        notes_dir=PROJECT_ROOT / "notes",
        themes_path=PROJECT_ROOT / "themes.json",
        text_dir=PROJECT_ROOT / "text",
        include_text=True,
    )
    status = rebuild_index(INDEX_PATH, records, project_id=PROJECT)
    print(index_status_markdown(status))

    results = search_index(INDEX_PATH, "charge separation", project_id=PROJECT)
    write_text("reports/search_demo_v0_5.md", search_results_markdown(results, "charge separation"), force=True)

    sidecar_query = "observations"
    sidecar_results = search_index(INDEX_PATH, sidecar_query, project_id=PROJECT, source_types={"text"})
    write_text("reports/full_text_sidecar_demo_v0_5.md", search_results_markdown(sidecar_results, sidecar_query), force=True)

    checked_status = index_status(INDEX_PATH, project_id=PROJECT, current_records=records)
    write_text("reports/index_status_v0_5.md", index_status_markdown(checked_status), force=True)
    print("Key takeaways:")
    print("- Indexed search is local and rebuildable.")
    print("- Sidecars are optional user-provided plain text.")
    print("- Default substring search remains available without the cache.")


if __name__ == "__main__":
    main()
