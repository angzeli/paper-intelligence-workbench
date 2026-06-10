# Example Literature Review Workflow

This walkthrough shows how to use the workbench as a local operating system for a small literature review. The examples use synthetic data only.

## Why This Workflow Matters

A literature review usually fails quietly when notes, claims, citations, and themes drift apart. This workflow keeps those pieces linked:

```text
registry -> notes -> claims -> themes -> reports -> outline
```

The tool does not decide whether a claim is true. It checks whether your own evidence tracking is complete enough to support writing.

## Step 1. Define a Review Project

Use a project profile when you want registry, notes, BibTeX, themes, and reports isolated from other reviews.

```bash
paperwb project list
paperwb project validate zis_photocatalysis
```

For a new review:

```bash
paperwb project init my_review
```

Then edit `projects/my_review/registry.csv`, `projects/my_review/bibtex/library.bib`, `projects/my_review/themes.json`, and files under `projects/my_review/notes/`.

## Step 2. Maintain the Paper Registry

The registry should contain only user-verified metadata.

```bash
paperwb validate-registry data/registries/example_papers.csv
paperwb list --registry data/registries/example_papers.csv --status unread
paperwb list --registry data/registries/example_papers.csv --tag photocorrosion
```

Use registry validation to catch duplicate DOIs, duplicate normalized titles, invalid status values, missing notes for read papers, and broken local PDF paths.

## Step 3. Validate BibTeX

BibTeX audit links citation keys back to registry rows.

```bash
paperwb validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv
```

Treat warnings as review prompts, not automatic corrections. The parser is intentionally lightweight and conservative.

## Step 4. Write Structured Notes

Generate a note template before reading a paper:

```bash
paperwb note-template synth_charge_2024 --registry data/registries/example_papers.csv --output /private/tmp/synth_charge_2024_note.md
```

Fill in claims only when you have read and verified the evidence. Claims should include evidence type, section/page location, confidence, strength, tags, and theme support.

## Step 5. Extract Claims

```bash
paperwb claims data/notes --output /private/tmp/paperwb_claims.csv
```

Claim extraction is conservative. If a note does not follow the template, the parser returns warnings instead of guessing.

## Step 6. Map Evidence to Themes

Themes live in JSON files and map tags to literature-review topics.

```bash
paperwb report evidence-map --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out /private/tmp/paperwb_evidence_map.md --force
paperwb report theme-dashboard --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out /private/tmp/paperwb_theme_dashboard.md --force
```

Use these reports before writing a subsection. They show strong claims, weak claims, missing evidence locations, missing notes, and themes that need more papers.

## Step 7. Audit Citations Before Drafting

```bash
paperwb report citation-audit --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out /private/tmp/paperwb_citation_audit.md --force
```

Review every finding that says a paper lacks notes, a claim lacks evidence location, a theme is under-supported, or a BibTeX key is missing.

## Step 8. Build an Evidence-Based Outline

```bash
paperwb report section-outline --theme photocorrosion --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out /private/tmp/paperwb_photocorrosion_outline.md --force
```

The outline is not a drafted literature review. It lists candidate papers, tracked claims, weak claims, unresolved questions, and missing evidence that should be addressed before writing prose.

## Step 9. Export Local Artifacts

```bash
paperwb export claims-json --project zis_photocatalysis --out /private/tmp/paperwb_zis_claims.json --force
paperwb export theme-claims --project zis_photocatalysis --theme photocorrosion --out /private/tmp/paperwb_photocorrosion_claims.json --force
```

Exports are local files. They should not contain absolute maintainer paths.

## Review Checklist

Before writing a literature-review subsection, confirm:

- Every cited paper has a registry row and BibTeX key.
- Every cited claim comes from a note.
- Every important claim has an evidence location.
- Weak or speculative claims are not used as core support.
- Themes have enough papers and claims for your review standard.
- Reports were regenerated after the latest note or registry edits.
