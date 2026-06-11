"""Local declarative rule engine for project-specific validation.

Rules are loaded from JSON and evaluated with explicit built-in condition
types only. This module never executes user-provided Python code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
import re
from typing import Any

from .audit import citation_audit
from .doctor import workspace_health
from .drafts import DraftAuditReport, ParagraphAuditFinding
from .manuscript import audit_manuscript
from .registry import display_authors, validate_registry, validate_registry_headers
from .schema import (
    BibTeXEntry,
    Claim,
    Paper,
    PaperNote,
    ProjectProfile,
    ProjectTheme,
    LocalFileRecord,
    ValidationFinding,
)
from .tags import group_claims_by_theme, normalize_tag, parse_tags, theme_by_tag


class RuleSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class RuleCategory(str, Enum):
    REGISTRY = "registry"
    BIBTEX = "bibtex"
    NOTE = "note"
    CLAIM = "claim"
    THEME = "theme"
    MANUSCRIPT = "manuscript"
    PROJECT = "project"
    FILE = "file"
    WORKSPACE = "workspace"
    IMPORT_EXPORT = "import_export"


RULE_TARGETS = {category.value for category in RuleCategory}
RULE_SEVERITIES = {severity.value for severity in RuleSeverity}
RULE_TYPES = {
    "required_field",
    "allowed_values",
    "regex_match",
    "min_count",
    "max_count",
    "contains_tag",
    "missing_note_for_status",
    "claim_strength_threshold",
    "evidence_type_required",
    "citation_key_required",
    "theme_min_papers",
    "theme_min_strong_claims",
    "manuscript_no_unknown_citations",
}
STRENGTH_ORDER = {"speculative": 0, "weak": 1, "moderate": 2, "strong": 3}


@dataclass(slots=True)
class Rule:
    rule_id: str
    name: str
    description: str = ""
    target: str = "workspace"
    severity: str = RuleSeverity.WARNING.value
    enabled: bool = True
    condition: dict[str, Any] = field(default_factory=dict)
    message: str = ""
    suggested_action: str = ""
    tags: list[str] = field(default_factory=list)
    project_scope: str = ""

    @property
    def rule_type(self) -> str:
        return str(self.condition.get("type", "")).strip()


@dataclass(slots=True)
class RuleSet:
    path: str = ""
    version: str = "1.5"
    name: str = "local rules"
    rules: list[Rule] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RuleFinding:
    severity: str
    rule_id: str
    target: str
    message: str
    identifier: str = ""
    suggested_action: str = ""
    source: str = ""
    category: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RuleContext:
    project: str = "default"
    root: str = "."
    registry_path: str = ""
    bibtex_path: str = ""
    notes_dir: str = ""
    themes_path: str = ""
    reports_dir: str = ""
    profile: ProjectProfile | None = None
    papers: list[Paper] = field(default_factory=list)
    bibtex_entries: list[BibTeXEntry] = field(default_factory=list)
    notes: list[PaperNote] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    themes: list[ProjectTheme] = field(default_factory=list)
    manuscript_audit: DraftAuditReport | None = None
    files: list[LocalFileRecord] = field(default_factory=list)


@dataclass(slots=True)
class RuleRunResult:
    context: RuleContext
    rule_set: RuleSet
    findings: list[RuleFinding] = field(default_factory=list)
    built_in_findings: list[RuleFinding] = field(default_factory=list)
    config_findings: list[RuleFinding] = field(default_factory=list)

    @property
    def errors(self) -> list[RuleFinding]:
        return [finding for finding in self.findings if finding.severity == RuleSeverity.ERROR.value]


BUILT_IN_RULE_DESCRIPTIONS: dict[str, str] = {
    "builtin.registry": "Adapts registry validation findings into rule-report findings.",
    "builtin.citation_audit": "Adapts citation-audit findings into rule-report findings.",
    "builtin.evidence_map": "Checks theme paper/claim coverage thresholds from local evidence maps.",
    "builtin.workspace_health": "Adapts workspace-health findings into rule-report findings.",
    "builtin.manuscript": "Adapts manuscript QA findings when a manuscript draft is supplied.",
}


def default_rule_file(root: str | Path = ".", *, project: str = "") -> Path:
    base = Path(root)
    if project:
        return base / "rules.json"
    return base / "rules.json"


def load_rule_set(path: str | Path) -> RuleSet:
    target = Path(path)
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid rule config JSON at {target}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("rule config must be a JSON object with a rules list")
    rules_data = data.get("rules", [])
    if not isinstance(rules_data, list):
        raise ValueError("rule config field 'rules' must be a list")
    rule_set = RuleSet(
        path=str(target),
        version=str(data.get("version", "1.5")),
        name=str(data.get("name", target.stem or "local rules")),
    )
    for index, raw_rule in enumerate(rules_data, start=1):
        if not isinstance(raw_rule, dict):
            raise ValueError(f"rule #{index} must be a JSON object")
        rule_set.rules.append(_rule_from_dict(raw_rule, index=index))
    return rule_set


def empty_rule_set(path: str = "") -> RuleSet:
    return RuleSet(path=path, name="no configured rules")


def validate_rule_set(rule_set: RuleSet) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    seen_ids: set[str] = set()
    for rule in rule_set.rules:
        if not rule.rule_id:
            findings.append(_config_finding("error", "config.missing_rule_id", "A rule is missing rule_id.", source=rule_set.path))
        if rule.rule_id in seen_ids:
            findings.append(
                _config_finding(
                    "error",
                    "config.duplicate_rule_id",
                    f"Rule ID {rule.rule_id!r} appears more than once.",
                    identifier=rule.rule_id,
                    source=rule_set.path,
                )
            )
        seen_ids.add(rule.rule_id)
        if rule.target not in RULE_TARGETS:
            findings.append(
                _config_finding(
                    "error",
                    "config.invalid_target",
                    f"{rule.rule_id} target {rule.target!r} is not supported.",
                    identifier=rule.rule_id,
                    source=rule_set.path,
                    suggested_action=f"Use one of: {', '.join(sorted(RULE_TARGETS))}.",
                )
            )
        if rule.severity not in RULE_SEVERITIES:
            findings.append(
                _config_finding(
                    "error",
                    "config.invalid_severity",
                    f"{rule.rule_id} severity {rule.severity!r} is not supported.",
                    identifier=rule.rule_id,
                    source=rule_set.path,
                    suggested_action=f"Use one of: {', '.join(sorted(RULE_SEVERITIES))}.",
                )
            )
        if rule.rule_type not in RULE_TYPES:
            findings.append(
                _config_finding(
                    "error",
                    "config.invalid_condition_type",
                    f"{rule.rule_id} condition type {rule.rule_type!r} is not supported.",
                    identifier=rule.rule_id,
                    source=rule_set.path,
                    suggested_action=f"Use one of: {', '.join(sorted(RULE_TYPES))}.",
                )
            )
        findings.extend(_validate_condition_shape(rule, source=rule_set.path))
    return findings


def run_rule_set(rule_set: RuleSet, context: RuleContext, *, include_builtins: bool = True) -> RuleRunResult:
    config_findings = validate_rule_set(rule_set)
    executable = [rule for rule in rule_set.rules if rule.enabled]
    if not any(finding.severity == RuleSeverity.ERROR.value for finding in config_findings):
        for rule in executable:
            config_findings.extend(_run_rule(rule, context))
    built_in = built_in_rule_findings(context) if include_builtins else []
    return RuleRunResult(
        context=context,
        rule_set=rule_set,
        findings=built_in + config_findings,
        built_in_findings=built_in,
        config_findings=config_findings,
    )


def built_in_rule_findings(context: RuleContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    registry_root = context.root
    registry_path = Path(context.registry_path) if context.registry_path else None
    if registry_path and registry_path.exists():
        for finding in validate_registry_headers(registry_path):
            findings.append(_from_validation_finding(finding, "builtin.registry", "registry"))
    for finding in validate_registry(context.papers, root=registry_root, claims=context.claims):
        findings.append(_from_validation_finding(finding, "builtin.registry", "registry"))
    for finding in citation_audit(
        context.papers,
        context.notes,
        context.claims,
        context.bibtex_entries,
        context.themes,
        root=context.root,
    ):
        findings.append(
            RuleFinding(
                severity=finding.severity,
                rule_id=f"builtin.citation_audit.{finding.code}",
                target="claim" if finding.claim_id else "registry",
                identifier=finding.claim_id or finding.paper_id or finding.theme,
                message=finding.message,
                suggested_action=finding.suggestion,
                category="citation_audit",
            )
        )
    grouped = group_claims_by_theme(context.claims, context.themes)
    for theme in context.themes:
        theme_claims = grouped.get(theme.theme_id, [])
        papers = {claim.paper_id for claim in theme_claims if claim.paper_id}
        if len(theme_claims) < theme.min_claims:
            findings.append(
                RuleFinding(
                    severity="warning",
                    rule_id="builtin.evidence_map.theme_min_claims",
                    target="theme",
                    identifier=theme.theme_id,
                    message=f"{theme.name} has {len(theme_claims)} claim(s); target is {theme.min_claims}.",
                    suggested_action="Add verified claim blocks or lower the theme threshold.",
                    category="evidence_map",
                )
            )
        if len(papers) < theme.min_papers:
            findings.append(
                RuleFinding(
                    severity="warning",
                    rule_id="builtin.evidence_map.theme_min_papers",
                    target="theme",
                    identifier=theme.theme_id,
                    message=f"{theme.name} has evidence from {len(papers)} paper(s); target is {theme.min_papers}.",
                    suggested_action="Add evidence from more papers or lower the theme threshold.",
                    category="evidence_map",
                )
            )
    if context.registry_path or context.notes_dir or context.bibtex_path:
        for finding in workspace_health(
            root=context.root,
            registry_path=context.registry_path,
            bibtex_path=context.bibtex_path,
            notes_dir=context.notes_dir,
            themes_path=context.themes_path,
            reports_dir=context.reports_dir,
            profile=context.profile,
        ):
            findings.append(_from_validation_finding(finding, "builtin.workspace_health", "workspace"))
    if context.manuscript_audit is not None:
        for finding in context.manuscript_audit.findings:
            findings.append(_from_paragraph_finding(finding))
    return _dedupe_findings(findings)


def maybe_audit_manuscript(
    manuscript_path: str | Path | None,
    context: RuleContext,
) -> DraftAuditReport | None:
    if not manuscript_path:
        return None
    return audit_manuscript(
        manuscript_path,
        context.papers,
        context.notes,
        context.claims,
        context.bibtex_entries,
        context.themes,
        project=context.project,
    ).audit


def rule_config_audit_report(rule_set: RuleSet, findings: list[RuleFinding]) -> str:
    lines = [
        "# Rule Configuration Audit v1.5",
        "",
        "This report validates declarative local JSON rules. Rule files are data only; they do not execute Python code.",
        "",
        f"Rule file: `{_portable_path(rule_set.path) if rule_set.path else '[none]'}`",
        f"Rule set: {rule_set.name}",
        f"Rules loaded: {len(rule_set.rules)}",
        "",
        "## Findings",
        "",
        _finding_table(findings),
        "",
        "## Rule IDs",
        "",
    ]
    if rule_set.rules:
        for rule in rule_set.rules:
            status = "enabled" if rule.enabled else "disabled"
            lines.append(f"- `{rule.rule_id}` ({rule.target}, {rule.rule_type}, {status}) - {rule.name}")
    else:
        lines.append("- No configured rules were loaded.")
    return "\n".join(lines).rstrip() + "\n"


def rule_report(result: RuleRunResult) -> str:
    lines = [
        "# Rule Report v1.5",
        "",
        "This report combines built-in validation adapters with optional project-specific declarative rules.",
        "It audits local metadata and evidence tracking only; it does not modify files or judge scientific truth.",
        "",
        f"Project: {result.context.project}",
        f"Rule file: `{_portable_path(result.rule_set.path) if result.rule_set.path else '[none]'}`",
        f"Configured rules: {len(result.rule_set.rules)}",
        f"Built-in adapter findings: {len(result.built_in_findings)}",
        f"Configured rule findings: {len(result.config_findings)}",
        f"Total findings: {len(result.findings)}",
        "",
        "## Findings",
        "",
        _finding_table(result.findings),
        "",
        "## Configured Rules",
        "",
    ]
    if not result.rule_set.rules:
        lines.append("No configured rules were loaded. Built-in adapters still ran.")
    for rule in result.rule_set.rules:
        status = "enabled" if rule.enabled else "disabled"
        lines.append(f"- `{rule.rule_id}` ({rule.target}, {rule.rule_type}, {status}): {rule.name}")
    return "\n".join(lines).rstrip() + "\n"


def explain_rule(rule_id: str, rule_set: RuleSet | None = None) -> str:
    lines = [f"# Rule Explanation: {rule_id}", ""]
    if rule_id in BUILT_IN_RULE_DESCRIPTIONS:
        lines.extend(
            [
                "Type: built-in adapter",
                "",
                BUILT_IN_RULE_DESCRIPTIONS[rule_id],
            ]
        )
        return "\n".join(lines).rstrip() + "\n"
    if rule_id.startswith("builtin."):
        prefix = ".".join(rule_id.split(".")[:2])
        if prefix in BUILT_IN_RULE_DESCRIPTIONS:
            lines.extend(["Type: built-in adapter finding", "", BUILT_IN_RULE_DESCRIPTIONS[prefix]])
            return "\n".join(lines).rstrip() + "\n"
    for rule in (rule_set.rules if rule_set else []):
        if rule.rule_id == rule_id:
            lines.extend(
                [
                    f"Name: {rule.name}",
                    f"Target: {rule.target}",
                    f"Severity: {rule.severity}",
                    f"Enabled: {rule.enabled}",
                    f"Condition type: {rule.rule_type}",
                    "",
                    rule.description or "No description provided.",
                    "",
                    f"Suggested action: {rule.suggested_action or '[none]'}",
                ]
            )
            return "\n".join(lines).rstrip() + "\n"
    lines.append("Rule ID was not found in built-in adapters or the loaded rule set.")
    return "\n".join(lines).rstrip() + "\n"


def _rule_from_dict(data: dict[str, Any], *, index: int) -> Rule:
    condition = data.get("condition", {})
    if not isinstance(condition, dict):
        condition = {}
    tags = data.get("tags", [])
    if isinstance(tags, str):
        tags = parse_tags(tags)
    elif isinstance(tags, list):
        tags = parse_tags([str(tag) for tag in tags])
    else:
        tags = []
    return Rule(
        rule_id=str(data.get("rule_id", f"unnamed_rule_{index}")).strip(),
        name=str(data.get("name", data.get("rule_id", f"Unnamed rule {index}"))).strip(),
        description=str(data.get("description", "")).strip(),
        target=str(data.get("target", "workspace")).strip().lower().replace("-", "_"),
        severity=str(data.get("severity", "warning")).strip().lower(),
        enabled=bool(data.get("enabled", True)),
        condition=condition,
        message=str(data.get("message", "")).strip(),
        suggested_action=str(data.get("suggested_action", "")).strip(),
        tags=tags,
        project_scope=str(data.get("project_scope", "")).strip(),
    )


def _validate_condition_shape(rule: Rule, *, source: str = "") -> list[RuleFinding]:
    required_by_type = {
        "required_field": ("field",),
        "allowed_values": ("field", "values"),
        "regex_match": ("field", "pattern"),
        "contains_tag": ("tag",),
        "claim_strength_threshold": ("min_strength",),
        "evidence_type_required": ("evidence_types",),
        "theme_min_papers": ("theme", "min_papers"),
        "theme_min_strong_claims": ("theme", "min_strong_claims"),
    }
    findings: list[RuleFinding] = []
    condition = rule.condition
    for field_name in required_by_type.get(rule.rule_type, ()):
        if field_name not in condition or condition.get(field_name) in ("", None, []):
            findings.append(
                _config_finding(
                    "error",
                    "config.missing_condition_field",
                    f"{rule.rule_id} condition is missing {field_name}.",
                    identifier=rule.rule_id,
                    source=source,
                    suggested_action=f"Add condition.{field_name} for {rule.rule_type}.",
                )
            )
    if rule.rule_type == "regex_match" and condition.get("pattern"):
        try:
            re.compile(str(condition["pattern"]))
        except re.error as exc:
            findings.append(
                _config_finding(
                    "error",
                    "config.invalid_regex",
                    f"{rule.rule_id} regex pattern is invalid: {exc}.",
                    identifier=rule.rule_id,
                    source=source,
                )
            )
    if rule.rule_type == "claim_strength_threshold" and condition.get("min_strength") not in STRENGTH_ORDER:
        findings.append(
            _config_finding(
                "error",
                "config.invalid_strength_threshold",
                f"{rule.rule_id} min_strength must be one of {', '.join(STRENGTH_ORDER)}.",
                identifier=rule.rule_id,
                source=source,
            )
        )
    return findings


def _run_rule(rule: Rule, context: RuleContext) -> list[RuleFinding]:
    rule_type = rule.rule_type
    if rule_type == "required_field":
        return _rule_required_field(rule, context)
    if rule_type == "allowed_values":
        return _rule_allowed_values(rule, context)
    if rule_type == "regex_match":
        return _rule_regex_match(rule, context)
    if rule_type in {"min_count", "max_count"}:
        return _rule_count(rule, context)
    if rule_type == "contains_tag":
        return _rule_contains_tag(rule, context)
    if rule_type == "missing_note_for_status":
        return _rule_missing_note_for_status(rule, context)
    if rule_type == "claim_strength_threshold":
        return _rule_claim_strength_threshold(rule, context)
    if rule_type == "evidence_type_required":
        return _rule_evidence_type_required(rule, context)
    if rule_type == "citation_key_required":
        return _rule_citation_key_required(rule, context)
    if rule_type == "theme_min_papers":
        return _rule_theme_min_papers(rule, context)
    if rule_type == "theme_min_strong_claims":
        return _rule_theme_min_strong_claims(rule, context)
    if rule_type == "manuscript_no_unknown_citations":
        return _rule_manuscript_no_unknown_citations(rule, context)
    return []


def _items_for_target(rule: Rule, context: RuleContext) -> list[Any]:
    items: dict[str, list[Any]] = {
        "registry": list(context.papers),
        "bibtex": list(context.bibtex_entries),
        "note": list(context.notes),
        "claim": list(context.claims),
        "theme": list(context.themes),
        "project": [context.profile] if context.profile else [],
        "file": list(context.files),
        "workspace": [context],
        "manuscript": [context.manuscript_audit] if context.manuscript_audit else [],
    }
    return items.get(rule.target, [])


def _rule_required_field(rule: Rule, context: RuleContext) -> list[RuleFinding]:
    field_name = str(rule.condition.get("field", ""))
    findings: list[RuleFinding] = []
    for item in _filtered_items(rule, context):
        value = _field_value(item, field_name)
        if _is_empty(value):
            findings.append(_rule_finding(rule, item, field=field_name, value=value))
    return findings


def _rule_allowed_values(rule: Rule, context: RuleContext) -> list[RuleFinding]:
    field_name = str(rule.condition.get("field", ""))
    allowed = {str(value).strip().lower() for value in _as_list(rule.condition.get("values"))}
    findings: list[RuleFinding] = []
    for item in _filtered_items(rule, context):
        value = _field_value(item, field_name)
        if not _is_empty(value) and str(value).strip().lower() not in allowed:
            findings.append(_rule_finding(rule, item, field=field_name, value=value))
    return findings


def _rule_regex_match(rule: Rule, context: RuleContext) -> list[RuleFinding]:
    field_name = str(rule.condition.get("field", ""))
    pattern = re.compile(str(rule.condition.get("pattern", "")))
    findings: list[RuleFinding] = []
    for item in _filtered_items(rule, context):
        value = str(_field_value(item, field_name) or "")
        if value and not pattern.search(value):
            findings.append(_rule_finding(rule, item, field=field_name, value=value))
    return findings


def _rule_count(rule: Rule, context: RuleContext) -> list[RuleFinding]:
    count = len(_filtered_items(rule, context))
    minimum = int(rule.condition.get("min", rule.condition.get("minimum", 0)) or 0)
    maximum = int(rule.condition.get("max", rule.condition.get("maximum", 0)) or 0)
    if rule.rule_type == "min_count" and count < minimum:
        return [_rule_finding(rule, context, count=count, minimum=minimum, identifier=rule.target)]
    if rule.rule_type == "max_count" and maximum and count > maximum:
        return [_rule_finding(rule, context, count=count, maximum=maximum, identifier=rule.target)]
    return []


def _rule_contains_tag(rule: Rule, context: RuleContext) -> list[RuleFinding]:
    wanted = normalize_tag(str(rule.condition.get("tag", "")))
    findings: list[RuleFinding] = []
    for item in _filtered_items(rule, context, apply_tag_filter=False):
        if wanted not in parse_tags(_field_value(item, "tags")):
            findings.append(_rule_finding(rule, item, tag=wanted))
    return findings


def _rule_missing_note_for_status(rule: Rule, context: RuleContext) -> list[RuleFinding]:
    statuses = {str(status).strip().lower() for status in _as_list(rule.condition.get("statuses") or ["read", "deeply_read"])}
    note_ids = {note.paper_id for note in context.notes if note.paper_id}
    findings: list[RuleFinding] = []
    for paper in context.papers:
        if paper.reading_status in statuses and paper.paper_id not in note_ids and not paper.notes_path:
            findings.append(_rule_finding(rule, paper, status=paper.reading_status))
    return findings


def _rule_claim_strength_threshold(rule: Rule, context: RuleContext) -> list[RuleFinding]:
    minimum = str(rule.condition.get("min_strength", "moderate"))
    findings: list[RuleFinding] = []
    for claim in _filtered_claims(rule, context):
        if STRENGTH_ORDER.get(claim.strength, -1) < STRENGTH_ORDER[minimum]:
            findings.append(_rule_finding(rule, claim, strength=claim.strength, minimum=minimum))
    return findings


def _rule_evidence_type_required(rule: Rule, context: RuleContext) -> list[RuleFinding]:
    allowed = {str(value).strip() for value in _as_list(rule.condition.get("evidence_types"))}
    findings: list[RuleFinding] = []
    for claim in _filtered_claims(rule, context):
        if claim.evidence_type not in allowed:
            findings.append(_rule_finding(rule, claim, evidence_type=claim.evidence_type, allowed=", ".join(sorted(allowed))))
    return findings


def _rule_citation_key_required(rule: Rule, context: RuleContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    for paper in context.papers:
        if not paper.bibtex_key:
            findings.append(_rule_finding(rule, paper, field="bibtex_key"))
    return findings


def _rule_theme_min_papers(rule: Rule, context: RuleContext) -> list[RuleFinding]:
    theme_id = normalize_tag(str(rule.condition.get("theme", "")))
    minimum = int(rule.condition.get("min_papers", 1) or 1)
    claims = group_claims_by_theme(context.claims, context.themes).get(theme_id, [])
    count = len({claim.paper_id for claim in claims if claim.paper_id})
    if count < minimum:
        return [_rule_finding(rule, context, identifier=theme_id, count=count, minimum=minimum)]
    return []


def _rule_theme_min_strong_claims(rule: Rule, context: RuleContext) -> list[RuleFinding]:
    theme_id = normalize_tag(str(rule.condition.get("theme", "")))
    minimum = int(rule.condition.get("min_strong_claims", 1) or 1)
    claims = group_claims_by_theme(context.claims, context.themes).get(theme_id, [])
    count = len([claim for claim in claims if claim.strength == "strong"])
    if count < minimum:
        return [_rule_finding(rule, context, identifier=theme_id, count=count, minimum=minimum)]
    return []


def _rule_manuscript_no_unknown_citations(rule: Rule, context: RuleContext) -> list[RuleFinding]:
    if context.manuscript_audit is None:
        return []
    unknown_codes = {"citation_key_not_in_bibtex", "citation_key_not_in_registry"}
    findings = [
        finding
        for finding in context.manuscript_audit.findings
        if finding.code in unknown_codes
    ]
    return [
        _rule_finding(
            rule,
            context,
            identifier=finding.citation_key,
            citation_key=finding.citation_key,
            paragraph_id=finding.paragraph_id,
        )
        for finding in findings
    ]


def _filtered_items(rule: Rule, context: RuleContext, *, apply_tag_filter: bool = True) -> list[Any]:
    items = _items_for_target(rule, context)
    field_filter = rule.condition.get("where_field")
    expected = rule.condition.get("where_equals")
    if field_filter and expected is not None:
        items = [item for item in items if str(_field_value(item, str(field_filter))) == str(expected)]
    if apply_tag_filter and rule.condition.get("tag"):
        tag = normalize_tag(str(rule.condition["tag"]))
        items = [item for item in items if tag in parse_tags(_field_value(item, "tags"))]
    return items


def _filtered_claims(rule: Rule, context: RuleContext) -> list[Claim]:
    claims = list(context.claims)
    theme = rule.condition.get("theme")
    tag = rule.condition.get("tag")
    if theme:
        theme_id = normalize_tag(str(theme))
        mapping = theme_by_tag(context.themes)
        claims = [claim for claim in claims if _claim_matches_theme(claim, theme_id, mapping)]
    if tag:
        wanted = normalize_tag(str(tag))
        claims = [claim for claim in claims if wanted in parse_tags(claim.tags)]
    return claims


def _claim_matches_theme(claim: Claim, theme_id: str, mapping: dict[str, ProjectTheme]) -> bool:
    if normalize_tag(claim.supports_theme) == theme_id:
        return True
    return any(tag in mapping and mapping[tag].theme_id == theme_id for tag in parse_tags(claim.tags))


def _field_value(item: Any, field_name: str) -> Any:
    if isinstance(item, dict):
        return item.get(field_name, "")
    if field_name == "authors" and hasattr(item, "authors"):
        return display_authors(getattr(item, "authors"))
    return getattr(item, field_name, "")


def _identifier(item: Any) -> str:
    for field_name in ("paper_id", "claim_id", "theme_id", "key", "name", "source_path", "root"):
        value = getattr(item, field_name, "")
        if value:
            return str(value)
    if isinstance(item, RuleContext):
        return item.project
    return ""


def _rule_finding(rule: Rule, item: Any, **values: Any) -> RuleFinding:
    identifier = str(values.pop("identifier", "") or _identifier(item))
    template_values = {
        "identifier": identifier,
        "rule_id": rule.rule_id,
        "target": rule.target,
        **values,
    }
    message = rule.message or f"{identifier or rule.target} violates {rule.name or rule.rule_id}."
    suggestion = rule.suggested_action
    return RuleFinding(
        severity=rule.severity,
        rule_id=rule.rule_id,
        target=rule.target,
        identifier=identifier,
        message=_format_template(message, template_values),
        suggested_action=_format_template(suggestion, template_values),
        source="configured",
        category=rule.target,
        tags=rule.tags,
    )


def _format_template(template: str, values: dict[str, Any]) -> str:
    try:
        return template.format(**values)
    except (KeyError, IndexError, ValueError):
        return template


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, list):
        return not value
    return not str(value).strip()


def _config_finding(
    severity: str,
    code: str,
    message: str,
    *,
    identifier: str = "",
    source: str = "",
    suggested_action: str = "Fix the rule JSON and rerun `paperwb rules validate-config`.",
) -> RuleFinding:
    return RuleFinding(
        severity=severity,
        rule_id=code,
        target="workspace",
        identifier=identifier,
        message=message,
        suggested_action=suggested_action,
        source=source,
        category="rule_config",
    )


def _from_validation_finding(finding: ValidationFinding, prefix: str, target: str) -> RuleFinding:
    return RuleFinding(
        severity=finding.severity,
        rule_id=f"{prefix}.{finding.code}",
        target=target,
        identifier=finding.identifier,
        message=finding.message,
        suggested_action=finding.suggestion,
        source=finding.source,
        category=prefix,
    )


def _from_paragraph_finding(finding: ParagraphAuditFinding) -> RuleFinding:
    return RuleFinding(
        severity=finding.severity,
        rule_id=f"builtin.manuscript.{finding.code}",
        target="manuscript",
        identifier=finding.paragraph_id or finding.citation_key,
        message=finding.message,
        suggested_action=finding.suggestion,
        source=finding.citation_key,
        category="manuscript",
    )


def _finding_table(findings: list[RuleFinding]) -> str:
    if not findings:
        return "No findings.\n"
    lines = ["| Severity | Rule ID | Target | Identifier | Message | Suggested action |", "| --- | --- | --- | --- | --- | --- |"]
    for finding in findings:
        lines.append(
            "| {severity} | {rule_id} | {target} | {identifier} | {message} | {suggestion} |".format(
                severity=finding.severity,
                rule_id=_escape(finding.rule_id),
                target=_escape(finding.target),
                identifier=_escape(finding.identifier),
                message=_escape(finding.message),
                suggestion=_escape(finding.suggested_action),
            )
        )
    return "\n".join(lines) + "\n"


def _escape(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def _portable_path(value: str | Path) -> str:
    if not value:
        return ""
    path = Path(value)
    try:
        return path.resolve(strict=False).relative_to(Path.cwd().resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def _dedupe_findings(findings: list[RuleFinding]) -> list[RuleFinding]:
    seen: set[tuple[str, str, str, str]] = set()
    result: list[RuleFinding] = []
    for finding in findings:
        key = (finding.severity, finding.rule_id, finding.identifier, finding.message)
        if key in seen:
            continue
        seen.add(key)
        result.append(finding)
    return result
