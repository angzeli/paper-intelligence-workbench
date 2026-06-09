"""Tag and theme normalization helpers."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import re

from .io import load_json
from .schema import Claim, Paper, ProjectTheme

TAG_SPLIT_RE = re.compile(r"[;,|]")


def normalize_tag(tag: str) -> str:
    value = tag.strip().lower().replace("_", "-")
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"[^a-z0-9.+-]+", "", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value


def parse_tags(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        raw_tags = value
    else:
        raw_tags = TAG_SPLIT_RE.split(value)
    seen: set[str] = set()
    tags: list[str] = []
    for raw in raw_tags:
        tag = normalize_tag(str(raw))
        if tag and tag not in seen:
            seen.add(tag)
            tags.append(tag)
    return tags


def format_tags(tags: list[str]) -> str:
    return "; ".join(parse_tags(tags))


def count_paper_tags(papers: list[Paper]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for paper in papers:
        counts.update(parse_tags(paper.tags))
    return counts


def count_claim_tags(claims: list[Claim]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for claim in claims:
        counts.update(parse_tags(claim.tags))
    return counts


def filter_papers_by_tag(papers: list[Paper], tag: str) -> list[Paper]:
    normalized = normalize_tag(tag)
    return [paper for paper in papers if normalized in parse_tags(paper.tags)]


def filter_claims_by_tag(claims: list[Claim], tag: str) -> list[Claim]:
    normalized = normalize_tag(tag)
    return [claim for claim in claims if normalized in parse_tags(claim.tags)]


def load_themes(path: str | Path) -> list[ProjectTheme]:
    data = load_json(path)
    rows = data.get("themes", data if isinstance(data, list) else [])
    themes: list[ProjectTheme] = []
    for row in rows:
        themes.append(
            ProjectTheme(
                theme_id=normalize_tag(row.get("theme_id") or row.get("name", "")),
                name=row.get("name", row.get("theme_id", "")),
                tags=parse_tags(row.get("tags", [])),
                min_claims=int(row.get("min_claims", 2) or 2),
                min_papers=int(row.get("min_papers", 1) or 1),
                description=row.get("description", ""),
            )
        )
    return themes


def theme_by_tag(themes: list[ProjectTheme]) -> dict[str, ProjectTheme]:
    mapping: dict[str, ProjectTheme] = {}
    for theme in themes:
        for tag in parse_tags(theme.tags + [theme.theme_id, theme.name]):
            mapping[tag] = theme
    return mapping


def themes_for_tags(tags: list[str], themes: list[ProjectTheme]) -> list[ProjectTheme]:
    mapping = theme_by_tag(themes)
    seen: set[str] = set()
    matched: list[ProjectTheme] = []
    for tag in parse_tags(tags):
        theme = mapping.get(tag)
        if theme and theme.theme_id not in seen:
            seen.add(theme.theme_id)
            matched.append(theme)
    return matched


def group_claims_by_theme(claims: list[Claim], themes: list[ProjectTheme]) -> dict[str, list[Claim]]:
    grouped: dict[str, list[Claim]] = defaultdict(list)
    mapping = theme_by_tag(themes)
    for claim in claims:
        claim_theme_ids: set[str] = set()
        matched = False
        if claim.supports_theme:
            theme_id = normalize_tag(claim.supports_theme)
            grouped[theme_id].append(claim)
            claim_theme_ids.add(theme_id)
            matched = True
        for tag in parse_tags(claim.tags):
            theme = mapping.get(tag)
            if theme and theme.theme_id not in claim_theme_ids:
                grouped[theme.theme_id].append(claim)
                claim_theme_ids.add(theme.theme_id)
                matched = True
        if not matched:
            grouped["unmapped"].append(claim)
    return dict(grouped)
