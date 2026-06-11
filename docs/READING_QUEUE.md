# Reading Queue

The reading queue ranks local papers for the next reading session using
transparent registry, note, claim, and theme metadata.

## Command

```bash
paperwb reading queue --project zis_photocatalysis
paperwb reading queue --project zis_photocatalysis --theme photocorrosion --limit 10
paperwb reading queue --project zis_photocatalysis --priority high --out scratch/reading_queue.md --force
```

## Ranking Signals

The queue prioritizes:

- high or critical `reading_priority`
- high user `priority`
- unread, skimmed, or partially read papers
- papers included in the literature review but missing parsed notes
- papers with notes but no extracted claims
- papers linked to weak or incomplete themes
- recently added papers

Warnings are shown for missing BibTeX keys or missing note paths.

## Interpretation Boundary

The queue is not a scientific quality score. It is a local workflow ordering
based on gaps the user has already tracked.

