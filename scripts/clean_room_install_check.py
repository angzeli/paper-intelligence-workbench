"""Run a local release-candidate install and workflow check.

The script avoids creating or deleting virtual environments by default. It checks
the current Python environment, runs the package by module path, and writes all
generated workflow outputs to a temporary directory.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


@dataclass(slots=True)
class CheckStep:
    name: str
    args: list[str]
    cwd: Path


@dataclass(slots=True)
class CheckResult:
    name: str
    args: list[str]
    cwd: Path
    returncode: int
    stdout: str
    stderr: str


def _python(*args: str) -> list[str]:
    return [sys.executable, *args]


def _paperwb(*args: str) -> list[str]:
    return _python("-m", "paper_workbench.cli", *args)


def build_steps(tmp: Path, *, quick: bool = False) -> list[CheckStep]:
    workspace = tmp / "clean_workspace"
    steps = [
        CheckStep("import package", _python("-c", "import paper_workbench; print(paper_workbench.__version__)"), ROOT),
        CheckStep("CLI help", _paperwb("--help"), ROOT),
        CheckStep("initialize temp workspace", _paperwb("init", "--root", str(workspace)), ROOT),
        CheckStep("create temp project", _paperwb("project", "init", "rc_demo", "--description", "Synthetic RC demo"), workspace),
        CheckStep("list temp projects", _paperwb("project", "list"), workspace),
        CheckStep("validate example registry", _paperwb("validate-registry", "data/registries/example_papers.csv"), ROOT),
        CheckStep(
            "validate example BibTeX",
            _paperwb("validate-bib", "data/bibtex/example_library.bib", "--registry", "data/registries/example_papers.csv"),
            ROOT,
        ),
    ]
    if quick:
        return steps
    steps.extend(
        [
            CheckStep(
                "generate note template",
                _paperwb(
                    "note-template",
                    "synth_charge_2024",
                    "--registry",
                    "data/registries/example_papers.csv",
                    "--output",
                    str(tmp / "synth_charge_2024_note.md"),
                    "--force",
                ),
                ROOT,
            ),
            CheckStep("extract claims", _paperwb("claims", "data/notes", "--output", str(tmp / "claims.csv")), ROOT),
            CheckStep(
                "generate evidence matrix",
                _paperwb(
                    "report",
                    "evidence-matrix",
                    "--project",
                    "zis_photocatalysis",
                    "--theme",
                    "photocorrosion",
                    "--out",
                    str(tmp / "evidence_matrix.md"),
                    "--force",
                ),
                ROOT,
            ),
            CheckStep(
                "generate citation audit",
                _paperwb(
                    "report",
                    "citation-audit",
                    "--project",
                    "zis_photocatalysis",
                    "--out",
                    str(tmp / "citation_audit.md"),
                    "--force",
                ),
                ROOT,
            ),
            CheckStep(
                "generate writing packet",
                _paperwb(
                    "writing-packet",
                    "--project",
                    "zis_photocatalysis",
                    "--theme",
                    "photocorrosion",
                    "--out",
                    str(tmp / "writing_packet.md"),
                    "--force",
                ),
                ROOT,
            ),
            CheckStep(
                "rebuild local index",
                _paperwb("index", "rebuild", "--project", "zis_photocatalysis", "--include-text", "--index", str(tmp / "index.sqlite")),
                ROOT,
            ),
            CheckStep(
                "indexed search",
                _paperwb("search", "photocorrosion", "--project", "zis_photocatalysis", "--indexed", "--index", str(tmp / "index.sqlite")),
                ROOT,
            ),
            CheckStep("workspace integrity", _paperwb("integrity", "check", "--project", "zis_photocatalysis"), ROOT),
            CheckStep("notebook structure check", _python("scripts/check_notebooks.py"), ROOT),
        ]
    )
    return steps


def run_step(step: CheckStep, *, tmp: Path) -> CheckResult:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{ROOT}{os.pathsep}{existing}" if existing else str(ROOT)
    result = subprocess.run(step.args, cwd=step.cwd, env=env, text=True, capture_output=True, check=False)
    return CheckResult(step.name, step.args, step.cwd, result.returncode, result.stdout, result.stderr)


def _portable_command(result: CheckResult, tmp: Path) -> str:
    parts: list[str] = []
    for index, arg in enumerate(result.args):
        if index == 0:
            parts.append("python")
        else:
            parts.append(arg.replace(str(tmp), "<temporary directory>").replace(str(ROOT), "<repository root>"))
    return " ".join(parts)


def report_markdown(results: list[CheckResult], *, tmp: Path, title: str) -> str:
    failures = [result for result in results if result.returncode != 0]
    lines = [
        f"# {title}",
        "",
        "This check runs in the current Python environment and writes generated files to a temporary directory.",
        "It does not create a virtual environment, publish packages, call network services, or modify checked-in examples.",
        "",
        "Temporary output directory: `<temporary directory>`",
        f"Steps run: {len(results)}",
        f"Failures: {len(failures)}",
        "",
        "| Step | Result | Command |",
        "| --- | --- | --- |",
    ]
    for result in results:
        status = "pass" if result.returncode == 0 else f"fail {result.returncode}"
        lines.append(f"| {result.name} | {status} | `{_portable_command(result, tmp)}` |")
    if failures:
        lines.extend(["", "## Failure Details", ""])
        for failure in failures:
            lines.extend([f"### {failure.name}", ""])
            stdout = failure.stdout.strip().replace(str(tmp), "<temporary directory>").replace(str(ROOT), "<repository root>")
            stderr = failure.stderr.strip().replace(str(tmp), "<temporary directory>").replace(str(ROOT), "<repository root>")
            if stdout:
                lines.extend(["stdout:", "```text", stdout, "```", ""])
            if stderr:
                lines.extend(["stderr:", "```text", stderr, "```", ""])
    lines.extend(
        [
            "",
            "## Manual Fresh-Venv Check",
            "",
            "For a stricter local clean-room install, run these commands in a disposable directory:",
            "",
            "```bash",
            "python -m venv .venv",
            ". .venv/bin/activate",
            "python -m pip install -e \".[test]\"",
            "paperwb --help",
            "python scripts/smoke_cli_workflow.py --quick",
            "```",
            "",
            "The scripted check uses `python -m paper_workbench.cli` so it also works before the console entry point is installed.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a local v1.0-rc clean-room install and workflow check.")
    parser.add_argument("--out", default="", help="Optional Markdown report path.")
    parser.add_argument("--quick", action="store_true", help="Run a shorter check for CI and tests.")
    parser.add_argument("--title", default="Clean-room Install Check v1.0-rc", help="Markdown report title.")
    args = parser.parse_args(argv)

    with tempfile.TemporaryDirectory(prefix="paperwb_clean_room_") as tmp_name:
        tmp = Path(tmp_name)
        results = [run_step(step, tmp=tmp) for step in build_steps(tmp, quick=args.quick)]
        markdown = report_markdown(results, tmp=tmp, title=args.title)
        if args.out:
            target = Path(args.out)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(markdown, encoding="utf-8")
            print(f"Wrote {target}")
        failures = sum(1 for result in results if result.returncode != 0)
        print(f"Ran {len(results)} clean-room check step(s); failures: {failures}")
        return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
