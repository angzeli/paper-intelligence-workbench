"""Deterministic synthetic corpus generation for stress testing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .io import write_json, write_text
from .projects import create_project_profile
from .registry import save_registry
from .schema import Author, Paper
from .tags import format_tags, normalize_tag


SYNTHETIC_DATE = "2026-06-10"

DOMAIN_THEMES = {
    "zis": [
        "charge separation",
        "photocorrosion",
        "thin-film fabrication",
        "catalyst stability",
        "band alignment",
    ],
    "finance": [
        "finance valuation",
        "risk modeling",
        "market microstructure",
        "disclosure quality",
        "portfolio construction",
    ],
    "ml": [
        "ML methodology",
        "robustness",
        "benchmark leakage",
        "dataset shift",
        "interpretability",
    ],
}

DOMAIN_LABELS = {
    "zis": "ZIS photocatalysis",
    "finance": "finance reading",
    "ml": "ML methods",
}

READING_STATUSES = ["unread", "skimmed", "partially_read", "read", "deeply_read", "archived"]
SOURCE_TYPES = ["journal_article", "conference_paper", "report", "review", "preprint"]
EVIDENCE_TYPES = [
    "experimental_result",
    "method_description",
    "theory_or_mechanism",
    "limitation",
    "background_context",
    "opinion_or_interpretation",
]
STRENGTHS = ["strong", "moderate", "weak", "speculative"]
CONFIDENCES = ["high", "medium", "low", ""]


@dataclass(slots=True)
class SyntheticProjectSummary:
    project: str
    root: str
    papers: int
    notes: int
    claims: int
    themes: int
    bibtex_entries: int


def _domain_key(domain: str) -> str:
    value = normalize_tag(domain)
    if value in {"zis", "zis-photocatalysis", "photocatalysis"}:
        return "zis"
    if value in {"finance", "finance-reading", "valuation"}:
        return "finance"
    if value in {"ml", "ml-methods", "machine-learning"}:
        return "ml"
    return "zis"


def _themes_for_domain(domain: str, theme_count: int) -> list[dict[str, object]]:
    key = _domain_key(domain)
    names = list(DOMAIN_THEMES[key])
    while len(names) < theme_count:
        names.append(f"synthetic {key} review theme {len(names) + 1}")
    themes: list[dict[str, object]] = []
    for index, name in enumerate(names[:theme_count]):
        theme_id = normalize_tag(name)
        themes.append(
            {
                "theme_id": theme_id,
                "name": name,
                "tags": [theme_id, f"{theme_id}-evidence", f"{key}-stress"],
                "min_claims": 5 if index < theme_count - 1 else 8,
                "min_papers": 3 if index < theme_count - 1 else 4,
                "description": f"Synthetic stress-test theme for {name}.",
            }
        )
    return themes


def _author(index: int) -> list[Author]:
    given = ["Avery", "Blair", "Casey", "Devon", "Emery", "Finley", "Gray", "Harper"][index % 8]
    family = ["Synthetic", "Fixture", "Local", "Example", "Review", "Workbench"][index % 6]
    second = ["Jordan", "Morgan", "Quinn", "Riley", "Taylor", "Skyler"][index % 6]
    return [Author(given=given, family=family, raw_name=f"{family}, {given}"), Author(given=second, family="Test", raw_name=f"Test, {second}")]


def _paper_title(domain_label: str, index: int, theme_name: str) -> str:
    return f"Synthetic {domain_label} Study {index:03d}: {theme_name.title()} under Local Review Conditions"


def _paper_id(prefix: str, index: int) -> str:
    return f"{prefix}_synthetic_{index:03d}"


def _citation_key(prefix: str, year: str, index: int) -> str:
    return f"{prefix}Synthetic{year}{index:03d}"


def _bibtex_entry(paper: Paper, index: int, *, duplicate_key: str = "") -> str:
    key = duplicate_key or paper.bibtex_key
    entry_type = "article"
    venue_field = f"  journal = {{{paper.journal}}},"
    extra = ""
    if index % 13 == 0:
        entry_type = "misc"
        venue_field = "  howpublished = {Synthetic local archive},"
    elif index % 11 == 0:
        entry_type = "inproceedings"
        venue_field = "  booktitle = {Synthetic Stress Proceedings},"
    elif index % 31 == 0:
        entry_type = "phdthesis"
        venue_field = "  school = {Synthetic Local University},"
    if index % 19 == 0:
        author = ""
    else:
        author = " and ".join(author.bibtex_display() for author in paper.authors)
    year = "20X9" if index % 29 == 0 else paper.year
    title = paper.title
    if index % 17 == 0:
        title = title.lower()
    if index % 23 == 0 and entry_type == "article":
        venue_field = "  journaltitle = {},"
    if index % 7 == 0:
        extra = "  note = {Synthetic stress fixture with conservative validation warnings},\n"
    return (
        f"@{entry_type}{{{key},\n"
        f"  title = {{{title}}},\n"
        f"  author = {{{author}}},\n"
        f"  year = {{{year}}},\n"
        f"{venue_field}\n"
        f"  doi = {{{paper.doi}}},\n"
        f"  url = {{{paper.url}}},\n"
        f"{extra}"
        f"}}\n"
    )


def _claim_block(paper: Paper, claim_number: int, theme: dict[str, object], domain_key: str) -> str:
    theme_id = str(theme["theme_id"])
    strength = STRENGTHS[claim_number % len(STRENGTHS)]
    confidence = CONFIDENCES[claim_number % len(CONFIDENCES)]
    if theme_id == normalize_tag(DOMAIN_THEMES[domain_key][0]):
        evidence_type = "review_statement"
    else:
        evidence_type = EVIDENCE_TYPES[claim_number % len(EVIDENCE_TYPES)]
    location = "" if claim_number % 9 == 0 else f"Section {1 + (claim_number % 6)} p. {2 + claim_number}"
    supports_theme = "undefined synthetic stress theme" if claim_number % 37 == 0 else str(theme["name"])
    tags = [theme_id, f"{domain_key}-stress"]
    if claim_number % 5 == 0:
        tags.append("cross-theme")
    location_line = f"- Section / page: {location}" if location else "- Section / page:"
    confidence_line = f"- Confidence: {confidence}" if confidence else "- Confidence:"
    return f"""### Claim {claim_number}
- Claim: Synthetic claim {claim_number} for {paper.paper_id} records user-tracked evidence about {theme['name']}.
- Evidence type: {evidence_type}
{location_line}
- Quote or paraphrase: Synthetic paraphrase only; no real paper quote is represented.
{confidence_line}
- Tags: {format_tags(tags)}
- User comment: Generated for local stress testing; verify real claims manually.
- Strength: {strength}
- Supports theme: {supports_theme}
"""


def _note_text(paper: Paper, claim_blocks: list[str]) -> str:
    bibtex_line = f"- BibTeX key: {paper.bibtex_key}" if paper.bibtex_key else "- BibTeX key:"
    return f"""# Paper Note: {paper.title}

## Metadata
- Paper ID: {paper.paper_id}
{bibtex_line}
- DOI: {paper.doi}
- Year: {paper.year}
- Journal: {paper.journal}
- Tags: {format_tags(paper.tags)}
- Reading status: {paper.reading_status}

## One-sentence summary
Synthetic summary for local stress testing only.

## Why this paper matters
This synthetic note exercises registry, claim, theme, and citation-audit workflows.

## Research question or problem
How does this synthetic fixture contribute to a larger local literature-review stress corpus?

## Method / approach
Deterministic generated metadata and structured notes.

## Key findings
Only user-entered synthetic claims below should be counted by the parser.

## Limitations
This is not a real publication and must not be cited as scientific evidence.

## Useful for my literature review
Useful for stress-testing report generation and audit completeness.

## Not useful for
Not useful as real paper metadata, a real claim, or a real quote.

## Claims and evidence

{chr(10).join(claim_blocks)}

## Open questions
- Which generated warnings should be fixed before a real release?

## Follow-up actions
- Inspect weak and missing-evidence claims in generated reports.

## Personal reading notes
Synthetic personal note text after the claim blocks should not be parsed as a claim.
"""


def _papers(prefix: str, project: str, domain: str, themes: list[dict[str, object]], paper_count: int) -> list[Paper]:
    domain_key = _domain_key(domain)
    domain_label = DOMAIN_LABELS[domain_key]
    papers: list[Paper] = []
    for index in range(1, paper_count + 1):
        theme = themes[(index - 1) % len(themes)]
        theme_id = str(theme["theme_id"])
        year = str(2016 + (index % 9))
        paper_id = _paper_id(prefix, index)
        title = _paper_title(domain_label, index, str(theme["name"]))
        if index == paper_count:
            title = _paper_title(domain_label, 1, str(themes[0]["name"]))
        doi = f"10.9300/synthetic.{prefix}.{index:03d}"
        if index == 2:
            doi = f"10.9300/synthetic.{prefix}.001"
        if index == 3:
            doi = "10.bad"
        bibtex_key = _citation_key(prefix, year, index)
        if index == 4:
            bibtex_key = _citation_key(prefix, str(2016 + (1 % 9)), 1)
        if index == 5:
            bibtex_key = ""
        note_exists = index % 8 != 0
        notes_path = f"notes/{paper_id}.md" if note_exists else ""
        status = READING_STATUSES[index % len(READING_STATUSES)]
        if not note_exists and index % 3 == 0:
            status = "read"
        tags = [theme_id, f"{domain_key}-stress"]
        if index % 6 == 0:
            tags.append(str(themes[(index + 1) % len(themes)]["theme_id"]))
        included = "true" if index % 4 in {0, 1} else "false"
        exclude_reason = "Synthetic exclusion for scope control." if included == "false" and index % 10 != 0 else ""
        local_pdf_path = "data/papers/missing_synthetic_fixture.pdf" if index % 21 == 0 else ""
        papers.append(
            Paper(
                paper_id=paper_id,
                title=title,
                authors=_author(index),
                year=year,
                journal=f"Synthetic {domain_label.title()} Reports",
                doi=doi,
                url=f"https://example.local/{project}/{paper_id}",
                local_pdf_path=local_pdf_path,
                bibtex_key=bibtex_key,
                tags=tags,
                reading_status=status,
                notes_path=notes_path,
                added_date=SYNTHETIC_DATE,
                last_reviewed_date=SYNTHETIC_DATE if note_exists else "",
                priority=["low", "medium", "high", "critical"][index % 4],
                project=project,
                source_type=SOURCE_TYPES[index % len(SOURCE_TYPES)],
                relevance_score=str(round((index % 11) / 2, 1)),
                reading_priority=["low", "medium", "high", "critical"][index % 4],
                included_in_lit_review=included,
                exclude_reason=exclude_reason,
                user_comment="Synthetic stress fixture; not real literature.",
            )
        )
    return papers


def _claim_plan(papers: list[Paper], themes: list[dict[str, object]], claim_count: int, domain_key: str) -> dict[str, list[str]]:
    noted = [paper for paper in papers if paper.notes_path]
    planned: dict[str, list[str]] = {paper.paper_id: [] for paper in noted}
    if not noted:
        return planned
    for claim_index in range(1, claim_count + 1):
        paper = noted[(claim_index - 1) % len(noted)]
        theme = themes[(claim_index - 1) % max(1, len(themes) - 1)]
        planned[paper.paper_id].append(_claim_block(paper, claim_index, theme, domain_key))
    return planned


def _write_notes(project_root: Path, papers: list[Paper], claim_blocks: dict[str, list[str]], force: bool) -> int:
    count = 0
    for paper in papers:
        if not paper.notes_path:
            continue
        target = project_root / paper.notes_path
        write_text(target, _note_text(paper, claim_blocks.get(paper.paper_id, [])), force=force)
        count += 1
    orphan = project_root / "notes" / "orphan_synthetic_note.md"
    write_text(
        orphan,
        """# Paper Note: Orphan Synthetic Note

## Metadata
- Paper ID: orphan_synthetic_note
- BibTeX key:
- DOI:
- Year: 2026
- Journal: Synthetic orphan fixture
- Tags: orphan; synthetic
- Reading status: read

## Claims and evidence

### Claim 1
- Claim: This orphan synthetic note intentionally has no matching registry entry.
- Evidence type: unclear
- Section / page:
- Quote or paraphrase: Synthetic paraphrase only.
- Confidence: low
- Tags: orphan
- User comment: Expected workspace-health warning.
- Strength: weak
- Supports theme: undefined orphan theme
""",
        force=force,
    )
    return count + 1


def _write_bibtex(path: Path, papers: list[Paper], prefix: str, force: bool) -> int:
    entries: list[str] = [
        '@string{synthetic_stress_journal = "Synthetic Stress Journal"}\n',
        "@comment{Synthetic stress bibliography generated locally.}\n",
    ]
    count = 0
    first_key = papers[0].bibtex_key if papers else ""
    for index, paper in enumerate(papers, start=1):
        if not paper.bibtex_key:
            continue
        if index % 17 == 0:
            continue
        duplicate_key = first_key if index == 4 else ""
        entries.append(_bibtex_entry(paper, index, duplicate_key=duplicate_key))
        count += 1
    entries.append(
        f"""@misc{{{prefix}UnlinkedSynthetic999,
  title = {{Synthetic Unlinked Stress Reference}},
  author = {{Fixture, Unlinked}},
  year = {{2026}},
  note = {{Intentionally not linked to any registry row}}
}}
"""
    )
    count += 1
    entries.append(
        f"""@article{{{prefix}BrokenRecoverable,
  title = {{Synthetic Broken Recoverable Entry}},
  author = {{Broken, Fixture}},
  year = {{2026}},
  journal = {{Synthetic Broken Journal}}
"""
    )
    count += 1
    write_text(path, "\n".join(entries), force=force)
    return count


def generate_synthetic_project(
    *,
    name: str,
    root: str | Path = ".",
    papers: int = 40,
    claims: int = 80,
    themes: int = 5,
    domain: str = "zis",
    force: bool = False,
) -> SyntheticProjectSummary:
    if papers < 1:
        raise ValueError("papers must be at least 1")
    if claims < 0:
        raise ValueError("claims must be non-negative")
    if themes < 1:
        raise ValueError("themes must be at least 1")
    project_path = Path(root) / "projects" / name
    if project_path.exists() and not force:
        raise FileExistsError(f"project {name!r} already exists")
    profile = create_project_profile(name, root=root, description="Synthetic stress corpus generated locally.", force=force)
    domain_key = _domain_key(domain)
    theme_rows = _themes_for_domain(domain_key, themes)
    prefix = normalize_tag(name).replace("-", "_")
    generated_papers = _papers(prefix, name, domain_key, theme_rows, papers)
    claim_blocks = _claim_plan(generated_papers, theme_rows, claims, domain_key)

    save_registry(generated_papers, profile.registry_path)
    write_json(profile.themes_path, {"themes": theme_rows}, force=True)
    note_count = _write_notes(Path(profile.root), generated_papers, claim_blocks, force=True)
    bib_count = _write_bibtex(Path(profile.bibtex_path), generated_papers, prefix, force=True)
    return SyntheticProjectSummary(
        project=name,
        root=str(profile.root),
        papers=len(generated_papers),
        notes=note_count,
        claims=claims + 1,
        themes=len(theme_rows),
        bibtex_entries=bib_count,
    )
