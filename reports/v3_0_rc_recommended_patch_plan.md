# v3.0rc Recommended Patch Plan

## Goal

Prepare Paper Intelligence Workbench for a coherent v3.0 release candidate as a
local-first literature-review evidence operating system.

## Recommended Scope

1. Freeze stable, experimental, internal, and deprecated CLI command groups.
2. Freeze documented v3 data schemas:
   - registry CSV
   - structured notes
   - claims export
   - project profiles
   - themes JSON
   - rule JSON
   - sync plans
   - backup manifests
3. Refresh public docs:
   - getting started
   - first real project
   - core workflow
   - CLI reference
   - data safety
   - known limitations
4. Run a clean external-user dogfooding simulation from the public docs.
5. Run data-safety, notebook validation, full pytest, and stable CLI smoke
   checks.
6. Defer broad feature expansion until after v3.0rc.

## Architecture Tasks To Consider

- Split `cli.py` only after stable command contracts are updated.
- Gradually migrate more reports to `paper_workbench.markdown`.
- Keep domain-specific finding dataclasses unless a concrete report adapter
  removes real duplication.
- Document which Python helpers are safe for local scripts.

## Must Not Expand

- No cloud APIs.
- No LLM APIs.
- No publisher scraping.
- No copied PDFs or full paper text.
- No automatic scientific claim generation.
- No arbitrary shell or Python execution from workflow/rule files.

## Release Gate

v3.0rc should be considered ready only when a new user can install or import the
package, create a clean dogfooding project, validate local data, extract claims
from manually written notes, generate core evidence reports, and understand the
experimental boundaries from the docs.

