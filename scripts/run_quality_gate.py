"""Run local quality gates for Paper Intelligence Workbench."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import importlib.util
from pathlib import Path
import re
import subprocess
import sys
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
USER_PATH_RE = re.compile("/" + "Users" + r"/[^\s`|,\"]+")
PRIVATE_PATH_RE = re.compile("/" + "private" + r"/[^\s`|,\"]+")
WINDOWS_PATTERN = "[" + "A-Za-z" + r"]:\\[^\s`|,\"]+\\[^\s`|,\"]+"
ESCAPED_WINDOWS_PATTERN = "[" + "A-Za-z" + r"]:\\\\[^\\s`|,\\\"]+\\\\[^\\s`|,\\\"]+"


@dataclass(frozen=True, slots=True)
class QualityStep:
    name: str
    args: tuple[str, ...]
    tool_module: str = ""
    description: str = ""


@dataclass(frozen=True, slots=True)
class QualityResult:
    step: QualityStep
    returncode: int
    stdout: str = ""
    stderr: str = ""
    skipped: bool = False
    reason: str = ""


Runner = Callable[..., subprocess.CompletedProcess[str]]


def _python_module(*args: str) -> tuple[str, ...]:
    return (sys.executable, "-m", *args)


def build_step_groups() -> dict[str, list[QualityStep]]:
    return {
        "tests": [
            QualityStep("pytest", _python_module("pytest", "-q"), "pytest", "Run the full test suite."),
        ],
        "lint": [
            QualityStep(
                "ruff lint",
                _python_module("ruff", "check", "paper_workbench", "scripts", "tests"),
                "ruff",
                "Run Pyflakes-style lint checks without broad formatting churn.",
            ),
        ],
        "format-check": [
            QualityStep(
                "ruff format check",
                _python_module("ruff", "format", "--check", "scripts/run_quality_gate.py"),
                "ruff",
                "Check formatting for the quality-gate script introduced in v3.3.",
            ),
        ],
        "type-check": [
            QualityStep(
                "mypy scripts",
                _python_module("mypy", "scripts", "--config-file", "pyproject.toml"),
                "mypy",
                "Type-check release and quality scripts first; package-wide typing is future work.",
            ),
        ],
        "smoke": [
            QualityStep(
                "CLI smoke workflow",
                (sys.executable, "scripts/smoke_cli_workflow.py", "--quick"),
                "",
                "Run non-destructive CLI smoke checks on synthetic data.",
            ),
        ],
        "notebooks": [
            QualityStep(
                "validate notebooks",
                (sys.executable, "scripts/validate_notebooks.py"),
                "",
                "Validate notebook JSON and absolute-path hygiene.",
            ),
            QualityStep(
                "check notebooks",
                (sys.executable, "scripts/check_notebooks.py"),
                "",
                "Check notebook titles and release-engineering metadata.",
            ),
        ],
        "data-safety": [
            QualityStep(
                "data safety audit",
                (
                    sys.executable,
                    "scripts/data_safety_audit.py",
                    "--out",
                    "scratch/quality_gate_data_safety.md",
                    "--strict",
                ),
                "",
                "Audit tracked files for private paths, PDFs, cache files, and other unsafe artifacts.",
            ),
        ],
        "build": [
            QualityStep(
                "build distributions",
                _python_module("build", "--sdist", "--wheel", "--no-isolation"),
                "setuptools.build_meta",
                "Build source and wheel distributions without network-backed build isolation.",
            ),
        ],
    }


RELEASE_GROUPS = ("lint", "format-check", "type-check", "tests", "smoke", "notebooks", "data-safety", "build")


def available_targets() -> list[str]:
    return sorted([*build_step_groups().keys(), "release"])


def expand_targets(targets: list[str]) -> list[QualityStep]:
    groups = build_step_groups()
    selected = targets or ["release"]
    steps: list[QualityStep] = []
    seen: set[str] = set()
    for target in selected:
        group_names = RELEASE_GROUPS if target == "release" else (target,)
        for group_name in group_names:
            if group_name not in groups:
                raise ValueError(f"Unknown quality target: {target}")
            for step in groups[group_name]:
                if step.name in seen:
                    continue
                steps.append(step)
                seen.add(step.name)
    return steps


def tool_available(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except Exception:
        return False


def run_steps(
    steps: list[QualityStep],
    *,
    allow_missing_tools: bool = False,
    runner: Runner = subprocess.run,
) -> list[QualityResult]:
    results: list[QualityResult] = []
    for step in steps:
        if step.tool_module and not tool_available(step.tool_module):
            reason = f"missing Python module: {step.tool_module}"
            returncode = 0 if allow_missing_tools else 127
            results.append(QualityResult(step, returncode, skipped=allow_missing_tools, reason=reason))
            if not allow_missing_tools:
                break
            continue
        completed = runner(
            list(step.args),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        results.append(QualityResult(step, completed.returncode, completed.stdout, completed.stderr))
        if completed.returncode != 0:
            break
    return results


def _display_command(step: QualityStep) -> str:
    parts = ["python" if index == 0 and arg == sys.executable else arg for index, arg in enumerate(step.args)]
    return " ".join(parts)


def sanitize_output(text: str) -> str:
    sanitized = text.replace(str(ROOT), "<repo-root>")
    sanitized = USER_PATH_RE.sub("<local-path>", sanitized)
    sanitized = PRIVATE_PATH_RE.sub("<local-path>", sanitized)
    sanitized = sanitized.replace(WINDOWS_PATTERN, "<windows-absolute-path-pattern>")
    sanitized = sanitized.replace(ESCAPED_WINDOWS_PATTERN, "<windows-absolute-path-pattern>")
    return sanitized


def results_markdown(results: list[QualityResult]) -> str:
    failures = [result for result in results if result.returncode != 0]
    skipped = [result for result in results if result.skipped]
    lines = [
        "# Quality Gate Report",
        "",
        "This report is generated from local commands only. It does not use cloud services, LLM APIs, or network-only checks.",
        "",
        f"Steps run: {len(results)}",
        f"Failures: {len(failures)}",
        f"Skipped optional steps: {len(skipped)}",
        "",
        "| Step | Result | Command |",
        "| --- | --- | --- |",
    ]
    for result in results:
        if result.skipped:
            status = f"skipped ({result.reason})"
        elif result.returncode == 0:
            status = "pass"
        else:
            status = f"fail {result.returncode}"
        lines.append(f"| {result.step.name} | {status} | `{_display_command(result.step)}` |")
    if failures:
        lines.extend(["", "## Failure Details", ""])
        for result in failures:
            lines.extend([f"### {result.step.name}", ""])
            if result.reason:
                lines.extend(["Reason:", "", result.reason, ""])
            if result.stdout:
                lines.extend(["stdout:", "```text", sanitize_output(result.stdout.strip()), "```", ""])
            if result.stderr:
                lines.extend(["stderr:", "```text", sanitize_output(result.stderr.strip()), "```", ""])
    return "\n".join(lines).rstrip() + "\n"


def print_summary(results: list[QualityResult]) -> None:
    for result in results:
        if result.skipped:
            print(f"SKIP {result.step.name}: {result.reason}")
        elif result.returncode == 0:
            print(f"PASS {result.step.name}")
        else:
            print(f"FAIL {result.step.name}: exit {result.returncode}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Paper Workbench quality gate targets.")
    parser.add_argument("targets", nargs="*", help="Gate targets. Defaults to release.")
    parser.add_argument("--list", action="store_true", help="List available targets and steps.")
    parser.add_argument("--allow-missing-tools", action="store_true", help="Skip optional tool-backed steps when tools are not installed.")
    parser.add_argument("--out", default="", help="Optional Markdown report path.")
    args = parser.parse_args(argv)

    if args.list:
        groups = build_step_groups()
        for target in available_targets():
            if target == "release":
                print(f"{target}: {', '.join(RELEASE_GROUPS)}")
                continue
            step_names = ", ".join(step.name for step in groups[target])
            print(f"{target}: {step_names}")
        return 0

    unknown_targets = sorted(set(args.targets) - set(available_targets()))
    if unknown_targets:
        parser.error(f"unknown target(s): {', '.join(unknown_targets)}")
    steps = expand_targets(args.targets)
    results = run_steps(steps, allow_missing_tools=args.allow_missing_tools)
    print_summary(results)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(results_markdown(results), encoding="utf-8")
        print(f"Wrote {out_path}")
    return 1 if any(result.returncode != 0 for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
