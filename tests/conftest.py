from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_REGISTRY = ROOT / "data" / "registries" / "example_papers.csv"
EXAMPLE_BIBTEX = ROOT / "data" / "bibtex" / "example_library.bib"
EXAMPLE_NOTES = ROOT / "data" / "notes"
EXAMPLE_THEMES = ROOT / "data" / "examples" / "themes.json"
PROJECTS = ROOT / "projects"
ZIS_PROJECT = PROJECTS / "zis_photocatalysis"
FINANCE_PROJECT = PROJECTS / "finance_reading"
ML_PROJECT = PROJECTS / "ml_methods"
STRESS_ZIS_PROJECT = PROJECTS / "stress_zis_photocatalysis"
STRESS_FINANCE_PROJECT = PROJECTS / "stress_finance_reading"
STRESS_ML_PROJECT = PROJECTS / "stress_ml_methods"
FIXTURES = ROOT / "tests" / "fixtures"
