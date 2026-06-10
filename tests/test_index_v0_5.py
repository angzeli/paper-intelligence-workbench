from __future__ import annotations

import sqlite3
import subprocess
import sys

from paper_workbench.index import (
    build_index_records,
    clear_index,
    index_status,
    rebuild_index,
    search_index,
    search_results_markdown,
)
from paper_workbench.search import search_papers
from paper_workbench.registry import load_registry

from conftest import EXAMPLE_REGISTRY, ROOT, ZIS_PROJECT


def run_cli(*args: str):
    return subprocess.run([sys.executable, "-m", "paper_workbench.cli", *args], check=False, text=True, capture_output=True)


def _zis_records(include_text: bool = True):
    return build_index_records(
        project_id="zis_photocatalysis",
        registry_path=ZIS_PROJECT / "registry.csv",
        bibtex_path=ZIS_PROJECT / "bibtex" / "library.bib",
        notes_dir=ZIS_PROJECT / "notes",
        themes_path=ZIS_PROJECT / "themes.json",
        text_dir=ZIS_PROJECT / "text",
        include_text=include_text,
    )


def test_sqlite_index_rebuild_search_and_status(tmp_path):
    index_path = tmp_path / "index.sqlite"
    records = _zis_records(include_text=True)
    status = rebuild_index(index_path, records, project_id="zis_photocatalysis")
    assert status.exists is True
    assert status.total_records == len(records)
    assert status.counts["paper"] == 2
    assert status.counts["claim"] == 2
    assert status.counts["text"] == 2

    results = search_index(index_path, "charge separation", project_id="zis_photocatalysis")
    assert results
    assert results[0].score >= results[-1].score
    assert any(result.source_type == "claim" for result in results)
    assert "Indexed Search Results" in search_results_markdown(results, "charge separation")


def test_text_sidecars_are_optional(tmp_path):
    without_text = _zis_records(include_text=False)
    with_text = _zis_records(include_text=True)
    assert not any(record.source_type == "text" for record in without_text)
    assert any(record.source_type == "text" for record in with_text)


def test_index_clear_removes_project_records(tmp_path):
    index_path = tmp_path / "index.sqlite"
    rebuild_index(index_path, _zis_records(), project_id="zis_photocatalysis")
    clear_index(index_path, project_id="zis_photocatalysis")
    status = index_status(index_path, project_id="zis_photocatalysis")
    assert status.exists is True
    assert status.total_records == 0


def test_index_status_detects_changed_local_records(tmp_path):
    index_path = tmp_path / "index.sqlite"
    records = _zis_records()
    rebuild_index(index_path, records, project_id="zis_photocatalysis")
    records[0].content_hash = "changed"
    status = index_status(index_path, project_id="zis_photocatalysis", current_records=records)
    assert status.changed_record_ids
    assert any("differ" in warning for warning in status.warnings)


def test_search_falls_back_when_fts_table_is_absent(tmp_path):
    index_path = tmp_path / "index.sqlite"
    rebuild_index(index_path, _zis_records(), project_id="zis_photocatalysis")
    with sqlite3.connect(index_path) as connection:
        connection.execute("DROP TABLE IF EXISTS records_fts")
    results = search_index(index_path, "photocorrosion", project_id="zis_photocatalysis")
    assert any(result.paper_id == "zis_stability_2024" for result in results)


def test_project_specific_indexing_keeps_results_scoped(tmp_path):
    index_path = tmp_path / "index.sqlite"
    records = _zis_records()
    rebuild_index(index_path, records, project_id="zis_photocatalysis")
    rebuild_index(index_path, [], project_id="empty_project")
    assert search_index(index_path, "charge separation", project_id="zis_photocatalysis")
    assert not search_index(index_path, "charge separation", project_id="empty_project")


def test_cli_index_rebuild_status_search_and_clear(tmp_path):
    index_path = tmp_path / "index.sqlite"
    status_report = tmp_path / "index_status.md"
    rebuild = run_cli(
        "index",
        "rebuild",
        "--project",
        "zis_photocatalysis",
        "--include-text",
        "--index",
        str(index_path),
        "--out",
        str(status_report),
        "--force",
    )
    assert rebuild.returncode == 0, rebuild.stderr
    assert "Records:" in rebuild.stdout
    assert status_report.exists()

    status = run_cli("index", "status", "--project", "zis_photocatalysis", "--include-text", "--check-files", "--index", str(index_path))
    assert status.returncode == 0, status.stderr
    assert "Total records" in status.stdout

    search = run_cli("search", "photocorrosion", "--project", "zis_photocatalysis", "--indexed", "--text", "--index", str(index_path))
    assert search.returncode == 0, search.stderr
    assert "zis_stability_2024" in search.stdout

    out = tmp_path / "search.md"
    exported = run_cli("search", "charge separation", "--project", "zis_photocatalysis", "--indexed", "--index", str(index_path), "--out", str(out))
    assert exported.returncode == 0, exported.stderr
    assert "Indexed Search Results" in out.read_text(encoding="utf-8")

    cleared = run_cli("index", "clear", "--project", "zis_photocatalysis", "--index", str(index_path))
    assert cleared.returncode == 0, cleared.stderr
    after = run_cli("index", "status", "--project", "zis_photocatalysis", "--index", str(index_path))
    assert "Total records: 0" in after.stdout


def test_old_substring_search_backward_compatibility():
    papers = load_registry(EXAMPLE_REGISTRY)
    assert search_papers(papers, "charge separation")
    result = run_cli("search", "photocorrosion", "--registry", str(EXAMPLE_REGISTRY), "--notes-dir", str(ROOT / "data" / "notes"))
    assert result.returncode == 0
    assert "synth_photo_2023" in result.stdout
