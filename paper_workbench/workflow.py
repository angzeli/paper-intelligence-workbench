"""Declarative local workflow recipes and report runner.

Workflow recipes are data only. They select from a fixed set of built-in step
types and never execute arbitrary shell commands or Python code from JSON.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from .audit import citation_audit
from .backups import create_backup
from .bibtex import parse_bibtex_file, validate_bibtex
from .claims import collect_notes, save_claims_csv
from .dashboard import build_dashboard, dashboard_markdown
from .doctor import workspace_health
from .exports import export_claims_csv, export_claims_json
from .index import build_index_records, index_status_markdown, rebuild_index
from .integrity import check_workspace_integrity, workspace_integrity_report
from .io import load_json, write_json, write_text
from .manuscript import audit_manuscript, manuscript_qa_report
from .paths import default_bibtex_path, default_notes_dir, default_registry_path, default_reports_dir, default_themes_path, display_path
from .projects import load_project_profile
from .registry import load_registry, validate_registry, validate_registry_headers
from .reporting import (
    bibtex_audit_report,
    citation_audit_report,
    evidence_map_report,
    inventory_report,
    missing_evidence_report,
    missing_notes_report,
    reading_status_report,
    theme_coverage_dashboard_report,
    weak_claims_report,
    workspace_health_report,
)
from .rules import RuleContext, empty_rule_set, load_rule_set, rule_report, run_rule_set, validate_rule_set
from .schema import BibTeXEntry, Claim, Paper, PaperNote, ProjectProfile, ProjectTheme, ValidationFinding
from .tags import load_themes, normalize_tag


ALLOWED_STEP_TYPES = {
    "validate_registry",
    "validate_bibtex",
    "extract_claims",
    "generate_report",
    "run_rules",
    "run_doctor",
    "run_integrity",
    "run_dashboard",
    "export_claims",
    "backup_create",
    "manuscript_qa",
    "writing_packet",
    "search_index_rebuild",
}
FORBIDDEN_STEP_FIELDS = {"command", "shell", "python", "script", "exec", "subprocess"}
REPORT_RECIPE_VERSION = "v2.3"


@dataclass(slots=True)
class WorkflowStep:
    step_id: str
    step_type: str
    name: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    output: str = ""
    enabled: bool = True
    raw_fields: list[str] = field(default_factory=list)


@dataclass(slots=True)
class WorkflowRecipe:
    recipe_id: str
    name: str
    description: str = ""
    project: str = ""
    steps: list[WorkflowStep] = field(default_factory=list)
    dry_run_default: bool = True
    outputs: dict[str, str] = field(default_factory=dict)
    safety_level: str = "read_only"
    source_path: str = ""


@dataclass(slots=True)
class WorkflowFinding:
    severity: str
    code: str
    step_id: str
    message: str
    suggested_action: str = ""


@dataclass(slots=True)
class WorkflowResult:
    step_id: str
    step_type: str
    status: str
    message: str
    output_paths: list[str] = field(default_factory=list)
    findings: list[WorkflowFinding] = field(default_factory=list)
    elapsed_seconds: float = 0.0


@dataclass(slots=True)
class WorkflowRun:
    recipe: WorkflowRecipe
    project: str
    root: str
    dry_run: bool
    results: list[WorkflowResult] = field(default_factory=list)
    output_paths: list[str] = field(default_factory=list)

    @property
    def errors(self) -> list[WorkflowFinding]:
        return [finding for result in self.results for finding in result.findings if finding.severity == "error"]

    @property
    def warnings(self) -> list[WorkflowFinding]:
        return [finding for result in self.results for finding in result.findings if finding.severity == "warning"]


@dataclass(slots=True)
class WorkflowPaths:
    root: Path
    project: str
    profile: ProjectProfile | None
    registry: Path
    bibtex: Path
    notes_dir: Path
    themes: Path
    reports_dir: Path


@dataclass(slots=True)
class WorkflowData:
    paths: WorkflowPaths
    papers: list[Paper]
    notes: list[PaperNote]
    claims: list[Claim]
    entries: list[BibTeXEntry]
    themes: list[ProjectTheme]


def builtin_recipes() -> dict[str, WorkflowRecipe]:
    return {recipe.recipe_id: recipe for recipe in _builtin_recipe_list()}


def list_workflow_recipes(project: str = "", *, root: str | Path = ".") -> list[WorkflowRecipe]:
    recipes = list(builtin_recipes().values())
    if project:
        recipes.extend(load_project_recipes(project, root=root, strict=False))
    return sorted(recipes, key=lambda recipe: recipe.recipe_id)


def load_project_recipes(project: str, *, root: str | Path = ".", strict: bool = True) -> list[WorkflowRecipe]:
    profile = load_project_profile(project, root=root)
    workflow_dir = Path(profile.root) / "workflows"
    if not workflow_dir.exists():
        return []
    recipes: list[WorkflowRecipe] = []
    for path in sorted(workflow_dir.glob("*.json")):
        try:
            recipe = load_workflow_recipe(path)
        except ValueError:
            if strict:
                raise
            continue
        recipes.append(recipe)
    return recipes


def find_workflow_recipe(recipe_ref: str, *, project: str = "", root: str | Path = ".") -> WorkflowRecipe:
    path = Path(recipe_ref)
    if path.exists():
        return load_workflow_recipe(path)
    builtins = builtin_recipes()
    if recipe_ref in builtins:
        return builtins[recipe_ref]
    if project:
        for recipe in load_project_recipes(project, root=root, strict=True):
            if recipe.recipe_id == recipe_ref or Path(recipe.source_path).stem == recipe_ref:
                return recipe
    raise ValueError(f"unknown workflow recipe: {recipe_ref}")


def load_workflow_recipe(path: str | Path) -> WorkflowRecipe:
    target = Path(path)
    data = load_json(target)
    recipe = workflow_recipe_from_dict(data, source_path=str(target))
    findings = validate_workflow_recipe(recipe)
    errors = [finding for finding in findings if finding.severity == "error"]
    if errors:
        details = "; ".join(f"{finding.step_id}: {finding.message}" for finding in errors)
        raise ValueError(f"invalid workflow recipe {target}: {details}")
    return recipe


def validate_workflow_recipe_file(path: str | Path) -> tuple[WorkflowRecipe, list[WorkflowFinding]]:
    target = Path(path)
    recipe = workflow_recipe_from_dict(load_json(target), source_path=str(target))
    return recipe, validate_workflow_recipe(recipe)


def save_workflow_recipe(recipe: WorkflowRecipe, path: str | Path, *, force: bool = False) -> Path:
    return write_json(path, workflow_recipe_to_dict(recipe), force=force)


def workflow_recipe_from_dict(data: dict[str, Any], *, source_path: str = "") -> WorkflowRecipe:
    if not isinstance(data, dict):
        raise ValueError("workflow recipe must be a JSON object")
    raw_steps = data.get("steps", [])
    if not isinstance(raw_steps, list):
        raise ValueError("workflow recipe field 'steps' must be a list")
    steps: list[WorkflowStep] = []
    for index, raw_step in enumerate(raw_steps, start=1):
        if not isinstance(raw_step, dict):
            raise ValueError(f"workflow step {index} must be a JSON object")
        step_id = str(raw_step.get("step_id") or raw_step.get("id") or f"step_{index}")
        params = raw_step.get("params", {})
        if not isinstance(params, dict):
            raise ValueError(f"workflow step {step_id} params must be a JSON object")
        steps.append(
            WorkflowStep(
                step_id=step_id,
                step_type=str(raw_step.get("step_type") or raw_step.get("type") or ""),
                name=str(raw_step.get("name") or step_id),
                params=dict(params),
                output=str(raw_step.get("output") or ""),
                enabled=bool(raw_step.get("enabled", True)),
                raw_fields=sorted(str(key) for key in raw_step),
            )
        )
    outputs = data.get("outputs", {})
    if not isinstance(outputs, dict):
        raise ValueError("workflow recipe field 'outputs' must be a JSON object")
    return WorkflowRecipe(
        recipe_id=str(data.get("recipe_id") or data.get("id") or Path(source_path).stem),
        name=str(data.get("name") or data.get("recipe_id") or Path(source_path).stem or "workflow"),
        description=str(data.get("description") or ""),
        project=str(data.get("project") or ""),
        steps=steps,
        dry_run_default=bool(data.get("dry_run_default", True)),
        outputs={str(key): str(value) for key, value in outputs.items()},
        safety_level=str(data.get("safety_level") or "read_only"),
        source_path=source_path,
    )


def workflow_recipe_to_dict(recipe: WorkflowRecipe) -> dict[str, Any]:
    return {
        "recipe_id": recipe.recipe_id,
        "name": recipe.name,
        "description": recipe.description,
        "project": recipe.project,
        "dry_run_default": recipe.dry_run_default,
        "safety_level": recipe.safety_level,
        "outputs": recipe.outputs,
        "steps": [
            {
                "step_id": step.step_id,
                "name": step.name,
                "step_type": step.step_type,
                "params": step.params,
                "output": step.output,
                "enabled": step.enabled,
            }
            for step in recipe.steps
        ],
    }


def validate_workflow_recipe(recipe: WorkflowRecipe) -> list[WorkflowFinding]:
    findings: list[WorkflowFinding] = []
    if not recipe.recipe_id:
        findings.append(WorkflowFinding("error", "recipe_missing_id", "recipe", "Recipe is missing recipe_id."))
    if not recipe.steps:
        findings.append(WorkflowFinding("warning", "recipe_no_steps", "recipe", "Recipe has no steps."))
    seen: set[str] = set()
    for step in recipe.steps:
        if not step.step_id:
            findings.append(WorkflowFinding("error", "step_missing_id", "[missing]", "Workflow step is missing step_id."))
        if step.step_id in seen:
            findings.append(WorkflowFinding("error", "duplicate_step_id", step.step_id, "Workflow step_id is duplicated."))
        seen.add(step.step_id)
        if step.step_type not in ALLOWED_STEP_TYPES:
            findings.append(
                WorkflowFinding(
                    "error",
                    "unknown_step_type",
                    step.step_id,
                    f"Unknown step_type `{step.step_type}`.",
                    suggested_action=f"Use one of: {', '.join(sorted(ALLOWED_STEP_TYPES))}.",
                )
            )
        forbidden = sorted((set(step.params) | set(step.raw_fields)) & FORBIDDEN_STEP_FIELDS)
        if forbidden:
            findings.append(
                WorkflowFinding(
                    "error",
                    "forbidden_execution_field",
                    step.step_id,
                    f"Workflow step contains forbidden execution field(s): {', '.join(forbidden)}.",
                    suggested_action="Use declarative built-in step types only; shell and Python execution are not supported.",
                )
            )
    return findings


def workflow_recipe_summary(recipe: WorkflowRecipe) -> str:
    return f"{recipe.recipe_id}\t{recipe.safety_level}\tdry_run_default={str(recipe.dry_run_default).lower()}\tsteps={len(recipe.steps)}\t{recipe.name}"


def workflow_recipe_markdown(recipe: WorkflowRecipe) -> str:
    lines = [
        f"# Workflow Recipe: {recipe.name}",
        "",
        f"Recipe ID: `{recipe.recipe_id}`",
        f"Safety level: `{recipe.safety_level}`",
        f"Dry-run default: `{str(recipe.dry_run_default).lower()}`",
        f"Source: `{recipe.source_path or 'built-in'}`",
        "",
        recipe.description or "No description provided.",
        "",
        "## Steps",
        "",
        "| Step | Type | Enabled | Output |",
        "| --- | --- | --- | --- |",
    ]
    for step in recipe.steps:
        output = step.output or step.params.get("output", "")
        step_name = f"<br>{_escape(step.name)}" if step.name else ""
        lines.append(f"| `{_escape(step.step_id)}`{step_name} | `{_escape(step.step_type)}` | {str(step.enabled).lower()} | `{_escape(output or '[none]')}` |")
    findings = validate_workflow_recipe(recipe)
    lines.extend(["", "## Validation", ""])
    if findings:
        for finding in findings:
            lines.append(f"- **{finding.severity} {finding.code}** `{finding.step_id}`: {finding.message}")
    else:
        lines.append("Recipe is valid.")
    return "\n".join(lines).rstrip() + "\n"


def workflow_validation_markdown(recipe: WorkflowRecipe, findings: list[WorkflowFinding]) -> str:
    lines = [
        "# Workflow Recipe Validation",
        "",
        f"Recipe ID: `{recipe.recipe_id}`",
        f"Source: `{recipe.source_path or 'built-in'}`",
        f"Steps: {len(recipe.steps)}",
        "",
    ]
    if not findings:
        lines.append("No validation findings.")
    else:
        lines.extend(["| Severity | Code | Step | Message | Suggested action |", "| --- | --- | --- | --- | --- |"])
        for finding in findings:
            lines.append(
                f"| {finding.severity} | `{finding.code}` | `{_escape(finding.step_id)}` | {_escape(finding.message)} | {_escape(finding.suggested_action)} |"
            )
    return "\n".join(lines).rstrip() + "\n"


def workflow_run_report(run: WorkflowRun) -> str:
    recipe = run.recipe
    lines = [
        f"# Workflow Run: {recipe.name}",
        "",
        "This report was generated from a local declarative workflow recipe. It does not execute shell commands, run untrusted Python code, use cloud services, or fabricate evidence.",
        "",
        f"Recipe ID: `{recipe.recipe_id}`",
        f"Project: `{run.project or recipe.project or 'default data workflow'}`",
        f"Root: `{_escape(run.root)}`",
        f"Dry run: `{str(run.dry_run).lower()}`",
        f"Safety level: `{recipe.safety_level}`",
        "",
        "## Step Results",
        "",
        "| Step | Type | Status | Message | Outputs |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in run.results:
        outputs = "<br>".join(f"`{_escape(path)}`" for path in result.output_paths) or ""
        lines.append(
            f"| `{_escape(result.step_id)}` | `{_escape(result.step_type)}` | {result.status} | {_escape(result.message)} | {outputs} |"
        )
    lines.extend(
        [
            "",
            "## Findings",
            "",
        ]
    )
    findings = [finding for result in run.results for finding in result.findings]
    if not findings:
        lines.append("No workflow findings.")
    else:
        lines.extend(["| Severity | Code | Step | Message | Suggested action |", "| --- | --- | --- | --- | --- |"])
        for finding in findings:
            lines.append(
                f"| {finding.severity} | `{finding.code}` | `{_escape(finding.step_id)}` | {_escape(finding.message)} | {_escape(finding.suggested_action)} |"
            )
    if run.output_paths:
        lines.extend(["", "## Files Written", ""])
        for path in run.output_paths:
            lines.append(f"- `{_escape(path)}`")
    return "\n".join(lines).rstrip() + "\n"


def run_workflow(
    recipe: WorkflowRecipe,
    *,
    project: str = "",
    root: str | Path = ".",
    dry_run: bool | None = None,
    force: bool = False,
    theme: str = "",
    manuscript: str = "",
) -> WorkflowRun:
    selected_project = project or recipe.project
    run_dry = recipe.dry_run_default if dry_run is None else dry_run
    data = _load_workflow_data(root=root, project=selected_project)
    run = WorkflowRun(
        recipe=recipe,
        project=selected_project,
        root=display_path(data.paths.root, base_path=Path(".")),
        dry_run=run_dry,
    )
    validation_findings = validate_workflow_recipe(recipe)
    if any(finding.severity == "error" for finding in validation_findings):
        result = WorkflowResult("recipe", "validate_recipe", "failed", "Recipe validation failed.", findings=validation_findings)
        run.results.append(result)
        return run
    options = {"theme": theme, "manuscript": manuscript, "project": selected_project}
    for step in recipe.steps:
        run.results.append(_run_step(step, recipe=recipe, data=data, dry_run=run_dry, force=force, options=options))
    for result in run.results:
        run.output_paths.extend(result.output_paths)
    return run


def write_workflow_run_report(run: WorkflowRun, path: str | Path, *, force: bool = False) -> Path:
    return write_text(path, workflow_run_report(run), force=force)


def default_workflow_report_path(recipe: WorkflowRecipe, data_paths: WorkflowPaths) -> Path:
    return data_paths.reports_dir / f"workflow_{normalize_tag(recipe.recipe_id)}_{REPORT_RECIPE_VERSION.replace('.', '_')}.md"


def default_workflow_run_report_path(recipe: WorkflowRecipe, *, project: str = "", root: str | Path = ".") -> Path:
    data = _load_workflow_data(root=root, project=project or recipe.project)
    return default_workflow_report_path(recipe, data.paths)


def _load_workflow_data(*, root: str | Path = ".", project: str = "") -> WorkflowData:
    root_path = Path(root).resolve()
    profile = load_project_profile(project, root=root_path) if project else None
    paths = WorkflowPaths(
        root=Path(profile.root) if profile else root_path,
        project=profile.name if profile else project,
        profile=profile,
        registry=Path(profile.registry_path) if profile else default_registry_path(root_path),
        bibtex=Path(profile.bibtex_path) if profile else default_bibtex_path(root_path),
        notes_dir=Path(profile.notes_dir) if profile else default_notes_dir(root_path),
        themes=Path(profile.themes_path) if profile else default_themes_path(root_path),
        reports_dir=Path(profile.reports_dir) if profile else default_reports_dir(root_path),
    )
    papers = load_registry(paths.registry) if paths.registry.exists() else []
    notes = collect_notes(paths.notes_dir) if paths.notes_dir.exists() else []
    claims = [claim for note in notes for claim in note.claims]
    entries = parse_bibtex_file(paths.bibtex) if paths.bibtex.exists() else []
    themes = load_themes(paths.themes) if paths.themes.exists() else []
    return WorkflowData(paths=paths, papers=papers, notes=notes, claims=claims, entries=entries, themes=themes)


def _run_step(
    step: WorkflowStep,
    *,
    recipe: WorkflowRecipe,
    data: WorkflowData,
    dry_run: bool,
    force: bool,
    options: dict[str, str],
) -> WorkflowResult:
    started = perf_counter()
    if not step.enabled:
        return WorkflowResult(step.step_id, step.step_type, "skipped", "Step is disabled.")
    try:
        result = _dispatch_step(step, recipe=recipe, data=data, dry_run=dry_run, force=force, options=options)
    except Exception as exc:  # Keep workflow failures reportable instead of crashing mid-run.
        result = WorkflowResult(
            step.step_id,
            step.step_type,
            "failed",
            str(exc),
            findings=[WorkflowFinding("error", "step_failed", step.step_id, str(exc), "Fix the step inputs or run this command directly for more detail.")],
        )
    result.elapsed_seconds = round(perf_counter() - started, 4)
    return result


def _dispatch_step(
    step: WorkflowStep,
    *,
    recipe: WorkflowRecipe,
    data: WorkflowData,
    dry_run: bool,
    force: bool,
    options: dict[str, str],
) -> WorkflowResult:
    if step.step_type == "validate_registry":
        return _step_validate_registry(step, data)
    if step.step_type == "validate_bibtex":
        return _step_validate_bibtex(step, data)
    if step.step_type == "extract_claims":
        return _step_extract_claims(step, recipe, data, dry_run=dry_run, force=force)
    if step.step_type == "generate_report":
        return _step_generate_report(step, recipe, data, dry_run=dry_run, force=force, options=options)
    if step.step_type == "run_rules":
        return _step_run_rules(step, recipe, data, dry_run=dry_run, force=force)
    if step.step_type == "run_doctor":
        return _step_doctor(step, recipe, data, dry_run=dry_run, force=force)
    if step.step_type == "run_integrity":
        return _step_integrity(step, recipe, data, dry_run=dry_run, force=force)
    if step.step_type == "run_dashboard":
        return _step_dashboard(step, recipe, data, dry_run=dry_run, force=force)
    if step.step_type == "export_claims":
        return _step_export_claims(step, recipe, data, dry_run=dry_run, force=force)
    if step.step_type == "backup_create":
        return _step_backup_create(step, data, dry_run=dry_run)
    if step.step_type == "manuscript_qa":
        return _step_manuscript_qa(step, recipe, data, dry_run=dry_run, force=force, options=options)
    if step.step_type == "writing_packet":
        return _step_writing_packet(step, recipe, data, dry_run=dry_run, force=force, options=options)
    if step.step_type == "search_index_rebuild":
        return _step_search_index_rebuild(step, recipe, data, dry_run=dry_run, force=force)
    raise ValueError(f"unknown step type: {step.step_type}")


def _step_validate_registry(step: WorkflowStep, data: WorkflowData) -> WorkflowResult:
    findings = validate_registry_headers(data.paths.registry) + validate_registry(data.papers, root=data.paths.root, claims=data.claims)
    return _finding_result(step, findings, f"Validated registry with {len(data.papers)} paper(s).")


def _step_validate_bibtex(step: WorkflowStep, data: WorkflowData) -> WorkflowResult:
    findings = validate_bibtex(data.entries, data.papers)
    return _finding_result(step, findings, f"Validated {len(data.entries)} BibTeX entrie(s).")


def _step_extract_claims(step: WorkflowStep, recipe: WorkflowRecipe, data: WorkflowData, *, dry_run: bool, force: bool) -> WorkflowResult:
    output = _step_output_path(step, recipe, data, default_suffix="claims.csv")
    if dry_run:
        return WorkflowResult(step.step_id, step.step_type, "planned", f"Would export {len(data.claims)} extracted claim(s).", [display_path(output, base_path=data.paths.root)])
    save_claims_csv(data.claims, output, force=force, root=data.paths.root)
    return WorkflowResult(step.step_id, step.step_type, "passed", f"Exported {len(data.claims)} extracted claim(s).", [display_path(output, base_path=data.paths.root)])


def _step_generate_report(
    step: WorkflowStep,
    recipe: WorkflowRecipe,
    data: WorkflowData,
    *,
    dry_run: bool,
    force: bool,
    options: dict[str, str],
) -> WorkflowResult:
    report_type = str(step.params.get("report_type") or "")
    content = _build_report(report_type, data, theme=_resolve_value(str(step.params.get("theme") or ""), options))
    output = _step_output_path(step, recipe, data, default_suffix=f"{normalize_tag(report_type or step.step_id)}.md")
    if dry_run:
        return WorkflowResult(step.step_id, step.step_type, "planned", f"Would generate {report_type} report.", [display_path(output, base_path=data.paths.root)])
    write_text(output, content, force=force)
    return WorkflowResult(step.step_id, step.step_type, "passed", f"Generated {report_type} report.", [display_path(output, base_path=data.paths.root)])


def _step_run_rules(step: WorkflowStep, recipe: WorkflowRecipe, data: WorkflowData, *, dry_run: bool, force: bool) -> WorkflowResult:
    rule_set = _load_rules_for_data(data)
    config_findings = validate_rule_set(rule_set)
    result = run_rule_set(rule_set, _rule_context(data), include_builtins=bool(step.params.get("include_builtins", True)))
    findings = [_workflow_finding_from_rule(step.step_id, finding) for finding in [*config_findings, *result.findings]]
    output = _step_output_path(step, recipe, data, default_suffix="rules.md")
    if dry_run:
        status = "planned" if not any(item.severity == "error" for item in findings) else "planned_with_errors"
        return WorkflowResult(step.step_id, step.step_type, status, f"Would run rules with {len(result.findings)} finding(s).", [display_path(output, base_path=data.paths.root)], findings)
    write_text(output, rule_report(result), force=force)
    return WorkflowResult(step.step_id, step.step_type, "passed" if not result.errors else "failed", f"Ran rules with {len(result.findings)} finding(s).", [display_path(output, base_path=data.paths.root)], findings)


def _step_doctor(step: WorkflowStep, recipe: WorkflowRecipe, data: WorkflowData, *, dry_run: bool, force: bool) -> WorkflowResult:
    findings = _workspace_findings(data)
    output = _step_output_path(step, recipe, data, default_suffix="workspace_health.md")
    workflow_findings = [_workflow_finding_from_validation(step.step_id, finding) for finding in findings]
    if dry_run:
        return WorkflowResult(step.step_id, step.step_type, "planned", f"Would run workspace health with {len(findings)} finding(s).", [display_path(output, base_path=data.paths.root)], workflow_findings)
    write_text(output, workspace_health_report(findings), force=force)
    return WorkflowResult(step.step_id, step.step_type, "passed" if not any(f.severity == "error" for f in findings) else "failed", f"Ran workspace health with {len(findings)} finding(s).", [display_path(output, base_path=data.paths.root)], workflow_findings)


def _step_integrity(step: WorkflowStep, recipe: WorkflowRecipe, data: WorkflowData, *, dry_run: bool, force: bool) -> WorkflowResult:
    result = check_workspace_integrity(
        root=data.paths.root,
        registry_path=data.paths.registry,
        bibtex_path=data.paths.bibtex,
        notes_dir=data.paths.notes_dir,
        themes_path=data.paths.themes,
        reports_dir=data.paths.reports_dir,
        profile=data.paths.profile,
    )
    workflow_findings = [_workflow_finding_from_validation(step.step_id, finding) for finding in result.findings]
    output = _step_output_path(step, recipe, data, default_suffix="integrity.md")
    if dry_run:
        return WorkflowResult(step.step_id, step.step_type, "planned", f"Would run integrity check with {len(result.findings)} finding(s).", [display_path(output, base_path=data.paths.root)], workflow_findings)
    write_text(output, workspace_integrity_report(result), force=force)
    return WorkflowResult(step.step_id, step.step_type, "passed" if not result.errors else "failed", f"Ran integrity check with {len(result.findings)} finding(s).", [display_path(output, base_path=data.paths.root)], workflow_findings)


def _step_dashboard(step: WorkflowStep, recipe: WorkflowRecipe, data: WorkflowData, *, dry_run: bool, force: bool) -> WorkflowResult:
    dashboard = _build_workflow_dashboard(data)
    output = _step_output_path(step, recipe, data, default_suffix="dashboard.md")
    if dry_run:
        return WorkflowResult(step.step_id, step.step_type, "planned", "Would generate dashboard report.", [display_path(output, base_path=data.paths.root)])
    write_text(output, dashboard_markdown(dashboard, title="Workflow Dashboard v2.3"), force=force)
    return WorkflowResult(step.step_id, step.step_type, "passed", "Generated dashboard report.", [display_path(output, base_path=data.paths.root)])


def _step_export_claims(step: WorkflowStep, recipe: WorkflowRecipe, data: WorkflowData, *, dry_run: bool, force: bool) -> WorkflowResult:
    output_format = str(step.params.get("format") or "csv")
    suffix = "claims.json" if output_format == "json" else "claims.csv"
    output = _step_output_path(step, recipe, data, default_suffix=suffix)
    if dry_run:
        return WorkflowResult(step.step_id, step.step_type, "planned", f"Would export {len(data.claims)} claims as {output_format}.", [display_path(output, base_path=data.paths.root)])
    if output_format == "json":
        export_claims_json(data.claims, output, force=force)
    else:
        export_claims_csv(data.claims, output, force=force, root=data.paths.root)
    return WorkflowResult(step.step_id, step.step_type, "passed", f"Exported {len(data.claims)} claims as {output_format}.", [display_path(output, base_path=data.paths.root)])


def _step_backup_create(step: WorkflowStep, data: WorkflowData, *, dry_run: bool) -> WorkflowResult:
    if dry_run:
        return WorkflowResult(step.step_id, step.step_type, "planned", "Would create a local backup snapshot. PDFs and caches remain excluded by default.")
    manifest, backup_path = create_backup(
        root=data.paths.root,
        registry_path=data.paths.registry,
        bibtex_path=data.paths.bibtex,
        notes_dir=data.paths.notes_dir,
        themes_path=data.paths.themes,
        reports_dir=data.paths.reports_dir,
        profile=data.paths.profile,
        include_reports=bool(step.params.get("include_reports", False)),
        notes=str(step.params.get("notes") or "Created by workflow runner."),
    )
    return WorkflowResult(step.step_id, step.step_type, "passed", f"Created backup {manifest.backup_id}.", [display_path(backup_path, base_path=data.paths.root)])


def _step_manuscript_qa(
    step: WorkflowStep,
    recipe: WorkflowRecipe,
    data: WorkflowData,
    *,
    dry_run: bool,
    force: bool,
    options: dict[str, str],
) -> WorkflowResult:
    manuscript = _resolve_value(str(step.params.get("manuscript") or "$manuscript"), options)
    if not manuscript:
        return WorkflowResult(step.step_id, step.step_type, "skipped", "No manuscript path supplied.")
    result = audit_manuscript(manuscript, data.papers, data.notes, data.claims, data.entries, data.themes, project=data.paths.project)
    output = _step_output_path(step, recipe, data, default_suffix="manuscript_qa.md")
    findings = [WorkflowFinding(finding.severity, finding.code, step.step_id, finding.message, getattr(finding, "suggested_action", "")) for finding in result.audit.findings]
    if dry_run:
        return WorkflowResult(step.step_id, step.step_type, "planned", f"Would run manuscript QA with verdict {result.verdict}.", [display_path(output, base_path=data.paths.root)], findings)
    write_text(output, manuscript_qa_report(result), force=force)
    return WorkflowResult(step.step_id, step.step_type, "passed", f"Ran manuscript QA with verdict {result.verdict}.", [display_path(output, base_path=data.paths.root)], findings)


def _step_writing_packet(
    step: WorkflowStep,
    recipe: WorkflowRecipe,
    data: WorkflowData,
    *,
    dry_run: bool,
    force: bool,
    options: dict[str, str],
) -> WorkflowResult:
    from .authoring import writing_packet_report

    theme = _resolve_value(str(step.params.get("theme") or "$theme"), options)
    if not theme:
        return WorkflowResult(step.step_id, step.step_type, "skipped", "No theme supplied for writing packet.")
    output = _step_output_path(step, recipe, data, default_suffix=f"{normalize_tag(theme)}_writing_packet.md")
    if dry_run:
        return WorkflowResult(step.step_id, step.step_type, "planned", f"Would generate writing packet for {theme}.", [display_path(output, base_path=data.paths.root)])
    content = writing_packet_report(theme, data.papers, data.notes, data.claims, data.entries, data.themes, project=data.paths.project)
    write_text(output, content, force=force)
    return WorkflowResult(step.step_id, step.step_type, "passed", f"Generated writing packet for {theme}.", [display_path(output, base_path=data.paths.root)])


def _step_search_index_rebuild(step: WorkflowStep, recipe: WorkflowRecipe, data: WorkflowData, *, dry_run: bool, force: bool) -> WorkflowResult:
    from .index import default_index_path

    index_path = Path(str(step.params.get("index") or default_index_path(data.paths.root)))
    if not index_path.is_absolute():
        index_path = data.paths.root / index_path
    records = build_index_records(
        registry_path=data.paths.registry,
        notes_dir=data.paths.notes_dir,
        bibtex_path=data.paths.bibtex,
        themes_path=data.paths.themes,
        project_id=data.paths.project,
        include_text=bool(step.params.get("include_text", False)),
        root=data.paths.root,
    )
    output = _step_output_path(step, recipe, data, default_suffix="index_status.md")
    if dry_run:
        return WorkflowResult(step.step_id, step.step_type, "planned", f"Would rebuild local search index with {len(records)} record(s).", [display_path(index_path, base_path=data.paths.root), display_path(output, base_path=data.paths.root)])
    status = rebuild_index(index_path, records, project_id=data.paths.project)
    write_text(output, index_status_markdown(status, base_path=data.paths.root), force=force)
    return WorkflowResult(step.step_id, step.step_type, "passed", f"Rebuilt local search index with {len(records)} record(s).", [display_path(index_path, base_path=data.paths.root), display_path(output, base_path=data.paths.root)])


def _build_report(report_type: str, data: WorkflowData, *, theme: str = "") -> str:
    bib_findings = validate_bibtex(data.entries, data.papers) if data.entries else []
    audit_findings = citation_audit(data.papers, data.notes, data.claims, data.entries, data.themes, root=data.paths.root)
    if report_type == "inventory":
        return inventory_report(data.papers, root=data.paths.root, claims=data.claims)
    if report_type == "reading-status":
        return reading_status_report(data.papers)
    if report_type == "bibtex-audit":
        return bibtex_audit_report(data.entries, bib_findings)
    if report_type == "evidence-map":
        return evidence_map_report(data.papers, data.claims, data.themes, data.notes)
    if report_type == "citation-audit":
        return citation_audit_report(audit_findings)
    if report_type == "missing-notes":
        return missing_notes_report(data.papers, data.notes)
    if report_type == "weak-claims":
        return weak_claims_report(data.claims)
    if report_type == "theme-dashboard":
        return theme_coverage_dashboard_report(data.papers, data.claims, data.themes, data.notes)
    if report_type == "missing-evidence":
        return missing_evidence_report(data.claims)
    if report_type == "workspace-health":
        return workspace_health_report(_workspace_findings(data))
    if report_type == "writing-packet":
        from .authoring import writing_packet_report

        if not theme:
            raise ValueError("writing-packet report requires a theme")
        return writing_packet_report(theme, data.papers, data.notes, data.claims, data.entries, data.themes, project=data.paths.project)
    raise ValueError(f"unsupported report_type for workflow: {report_type}")


def _finding_result(step: WorkflowStep, findings: list[ValidationFinding], message: str) -> WorkflowResult:
    workflow_findings = [_workflow_finding_from_validation(step.step_id, finding) for finding in findings]
    status = "passed" if not any(finding.severity == "error" for finding in findings) else "failed"
    return WorkflowResult(step.step_id, step.step_type, status, f"{message} Findings: {len(findings)}.", findings=workflow_findings)


def _workspace_findings(data: WorkflowData) -> list[ValidationFinding]:
    return workspace_health(
        root=data.paths.root,
        registry_path=data.paths.registry,
        bibtex_path=data.paths.bibtex,
        notes_dir=data.paths.notes_dir,
        themes_path=data.paths.themes,
        reports_dir=data.paths.reports_dir,
        profile=data.paths.profile,
    )


def _rule_context(data: WorkflowData) -> RuleContext:
    return RuleContext(
        project=data.paths.project,
        root=str(data.paths.root),
        registry_path=str(data.paths.registry),
        bibtex_path=str(data.paths.bibtex),
        notes_dir=str(data.paths.notes_dir),
        themes_path=str(data.paths.themes),
        reports_dir=str(data.paths.reports_dir),
        profile=data.paths.profile,
        papers=data.papers,
        bibtex_entries=data.entries,
        notes=data.notes,
        claims=data.claims,
        themes=data.themes,
    )


def _load_rules_for_data(data: WorkflowData):
    candidate = data.paths.root / "rules.json"
    if candidate.exists():
        return load_rule_set(candidate)
    return empty_rule_set()


def _build_workflow_dashboard(data: WorkflowData):
    bib_findings = validate_bibtex(data.entries, data.papers) if data.entries else []
    citation_findings = citation_audit(data.papers, data.notes, data.claims, data.entries, data.themes, root=data.paths.root)
    health_findings = _workspace_findings(data)
    rule_result = run_rule_set(_load_rules_for_data(data), _rule_context(data), include_builtins=True)
    return build_dashboard(
        project=data.paths.project or "default",
        root=display_path(data.paths.root, base_path=Path(".")),
        papers=data.papers,
        notes=data.notes,
        claims=data.claims,
        bibtex_entries=data.entries,
        themes=data.themes,
        project_profiles=[],
        bibtex_findings=bib_findings,
        citation_findings=citation_findings,
        health_findings=health_findings,
        rule_findings=rule_result.findings,
        manuscript_findings=[],
        reading_queue=[],
        followups=[],
        audit_events=[],
        report_paths=[],
        limit=10,
    )


def _workflow_finding_from_validation(step_id: str, finding: ValidationFinding) -> WorkflowFinding:
    return WorkflowFinding(
        severity=finding.severity,
        code=finding.code,
        step_id=step_id,
        message=f"{finding.identifier}: {finding.message}" if finding.identifier else finding.message,
        suggested_action=finding.suggestion,
    )


def _workflow_finding_from_rule(step_id: str, finding) -> WorkflowFinding:
    return WorkflowFinding(
        severity=finding.severity,
        code=finding.rule_id,
        step_id=step_id,
        message=f"{finding.identifier}: {finding.message}" if getattr(finding, "identifier", "") else finding.message,
        suggested_action=getattr(finding, "suggested_action", ""),
    )


def _step_output_path(step: WorkflowStep, recipe: WorkflowRecipe, data: WorkflowData, *, default_suffix: str) -> Path:
    raw = step.output or str(step.params.get("output") or "") or f"reports/workflow_{normalize_tag(recipe.recipe_id)}_{normalize_tag(step.step_id)}_{default_suffix}"
    path = Path(raw)
    if path.is_absolute():
        return path
    return data.paths.root / path


def _resolve_value(value: str, options: dict[str, str]) -> str:
    if value == "$theme":
        return options.get("theme", "")
    if value == "$manuscript":
        return options.get("manuscript", "")
    if value == "$project":
        return options.get("project", "")
    return value


def _escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _builtin_recipe_list() -> list[WorkflowRecipe]:
    return [
        WorkflowRecipe(
            recipe_id="daily_check",
            name="Daily Project Check",
            description="Validate the local registry and BibTeX, run workspace diagnostics, rules, and a dashboard report.",
            dry_run_default=False,
            safety_level="writes_reports",
            steps=[
                WorkflowStep("validate_registry", "validate_registry", "Validate registry"),
                WorkflowStep("validate_bibtex", "validate_bibtex", "Validate BibTeX"),
                WorkflowStep("doctor", "run_doctor", "Run workspace health", output="reports/workflow_daily_check_workspace_health.md"),
                WorkflowStep("rules", "run_rules", "Run rules", output="reports/workflow_daily_check_rules.md"),
                WorkflowStep("dashboard", "run_dashboard", "Generate dashboard", output="reports/workflow_daily_check_dashboard.md"),
            ],
        ),
        WorkflowRecipe(
            recipe_id="weekly_review",
            name="Weekly Review",
            description="Refresh claims and core evidence reports for a weekly literature-review check-in.",
            dry_run_default=False,
            safety_level="writes_reports",
            steps=[
                WorkflowStep("validate_registry", "validate_registry", "Validate registry"),
                WorkflowStep("validate_bibtex", "validate_bibtex", "Validate BibTeX"),
                WorkflowStep("extract_claims", "extract_claims", "Export claims", output="reports/workflow_weekly_review_claims.csv"),
                WorkflowStep("evidence_map", "generate_report", "Generate evidence map", params={"report_type": "evidence-map"}, output="reports/workflow_weekly_review_evidence_map.md"),
                WorkflowStep("citation_audit", "generate_report", "Generate citation audit", params={"report_type": "citation-audit"}, output="reports/workflow_weekly_review_citation_audit.md"),
                WorkflowStep("weak_claims", "generate_report", "Generate weak claims", params={"report_type": "weak-claims"}, output="reports/workflow_weekly_review_weak_claims.md"),
                WorkflowStep("dashboard", "run_dashboard", "Generate dashboard", output="reports/workflow_weekly_review_dashboard.md"),
            ],
        ),
        WorkflowRecipe(
            recipe_id="pre_writing_check",
            name="Pre-writing Check",
            description="Refresh evidence, citation, missing evidence, and optional theme writing-packet checks before drafting.",
            dry_run_default=False,
            safety_level="writes_reports",
            steps=[
                WorkflowStep("validate_registry", "validate_registry", "Validate registry"),
                WorkflowStep("validate_bibtex", "validate_bibtex", "Validate BibTeX"),
                WorkflowStep("evidence_map", "generate_report", "Generate evidence map", params={"report_type": "evidence-map"}, output="reports/workflow_pre_writing_evidence_map.md"),
                WorkflowStep("citation_audit", "generate_report", "Generate citation audit", params={"report_type": "citation-audit"}, output="reports/workflow_pre_writing_citation_audit.md"),
                WorkflowStep("missing_evidence", "generate_report", "Generate missing evidence", params={"report_type": "missing-evidence"}, output="reports/workflow_pre_writing_missing_evidence.md"),
                WorkflowStep("writing_packet", "writing_packet", "Generate writing packet if --theme is supplied", params={"theme": "$theme"}),
            ],
        ),
        WorkflowRecipe(
            recipe_id="pre_manuscript_check",
            name="Pre-manuscript Check",
            description="Run registry/BibTeX validation, evidence reports, and manuscript QA when a draft path is supplied.",
            dry_run_default=False,
            safety_level="writes_reports",
            steps=[
                WorkflowStep("validate_registry", "validate_registry", "Validate registry"),
                WorkflowStep("validate_bibtex", "validate_bibtex", "Validate BibTeX"),
                WorkflowStep("citation_audit", "generate_report", "Generate citation audit", params={"report_type": "citation-audit"}, output="reports/workflow_pre_manuscript_citation_audit.md"),
                WorkflowStep("manuscript_qa", "manuscript_qa", "Run manuscript QA if --manuscript is supplied", params={"manuscript": "$manuscript"}, output="reports/workflow_pre_manuscript_qa.md"),
            ],
        ),
        WorkflowRecipe(
            recipe_id="pre_backup_check",
            name="Pre-backup Check",
            description="Run validation and integrity checks before optionally creating a local backup.",
            dry_run_default=True,
            safety_level="writes_backup",
            steps=[
                WorkflowStep("validate_registry", "validate_registry", "Validate registry"),
                WorkflowStep("validate_bibtex", "validate_bibtex", "Validate BibTeX"),
                WorkflowStep("integrity", "run_integrity", "Run integrity check", output="reports/workflow_pre_backup_integrity.md"),
                WorkflowStep("backup", "backup_create", "Create backup when not dry-run"),
            ],
        ),
        WorkflowRecipe(
            recipe_id="external_user_demo",
            name="External User Demo",
            description="Run a safe synthetic demo workflow covering validation, claims, evidence reports, and dashboard output.",
            dry_run_default=False,
            safety_level="writes_reports",
            steps=[
                WorkflowStep("validate_registry", "validate_registry", "Validate registry"),
                WorkflowStep("validate_bibtex", "validate_bibtex", "Validate BibTeX"),
                WorkflowStep("extract_claims", "extract_claims", "Export claims", output="reports/workflow_external_demo_claims.csv"),
                WorkflowStep("evidence_map", "generate_report", "Generate evidence map", params={"report_type": "evidence-map"}, output="reports/workflow_external_demo_evidence_map.md"),
                WorkflowStep("citation_audit", "generate_report", "Generate citation audit", params={"report_type": "citation-audit"}, output="reports/workflow_external_demo_citation_audit.md"),
                WorkflowStep("dashboard", "run_dashboard", "Generate dashboard", output="reports/workflow_external_demo_dashboard.md"),
            ],
        ),
        WorkflowRecipe(
            recipe_id="release_candidate_check",
            name="Release Candidate Check",
            description="Run representative local validation, diagnostics, rules, dashboard, and index checks without cloud or shell execution.",
            dry_run_default=True,
            safety_level="read_only_or_cache",
            steps=[
                WorkflowStep("validate_registry", "validate_registry", "Validate registry"),
                WorkflowStep("validate_bibtex", "validate_bibtex", "Validate BibTeX"),
                WorkflowStep("doctor", "run_doctor", "Run workspace health", output="reports/workflow_release_candidate_workspace_health.md"),
                WorkflowStep("integrity", "run_integrity", "Run integrity check", output="reports/workflow_release_candidate_integrity.md"),
                WorkflowStep("rules", "run_rules", "Run rules", output="reports/workflow_release_candidate_rules.md"),
                WorkflowStep("dashboard", "run_dashboard", "Generate dashboard", output="reports/workflow_release_candidate_dashboard.md"),
                WorkflowStep("index", "search_index_rebuild", "Rebuild local search index when not dry-run", output="reports/workflow_release_candidate_index_status.md"),
            ],
        ),
    ]
