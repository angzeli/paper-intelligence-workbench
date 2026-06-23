"""Dogfooding scaffolds for starting real local literature-review projects."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from .bibtex import parse_bibtex_file
from .claims import collect_notes
from .io import write_json, write_text
from .projects import project_dir, resolve_project_profile
from .registry import load_registry
from .schema import ProjectProfile
from .tags import load_themes, normalize_tag
from .templates import BASE_NOTE_TEMPLATE, create_project_from_template


DOGFOOD_TEMPLATE_ALIASES = {
    "photocatalysis": "photocatalysis",
    "fyp-photocatalysis": "photocatalysis",
    "fyp": "photocatalysis",
    "finance": "finance",
    "valuation": "finance",
    "ml": "ml-methods",
    "ml-methods": "ml-methods",
    "generic": "generic",
}


def _theme(theme_id: str, name: str, tags: list[str], *, min_papers: int = 3) -> dict[str, Any]:
    return {
        "theme_id": normalize_tag(theme_id),
        "name": name,
        "tags": [normalize_tag(tag) for tag in tags],
        "min_claims": 2,
        "min_papers": min_papers,
        "description": "Empty FYP dogfooding theme. Add only user-verified papers and user-written claims.",
    }


FYP_PHOTOCATALYSIS_THEMES: list[dict[str, Any]] = [
    _theme("metal-sulfide-photocatalysts", "Metal sulfide photocatalysts", ["metal-sulfide", "photocatalyst"]),
    _theme("znin2s4-photocatalysis", "ZnIn2S4 photocatalysis", ["znin2s4", "photocatalysis", "co2-reduction"]),
    _theme("znin2s4-structure-phases", "ZnIn2S4 structure and phases", ["znin2s4", "structure", "phase"]),
    _theme("precursor-chemistry", "Precursor chemistry", ["precursor", "chemistry", "synthesis"]),
    _theme("precursor-derived-thin-films", "Precursor-derived thin films", ["precursor-derived", "thin-film", "thermal-decomposition"]),
    _theme("xanthate-derived-thin-films", "Xanthate-derived thin films", ["xanthate", "thin-film", "precursor"]),
    _theme("thin-film-fabrication", "Thin-film fabrication", ["thin-film", "fabrication", "deposition"]),
    _theme("film-morphology", "Film morphology", ["morphology", "sem", "surface"]),
    _theme("charge-separation", "Charge separation", ["charge-separation", "photocarrier", "interface"]),
    _theme("heterojunctions", "Heterojunctions", ["heterojunction", "band-alignment", "interface"]),
    _theme("cocatalysts", "Cocatalysts", ["cocatalyst", "surface-active-site", "loading"]),
    _theme("co-pi-coox", "Co-Pi and CoOx", ["co-pi", "coox", "cobalt-cocatalyst"]),
    _theme("photocorrosion-stability", "Photocorrosion and stability", ["photocorrosion", "stability", "degradation"]),
    _theme("co2-adsorption-activation", "CO2 adsorption and activation", ["co2", "adsorption", "activation"]),
    _theme("co2-reduction-products", "CO2 reduction products", ["co2-reduction", "products", "co2rr"]),
    _theme("selectivity", "Selectivity", ["selectivity", "product-distribution"]),
    _theme("sacrificial-agents", "Sacrificial agents", ["sacrificial-agent", "hole-scavenger"]),
    _theme("reactor-configuration", "Reactor configuration", ["reactor", "cell-design", "mass-transfer"]),
    _theme("characterization-methods", "Characterization methods", ["xps", "xrd", "spectroscopy", "microscopy"]),
    _theme("quantum-efficiency", "Quantum efficiency", ["quantum-efficiency", "aqe", "conversion-efficiency"]),
    _theme("limitations-controls", "Limitations and controls", ["limitations", "control-experiment", "reproducibility"]),
]


@dataclass(slots=True)
class DogfoodCreateResult:
    profile: ProjectProfile
    template_id: str
    written_paths: list[Path]


@dataclass(slots=True)
class DogfoodFilePlan:
    project: str
    references_dir: Path
    bibtex_path: Path
    pdf_count: int
    supplement_count: int
    bibtex_key_count: int
    matched: list[tuple[str, str]]
    unmatched_pdfs: list[str]
    unmatched_bibtex_keys: list[str]
    selected: list[tuple[str, str]]


def dogfood_template_id(template_id: str) -> str:
    key = normalize_tag(template_id)
    if key not in DOGFOOD_TEMPLATE_ALIASES:
        available = ", ".join(sorted(DOGFOOD_TEMPLATE_ALIASES))
        raise ValueError(f"unknown dogfood template {template_id!r}; available templates: {available}")
    return DOGFOOD_TEMPLATE_ALIASES[key]


def create_dogfood_project(template_id: str, project_name: str, *, root: str | Path = ".") -> DogfoodCreateResult:
    resolved_template = dogfood_template_id(template_id)
    target = project_dir(project_name, root)
    if target.exists():
        raise FileExistsError(f"project path already exists: {target}")

    result = create_project_from_template(resolved_template, project_name, root=root)
    profile = result.profile
    project_root = Path(profile.root)
    for dirname in ("drafts", "reading_sessions"):
        (project_root / dirname).mkdir(parents=True, exist_ok=True)

    written = list(result.written_paths)
    if resolved_template == "photocatalysis":
        written.extend(
            [
                write_json(profile.themes_path, {"themes": FYP_PHOTOCATALYSIS_THEMES}, force=True),
                write_json(project_root / "rules.json", _fyp_rules(), force=True),
                write_json(project_root / "reading_queue_config.json", _fyp_reading_queue_config(), force=True),
            ]
        )
    written.extend(
        [
            write_text(project_root / "README.md", dogfood_project_readme(profile, resolved_template), force=True),
            write_text(project_root / "project_onboarding.md", project_onboarding_markdown(profile, resolved_template), force=True),
            write_text(project_root / "first_week_plan.md", first_week_plan_markdown(profile, resolved_template), force=True),
            write_text(project_root / "evidence_tracking_checklist.md", evidence_tracking_checklist_markdown(profile), force=True),
            write_text(project_root / "fyp_lit_review_workflow.md", fyp_lit_review_workflow_markdown(profile, resolved_template), force=True),
            write_text(project_root / "templates" / "NOTE_TEMPLATE.md", BASE_NOTE_TEMPLATE, force=True),
        ]
    )
    return DogfoodCreateResult(profile=profile, template_id=resolved_template, written_paths=_dedupe_paths(written))


def load_dogfood_profile(project: str, *, root: str | Path = ".") -> ProjectProfile:
    return resolve_project_profile(project, root=root)


def dogfood_status(project: str, *, root: str | Path = ".") -> str:
    profile = load_dogfood_profile(project, root=root)
    papers = load_registry(profile.registry_path)
    notes = collect_notes(profile.notes_dir) if Path(profile.notes_dir).exists() else []
    claims = [claim for note in notes for claim in note.claims]
    entries = parse_bibtex_file(profile.bibtex_path) if Path(profile.bibtex_path).exists() else []
    themes = load_themes(profile.themes_path) if Path(profile.themes_path).exists() else []

    lines = [
        f"# Dogfood Status: {profile.name}",
        "",
        f"Project root: `{Path(profile.root)}`",
        f"Papers: {len(papers)}",
        f"BibTeX entries: {len(entries)}",
        f"Structured notes: {len(notes)}",
        f"Extracted claims: {len(claims)}",
        f"Themes: {len(themes)}",
        "",
        "## Current State",
        "",
    ]
    if not papers:
        lines.append("- No papers yet. Next step: add verified metadata manually or run an import dry-run.")
    if not entries:
        lines.append("- No BibTeX entries yet. Next step: add a local BibTeX entry for the first paper.")
    if not notes:
        lines.append("- No notes yet. Next step: generate a note template after adding the first paper.")
    if not claims:
        lines.append("- No claims yet. Next step: write claims manually in structured notes, then run `paperwb claims`.")
    if papers and entries and notes and claims:
        lines.append("- Project has initial metadata, citations, notes, and claims.")
    lines.extend(
        [
            "",
            "## Safe Next Command",
            "",
            f"`paperwb dogfood checklist --project {profile.name}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def dogfood_checklist(project: str, *, root: str | Path = ".") -> str:
    profile = load_dogfood_profile(project, root=root)
    themes = load_themes(profile.themes_path) if Path(profile.themes_path).exists() else []
    template_id = _template_id_from_themes({theme.theme_id for theme in themes})
    return project_onboarding_markdown(profile, template_id)


def build_file_plan(
    template_id: str,
    project: str,
    references_dir: str | Path,
    bibtex_path: str | Path,
    *,
    limit: int = 15,
) -> DogfoodFilePlan:
    dogfood_template_id(template_id)
    if limit <= 0:
        raise ValueError("--limit must be a positive integer")
    references = Path(references_dir).expanduser()
    bibtex = Path(bibtex_path).expanduser()
    if not references.exists() or not references.is_dir():
        raise FileNotFoundError(f"references directory not found: {references}")
    if not bibtex.exists() or not bibtex.is_file():
        raise FileNotFoundError(f"BibTeX file not found: {bibtex}")

    pdfs = sorted(path for path in references.iterdir() if path.is_file() and path.suffix.lower() == ".pdf")
    supplements = [path for path in pdfs if _looks_like_supplement(path.name)]
    primary_pdfs = [path for path in pdfs if path not in supplements]
    entries = parse_bibtex_file(bibtex)
    keys = sorted({entry.key for entry in entries if entry.key})
    key_set = set(keys)

    pdf_slug_by_name = {path.name: _pdf_slug(path.stem) for path in primary_pdfs}
    matched = sorted((name, slug) for name, slug in pdf_slug_by_name.items() if slug in key_set)
    matched_names = {name for name, _key in matched}
    matched_keys = {key for _name, key in matched}
    unmatched_pdfs = sorted(name for name in pdf_slug_by_name if name not in matched_names)
    unmatched_keys = sorted(key for key in key_set if key not in matched_keys)
    return DogfoodFilePlan(
        project=project,
        references_dir=references,
        bibtex_path=bibtex,
        pdf_count=len(pdfs),
        supplement_count=len(supplements),
        bibtex_key_count=len(keys),
        matched=matched,
        unmatched_pdfs=unmatched_pdfs,
        unmatched_bibtex_keys=unmatched_keys,
        selected=matched[:limit],
    )


def dogfood_file_plan_markdown(plan: DogfoodFilePlan) -> str:
    lines = [
        "# Metadata-backed Dogfood Plan",
        "",
        "This is a local planning report. It does not copy PDFs, read PDF text, write registry rows, or fabricate metadata.",
        "",
        f"Project: `{plan.project}`",
        f"References directory: `{plan.references_dir}`",
        f"BibTeX file: `{plan.bibtex_path}`",
        "",
        "## Summary",
        "",
        f"- PDF files found: {plan.pdf_count}",
        f"- Obvious supplement files excluded: {plan.supplement_count}",
        f"- BibTeX keys found: {plan.bibtex_key_count}",
        f"- Direct filename/BibTeX key matches: {len(plan.matched)}",
        f"- Starter papers selected: {len(plan.selected)}",
        "",
        "## 15-paper Starter Shortlist",
        "",
    ]
    if plan.selected:
        lines.extend(["| PDF filename | BibTeX key |", "| --- | --- |"])
        lines.extend(f"| `{filename}` | `{key}` |" for filename, key in plan.selected)
    else:
        lines.append("No direct filename/BibTeX key matches were found.")
    lines.extend(["", "## Unmatched PDFs", ""])
    if plan.unmatched_pdfs:
        lines.extend(f"- `{name}`" for name in plan.unmatched_pdfs[:50])
        if len(plan.unmatched_pdfs) > 50:
            lines.append(f"- ... {len(plan.unmatched_pdfs) - 50} more")
    else:
        lines.append("None.")
    lines.extend(["", "## Next Safe Steps", ""])
    lines.extend(
        [
            "1. Review the shortlist manually.",
            "2. Add verified registry metadata by hand or through a dry-run importer.",
            "3. Link local files only after checking paths and permissions.",
            "4. Generate note templates and write claims manually after reading.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def dogfood_project_readme(profile: ProjectProfile, template_id: str) -> str:
    return f"""# {profile.name}

This is a local dogfooding scaffold for a `{template_id}` literature-review project.
It contains no real paper metadata, claims, PDFs, or copied paper text.

## First Commands

```bash
paperwb dogfood status --project {profile.name}
paperwb dogfood checklist --project {profile.name}
paperwb validate-registry projects/{profile.name}/registry.csv
paperwb validate-bib projects/{profile.name}/bibtex/library.bib --registry projects/{profile.name}/registry.csv
```

## Real-use Rule

Add only metadata, BibTeX entries, notes, and claims that you have verified
yourself. The workbench tracks evidence; it does not invent it.
"""


def project_onboarding_markdown(profile: ProjectProfile, template_id: str) -> str:
    return f"""# Project Onboarding: {profile.name}

Template: `{template_id}`

## Intake Loop

- [ ] Add one verified paper row to `registry.csv`.
- [ ] Add or import the matching BibTeX entry into `bibtex/library.bib`.
- [ ] Run `paperwb validate-registry projects/{profile.name}/registry.csv`.
- [ ] Run `paperwb validate-bib projects/{profile.name}/bibtex/library.bib --registry projects/{profile.name}/registry.csv`.
- [ ] Generate a note template with `paperwb note-template PAPER_ID --project {profile.name}`.
- [ ] Read the paper yourself and fill the note manually.
- [ ] Add user-written claims with section/page evidence where possible.
- [ ] Run `paperwb claims --project {profile.name}`.
- [ ] Run `paperwb report evidence-map --project {profile.name} --out projects/{profile.name}/reports/evidence_map.md --force`.
- [ ] Run `paperwb report citation-audit --project {profile.name} --out projects/{profile.name}/reports/citation_audit.md --force`.
- [ ] Back up before larger edits with `paperwb backup create --project {profile.name}`.

## Boundaries

- Do not copy PDFs into Git.
- Do not paste copyrighted paper text into examples.
- Do not fabricate metadata, citations, notes, claims, or quotes.
- Treat all reports as planning aids, not scientific-truth judgments.
"""


def first_week_plan_markdown(profile: ProjectProfile, template_id: str) -> str:
    return f"""# First Week Plan: {profile.name}

## Day 1: Setup

- [ ] Run `paperwb dogfood status --project {profile.name}`.
- [ ] Choose 10-15 papers from verified metadata sources.
- [ ] Add the first 3-5 registry rows manually or through dry-run import review.

## Day 2-3: First Notes

- [ ] Generate note templates for the first papers.
- [ ] Fill notes manually while reading.
- [ ] Record only claims supported by your notes.

## Day 4-5: First Evidence Checks

- [ ] Extract claims.
- [ ] Generate evidence map and citation audit reports.
- [ ] Identify weak themes and missing BibTeX links.

## End-of-week Review

- [ ] Run dashboard and rules reports.
- [ ] Create a local backup.
- [ ] Decide the next reading queue from local gaps.
"""


def evidence_tracking_checklist_markdown(profile: ProjectProfile) -> str:
    return f"""# Evidence Tracking Checklist: {profile.name}

- [ ] Every included paper has a BibTeX key.
- [ ] Every read paper has a structured note.
- [ ] Every strong claim has page or section evidence.
- [ ] Review statements are not used as primary experimental evidence.
- [ ] Manuscript citations are known to local registry and BibTeX.
- [ ] Weak themes are flagged before drafting.
- [ ] Reports are regenerated after major note or registry edits.
"""


def fyp_lit_review_workflow_markdown(profile: ProjectProfile, template_id: str) -> str:
    return f"""# FYP Literature-review Workflow: {profile.name}

Template: `{template_id}`

This workflow is a placeholder for future real dogfooding. It contains no real
paper metadata, claims, citations, PDFs, or copied paper text.

## First Real-use Loop

1. Keep the real workspace outside this repository.
2. Add 10-15 verified papers manually or through reviewed local import files.
3. Validate registry and BibTeX after every batch.
4. Generate note templates only for papers you are about to read.
5. Read papers manually and write structured notes yourself.
6. Extract claims from your notes, then review missing evidence locations.
7. Generate evidence maps, citation audits, and writing packets.
8. Draft one 600-1000 word subsection yourself.
9. Run manuscript QA as a heuristic audit, not as final prose generation.
10. Back up the external workspace before large edits.

## Boundary

- Do not copy PDFs into Git.
- Do not paste copyrighted full text into committed examples.
- Do not invent claims, citations, or metadata.
- Do not treat weak evidence warnings as scientific truth.
"""


def _fyp_rules() -> dict[str, Any]:
    rules: list[dict[str, Any]] = []
    for theme in FYP_PHOTOCATALYSIS_THEMES:
        rules.append(
            {
                "rule_id": f"fyp.{theme['theme_id']}.min_papers",
                "name": f"{theme['name']} should have at least 3 papers before writing",
                "target": "theme",
                "severity": "warning",
                "condition": {"type": "theme_min_papers", "theme": theme["theme_id"], "min_papers": 3},
                "message": f"{theme['name']} has only {{count}} supporting paper(s); target is {{minimum}} before drafting.",
                "suggested_action": "Add verified papers and user-written notes before relying on this theme.",
            }
        )
    rules.extend(
        [
            {
                "rule_id": "fyp.read_papers_need_notes",
                "name": "Read papers should have notes",
                "target": "registry",
                "severity": "warning",
                "condition": {"type": "missing_note_for_status", "statuses": ["read", "deeply_read"]},
                "message": "{identifier} is marked as read but has no structured note.",
                "suggested_action": "Create or link a structured note before using this paper in the review.",
            },
            {
                "rule_id": "fyp.included_papers_need_bibtex",
                "name": "Included papers need BibTeX keys",
                "target": "registry",
                "severity": "error",
                "condition": {"type": "required_field", "field": "bibtex_key", "where_field": "included_in_lit_review", "where_equals": True},
                "message": "{identifier} is included in the review but has no BibTeX key.",
                "suggested_action": "Add a verified BibTeX key before drafting.",
            },
            {
                "rule_id": "fyp.strong_claims_need_evidence_location",
                "name": "Strong claims should have page or section evidence",
                "target": "claim",
                "severity": "error",
                "condition": {"type": "required_field", "field": "section", "where_field": "strength", "where_equals": "strong"},
                "message": "{identifier} is marked strong but has no section/page evidence location.",
                "suggested_action": "Add page or section evidence in the structured note before citing confidently.",
            },
        ]
    )
    return {"version": "2.0", "name": "FYP photocatalysis dogfood rules", "rules": rules}


def _fyp_reading_queue_config() -> dict[str, Any]:
    return {
        "version": "2.0",
        "ranking_notes": [
            "Start with directly relevant ZnIn2S4 and thin-film fabrication papers.",
            "Move papers with missing notes but included-in-review intent up the queue.",
            "Use weak themes from evidence maps to choose follow-up reading.",
        ],
        "important_tags": [
            "znin2s4",
            "xanthate",
            "thin-film",
            "charge-separation",
            "photocorrosion",
            "co2-reduction",
            "cocatalyst",
        ],
    }


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    result: list[Path] = []
    for path in paths:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        result.append(path)
    return result


def _template_id_from_themes(theme_ids: set[str]) -> str:
    if "znin2s4-structure-phases" in theme_ids:
        return "photocatalysis"
    if "valuation" in theme_ids:
        return "finance"
    if "model-assumptions" in theme_ids:
        return "ml-methods"
    return "generic"


def _pdf_slug(stem: str) -> str:
    value = stem.lower()
    value = re.sub(r"^\d+[_\-. ]+", "", value)
    value = re.sub(r"[^a-z0-9]+", "", value)
    return value


def _looks_like_supplement(filename: str) -> bool:
    value = filename.lower()
    return any(marker in value for marker in ("_esi", "-esi", "supplement", "supporting", "si.pdf"))
