from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import run_quality_gate as quality_gate


def test_release_target_includes_expected_gate_steps():
    steps = quality_gate.expand_targets(["release"])
    names = [step.name for step in steps]

    assert "ruff lint" in names
    assert "ruff format check" in names
    assert "mypy scripts" in names
    assert "pytest" in names
    assert "CLI smoke workflow" in names
    assert "validate notebooks" in names
    assert "check notebooks" in names
    assert "data safety audit" in names
    assert "build distributions" in names


def test_local_diagnostic_target_matches_release_steps():
    release_names = [step.name for step in quality_gate.expand_targets(["release"])]
    diagnostic_names = [step.name for step in quality_gate.expand_targets(["local-diagnostic"])]

    assert diagnostic_names == release_names
    assert "local-diagnostic" in quality_gate.available_targets()


def test_quality_gate_steps_use_argument_vectors_not_shell_strings():
    steps = quality_gate.expand_targets(["release"])

    assert steps
    for step in steps:
        assert isinstance(step.args, tuple)
        assert step.args
        assert all(isinstance(part, str) for part in step.args)
        assert not any(";" in part or "&&" in part or "|" in part for part in step.args)


def test_missing_tool_can_be_skipped(monkeypatch):
    step = quality_gate.QualityStep("ruff lint", ("python", "-m", "ruff", "check"), tool_module="ruff")

    monkeypatch.setattr(quality_gate, "tool_available", lambda module_name: False)

    def runner(*args, **kwargs):  # pragma: no cover - should never run when tool is missing.
        raise AssertionError("runner should not be called for missing optional tools")

    results = quality_gate.run_steps([step], allow_missing_tools=True, runner=runner)

    assert len(results) == 1
    assert results[0].skipped
    assert results[0].returncode == 0
    assert "missing Python module: ruff" == results[0].reason


def test_release_target_rejects_allow_missing_tools():
    with pytest.raises(SystemExit) as excinfo:
        quality_gate.main(["release", "--allow-missing-tools"])

    assert excinfo.value.code == 2


def test_local_diagnostic_enables_missing_tool_allowance(monkeypatch):
    captured = {}
    step = quality_gate.QualityStep("ruff lint", ("python", "-m", "ruff", "check"), tool_module="ruff")

    monkeypatch.setattr(quality_gate, "expand_targets", lambda targets: [step])

    def fake_run_steps(steps, *, allow_missing_tools):
        captured["allow_missing_tools"] = allow_missing_tools
        return [quality_gate.QualityResult(step, 0, skipped=True, reason="missing Python module: ruff")]

    monkeypatch.setattr(quality_gate, "run_steps", fake_run_steps)

    assert quality_gate.main(["local-diagnostic"]) == 0
    assert captured["allow_missing_tools"] is True


def test_quality_docs_use_local_diagnostic_for_missing_tools():
    docs = [
        Path("docs/QUALITY_GATE.md"),
        Path("docs/DEVELOPMENT_WORKFLOW.md"),
        Path("docs/RELEASE_VALIDATION.md"),
    ]

    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        assert "release --allow-missing-tools" not in text
        assert "local-diagnostic" in text


def test_missing_tool_fails_without_allowance(monkeypatch):
    step = quality_gate.QualityStep("ruff lint", ("python", "-m", "ruff", "check"), tool_module="ruff")

    monkeypatch.setattr(quality_gate, "tool_available", lambda module_name: False)

    results = quality_gate.run_steps([step], allow_missing_tools=False)

    assert len(results) == 1
    assert not results[0].skipped
    assert results[0].returncode == 127


def test_tool_available_returns_false_when_probe_raises(monkeypatch):
    def broken_find_spec(module_name: str):
        raise ImportError("broken import")

    monkeypatch.setattr(quality_gate.importlib.util, "find_spec", broken_find_spec)

    assert quality_gate.tool_available("setuptools.build_meta") is False


def test_results_markdown_records_skipped_and_failed_steps():
    skipped = quality_gate.QualityResult(
        quality_gate.QualityStep("ruff lint", ("python", "-m", "ruff", "check"), tool_module="ruff"),
        0,
        skipped=True,
        reason="missing Python module: ruff",
    )
    failed = quality_gate.QualityResult(
        quality_gate.QualityStep("pytest", ("python", "-m", "pytest")),
        1,
        stdout="",
        stderr="failed",
    )

    markdown = quality_gate.results_markdown([skipped, failed])

    assert "Skipped optional steps: 1" in markdown
    assert "| ruff lint | skipped (missing Python module: ruff)" in markdown
    assert "not a strict release-gate pass" in markdown
    assert "### pytest" in markdown
    assert "failed" in markdown


def test_results_markdown_sanitizes_absolute_path_patterns():
    private_tmp = "/" + "private" + "/tmp/work"
    windows_pattern = "[" + "A-Za-z" + r"]:\\[^\s`|,\"]+\\[^\s`|,\"]+"
    failed = quality_gate.QualityResult(
        quality_gate.QualityStep("pytest", ("python", "-m", "pytest")),
        1,
        stdout=f"{quality_gate.ROOT}/secret\n{private_tmp}\n{windows_pattern}",
        stderr="",
    )

    markdown = quality_gate.results_markdown([failed])

    assert str(quality_gate.ROOT) not in markdown
    assert "/" + "private" + "/tmp" not in markdown
    assert "[" + "A-Za-z" + "]:" not in markdown
    assert "<repo-root>" in markdown
    assert "<local-path>" in markdown
    assert "<windows-absolute-path-pattern>" in markdown


def test_runner_invocation_uses_repo_cwd_and_no_shell(monkeypatch):
    step = quality_gate.QualityStep("custom", ("python", "--version"))
    calls = []

    def runner(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="ok", stderr="")

    results = quality_gate.run_steps([step], runner=runner)

    assert results[0].returncode == 0
    assert calls[0][0] == ["python", "--version"]
    assert calls[0][1]["cwd"] == quality_gate.ROOT
    assert calls[0][1]["capture_output"] is True
    assert "shell" not in calls[0][1]
