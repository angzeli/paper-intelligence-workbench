# Contradictions And Tensions

v2.2 supports manual contradiction or tension groups. A group records claims the
user wants to review together because they may conflict, depend on different
conditions, or need careful framing.

```bash
paperwb contradictions create --project zis_photocatalysis --theme photocorrosion --description "Different stability outcomes under different controls."
paperwb contradictions add contradiction_photocorrosion_1 PAPER_ID:c1 --project zis_photocatalysis
paperwb contradictions report --project zis_photocatalysis --out reports/contradictions.md
```

The report may include simple tag-based possible-tension suggestions, but these
are not automatic contradiction findings. Users decide what belongs in a group
and how it is resolved.
