"""Project-aware local SQLite search index."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
import sqlite3

from .bibtex import parse_bibtex_file
from .claims import collect_notes
from .io import read_text
from .paths import display_path as _shared_display_path
from .registry import display_authors, load_registry, normalize_doi, normalize_title
from .schema import BibTeXEntry, Claim, Paper, PaperNote, ProjectTheme
from .tags import format_tags, load_themes, parse_tags


INDEX_SCHEMA_VERSION = "1"
DEFAULT_LIMIT = 25
SOURCE_WEIGHTS = {
    "paper": 10,
    "claim": 9,
    "text": 8,
    "note": 7,
    "bibtex": 5,
    "theme": 4,
    "tag": 3,
}


@dataclass(slots=True)
class IndexedRecord:
    record_id: str
    project_id: str
    source_type: str
    source_path: str = ""
    paper_id: str = ""
    title: str = ""
    body_text: str = ""
    tags: str = ""
    year: str = ""
    reading_status: str = ""
    content_hash: str = ""


@dataclass(slots=True)
class SearchResult:
    record_id: str
    project_id: str
    source_type: str
    paper_id: str
    title: str
    matched_field: str
    snippet: str
    score: int
    path: str = ""


@dataclass(slots=True)
class IndexStatus:
    index_path: str
    project_id: str
    exists: bool
    fts_enabled: bool = False
    last_rebuild: str = ""
    total_records: int = 0
    counts: dict[str, int] = field(default_factory=dict)
    changed_record_ids: list[str] = field(default_factory=list)
    missing_record_ids: list[str] = field(default_factory=list)
    orphaned_record_ids: list[str] = field(default_factory=list)
    orphaned_record_paths: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


def default_index_path(root: str | Path = ".") -> Path:
    return Path(root) / ".paperwb" / "index.sqlite"


def sqlite_fts5_available() -> bool:
    try:
        connection = sqlite3.connect(":memory:")
        connection.execute("CREATE VIRTUAL TABLE fts_probe USING fts5(content)")
        connection.close()
        return True
    except sqlite3.Error:
        return False


def _connect(index_path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(index_path)
    connection.row_factory = sqlite3.Row
    return connection


def _has_fts_table(connection: sqlite3.Connection) -> bool:
    row = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'records_fts'").fetchone()
    return row is not None


def init_index(index_path: str | Path) -> bool:
    target = Path(index_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fts_enabled = sqlite_fts5_available()
    with _connect(target) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                record_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source_path TEXT NOT NULL,
                paper_id TEXT NOT NULL,
                title TEXT NOT NULL,
                body_text TEXT NOT NULL,
                tags TEXT NOT NULL,
                year TEXT NOT NULL,
                reading_status TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                indexed_at TEXT NOT NULL
            )
            """
        )
        connection.execute("CREATE INDEX IF NOT EXISTS idx_records_project ON records(project_id)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_records_source ON records(project_id, source_type)")
        if fts_enabled and not _has_fts_table(connection):
            connection.execute(
                """
                CREATE VIRTUAL TABLE records_fts USING fts5(
                    record_id UNINDEXED,
                    title,
                    body_text,
                    tags
                )
                """
            )
        connection.execute("INSERT OR REPLACE INTO metadata(key, value) VALUES(?, ?)", ("schema_version", INDEX_SCHEMA_VERSION))
        connection.execute("INSERT OR REPLACE INTO metadata(key, value) VALUES(?, ?)", ("fts_enabled", str(fts_enabled).lower()))
    return fts_enabled


def clear_index(index_path: str | Path, *, project_id: str | None = None) -> None:
    target = Path(index_path)
    if not target.exists():
        return
    with _connect(target) as connection:
        has_fts = _has_fts_table(connection)
        if project_id:
            record_ids = [row["record_id"] for row in connection.execute("SELECT record_id FROM records WHERE project_id = ?", (project_id,))]
            if has_fts and record_ids:
                connection.executemany("DELETE FROM records_fts WHERE record_id = ?", [(record_id,) for record_id in record_ids])
            connection.execute("DELETE FROM records WHERE project_id = ?", (project_id,))
            connection.execute("DELETE FROM metadata WHERE key LIKE ?", (f"project:{project_id}:%",))
        else:
            if has_fts:
                connection.execute("DELETE FROM records_fts")
            connection.execute("DELETE FROM records")
            connection.execute("DELETE FROM metadata WHERE key LIKE 'project:%'")


def rebuild_index(index_path: str | Path, records: list[IndexedRecord], *, project_id: str) -> IndexStatus:
    records = unique_indexed_records(records)
    init_index(index_path)
    now = datetime.now(timezone.utc).isoformat()
    with _connect(index_path) as connection:
        has_fts = _has_fts_table(connection)
        record_ids = [row["record_id"] for row in connection.execute("SELECT record_id FROM records WHERE project_id = ?", (project_id,))]
        if has_fts and record_ids:
            connection.executemany("DELETE FROM records_fts WHERE record_id = ?", [(record_id,) for record_id in record_ids])
        connection.execute("DELETE FROM records WHERE project_id = ?", (project_id,))
        rows = [
            (
                record.record_id,
                record.project_id,
                record.source_type,
                record.source_path,
                record.paper_id,
                record.title,
                record.body_text,
                record.tags,
                record.year,
                record.reading_status,
                record.content_hash,
                now,
            )
            for record in records
        ]
        connection.executemany(
            """
            INSERT INTO records (
                record_id, project_id, source_type, source_path, paper_id, title,
                body_text, tags, year, reading_status, content_hash, indexed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        if has_fts:
            connection.executemany(
                "INSERT INTO records_fts(record_id, title, body_text, tags) VALUES(?, ?, ?, ?)",
                [(record.record_id, record.title, record.body_text, record.tags) for record in records],
            )
        connection.execute("INSERT OR REPLACE INTO metadata(key, value) VALUES(?, ?)", (f"project:{project_id}:last_rebuild", now))
        connection.execute("INSERT OR REPLACE INTO metadata(key, value) VALUES(?, ?)", (f"project:{project_id}:record_count", str(len(records))))
    return index_status(index_path, project_id=project_id)


def _record_hash(*parts: str) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update((part or "").encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def unique_indexed_records(records: list[IndexedRecord]) -> list[IndexedRecord]:
    """Return records with deterministic unique IDs for SQLite primary keys."""
    seen: Counter[str] = Counter()
    unique: list[IndexedRecord] = []
    for record in records:
        seen[record.record_id] += 1
        if seen[record.record_id] == 1:
            unique.append(record)
            continue
        unique.append(
            IndexedRecord(
                record_id=f"{record.record_id}:dup{seen[record.record_id]}",
                project_id=record.project_id,
                source_type=record.source_type,
                source_path=record.source_path,
                paper_id=record.paper_id,
                title=record.title,
                body_text=record.body_text,
                tags=record.tags,
                year=record.year,
                reading_status=record.reading_status,
                content_hash=record.content_hash,
            )
        )
    return unique


def _record(
    *,
    project_id: str,
    kind: str,
    key: str,
    source_path: str = "",
    paper_id: str = "",
    title: str = "",
    body_text: str = "",
    tags: str | list[str] = "",
    year: str = "",
    reading_status: str = "",
) -> IndexedRecord:
    tag_text = format_tags(tags) if isinstance(tags, list) else str(tags or "")
    record_id = f"{project_id}:{kind}:{key or hashlib.sha1((title + body_text).encode('utf-8')).hexdigest()[:12]}"
    return IndexedRecord(
        record_id=record_id,
        project_id=project_id,
        source_type=kind,
        source_path=source_path,
        paper_id=paper_id,
        title=title,
        body_text=body_text,
        tags=tag_text,
        year=year,
        reading_status=reading_status,
        content_hash=_record_hash(kind, source_path, paper_id, title, body_text, tag_text, year, reading_status),
    )


def build_index_records(
    *,
    project_id: str,
    registry_path: str | Path,
    bibtex_path: str | Path,
    notes_dir: str | Path,
    themes_path: str | Path,
    text_dir: str | Path | None = None,
    include_text: bool = False,
) -> list[IndexedRecord]:
    records: list[IndexedRecord] = []
    papers = load_registry(registry_path) if Path(registry_path).exists() else []
    paper_by_id = {paper.paper_id: paper for paper in papers}
    paper_by_key = {paper.bibtex_key: paper for paper in papers if paper.bibtex_key}
    paper_by_doi = {normalize_doi(paper.doi): paper for paper in papers if paper.doi}
    paper_by_title = {normalize_title(paper.title): paper for paper in papers if paper.title}

    for paper in papers:
        body = "\n".join(
            [
                f"Authors: {display_authors(paper.authors)}",
                f"Year: {paper.year}",
                f"Journal: {paper.journal}",
                f"DOI: {paper.doi}",
                f"BibTeX key: {paper.bibtex_key}",
                f"Reading status: {paper.reading_status}",
                f"Comment: {paper.user_comment}",
            ]
        )
        records.append(
            _record(
                project_id=project_id,
                kind="paper",
                key=paper.paper_id,
                source_path=str(registry_path),
                paper_id=paper.paper_id,
                title=paper.title,
                body_text=body,
                tags=paper.tags,
                year=paper.year,
                reading_status=paper.reading_status,
            )
        )

    if Path(bibtex_path).exists():
        for index, entry in enumerate(parse_bibtex_file(bibtex_path), start=1):
            paper = _match_entry_to_paper(entry, paper_by_key, paper_by_doi, paper_by_title)
            fields = "\n".join(f"{key}: {value}" for key, value in sorted(entry.raw_fields.items()))
            records.append(
                _record(
                    project_id=project_id,
                    kind="bibtex",
                    key=entry.key or str(index),
                    source_path=str(bibtex_path),
                    paper_id=paper.paper_id if paper else "",
                    title=entry.title or entry.key,
                    body_text=f"Entry type: {entry.entry_type}\nKey: {entry.key}\nAuthors: {display_authors(entry.authors)}\n{fields}",
                    year=entry.year,
                )
            )

    notes = collect_notes(notes_dir) if Path(notes_dir).exists() else []
    for note in notes:
        note_body = read_text(note.source_path) if note.source_path and Path(note.source_path).exists() else _note_body(note)
        paper = paper_by_id.get(note.paper_id)
        records.append(
            _record(
                project_id=project_id,
                kind="note",
                key=Path(note.source_path).stem if note.source_path else note.paper_id,
                source_path=note.source_path,
                paper_id=note.paper_id,
                title=f"Note for {paper.title if paper else note.paper_id}",
                body_text=note_body,
                tags=note.tags,
                reading_status=note.reading_status,
            )
        )
        for claim in note.claims:
            records.append(_claim_record(project_id, claim))

    themes = load_themes(themes_path) if Path(themes_path).exists() else []
    for theme in themes:
        records.append(_theme_record(project_id, theme, themes_path))
    for tag in sorted({tag for paper in papers for tag in parse_tags(paper.tags)} | {tag for theme in themes for tag in theme.tags}):
        tagged_papers = [paper.paper_id for paper in papers if tag in parse_tags(paper.tags)]
        records.append(
            _record(
                project_id=project_id,
                kind="tag",
                key=tag,
                source_path=str(themes_path),
                title=f"Tag: {tag}",
                body_text="Papers: " + ", ".join(tagged_papers),
                tags=tag,
            )
        )

    if include_text and text_dir and Path(text_dir).exists():
        for sidecar in sorted(Path(text_dir).glob("*.txt")):
            paper_id = sidecar.stem
            paper = paper_by_id.get(paper_id)
            records.append(
                _record(
                    project_id=project_id,
                    kind="text",
                    key=paper_id,
                    source_path=str(sidecar),
                    paper_id=paper_id,
                    title=f"Text sidecar for {paper.title if paper else paper_id}",
                    body_text=read_text(sidecar),
                    tags=paper.tags if paper else "",
                    year=paper.year if paper else "",
                    reading_status=paper.reading_status if paper else "",
                )
            )
    return unique_indexed_records(records)


def _match_entry_to_paper(
    entry: BibTeXEntry,
    paper_by_key: dict[str, Paper],
    paper_by_doi: dict[str, Paper],
    paper_by_title: dict[str, Paper],
) -> Paper | None:
    if entry.key and entry.key in paper_by_key:
        return paper_by_key[entry.key]
    if entry.doi and normalize_doi(entry.doi) in paper_by_doi:
        return paper_by_doi[normalize_doi(entry.doi)]
    return paper_by_title.get(normalize_title(entry.title))


def _note_body(note: PaperNote) -> str:
    return "\n".join(
        [
            note.one_sentence_summary,
            note.why_it_matters,
            note.research_question,
            note.methods,
            note.key_findings,
            note.limitations,
            note.useful_for,
            note.not_useful_for,
            note.personal_reading_notes,
        ]
    )


def _claim_record(project_id: str, claim: Claim) -> IndexedRecord:
    body = "\n".join(
        [
            claim.claim_text,
            f"Evidence type: {claim.evidence_type}",
            f"Location: {claim.section or claim.page}",
            f"Quote or paraphrase: {claim.quote_or_paraphrase}",
            f"Confidence: {claim.confidence}",
            f"Strength: {claim.strength}",
            f"Supports theme: {claim.supports_theme}",
            f"Comment: {claim.user_comment}",
        ]
    )
    return _record(
        project_id=project_id,
        kind="claim",
        key=claim.claim_id,
        source_path=claim.note_file,
        paper_id=claim.paper_id,
        title=claim.claim_text,
        body_text=body,
        tags=claim.tags,
    )


def _theme_record(project_id: str, theme: ProjectTheme, themes_path: str | Path) -> IndexedRecord:
    return _record(
        project_id=project_id,
        kind="theme",
        key=theme.theme_id,
        source_path=str(themes_path),
        title=theme.name,
        body_text=f"{theme.description}\nMinimum claims: {theme.min_claims}\nMinimum papers: {theme.min_papers}",
        tags=theme.tags,
    )


def index_status(index_path: str | Path, *, project_id: str, current_records: list[IndexedRecord] | None = None) -> IndexStatus:
    target = Path(index_path)
    if not target.exists():
        return IndexStatus(
            index_path=str(target),
            project_id=project_id,
            exists=False,
            warnings=["Index is missing. Run `paperwb index rebuild`."],
        )
    with _connect(target) as connection:
        fts_enabled = _has_fts_table(connection)
        counts = {
            row["source_type"]: int(row["count"])
            for row in connection.execute(
                "SELECT source_type, COUNT(*) AS count FROM records WHERE project_id = ? GROUP BY source_type",
                (project_id,),
            )
        }
        total = sum(counts.values())
        metadata = {
            row["key"]: row["value"]
            for row in connection.execute("SELECT key, value FROM metadata WHERE key LIKE ?", (f"project:{project_id}:%",))
        }
        changed: list[str] = []
        missing: list[str] = []
        orphaned: list[str] = []
        orphaned_paths: dict[str, str] = {}
        warnings: list[str] = []
        if current_records is not None:
            stored = {
                row["record_id"]: {"content_hash": row["content_hash"], "source_path": row["source_path"]}
                for row in connection.execute("SELECT record_id, content_hash, source_path FROM records WHERE project_id = ?", (project_id,))
            }
            current_ids = {record.record_id for record in current_records}
            for record in current_records:
                if record.record_id not in stored:
                    missing.append(record.record_id)
                elif stored[record.record_id]["content_hash"] != record.content_hash:
                    changed.append(record.record_id)
            for record_id, stored_record in stored.items():
                if record_id not in current_ids:
                    orphaned.append(record_id)
                    orphaned_paths[record_id] = stored_record["source_path"]
            if changed:
                warnings.append(f"{len(changed)} indexed record(s) differ from local files.")
            if missing:
                warnings.append(f"{len(missing)} local record(s) are missing from the index.")
            if orphaned:
                warnings.append(f"{len(orphaned)} indexed record(s) are no longer present in local files.")
        return IndexStatus(
            index_path=str(target),
            project_id=project_id,
            exists=True,
            fts_enabled=fts_enabled,
            last_rebuild=metadata.get(f"project:{project_id}:last_rebuild", ""),
            total_records=total,
            counts=counts,
            changed_record_ids=changed,
            missing_record_ids=missing,
            orphaned_record_ids=orphaned,
            orphaned_record_paths=orphaned_paths,
            warnings=warnings,
        )


def _source_filter(source_types: set[str] | None) -> tuple[str, list[str]]:
    if not source_types:
        return "", []
    placeholders = ", ".join("?" for _ in source_types)
    return f" AND source_type IN ({placeholders})", sorted(source_types)


def search_index(
    index_path: str | Path,
    query: str,
    *,
    project_id: str | None = None,
    source_types: set[str] | None = None,
    exact: bool = False,
    limit: int = DEFAULT_LIMIT,
) -> list[SearchResult]:
    target = Path(index_path)
    if not target.exists():
        raise FileNotFoundError(f"Index not found: {target}")
    with _connect(target) as connection:
        rows = _search_with_fts(connection, query, project_id=project_id, source_types=source_types, exact=exact)
        like_rows = _search_with_like(connection, query, project_id=project_id, source_types=source_types, exact=exact)
        if rows is None:
            rows = like_rows
        else:
            rows = _merge_rows(rows, like_rows)
    results = [_row_to_result(row, query, exact=exact) for row in rows]
    results = [result for result in results if result.score > 0]
    results.sort(key=lambda result: (-result.score, result.source_type, result.paper_id, result.record_id))
    return results[:limit]


def _search_with_fts(
    connection: sqlite3.Connection,
    query: str,
    *,
    project_id: str | None,
    source_types: set[str] | None,
    exact: bool,
) -> list[sqlite3.Row] | None:
    if not _has_fts_table(connection):
        return None
    fts_query = _fts_query(query, exact=exact)
    if not fts_query:
        return []
    source_sql, source_params = _source_filter(source_types)
    project_sql = " AND r.project_id = ?" if project_id else ""
    params: list[str] = [fts_query]
    if project_id:
        params.append(project_id)
    params.extend(source_params)
    try:
        return list(
            connection.execute(
                f"""
                SELECT r.* FROM records r
                JOIN records_fts f ON r.record_id = f.record_id
                WHERE records_fts MATCH ?{project_sql}{source_sql}
                """,
                params,
            )
        )
    except sqlite3.Error:
        return None


def _search_with_like(
    connection: sqlite3.Connection,
    query: str,
    *,
    project_id: str | None,
    source_types: set[str] | None,
    exact: bool,
) -> list[sqlite3.Row]:
    source_sql, source_params = _source_filter(source_types)
    project_sql = "WHERE project_id = ?" if project_id else "WHERE 1 = 1"
    params: list[str] = [project_id] if project_id else []
    params.extend(source_params)
    rows = list(connection.execute(f"SELECT * FROM records {project_sql}{source_sql}", params))
    return [row for row in rows if _matches_record(row, query, exact=exact)]


def _merge_rows(primary: list[sqlite3.Row], secondary: list[sqlite3.Row]) -> list[sqlite3.Row]:
    seen: set[str] = set()
    merged: list[sqlite3.Row] = []
    for row in [*primary, *secondary]:
        record_id = row["record_id"]
        if record_id in seen:
            continue
        seen.add(record_id)
        merged.append(row)
    return merged


def _fts_query(query: str, *, exact: bool) -> str:
    if exact:
        phrase = query.strip().replace('"', " ")
        return f'"{phrase}"' if phrase else ""
    terms = re.findall(r"[A-Za-z0-9_]+", query.lower())
    return " ".join(terms)


def _matches_record(row: sqlite3.Row, query: str, *, exact: bool) -> bool:
    haystack = " ".join([row["title"], row["body_text"], row["tags"], row["paper_id"], row["year"], row["reading_status"]]).lower()
    needle = query.lower()
    if exact:
        return needle in haystack
    return all(term in haystack for term in needle.split())


def _row_to_result(row: sqlite3.Row, query: str, *, exact: bool) -> SearchResult:
    matched_field = _matched_field(row, query, exact=exact)
    return SearchResult(
        record_id=row["record_id"],
        project_id=row["project_id"],
        source_type=row["source_type"],
        paper_id=row["paper_id"],
        title=row["title"],
        matched_field=matched_field,
        snippet=_snippet(row[matched_field] if matched_field in {"title", "body_text", "tags"} else row["body_text"], query),
        score=_score_row(row, query, exact=exact),
        path=row["source_path"],
    )


def _matched_field(row: sqlite3.Row, query: str, *, exact: bool) -> str:
    fields = ("title", "tags", "body_text")
    for field_name in fields:
        value = row[field_name].lower()
        if exact and query.lower() in value:
            return field_name
        if not exact and all(term in value for term in query.lower().split()):
            return field_name
    return "body_text"


def _score_row(row: sqlite3.Row, query: str, *, exact: bool) -> int:
    query_l = query.lower()
    terms = [query_l] if exact else query_l.split()
    title = row["title"].lower()
    tags = row["tags"].lower()
    body = row["body_text"].lower()
    score = SOURCE_WEIGHTS.get(row["source_type"], 1)
    if query_l and query_l in title:
        score += 30
    if query_l and query_l in tags:
        score += 24
    if query_l and query_l in body:
        score += 18
    for term in terms:
        if not term:
            continue
        score += 6 * title.count(term)
        score += 4 * tags.count(term)
        score += min(10, body.count(term))
    return score


def _snippet(text: str, query: str, *, width: int = 180) -> str:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    if not cleaned:
        return ""
    lower = cleaned.lower()
    query_l = query.lower().strip()
    positions = [lower.find(query_l)] if query_l else [-1]
    if not query_l or positions[0] == -1:
        terms = [term for term in query_l.split() if term]
        positions = [lower.find(term) for term in terms if lower.find(term) >= 0]
    position = min(positions) if positions else 0
    start = max(0, position - width // 3)
    end = min(len(cleaned), start + width)
    snippet = cleaned[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(cleaned):
        snippet += "..."
    return snippet


def display_path(path: str | Path, *, base_path: str | Path | None = None) -> str:
    return _shared_display_path(path, base_path=base_path)


def search_results_markdown(results: list[SearchResult], query: str, *, base_path: str | Path | None = None) -> str:
    lines = [
        f"# Indexed Search Results: {query}",
        "",
        "| Source | Paper ID | Title | Matched Field | Score | Snippet | Path |",
        "| --- | --- | --- | --- | ---: | --- | --- |",
    ]
    if not results:
        lines.append("| none |  | No matches. |  | 0 |  |  |")
    for result in results:
        lines.append(
            "| {source} | {paper_id} | {title} | {field} | {score} | {snippet} | {path} |".format(
                source=_escape(result.source_type),
                paper_id=_escape(result.paper_id),
                title=_escape(result.title),
                field=_escape(result.matched_field),
                score=result.score,
                snippet=_escape(result.snippet),
                path=_escape(display_path(result.path, base_path=base_path)),
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def index_status_markdown(status: IndexStatus, *, base_path: str | Path | None = None) -> str:
    lines = [
        "# Local Search Index Status",
        "",
        f"- Project: {status.project_id}",
        f"- Index path: {display_path(status.index_path, base_path=base_path)}",
        f"- Index exists: {str(status.exists).lower()}",
        f"- FTS5 enabled: {str(status.fts_enabled).lower()}",
        f"- Last rebuild: {status.last_rebuild or 'never'}",
        f"- Total records: {status.total_records}",
        "",
        "## Records by Source Type",
        "",
        "| Source type | Records |",
        "| --- | ---: |",
    ]
    for source_type, count in sorted(status.counts.items()):
        lines.append(f"| {source_type} | {count} |")
    if not status.counts:
        lines.append("| none | 0 |")
    lines.extend(["", "## Diagnostics", ""])
    if status.warnings:
        lines.extend(f"- {warning}" for warning in status.warnings)
    else:
        lines.append("- No stale-index warnings.")
    if status.changed_record_ids:
        lines.extend(["", "### Changed Records", ""])
        lines.extend(f"- {record_id}" for record_id in status.changed_record_ids[:50])
    if status.missing_record_ids:
        lines.extend(["", "### Missing Records", ""])
        lines.extend(f"- {record_id}" for record_id in status.missing_record_ids[:50])
    if status.orphaned_record_ids:
        lines.extend(["", "### Orphaned Indexed Records", ""])
        for record_id in status.orphaned_record_ids[:50]:
            source_path = display_path(status.orphaned_record_paths.get(record_id, ""), base_path=base_path)
            suffix = f" ({source_path})" if source_path else ""
            lines.append(f"- {record_id}{suffix}")
    return "\n".join(lines).rstrip() + "\n"


def _escape(value: str) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def source_counts(records: list[IndexedRecord]) -> dict[str, int]:
    return dict(Counter(record.source_type for record in records))
