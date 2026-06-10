from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_REGISTRY = ROOT / "data" / "registries" / "example_papers.csv"
EXAMPLE_BIBTEX = ROOT / "data" / "bibtex" / "example_library.bib"
EXAMPLE_NOTES = ROOT / "data" / "notes"
EXAMPLE_THEMES = ROOT / "data" / "examples" / "themes.json"
EXAMPLE_ZOTERO_CSV = ROOT / "data" / "examples" / "zotero_export.csv"
EXAMPLE_GENERIC_CSV = ROOT / "data" / "examples" / "generic_papers.csv"
EXAMPLE_GENERIC_MAPPING = ROOT / "data" / "examples" / "generic_mapping.json"
EXAMPLE_IMPORT_BIBTEX = ROOT / "data" / "examples" / "library_import.bib"
EXAMPLE_RIS = ROOT / "data" / "examples" / "library.ris"
PROJECTS = ROOT / "projects"
ZIS_PROJECT = PROJECTS / "zis_photocatalysis"
FINANCE_PROJECT = PROJECTS / "finance_reading"
ML_PROJECT = PROJECTS / "ml_methods"
STRESS_ZIS_PROJECT = PROJECTS / "stress_zis_photocatalysis"
STRESS_FINANCE_PROJECT = PROJECTS / "stress_finance_reading"
STRESS_ML_PROJECT = PROJECTS / "stress_ml_methods"
FIXTURES = ROOT / "tests" / "fixtures"
