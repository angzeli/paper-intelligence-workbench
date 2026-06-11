"""Run the repository data-safety audit and optionally write a Markdown report."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_workbench.safety import audit_data_safety, safety_audit_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit tracked repository files for local-first data-safety risks.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to the current directory.")
    parser.add_argument("--out", default="reports/data_safety_audit_v0_10.md", help="Optional Markdown report path.")
    parser.add_argument("--max-file-bytes", type=int, default=1_000_000, help="Warn on tracked files larger than this size.")
    parser.add_argument("--title", default="Data Safety Audit v0.10", help="Markdown report title.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when error-severity findings exist.")
    args = parser.parse_args(argv)

    result = audit_data_safety(args.root, max_file_bytes=args.max_file_bytes)
    markdown = safety_audit_markdown(result, title=args.title)
    if args.out:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(markdown, encoding="utf-8")
        print(f"Wrote {target}")
    print(f"Checked {result.files_checked} repository files: {len(result.errors)} error(s), {len(result.warnings)} warning(s).")
    if result.errors:
        for finding in result.errors:
            print(f"error {finding.code}: {finding.path}: {finding.message}", file=sys.stderr)
    return 1 if args.strict and result.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
