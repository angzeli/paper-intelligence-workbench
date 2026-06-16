from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_workbench.io import write_text
from paper_workbench.synthetic import generate_synthetic_project


def stress_report(summary, *, papers: int, claims: int, themes: int) -> str:
    root_label = f"<stress_root>/projects/{summary.project}"
    return "\n".join(
        [
            "# Stress Project Summary",
            "",
            "This report describes a synthetic local stress project. It contains no real paper metadata, PDFs, quotes, or paper full text.",
            "",
            "## Requested Workload",
            "",
            f"- Papers: {papers}",
            f"- Claims: {claims}",
            f"- Themes: {themes}",
            "",
            "## Generated Project",
            "",
            f"- Project: `{summary.project}`",
            f"- Root: `{root_label}`",
            f"- Registry papers: {summary.papers}",
            f"- Notes: {summary.notes}",
            f"- Claims: {summary.claims}",
            f"- Themes: {summary.themes}",
            f"- BibTeX entries: {summary.bibtex_entries}",
            "",
            "## Safety Boundary",
            "",
            "- Synthetic data only.",
            "- No cloud APIs, LLM APIs, publisher scraping, PDFs, or copyrighted text.",
            "- Existing project paths are refused unless `--force` is explicit.",
        ]
    ).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a synthetic stress project for local scale checks.")
    parser.add_argument("--root", default="scratch/stress_v2_5", help="Workspace root for the generated synthetic project.")
    parser.add_argument("--project", default="stress_v2_5", help="Synthetic project name.")
    parser.add_argument("--papers", type=int, default=500, help="Number of synthetic papers.")
    parser.add_argument("--claims", type=int, default=1500, help="Number of synthetic claims.")
    parser.add_argument("--themes", type=int, default=50, help="Number of synthetic themes.")
    parser.add_argument("--domain", default="zis", choices=["zis", "finance", "ml"], help="Synthetic domain theme family.")
    parser.add_argument("--out", default="reports/stress_project_summary_v2_5.md", help="Markdown summary report path.")
    parser.add_argument("--force", action="store_true", help="Allow overwriting the selected synthetic project/report.")
    args = parser.parse_args()

    summary = generate_synthetic_project(
        name=args.project,
        root=args.root,
        papers=args.papers,
        claims=args.claims,
        themes=args.themes,
        domain=args.domain,
        force=args.force,
    )
    path = write_text(args.out, stress_report(summary, papers=args.papers, claims=args.claims, themes=args.themes), force=args.force)
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
