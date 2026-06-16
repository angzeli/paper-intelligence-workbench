# Performance

Paper Intelligence Workbench is designed for local projects with hundreds of
papers, many notes, and repeated report runs. v2.5 adds lightweight performance
sanity checks rather than a heavy benchmark suite.

## Sanity Script

```bash
python scripts/performance_sanity.py --papers 500 --claims 1500 --themes 50 --out reports/performance_sanity_v2_5.md --force
```

The script creates a temporary synthetic project and times:

- project generation
- registry loading
- note and claim parsing
- BibTeX parsing
- theme loading
- registry validation
- BibTeX validation
- citation audit
- workspace doctor
- search-index record building
- SQLite index rebuild
- search-index status check
- evidence-map rendering

This is a smoke check, not a strict benchmark. Results depend on the local
machine, Python version, and filesystem.

## Stress Project Generation

```bash
python scripts/stress_project_generation.py --root scratch/stress_v2_5 --project stress_v2_5 --papers 500 --claims 1500 --themes 50 --force
```

Stress projects are synthetic and intentionally include some malformed or weak
data to exercise validation paths. Keep them under ignored scratch or temporary
folders.
