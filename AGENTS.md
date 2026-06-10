# AGENTS.md

Instructions for future agents working in this repository:

- Do not add copyrighted PDFs.
- Do not fabricate paper metadata.
- Do not fabricate claims, quotes, conclusions, or paper summaries.
- Preserve user notes and raw files.
- Do not overwrite notes without an explicit force option.
- Keep generated reports reproducible from local inputs.
- Add tests for new parsing or validation rules.
- Prefer lightweight dependencies and the Python standard library.
- Run tests before the final response.
- Run representative CLI smoke tests before the final response.
- Do not push.
- Do not use cloud APIs, LLM APIs, or publisher scraping.
- Keep changes focused and reviewable.
- Keep parsing conservative and transparent; warnings are better than guessed fixes.
- Preserve project-profile files under `projects/` unless explicitly asked to migrate or remove them.
- Do not run destructive workspace migrations. Generate migration reports instead.
- Keep synthetic stress data clearly labelled as synthetic.
- Do not replace synthetic fixtures with real paper metadata or real claims.
- Update golden report tests only when report behavior intentionally changes.
- Avoid brittle tests that depend on timestamps, absolute paths, local machines, or unordered sets.
- Run stress-focused tests before a release when stress fixtures or report generation change.
- Never overwrite non-empty user registry fields during imports without an explicit future overwrite option.
- Prefer `--dry-run` for risky imports and keep import mappings transparent.
- Do not include PDFs in backup bundles by default.
- Add or update tests for every importer, exporter, and mapping rule.
