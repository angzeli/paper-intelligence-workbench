"""Reusable local project templates for real-use literature-review setup."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .io import write_json, write_text
from .projects import create_project_profile, project_dir
from .registry import REGISTRY_FIELDS
from .schema import ProjectProfile
from .tags import normalize_tag


@dataclass(slots=True)
class ProjectTemplate:
    template_id: str
    name: str
    description: str
    themes: list[dict[str, Any]]
    rules: dict[str, Any]
    note_template: str
    report_checklist: str
    manuscript_qa_checklist: str
    dashboard_expectations: str
    reading_queue_config: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TemplateCreateResult:
    template: ProjectTemplate
    profile: ProjectProfile
    written_paths: list[Path]


def list_templates() -> list[ProjectTemplate]:
    return [TEMPLATES[key] for key in sorted(TEMPLATES)]


def get_template(template_id: str) -> ProjectTemplate:
    key = normalize_tag(template_id).replace("_", "-")
    aliases = {
        "ml": "ml-methods",
        "ml-methods": "ml-methods",
        "machine-learning": "ml-methods",
        "photocatalysis": "photocatalysis",
        "finance": "finance",
        "valuation": "finance",
        "generic": "generic",
        "generic-literature-review": "generic",
    }
    resolved = aliases.get(key, key)
    if resolved not in TEMPLATES:
        available = ", ".join(sorted(TEMPLATES))
        raise ValueError(f"unknown template {template_id!r}; available templates: {available}")
    return TEMPLATES[resolved]


def template_summary(template: ProjectTemplate) -> str:
    return f"{template.template_id}\t{template.name}\t{len(template.themes)} themes"


def inspect_template(template_id: str) -> str:
    template = get_template(template_id)
    lines = [
        f"# Template: {template.name}",
        "",
        f"ID: `{template.template_id}`",
        "",
        template.description,
        "",
        "## Themes",
        "",
    ]
    for theme in template.themes:
        lines.append(f"- `{theme['theme_id']}`: {theme['name']} ({', '.join(theme.get('tags', []))})")
    lines.extend(["", "## Rule Examples", ""])
    for rule in template.rules.get("rules", []):
        lines.append(f"- `{rule['rule_id']}` ({rule['severity']}): {rule['name']}")
    lines.extend(
        [
            "",
            "## Generated Files",
            "",
            "- `registry.csv` with the standard registry schema and no fabricated papers",
            "- `themes.json`",
            "- `rules.json`",
            "- `templates/NOTE_TEMPLATE.md`",
            "- `registry_schema.md`",
            "- `report_checklist.md`",
            "- `manuscript_qa_checklist.md`",
            "- `dashboard_expectations.md`",
            "- `reading_queue_config.json`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def create_project_from_template(
    template_id: str,
    project_name: str,
    *,
    root: str | Path = ".",
) -> TemplateCreateResult:
    template = get_template(template_id)
    target = project_dir(project_name, root)
    if target.exists():
        raise FileExistsError(f"project path already exists: {target}")
    profile = create_project_profile(project_name, root=root, description=f"{template.name} project from template {template.template_id}")
    project_root = Path(profile.root)
    written: list[Path] = [
        write_json(profile.themes_path, {"themes": template.themes}, force=True),
        write_json(project_root / "rules.json", template.rules, force=True),
        write_text(project_root / "templates" / "NOTE_TEMPLATE.md", template.note_template, force=True),
        write_text(project_root / "registry_schema.md", registry_schema_markdown(template), force=True),
        write_text(project_root / "report_checklist.md", template.report_checklist, force=True),
        write_text(project_root / "manuscript_qa_checklist.md", template.manuscript_qa_checklist, force=True),
        write_text(project_root / "dashboard_expectations.md", template.dashboard_expectations, force=True),
        write_json(project_root / "reading_queue_config.json", template.reading_queue_config, force=True),
        write_text(project_root / "README.md", project_readme(template, profile), force=True),
    ]
    return TemplateCreateResult(template=template, profile=profile, written_paths=written)


def registry_schema_markdown(template: ProjectTemplate) -> str:
    rows = "\n".join(f"| `{field}` | Standard registry field |" for field in REGISTRY_FIELDS)
    return f"""# Registry Schema: {template.name}

This project uses the standard Paper Intelligence Workbench registry schema.
The generated `registry.csv` is intentionally empty except for headers. Add
only user-verified paper metadata.

| Field | Purpose |
| --- | --- |
{rows}
"""


def project_readme(template: ProjectTemplate, profile: ProjectProfile) -> str:
    return f"""# {profile.name}

Template: {template.name}

This project scaffold is local-first and contains no real paper metadata,
copyrighted PDFs, or fabricated claims. Add only user-verified papers, notes,
BibTeX entries, and evidence.

## Suggested First Commands

```bash
paperwb doctor --project {profile.name}
paperwb dashboard --project {profile.name} --no-audit-log
paperwb rules validate-config --project {profile.name}
paperwb report evidence-map --project {profile.name} --out scratch/{profile.name}_evidence_map.md --force
```
"""


def template_overview_report(template_id: str) -> str:
    template = get_template(template_id)
    return "\n".join(
        [
            f"# {template.name} Template Overview",
            "",
            template.description,
            "",
            "## Included Themes",
            "",
            _theme_table(template),
            "",
            "## Included Rule Examples",
            "",
            _rule_table(template),
            "",
            "## Dogfooding Checklist",
            "",
            "- Create a project with `paperwb template create ... --project PROJECT`.",
            "- Add only verified local paper metadata to `registry.csv`.",
            "- Add BibTeX entries from local sources.",
            "- Generate notes with `paperwb note-template` or copy `templates/NOTE_TEMPLATE.md` into `notes/` for a specific paper.",
            "- Run `paperwb doctor`, `paperwb rules report`, and `paperwb dashboard --no-audit-log` before writing.",
            "- Use manuscript QA and writing packets as planning aids only.",
        ]
    ).rstrip() + "\n"


def _theme_table(template: ProjectTemplate) -> str:
    lines = ["| Theme ID | Name | Tags |", "| --- | --- | --- |"]
    for theme in template.themes:
        lines.append(f"| `{theme['theme_id']}` | {theme['name']} | {', '.join(theme.get('tags', []))} |")
    return "\n".join(lines)


def _rule_table(template: ProjectTemplate) -> str:
    lines = ["| Rule ID | Target | Severity | Purpose |", "| --- | --- | --- | --- |"]
    for rule in template.rules.get("rules", []):
        lines.append(f"| `{rule['rule_id']}` | {rule['target']} | {rule['severity']} | {rule['name']} |")
    return "\n".join(lines)


def _theme(theme_id: str, name: str, tags: list[str], *, min_claims: int = 2, min_papers: int = 3, description: str = "") -> dict[str, Any]:
    return {
        "theme_id": normalize_tag(theme_id),
        "name": name,
        "tags": [normalize_tag(tag) for tag in tags],
        "min_claims": min_claims,
        "min_papers": min_papers,
        "description": description,
    }


def _required_note_rule() -> dict[str, Any]:
    return {
        "rule_id": "template.read_papers_need_notes",
        "name": "Read papers should have notes",
        "target": "registry",
        "severity": "warning",
        "condition": {"type": "missing_note_for_status", "statuses": ["read", "deeply_read"]},
        "message": "{identifier} is marked as read but has no structured note.",
        "suggested_action": "Create or link a structured note before relying on this paper.",
    }


def _citation_key_rule() -> dict[str, Any]:
    return {
        "rule_id": "template.included_papers_need_bibtex",
        "name": "Included papers need BibTeX keys",
        "target": "registry",
        "severity": "error",
        "condition": {"type": "required_field", "field": "bibtex_key", "where_field": "included_in_lit_review", "where_equals": True},
        "message": "{identifier} is included in the review but has no BibTeX key.",
        "suggested_action": "Add or import a verified BibTeX key before drafting.",
    }


def _strong_claim_location_rule() -> dict[str, Any]:
    return {
        "rule_id": "template.strong_claims_need_evidence_location",
        "name": "Strong claims should have page or section evidence",
        "target": "claim",
        "severity": "error",
        "condition": {"type": "required_field", "field": "section", "where_field": "strength", "where_equals": "strong"},
        "message": "{identifier} is marked strong but has no section/page evidence location.",
        "suggested_action": "Add page or section evidence in the structured note before citing confidently.",
    }


def _manuscript_unknown_citation_rule() -> dict[str, Any]:
    return {
        "rule_id": "template.manuscript_no_unknown_citations",
        "name": "Manuscript citations should be known locally",
        "target": "manuscript",
        "severity": "error",
        "condition": {"type": "manuscript_no_unknown_citations"},
        "message": "Citation {citation_key} in paragraph {paragraph_id} is not linked to local registry/BibTeX data.",
        "suggested_action": "Add the citation to the registry and BibTeX library or remove it from the draft.",
    }


def _theme_min_paper_rules(template_key: str, themes: list[dict[str, Any]], minimum: int) -> list[dict[str, Any]]:
    rules = []
    for theme in themes:
        threshold = int(theme.get("min_papers") or minimum)
        rules.append(
            {
                "rule_id": f"{template_key}.{theme['theme_id']}.min_papers",
                "name": f"{theme['name']} needs enough papers before writing",
                "target": "theme",
                "severity": "warning",
                "condition": {"type": "theme_min_papers", "theme": theme["theme_id"], "min_papers": threshold},
                "message": f"{theme['name']} has only {{count}} supporting paper(s); target is {{minimum}} before drafting.",
                "suggested_action": "Add verified papers and structured claims for this theme before writing.",
            }
        )
    return rules


BASE_NOTE_TEMPLATE = """# Paper Note: [Title]

## Metadata
- Paper ID:
- BibTeX key:
- DOI:
- Year:
- Journal:
- Tags:
- Reading status:

## One-sentence summary

## Why this paper matters

## Research question or problem

## Method / approach

## Key findings

## Limitations

## Useful for my literature review

## Not useful for

## Claims and evidence

### Claim 1
- Claim:
- Evidence type:
- Section / page:
- Quote or paraphrase:
- Confidence:
- Strength:
- Tags:
- Supports theme:
- User comment:

## Open questions

## Follow-up actions

## Personal reading notes
"""


def _report_checklist(name: str) -> str:
    return f"""# Report Checklist: {name}

- `paperwb doctor --project PROJECT`
- `paperwb validate-bib projects/PROJECT/bibtex/library.bib --registry projects/PROJECT/registry.csv`
- `paperwb rules report --project PROJECT --out projects/PROJECT/reports/rule_report.md --force`
- `paperwb dashboard --project PROJECT --no-audit-log --out projects/PROJECT/reports/dashboard.md --force`
- `paperwb report evidence-map --project PROJECT --out projects/PROJECT/reports/evidence_map.md --force`
- `paperwb report citation-audit --project PROJECT --out projects/PROJECT/reports/citation_audit.md --force`
- `paperwb report weak-claims --project PROJECT --out projects/PROJECT/reports/weak_claims.md --force`
"""


def _manuscript_checklist(name: str) -> str:
    return f"""# Manuscript QA Checklist: {name}

- Run `paperwb manuscript qa DRAFT.md --project PROJECT` before submitting a section for review.
- Check unknown citation keys before interpreting evidence warnings.
- Treat review-only support as a follow-up flag when primary evidence is needed.
- Do not use this checklist as scientific truth evaluation.
- Do not let the tool rewrite final prose.
"""


def _dashboard_expectations(name: str) -> str:
    return f"""# Dashboard Expectations: {name}

The dashboard should be used as a read-only triage view.

- Missing notes should become reading-session or note-template actions.
- Weak claims should become evidence-gathering actions.
- Rule findings should guide local cleanup before drafting.
- Use `--no-audit-log` when generating reports for sharing or committing.
- Do not run next-action commands automatically without user review.
"""


def _reading_config(primary_tags: list[str]) -> dict[str, Any]:
    return {
        "version": "1.7",
        "ranking_notes": [
            "High-priority papers first.",
            "Included papers without notes should be read before drafting.",
            "Themes with weak evidence should move papers up the queue.",
        ],
        "important_tags": [normalize_tag(tag) for tag in primary_tags],
    }


PHOTOCATALYSIS_THEMES = [
    _theme("material-synthesis", "Material synthesis", ["synthesis", "precursor", "crystal-growth"]),
    _theme("thin-films", "Thin films", ["thin-film", "deposition", "coating"]),
    _theme("charge-separation", "Charge separation", ["charge-separation", "photocarrier", "interface"]),
    _theme("photocorrosion", "Photocorrosion", ["photocorrosion", "degradation", "self-oxidation"]),
    _theme("cocatalysts", "Cocatalysts", ["cocatalyst", "surface-active-site", "loading"]),
    _theme("co2-reduction", "CO2 reduction", ["co2-reduction", "co2rr", "carbon-products"]),
    _theme("selectivity", "Selectivity", ["selectivity", "faradaic-efficiency", "product-distribution"]),
    _theme("stability", "Stability", ["stability", "durability", "cycling"]),
    _theme("reactor-design", "Reactor design", ["reactor", "cell-design", "mass-transfer"]),
    _theme("characterization", "Characterization", ["xps", "xrd", "sem", "tem", "spectroscopy"]),
]

FINANCE_THEMES = [
    _theme("valuation", "Valuation", ["valuation", "dcf", "multiples"]),
    _theme("financial-statements", "Financial statements", ["income-statement", "balance-sheet", "accounting"]),
    _theme("profitability", "Profitability", ["margins", "roic", "earnings-quality"]),
    _theme("leverage", "Leverage", ["debt", "coverage", "capital-structure"]),
    _theme("cash-flow", "Cash flow", ["free-cash-flow", "working-capital", "capex"]),
    _theme("market-cycles", "Market cycles", ["cycle", "liquidity", "regime"]),
    _theme("risk", "Risk", ["risk", "drawdown", "scenario-analysis"]),
    _theme("behavioral-finance", "Behavioral finance", ["behavioral-finance", "bias", "sentiment"]),
    _theme("macro", "Macro", ["macro", "rates", "inflation"]),
]

ML_METHODS_THEMES = [
    _theme("model-assumptions", "Model assumptions", ["assumptions", "inductive-bias", "model-design"]),
    _theme("benchmarks", "Benchmarks", ["benchmark", "dataset", "baseline"]),
    _theme("uncertainty", "Uncertainty", ["uncertainty", "calibration", "confidence"]),
    _theme("optimization", "Optimization", ["optimization", "training", "convergence"]),
    _theme("evaluation-metrics", "Evaluation metrics", ["metrics", "evaluation", "measurement"]),
    _theme("reproducibility", "Reproducibility", ["reproducibility", "replication", "open-code"]),
    _theme("limitations", "Limitations", ["limitations", "failure-mode", "scope"]),
]

GENERIC_THEMES = [
    _theme("background", "Background", ["background", "context"], min_papers=2),
    _theme("methods", "Methods", ["methods", "approach"], min_papers=2),
    _theme("findings", "Findings", ["findings", "evidence"], min_papers=2),
    _theme("limitations", "Limitations", ["limitations", "gaps"], min_papers=2),
    _theme("future-work", "Future work", ["future-work", "open-question"], min_papers=1),
]


def _rules(name: str, template_key: str, themes: list[dict[str, Any]], *, min_papers: int = 3, extra_rules: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    rules = [
        *_theme_min_paper_rules(template_key, themes, min_papers),
        _required_note_rule(),
        _citation_key_rule(),
        _strong_claim_location_rule(),
        _manuscript_unknown_citation_rule(),
    ]
    rules.extend(extra_rules or [])
    return {"version": "1.7", "name": f"{name} template rules", "rules": rules}


TEMPLATES: dict[str, ProjectTemplate] = {
    "photocatalysis": ProjectTemplate(
        template_id="photocatalysis",
        name="Photocatalysis Literature Review",
        description="Synthetic scaffold for an FYP-style photocatalysis literature review. It contains no real paper metadata or claims.",
        themes=PHOTOCATALYSIS_THEMES,
        rules=_rules("Photocatalysis", "photocatalysis", PHOTOCATALYSIS_THEMES, min_papers=3),
        note_template=BASE_NOTE_TEMPLATE,
        report_checklist=_report_checklist("Photocatalysis"),
        manuscript_qa_checklist=_manuscript_checklist("Photocatalysis"),
        dashboard_expectations=_dashboard_expectations("Photocatalysis"),
        reading_queue_config=_reading_config(["photocorrosion", "charge-separation", "stability", "co2-reduction"]),
    ),
    "finance": ProjectTemplate(
        template_id="finance",
        name="Finance / Valuation Reading",
        description="Synthetic scaffold for finance and valuation reading. It is for reading organization only and does not provide investment advice.",
        themes=FINANCE_THEMES,
        rules=_rules(
            "Finance",
            "finance",
            FINANCE_THEMES,
            min_papers=2,
            extra_rules=[
                {
                    "rule_id": "finance.included_needs_partial_read",
                    "name": "Included finance papers should be at least partially read",
                    "target": "registry",
                    "severity": "warning",
                    "condition": {
                        "type": "allowed_values",
                        "field": "reading_status",
                        "values": ["partially_read", "read", "deeply_read"],
                        "where_field": "included_in_lit_review",
                        "where_equals": True,
                    },
                    "message": "{identifier} is included but has not been read enough for citation planning.",
                    "suggested_action": "Read or exclude this item before using it in a finance review.",
                }
            ],
        ),
        note_template=BASE_NOTE_TEMPLATE,
        report_checklist=_report_checklist("Finance"),
        manuscript_qa_checklist=_manuscript_checklist("Finance"),
        dashboard_expectations=_dashboard_expectations("Finance"),
        reading_queue_config=_reading_config(["valuation", "cash-flow", "risk", "profitability"]),
    ),
    "ml-methods": ProjectTemplate(
        template_id="ml-methods",
        name="ML Methods Reading",
        description="Synthetic scaffold for machine-learning methods reading. It emphasizes assumptions, benchmarks, uncertainty, and reproducibility.",
        themes=ML_METHODS_THEMES,
        rules=_rules("ML Methods", "ml", ML_METHODS_THEMES, min_papers=2),
        note_template=BASE_NOTE_TEMPLATE,
        report_checklist=_report_checklist("ML Methods"),
        manuscript_qa_checklist=_manuscript_checklist("ML Methods"),
        dashboard_expectations=_dashboard_expectations("ML Methods"),
        reading_queue_config=_reading_config(["benchmarks", "uncertainty", "reproducibility", "limitations"]),
    ),
    "generic": ProjectTemplate(
        template_id="generic",
        name="Generic Literature Review",
        description="Synthetic scaffold for a general literature review when no domain-specific template fits.",
        themes=GENERIC_THEMES,
        rules=_rules("Generic", "generic", GENERIC_THEMES, min_papers=2),
        note_template=BASE_NOTE_TEMPLATE,
        report_checklist=_report_checklist("Generic"),
        manuscript_qa_checklist=_manuscript_checklist("Generic"),
        dashboard_expectations=_dashboard_expectations("Generic"),
        reading_queue_config=_reading_config(["background", "methods", "findings", "limitations"]),
    ),
}
