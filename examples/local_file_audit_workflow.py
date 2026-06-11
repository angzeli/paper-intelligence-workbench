"""Synthetic local-file audit workflow for v0.7.

Run from the repository root:

    python examples/local_file_audit_workflow.py

The script creates a temporary project with synthetic placeholder files only.
It does not download, scrape, OCR, or include real paper text.
"""

from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from paper_workbench.files import (
    duplicate_files_report,
    link_file_to_paper,
    local_files_audit_report,
    scan_local_files,
    text_sidecars_report,
)
from paper_workbench.registry import save_registry
from paper_workbench.schema import Author, Paper


def main() -> None:
    with TemporaryDirectory(prefix="paperwb-local-files-") as tmp:
        root = Path(tmp) / "synthetic_project"
        for dirname in ("papers", "text", "notes", "bibtex", "reports"):
            (root / dirname).mkdir(parents=True)
        registry = root / "registry.csv"
        files_csv = root / "files.csv"
        save_registry(
            [
                Paper(
                    paper_id="synthetic_alpha",
                    title="Synthetic Alpha File Audit Paper",
                    authors=[Author(given="Ada", family="Alpha", raw_name="Ada Alpha")],
                    year="2026",
                    notes_path="notes/synthetic_alpha.md",
                )
            ],
            registry,
        )
        (root / "papers" / "synthetic_alpha.pdf").write_bytes(b"%PDF-1.4 synthetic placeholder only\n")
        (root / "text" / "synthetic_alpha.txt").write_text("Synthetic sidecar text for local indexing.\n", encoding="utf-8")
        (root / "text" / "orphan_sidecar.txt").write_text("Synthetic unmatched sidecar.\n", encoding="utf-8")
        (root / "notes" / "synthetic_alpha.md").write_text("# Synthetic Note\n", encoding="utf-8")
        link_file_to_paper(
            paper_id="synthetic_alpha",
            file_path="papers/synthetic_alpha.pdf",
            root=root,
            registry_path=registry,
            file_registry_path=files_csv,
        )
        scan = scan_local_files(root=root, registry_path=registry, file_registry_path=files_csv)
        print(local_files_audit_report(scan))
        print(duplicate_files_report(scan))
        print(text_sidecars_report(scan))


if __name__ == "__main__":
    main()
