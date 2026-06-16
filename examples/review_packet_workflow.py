"""Demonstrate the local review-packet workflow on synthetic project data.

Run from the repository root:

    python examples/review_packet_workflow.py

Outputs are written under scratch/ and can be deleted after inspection.
"""

from __future__ import annotations

import csv
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = ROOT / "scratch" / "review_packet_demo"
COMMENTS_CSV = ROOT / "scratch" / "review_packet_demo_comments.csv"
COMMENTS_STORE = ROOT / "scratch" / "review_packet_demo_comments.json"
RESPONSE = ROOT / "scratch" / "review_packet_demo_response.md"


def run(*args: str) -> None:
    command = [sys.executable, "-m", "paper_workbench.cli", *args]
    print("$", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def write_demo_comment() -> None:
    COMMENTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with COMMENTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "comment_id",
                "item_id",
                "item_type",
                "reviewer",
                "status",
                "comment",
                "recommendation",
                "requires_reread",
                "requires_citation_check",
                "weak_evidence",
                "created_at",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerow(
            {
                "comment_id": "demo_review_1",
                "item_id": "claim:zis_stability_2024:c1",
                "item_type": "claim",
                "reviewer": "Synthetic Reviewer",
                "status": "needs_reread",
                "comment": "Verify the evidence location before using this claim.",
                "recommendation": "Add a page or section reference.",
                "requires_reread": "true",
                "requires_citation_check": "",
                "weak_evidence": "true",
                "created_at": "2026-06-16T00:00:00+00:00",
            }
        )


def main() -> None:
    run(
        "review-packet",
        "create",
        "--project",
        "zis_photocatalysis",
        "--theme",
        "photocorrosion",
        "--out",
        str(PACKET_DIR),
        "--force",
    )
    write_demo_comment()
    run(
        "review-packet",
        "import-comments",
        str(COMMENTS_CSV),
        "--project",
        "zis_photocatalysis",
        "--theme",
        "photocorrosion",
        "--comments-store",
        str(COMMENTS_STORE),
        "--dry-run",
    )
    run(
        "review-packet",
        "import-comments",
        str(COMMENTS_CSV),
        "--project",
        "zis_photocatalysis",
        "--theme",
        "photocorrosion",
        "--comments-store",
        str(COMMENTS_STORE),
        "--force",
        "--out",
        str(ROOT / "scratch" / "review_packet_demo_import.md"),
        "--force-report",
    )
    run(
        "review-packet",
        "response",
        "--project",
        "zis_photocatalysis",
        "--theme",
        "photocorrosion",
        "--comments-store",
        str(COMMENTS_STORE),
        "--out",
        str(RESPONSE),
        "--force",
    )


if __name__ == "__main__":
    main()
