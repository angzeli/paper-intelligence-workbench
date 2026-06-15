"""Synthetic v2.2 claim lifecycle workflow.

Run from the repository root:

    python examples/claim_lifecycle_workflow.py

The script uses a temporary workspace and writes no project files into the repo.
"""

from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import tempfile

from paper_workbench.registry import save_registry
from paper_workbench.schema import Author, Paper


NOTE = """# Paper Note: Synthetic

## Metadata
- Paper ID: paper_a
- BibTeX key: paperA2026
- Tags: photocorrosion
- Reading status: skimmed

## Claims and evidence

### Claim 1
- Claim: Synthetic photocorrosion stability improves under tracked control conditions.
- Evidence type: experimental_result
- Section / page:
- Confidence: high
- Tags: photocorrosion
- Strength: strong
- Supports theme: photocorrosion
"""


THEMES = """{"themes":[{"theme_id":"photocorrosion","name":"Photocorrosion","tags":["photocorrosion"],"min_papers":1,"min_claims":1}]}"""


def run(root: Path, *args: str) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    result = subprocess.run([sys.executable, "-m", "paper_workbench.cli", *args], cwd=root, text=True, capture_output=True, check=False, env=env)
    print(f"$ paperwb {' '.join(args)}")
    print(result.stdout or result.stderr)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="paperwb-claim-lifecycle-") as tmp:
        root = Path(tmp)
        notes = root / "data" / "notes"
        examples = root / "data" / "examples"
        notes.mkdir(parents=True)
        examples.mkdir(parents=True)
        save_registry(
            [
                Paper(
                    paper_id="paper_a",
                    title="Synthetic Claim Lifecycle Paper",
                    authors=[Author(given="Ada", family="Example", raw_name="Ada Example")],
                    year="2026",
                    bibtex_key="paperA2026",
                    reading_status="skimmed",
                    tags=["photocorrosion"],
                )
            ],
            root / "data" / "registries" / "papers.csv",
        )
        (notes / "paper_a.md").write_text(NOTE, encoding="utf-8")
        (examples / "themes.json").write_text(THEMES, encoding="utf-8")
        run(root, "claim-review", "queue")
        run(root, "claim-review", "mark", "paper_a:c1", "--status", "verified", "--verification-date", "2026-06-15")
        run(root, "claim-review", "verified")
        run(root, "contradictions", "create", "--theme", "photocorrosion", "--group-id", "synthetic_group")
        run(root, "contradictions", "add", "synthetic_group", "paper_a:c1")
        run(root, "contradictions", "report")


if __name__ == "__main__":
    main()
