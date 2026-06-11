"""Run a non-destructive CLI smoke workflow against synthetic data."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


@dataclass(slots=True)
class SmokeStep:
    name: str
    args: list[str]


@dataclass(slots=True)
class SmokeResult:
    name: str
    args: list[str]
    returncode: int
    stdout: str
    stderr: str


def _cli_args(*args: str) -> list[str]:
    return [sys.executable, "-m", "paper_workbench.cli", *args]


def build_steps(tmp: Path, *, quick: bool = False) -> list[SmokeStep]:
    steps = [
        SmokeStep("help", _cli_args("--help")),
        SmokeStep("init temp workspace", _cli_args("init", "--root", str(tmp / "workspace"))),
        SmokeStep("validate registry", _cli_args("validate-registry", "data/registries/example_papers.csv")),
        SmokeStep(
            "validate bibtex",
            _cli_args("validate-bib", "data/bibtex/example_library.bib", "--registry", "data/registries/example_papers.csv"),
        ),
        SmokeStep(
            "note template",
            _cli_args(
                "note-template",
                "synth_charge_2024",
                "--registry",
                "data/registries/example_papers.csv",
                "--output",
                str(tmp / "synth_charge_2024_note.md"),
                "--force",
            ),
        ),
        SmokeStep("claims extraction", _cli_args("claims", "data/notes", "--output", str(tmp / "claims.csv"))),
        SmokeStep(
            "evidence map",
            _cli_args(
                "report",
                "evidence-map",
                "--registry",
                "data/registries/example_papers.csv",
                "--bibtex",
                "data/bibtex/example_library.bib",
                "--notes-dir",
                "data/notes",
                "--themes",
                "data/examples/themes.json",
                "--out",
                str(tmp / "evidence_map.md"),
                "--force",
            ),
        ),
        SmokeStep(
            "citation audit",
            _cli_args(
                "report",
                "citation-audit",
                "--registry",
                "data/registries/example_papers.csv",
                "--bibtex",
                "data/bibtex/example_library.bib",
                "--notes-dir",
                "data/notes",
                "--themes",
                "data/examples/themes.json",
                "--out",
                str(tmp / "citation_audit.md"),
                "--force",
            ),
        ),
        SmokeStep("project list", _cli_args("project", "list")),
        SmokeStep("project search", _cli_args("search", "photocorrosion", "--project", "zis_photocatalysis")),
        SmokeStep("files scan", _cli_args("files", "scan", "--project", "zis_photocatalysis")),
    ]
    if quick:
        return steps
    steps.extend(
        [
            SmokeStep(
                "zotero dry-run import",
                _cli_args(
                    "import",
                    "zotero-csv",
                    "data/examples/zotero_export.csv",
                    "--project",
                    "zis_photocatalysis",
                    "--dry-run",
                    "--report",
                    str(tmp / "import_zotero.md"),
                    "--force",
                ),
            ),
            SmokeStep(
                "writing packet",
                _cli_args(
                    "writing-packet",
                    "--project",
                    "zis_photocatalysis",
                    "--theme",
                    "photocorrosion",
                    "--out",
                    str(tmp / "writing_packet.md"),
                    "--force",
                ),
            ),
            SmokeStep(
                "indexed search rebuild",
                _cli_args("index", "rebuild", "--project", "zis_photocatalysis", "--include-text", "--index", str(tmp / "index.sqlite")),
            ),
            SmokeStep(
                "indexed search",
                _cli_args("search", "photocorrosion", "--project", "zis_photocatalysis", "--indexed", "--text", "--index", str(tmp / "index.sqlite")),
            ),
            SmokeStep("file audit", _cli_args("files", "audit", "--project", "zis_photocatalysis", "--reports-dir", str(tmp / "file_reports"), "--force")),
            SmokeStep("obsidian export", _cli_args("export", "obsidian", "--project", "zis_photocatalysis", "--out", str(tmp / "obsidian_zis"))),
            SmokeStep("report index export", _cli_args("export", "report-index", "--out", str(tmp / "report_index.md"), "--force")),
        ]
    )
    return steps


def run_step(step: SmokeStep) -> SmokeResult:
    result = subprocess.run(step.args, cwd=ROOT, text=True, capture_output=True, check=False)
    return SmokeResult(step.name, step.args, result.returncode, result.stdout, result.stderr)


def report_markdown(results: list[SmokeResult], tmp: Path, *, title: str = "CLI Smoke Workflow v0.8") -> str:
    lines = [
        f"# {title}",
        "",
        "This smoke workflow uses synthetic checked-in data and writes generated outputs to a temporary directory.",
        "",
        "Temporary output directory: `<temporary directory>`",
        f"Steps run: {len(results)}",
        f"Failures: {sum(1 for result in results if result.returncode != 0)}",
        "",
        "| Step | Result | Command |",
        "| --- | --- | --- |",
    ]
    for result in results:
        status = "pass" if result.returncode == 0 else f"fail {result.returncode}"
        display_args = ["python" if index == 0 else arg.replace(str(tmp), "<temporary directory>") for index, arg in enumerate(result.args)]
        command = " ".join(display_args)
        lines.append(f"| {result.name} | {status} | `{command}` |")
    failures = [result for result in results if result.returncode != 0]
    if failures:
        lines.extend(["", "## Failure Details", ""])
        for failure in failures:
            lines.append(f"### {failure.name}")
            lines.append("")
            if failure.stdout:
                lines.extend(["stdout:", "```text", failure.stdout.strip().replace(str(tmp), "<temporary directory>"), "```", ""])
            if failure.stderr:
                lines.extend(["stderr:", "```text", failure.stderr.strip().replace(str(tmp), "<temporary directory>"), "```", ""])
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a non-destructive Paper Workbench CLI smoke workflow.")
    parser.add_argument("--out", default="", help="Optional Markdown report path.")
    parser.add_argument("--quick", action="store_true", help="Run a shorter smoke set for unit tests.")
    parser.add_argument("--title", default="CLI Smoke Workflow v0.8", help="Markdown report title.")
    args = parser.parse_args(argv)

    with tempfile.TemporaryDirectory(prefix="paperwb_smoke_") as tmp_name:
        tmp = Path(tmp_name)
        results = [run_step(step) for step in build_steps(tmp, quick=args.quick)]
        markdown = report_markdown(results, tmp, title=args.title)
        if args.out:
            target = Path(args.out)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(markdown, encoding="utf-8")
            print(f"Wrote {target}")
        print(f"Ran {len(results)} smoke step(s); failures: {sum(1 for result in results if result.returncode != 0)}")
        return 1 if any(result.returncode != 0 for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
