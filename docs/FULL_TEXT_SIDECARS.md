# Full-text Sidecars

Paper Workbench does not parse real PDFs by default. v0.5 supports user-provided plain-text sidecars:

```text
data/text/PAPER_ID.txt
projects/zis_photocatalysis/text/PAPER_ID.txt
```

These files must be text the user has the right to store and index. Do not add copyrighted paper text to the repository.

## Index Sidecars

```bash
paperwb index rebuild --project zis_photocatalysis --include-text
paperwb search photocorrosion --project zis_photocatalysis --indexed --text
```

Sidecar IDs are inferred from filenames. For example:

```text
projects/zis_photocatalysis/text/zis_charge_2025.txt
```

maps to paper ID `zis_charge_2025`.

The checked-in sidecars are synthetic fixtures only.

