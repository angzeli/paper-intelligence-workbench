"""Local evidence graph model, builder, analytics, and exports.

The evidence graph is derived only from user-provided local data already
tracked by the workbench. It does not infer scientific truth or invent claims.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Any, Iterable

from .bibtex import parse_bibtex_file
from .claim_lifecycle import ClaimLifecycleRecord, lifecycle_status_for_claim
from .claims import collect_notes
from .io import write_text
from .reading import ReadingSession, load_reading_sessions_with_warnings
from .registry import display_authors, load_registry, normalize_title
from .schema import BibTeXEntry, Claim, Paper, PaperNote, ProjectTheme, dataclass_to_plain
from .tags import load_themes, normalize_tag, parse_tags, theme_by_tag


PAPER = "paper"
AUTHOR = "author"
BIBTEX_ENTRY = "bibtex_entry"
NOTE = "note"
CLAIM = "claim"
EVIDENCE_LOCATION = "evidence_location"
THEME = "theme"
TAG = "tag"
DRAFT = "draft"
CITATION = "citation"
READING_SESSION = "reading_session"
FOLLOWUP = "followup"

AUTHORED_BY = "authored_by"
HAS_BIBTEX = "has_bibtex"
HAS_NOTE = "has_note"
CONTAINS_CLAIM = "contains_claim"
SUPPORTS_THEME = "supports_theme"
TAGGED_WITH = "tagged_with"
CITES = "cites"
CITED_IN_DRAFT = "cited_in_draft"
HAS_EVIDENCE_LOCATION = "has_evidence_location"
DERIVED_FROM_NOTE = "derived_from_note"
HAS_FOLLOWUP = "has_followup"
READ_IN_SESSION = "read_in_session"


@dataclass(slots=True)
class GraphNode:
    node_id: str
    node_type: str
    label: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class GraphEdge:
    source: str
    target: str
    edge_type: str
    label: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EvidenceGraph:
    project: str
    nodes: dict[str, GraphNode] = field(default_factory=dict)
    edges: list[GraphEdge] = field(default_factory=list)

    def add_node(self, node_type: str, key: str, label: str, **metadata: Any) -> GraphNode:
        node_id = make_node_id(node_type, key)
        if node_id not in self.nodes:
            self.nodes[node_id] = GraphNode(node_id=node_id, node_type=node_type, label=label, metadata=_clean_metadata(metadata))
        else:
            self.nodes[node_id].metadata.update(_clean_metadata(metadata))
            if label and not self.nodes[node_id].label:
                self.nodes[node_id].label = label
        return self.nodes[node_id]

    def add_edge(self, source: str, target: str, edge_type: str, label: str = "", **metadata: Any) -> None:
        if source not in self.nodes or target not in self.nodes:
            return
        edge_key = (source, target, edge_type, label)
        for edge in self.edges:
            if (edge.source, edge.target, edge.edge_type, edge.label) == edge_key:
                edge.metadata.update(_clean_metadata(metadata))
                return
        self.edges.append(GraphEdge(source=source, target=target, edge_type=edge_type, label=label, metadata=_clean_metadata(metadata)))

    def node_counts(self) -> Counter[str]:
        return Counter(node.node_type for node in self.nodes.values())

    def edge_counts(self) -> Counter[str]:
        return Counter(edge.edge_type for edge in self.edges)

    def neighbors(self, node_id: str, edge_type: str | None = None) -> list[str]:
        return [
            edge.target
            for edge in self.edges
            if edge.source == node_id and (edge_type is None or edge.edge_type == edge_type)
        ]

    def incoming(self, node_id: str, edge_type: str | None = None) -> list[str]:
        return [
            edge.source
            for edge in self.edges
            if edge.target == node_id and (edge_type is None or edge.edge_type == edge_type)
        ]

    def degree(self, node_id: str) -> int:
        return sum(1 for edge in self.edges if edge.source == node_id or edge.target == node_id)


@dataclass(slots=True)
class ThemeConnectivity:
    theme_id: str
    name: str
    paper_count: int
    claim_count: int
    min_papers: int
    min_claims: int
    review_like_paper_count: int

    @property
    def is_weak(self) -> bool:
        return self.paper_count < self.min_papers or self.claim_count < self.min_claims

    @property
    def is_review_heavy(self) -> bool:
        return self.paper_count > 0 and self.review_like_paper_count >= self.paper_count


@dataclass(slots=True)
class GraphAnalytics:
    orphan_papers: list[str] = field(default_factory=list)
    papers_without_notes: list[str] = field(default_factory=list)
    notes_without_claims: list[str] = field(default_factory=list)
    claims_without_themes: list[str] = field(default_factory=list)
    claims_missing_evidence_locations: list[str] = field(default_factory=list)
    isolated_themes: list[str] = field(default_factory=list)
    theme_connectivity: list[ThemeConnectivity] = field(default_factory=list)
    central_papers: list[tuple[str, str, int]] = field(default_factory=list)
    review_paper_heavy_themes: list[str] = field(default_factory=list)
    draft_citations_without_graph_support: list[str] = field(default_factory=list)
    deprecated_claims: list[str] = field(default_factory=list)
    unverified_claims: list[str] = field(default_factory=list)


def make_node_id(node_type: str, key: str) -> str:
    slug = normalize_tag(key) or "unknown"
    return f"{node_type}:{slug}"


def build_project_graph(
    *,
    project: str,
    root: str | Path,
    registry_path: str | Path,
    bibtex_path: str | Path,
    notes_dir: str | Path,
    themes_path: str | Path,
    sessions_path: str | Path | None = None,
) -> EvidenceGraph:
    papers = load_registry(registry_path)
    entries = parse_bibtex_file(bibtex_path) if Path(bibtex_path).exists() else []
    notes = collect_notes(notes_dir) if Path(notes_dir).exists() else []
    themes = load_themes(themes_path) if Path(themes_path).exists() else []
    sessions: list[ReadingSession] = []
    if sessions_path:
        sessions, _warnings = load_reading_sessions_with_warnings(sessions_path)
    return build_evidence_graph(
        project=project,
        root=root,
        papers=papers,
        bibtex_entries=entries,
        notes=notes,
        themes=themes,
        reading_sessions=sessions,
    )


def build_evidence_graph(
    *,
    project: str,
    root: str | Path,
    papers: list[Paper],
    bibtex_entries: list[BibTeXEntry],
    notes: list[PaperNote],
    themes: list[ProjectTheme],
    reading_sessions: list[ReadingSession] | None = None,
    claim_lifecycle: dict[str, ClaimLifecycleRecord] | None = None,
) -> EvidenceGraph:
    graph = EvidenceGraph(project=project)
    entries_by_key = {entry.key: entry for entry in bibtex_entries if entry.key}
    notes_by_paper = {note.paper_id: note for note in notes if note.paper_id}
    themes_by_id = {theme.theme_id: theme for theme in themes}
    themes_by_tag = theme_by_tag(themes)
    papers_by_id = {paper.paper_id: paper for paper in papers if paper.paper_id}

    for theme in themes:
        graph.add_node(
            THEME,
            theme.theme_id,
            theme.name or theme.theme_id,
            min_papers=theme.min_papers,
            min_claims=theme.min_claims,
            description=theme.description,
            tags=theme.tags,
        )
        for tag in theme.tags:
            _add_tag(graph, tag)
            graph.add_edge(make_node_id(THEME, theme.theme_id), make_node_id(TAG, tag), TAGGED_WITH)

    for entry in bibtex_entries:
        key = entry.key or f"bibtex-{len(graph.nodes)}"
        graph.add_node(
            BIBTEX_ENTRY,
            key,
            key,
            entry_type=entry.entry_type,
            title=entry.title,
            year=entry.year,
            doi=entry.doi,
            venue=entry.venue(),
        )

    for paper in papers:
        paper_node = graph.add_node(
            PAPER,
            paper.paper_id,
            paper.title or paper.paper_id,
            paper_id=paper.paper_id,
            title=paper.title,
            year=paper.year,
            journal=paper.journal,
            doi=paper.doi,
            bibtex_key=paper.bibtex_key,
            reading_status=paper.reading_status,
            source_type=paper.source_type,
            included_in_lit_review=paper.included_in_lit_review,
            tags=paper.tags,
        )
        for author in paper.authors:
            label = author.display()
            if not label:
                continue
            author_key = _author_key(label)
            graph.add_node(AUTHOR, author_key, label)
            graph.add_edge(paper_node.node_id, make_node_id(AUTHOR, author_key), AUTHORED_BY)
        if paper.bibtex_key and paper.bibtex_key in entries_by_key:
            graph.add_edge(paper_node.node_id, make_node_id(BIBTEX_ENTRY, paper.bibtex_key), HAS_BIBTEX)
        for tag in paper.tags:
            _add_tag(graph, tag)
            graph.add_edge(paper_node.node_id, make_node_id(TAG, tag), TAGGED_WITH)
            theme = themes_by_tag.get(normalize_tag(tag))
            if theme:
                graph.add_edge(paper_node.node_id, make_node_id(THEME, theme.theme_id), SUPPORTS_THEME, label="paper_tag")
        note = notes_by_paper.get(paper.paper_id)
        if note:
            _add_note(graph, note, paper_node.node_id)

    for note in notes:
        if note.paper_id and note.paper_id not in papers_by_id:
            note_node = _add_note(graph, note, "")
            for tag in note.tags:
                _add_tag(graph, tag)
                graph.add_edge(note_node.node_id, make_node_id(TAG, tag), TAGGED_WITH)

    for note in notes:
        note_id = make_node_id(NOTE, note.paper_id or note.source_path or "unknown-note")
        for claim in note.claims:
            claim_status = lifecycle_status_for_claim(claim, claim_lifecycle) if claim_lifecycle is not None else ""
            lifecycle_record = (claim_lifecycle or {}).get(claim.claim_id)
            claim_node = graph.add_node(
                CLAIM,
                claim.claim_id,
                _short_label(claim.claim_text, fallback=claim.claim_id),
                claim_id=claim.claim_id,
                paper_id=claim.paper_id,
                strength=claim.strength,
                confidence=claim.confidence,
                evidence_type=claim.evidence_type,
                section=claim.section,
                page=claim.page,
                supports_theme=claim.supports_theme,
                note_file=claim.note_file,
                tags=claim.tags,
                claim_status=claim_status,
                review_status=lifecycle_record.review_status if lifecycle_record else "",
                verification_date=lifecycle_record.verification_date if lifecycle_record else "",
                deprecated_reason=lifecycle_record.deprecated_reason if lifecycle_record else "",
                contradiction_group=lifecycle_record.contradiction_group if lifecycle_record else "",
                needs_reread=lifecycle_record.needs_reread if lifecycle_record else False,
                used_in_draft=lifecycle_record.used_in_draft if lifecycle_record else False,
            )
            if note_id in graph.nodes:
                graph.add_edge(note_id, claim_node.node_id, CONTAINS_CLAIM)
                graph.add_edge(claim_node.node_id, note_id, DERIVED_FROM_NOTE)
            paper_id = claim.paper_id or note.paper_id
            if paper_id and make_node_id(PAPER, paper_id) in graph.nodes:
                graph.add_edge(make_node_id(PAPER, paper_id), claim_node.node_id, CONTAINS_CLAIM)
            for tag in claim.tags:
                _add_tag(graph, tag)
                graph.add_edge(claim_node.node_id, make_node_id(TAG, tag), TAGGED_WITH)
                theme = themes_by_tag.get(normalize_tag(tag))
                if theme:
                    graph.add_edge(claim_node.node_id, make_node_id(THEME, theme.theme_id), SUPPORTS_THEME, label="claim_tag")
                    if paper_id and make_node_id(PAPER, paper_id) in graph.nodes:
                        graph.add_edge(make_node_id(PAPER, paper_id), make_node_id(THEME, theme.theme_id), SUPPORTS_THEME, label="claim_tag")
            if claim.supports_theme:
                theme_id = normalize_tag(claim.supports_theme)
                if theme_id in themes_by_id:
                    graph.add_edge(claim_node.node_id, make_node_id(THEME, theme_id), SUPPORTS_THEME, label="claim_theme")
                    if paper_id and make_node_id(PAPER, paper_id) in graph.nodes:
                        graph.add_edge(make_node_id(PAPER, paper_id), make_node_id(THEME, theme_id), SUPPORTS_THEME, label="claim_theme")
            if claim.section or claim.page:
                location_key = f"{claim.claim_id}:{claim.section}:{claim.page}"
                location_label = " / ".join(part for part in (claim.section, f"p. {claim.page}" if claim.page else "") if part)
                graph.add_node(
                    EVIDENCE_LOCATION,
                    location_key,
                    location_label or "evidence location",
                    claim_id=claim.claim_id,
                    paper_id=claim.paper_id,
                    section=claim.section,
                    page=claim.page,
                    evidence_type=claim.evidence_type,
                )
                graph.add_edge(claim_node.node_id, make_node_id(EVIDENCE_LOCATION, location_key), HAS_EVIDENCE_LOCATION)

    for session in reading_sessions or []:
        if session.project and session.project != project:
            continue
        session_node = graph.add_node(
            READING_SESSION,
            session.session_id,
            session.session_id,
            paper_id=session.paper_id,
            started_at=session.started_at,
            completed_at=session.completed_at,
            session_status=session.session_status,
            status_before=session.status_before,
            status_after=session.status_after,
        )
        paper_id = make_node_id(PAPER, session.paper_id)
        if paper_id in graph.nodes:
            graph.add_edge(paper_id, session_node.node_id, READ_IN_SESSION)
        for index, action in enumerate(session.follow_up_actions, start=1):
            _add_followup(graph, project, session.paper_id, action, source=session.session_id, index=index, parent_node=session_node.node_id)

    return graph


def analyze_graph(graph: EvidenceGraph) -> GraphAnalytics:
    paper_nodes = _nodes_by_type(graph, PAPER)
    note_nodes = _nodes_by_type(graph, NOTE)
    claim_nodes = _nodes_by_type(graph, CLAIM)
    theme_nodes = _nodes_by_type(graph, THEME)
    analytics = GraphAnalytics()
    for paper_id, node in paper_nodes.items():
        has_note = bool(graph.neighbors(node.node_id, HAS_NOTE))
        has_claim = bool(graph.neighbors(node.node_id, CONTAINS_CLAIM))
        has_theme = bool(graph.neighbors(node.node_id, SUPPORTS_THEME))
        if not has_note:
            analytics.papers_without_notes.append(node.metadata.get("paper_id", "") or paper_id)
        if not has_note and not has_claim and not has_theme:
            analytics.orphan_papers.append(node.metadata.get("paper_id", "") or paper_id)
    for note_id, node in note_nodes.items():
        if not graph.neighbors(node.node_id, CONTAINS_CLAIM):
            analytics.notes_without_claims.append(str(node.metadata.get("paper_id", "") or note_id))
    for claim_id, node in claim_nodes.items():
        if not graph.neighbors(node.node_id, SUPPORTS_THEME):
            analytics.claims_without_themes.append(str(node.metadata.get("claim_id", "") or claim_id))
        if not graph.neighbors(node.node_id, HAS_EVIDENCE_LOCATION):
            analytics.claims_missing_evidence_locations.append(str(node.metadata.get("claim_id", "") or claim_id))
        claim_status = str(node.metadata.get("claim_status", "") or "")
        if claim_status == "deprecated":
            analytics.deprecated_claims.append(str(node.metadata.get("claim_id", "") or claim_id))
        elif claim_status and claim_status not in {"verified", "ready_for_draft_use"}:
            analytics.unverified_claims.append(str(node.metadata.get("claim_id", "") or claim_id))
    for _theme_id, node in theme_nodes.items():
        papers = set(graph.incoming(node.node_id, SUPPORTS_THEME))
        claims = {source for source in graph.incoming(node.node_id, SUPPORTS_THEME) if graph.nodes[source].node_type == CLAIM}
        paper_sources = {source for source in papers if graph.nodes[source].node_type == PAPER}
        if not paper_sources and not claims:
            analytics.isolated_themes.append(_node_key(node))
        review_like = sum(1 for source in paper_sources if _is_review_like(graph.nodes[source]))
        connectivity = ThemeConnectivity(
            theme_id=_node_key(node),
            name=node.label,
            paper_count=len(paper_sources),
            claim_count=len(claims),
            min_papers=int(node.metadata.get("min_papers") or 1),
            min_claims=int(node.metadata.get("min_claims") or 1),
            review_like_paper_count=review_like,
        )
        analytics.theme_connectivity.append(connectivity)
        if connectivity.is_review_heavy:
            analytics.review_paper_heavy_themes.append(connectivity.theme_id)
    analytics.theme_connectivity.sort(key=lambda item: (item.is_weak is False, item.paper_count, item.claim_count, item.theme_id))
    central = [(str(node.metadata.get("paper_id", "") or node_id.removeprefix(f"{PAPER}:")), node.label, graph.degree(node_id)) for node_id, node in paper_nodes.items()]
    analytics.central_papers = [
        (paper_id, label, degree)
        for paper_id, label, degree in sorted(central, key=lambda item: (-item[2], item[1], item[0]))
    ]
    return analytics


def graph_to_json(graph: EvidenceGraph) -> dict[str, Any]:
    return {
        "project": graph.project,
        "nodes": [dataclass_to_plain(node) for node in sorted(graph.nodes.values(), key=lambda item: item.node_id)],
        "edges": [dataclass_to_plain(edge) for edge in sorted(graph.edges, key=lambda item: (item.source, item.target, item.edge_type, item.label))],
    }


def graph_to_json_text(graph: EvidenceGraph) -> str:
    return json.dumps(graph_to_json(graph), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def graph_to_dot(graph: EvidenceGraph) -> str:
    lines = ["digraph evidence_graph {", '  graph [label="Paper Workbench Evidence Graph", labelloc="t"];', "  node [shape=box];"]
    for node in sorted(graph.nodes.values(), key=lambda item: item.node_id):
        shape = _dot_shape(node.node_type)
        label = _dot_escape(f"{node.node_type}\\n{node.label}")
        lines.append(f'  "{_dot_escape(node.node_id)}" [label="{label}", shape={shape}];')
    for edge in sorted(graph.edges, key=lambda item: (item.source, item.target, item.edge_type, item.label)):
        label = _dot_escape(edge.label or edge.edge_type)
        lines.append(f'  "{_dot_escape(edge.source)}" -> "{_dot_escape(edge.target)}" [label="{label}"];')
    lines.append("}")
    return "\n".join(lines) + "\n"


def graph_summary_markdown(graph: EvidenceGraph, analytics: GraphAnalytics | None = None, *, title: str = "Evidence Graph Summary v2.1") -> str:
    analytics = analytics or analyze_graph(graph)
    node_counts = graph.node_counts()
    edge_counts = graph.edge_counts()
    lines = [
        f"# {title}",
        "",
        "This report summarizes a local evidence graph derived from registry, BibTeX, structured notes, claims, themes, and reading-session state. It is a completeness and connectivity aid, not a truth score.",
        "",
        f"Project: `{_escape(graph.project)}`",
        "",
        "## Node Counts",
        "",
        "| Node type | Count |",
        "| --- | ---: |",
    ]
    for node_type, count in sorted(node_counts.items()):
        lines.append(f"| `{_escape(node_type)}` | {count} |")
    if not node_counts:
        lines.append("| none | 0 |")
    lines.extend(["", "## Edge Counts", "", "| Edge type | Count |", "| --- | ---: |"])
    for edge_type, count in sorted(edge_counts.items()):
        lines.append(f"| `{_escape(edge_type)}` | {count} |")
    if not edge_counts:
        lines.append("| none | 0 |")
    lines.extend(
        [
            "",
            "## Connectivity Warnings",
            "",
            f"- Orphan papers: {len(analytics.orphan_papers)}",
            f"- Papers without notes: {len(analytics.papers_without_notes)}",
            f"- Notes without claims: {len(analytics.notes_without_claims)}",
            f"- Claims without themes: {len(analytics.claims_without_themes)}",
            f"- Claims missing evidence locations: {len(analytics.claims_missing_evidence_locations)}",
            f"- Deprecated claims: {len(analytics.deprecated_claims)}",
            f"- Unverified lifecycle claims: {len(analytics.unverified_claims)}",
            f"- Isolated themes: {len(analytics.isolated_themes)}",
            f"- Review-paper-heavy themes: {len(analytics.review_paper_heavy_themes)}",
            "",
            "## Central Papers",
            "",
            _central_papers_table(analytics.central_papers[:10]),
            "",
            "## Theme Connectivity",
            "",
            _theme_connectivity_table(analytics.theme_connectivity),
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def orphan_nodes_markdown(graph: EvidenceGraph, analytics: GraphAnalytics | None = None, *, title: str = "Orphan Nodes v2.1") -> str:
    analytics = analytics or analyze_graph(graph)
    lines = [
        f"# {title}",
        "",
        "Orphan papers are registry papers with no parsed note, no extracted claim edge, and no theme edge. This is a local completeness warning only.",
        "",
        "## Orphan Papers",
        "",
    ]
    lines.extend(_bullet_list(analytics.orphan_papers, empty="No orphan papers found."))
    lines.extend(["", "## Papers Without Notes", ""])
    lines.extend(_bullet_list(analytics.papers_without_notes, empty="No paper-without-note warnings."))
    lines.extend(["", "## Notes Without Claims", ""])
    lines.extend(_bullet_list(analytics.notes_without_claims, empty="No note-without-claim warnings."))
    return "\n".join(lines).rstrip() + "\n"


def theme_connectivity_markdown(graph: EvidenceGraph, analytics: GraphAnalytics | None = None, *, title: str = "Theme Connectivity v2.1") -> str:
    analytics = analytics or analyze_graph(graph)
    return "\n".join(
        [
            f"# {title}",
            "",
            "Theme connectivity counts papers and claims linked through local tags or explicit `supports_theme` fields.",
            "",
            _theme_connectivity_table(analytics.theme_connectivity),
            "",
            "## Isolated Themes",
            "",
            *_bullet_list(analytics.isolated_themes, empty="No isolated themes found."),
            "",
            "## Review-paper-heavy Themes",
            "",
            *_bullet_list(analytics.review_paper_heavy_themes, empty="No review-paper-heavy themes found."),
        ]
    ).rstrip() + "\n"


def central_papers_markdown(graph: EvidenceGraph, analytics: GraphAnalytics | None = None, *, title: str = "Central Papers v2.1") -> str:
    analytics = analytics or analyze_graph(graph)
    return "\n".join(
        [
            f"# {title}",
            "",
            "Centrality is a transparent degree count over the local evidence graph. It is not a quality, importance, or truth score.",
            "",
            _central_papers_table(analytics.central_papers),
        ]
    ).rstrip() + "\n"


def graph_export_inventory_markdown(graph: EvidenceGraph, analytics: GraphAnalytics | None = None, *, title: str = "Graph Export Inventory v2.1") -> str:
    analytics = analytics or analyze_graph(graph)
    return "\n".join(
        [
            f"# {title}",
            "",
            "The graph can be exported as JSON for local tooling or DOT for Graphviz-compatible visual inspection.",
            "",
            "## Export Formats",
            "",
            "| Format | Contents | Boundary |",
            "| --- | --- | --- |",
            "| JSON | Nodes, edges, labels, and local metadata | No PDF text or fabricated claims |",
            "| DOT | Graphviz directed graph with node and edge labels | Visualization aid only |",
            "",
            "## Current Graph Size",
            "",
            f"- Nodes: {len(graph.nodes)}",
            f"- Edges: {len(graph.edges)}",
            f"- Orphan papers: {len(analytics.orphan_papers)}",
            f"- Weak or isolated themes: {sum(1 for item in analytics.theme_connectivity if item.is_weak)}",
        ]
    ).rstrip() + "\n"


def write_graph_export(graph: EvidenceGraph, path: str | Path, *, export_format: str, force: bool = False) -> Path:
    if export_format == "json":
        return write_text(path, graph_to_json_text(graph), force=force)
    if export_format == "dot":
        return write_text(path, graph_to_dot(graph), force=force)
    raise ValueError(f"unsupported graph export format: {export_format}")


def write_graph_report(content: str, path: str | Path, *, force: bool = False) -> Path:
    return write_text(path, content, force=force)


def _add_note(graph: EvidenceGraph, note: PaperNote, paper_node_id: str) -> GraphNode:
    note_key = note.paper_id or note.source_path or f"note-{len(graph.nodes)}"
    note_node = graph.add_node(
        NOTE,
        note_key,
        note.paper_id or Path(note.source_path).name or "note",
        paper_id=note.paper_id,
        citation_key=note.citation_key,
        reading_status=note.reading_status,
        source_path=note.source_path,
        tags=note.tags,
        follow_up_count=len(note.follow_up_actions),
        claim_count=len(note.claims),
    )
    if paper_node_id:
        graph.add_edge(paper_node_id, note_node.node_id, HAS_NOTE)
    for tag in note.tags:
        _add_tag(graph, tag)
        graph.add_edge(note_node.node_id, make_node_id(TAG, tag), TAGGED_WITH)
    for index, action in enumerate(note.follow_up_actions, start=1):
        _add_followup(graph, graph.project, note.paper_id, action, source=note.source_path, index=index, parent_node=note_node.node_id)
    return note_node


def _add_tag(graph: EvidenceGraph, tag: str) -> None:
    normalized = normalize_tag(tag)
    if normalized:
        graph.add_node(TAG, normalized, normalized)


def _add_followup(graph: EvidenceGraph, project: str, paper_id: str, text: str, *, source: str, index: int, parent_node: str) -> None:
    key = f"{paper_id or 'workspace'}:{source}:{index}"
    graph.add_node(FOLLOWUP, key, _short_label(text, fallback="follow-up"), project=project, paper_id=paper_id, source=source, text=text)
    graph.add_edge(parent_node, make_node_id(FOLLOWUP, key), HAS_FOLLOWUP)


def _nodes_by_type(graph: EvidenceGraph, node_type: str) -> dict[str, GraphNode]:
    return {node_id: node for node_id, node in graph.nodes.items() if node.node_type == node_type}


def _author_key(label: str) -> str:
    return normalize_title(label).replace(" ", "-") or label


def _node_key(node: GraphNode) -> str:
    prefix = f"{node.node_type}:"
    return node.node_id.removeprefix(prefix)


def _is_review_like(node: GraphNode) -> bool:
    source_type = str(node.metadata.get("source_type", "")).lower()
    tags = {normalize_tag(tag) for tag in node.metadata.get("tags", []) if tag}
    label = node.label.lower()
    return source_type == "review" or "review" in tags or "review-statement" in tags or "review" in label


def _clean_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    return {key: dataclass_to_plain(value) for key, value in metadata.items() if value not in ("", None, [], {})}


def _short_label(value: str, *, fallback: str) -> str:
    text = re.sub(r"\s+", " ", (value or "").strip())
    if not text:
        return fallback
    return text if len(text) <= 80 else text[:77].rstrip() + "..."


def _central_papers_table(rows: list[tuple[str, str, int]]) -> str:
    lines = ["| Rank | Paper | Degree |", "| ---: | --- | ---: |"]
    if not rows:
        lines.append("| 0 | No paper nodes found. | 0 |")
    for index, (paper_id, label, degree) in enumerate(rows, start=1):
        lines.append(f"| {index} | `{_escape(paper_id)}`: {_escape(label)} | {degree} |")
    return "\n".join(lines)


def _theme_connectivity_table(rows: list[ThemeConnectivity]) -> str:
    lines = ["| Theme | Papers | Claims | Minimum papers | Minimum claims | Review-like papers | Warning |", "| --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    if not rows:
        lines.append("| none | 0 | 0 | 0 | 0 | 0 | No themes loaded. |")
    for row in rows:
        warnings = []
        if row.is_weak:
            warnings.append("below configured minimum")
        if row.is_review_heavy:
            warnings.append("review-heavy")
        lines.append(
            f"| `{_escape(row.theme_id)}` {_escape(row.name)} | {row.paper_count} | {row.claim_count} | {row.min_papers} | {row.min_claims} | {row.review_like_paper_count} | {_escape('; '.join(warnings) or 'ok')} |"
        )
    return "\n".join(lines)


def _bullet_list(values: Iterable[str], *, empty: str) -> list[str]:
    rows = [f"- `{_escape(value)}`" for value in values]
    return rows or [f"- {empty}"]


def _dot_shape(node_type: str) -> str:
    return {
        PAPER: "box",
        AUTHOR: "ellipse",
        BIBTEX_ENTRY: "note",
        NOTE: "folder",
        CLAIM: "component",
        EVIDENCE_LOCATION: "tab",
        THEME: "hexagon",
        TAG: "oval",
        READING_SESSION: "diamond",
        FOLLOWUP: "parallelogram",
        DRAFT: "box3d",
        CITATION: "cds",
    }.get(node_type, "box")


def _dot_escape(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
