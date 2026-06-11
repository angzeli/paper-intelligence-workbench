# Text Sidecars

Text sidecars are user-provided `.txt` files that can be audited and indexed locally.

Typical project path:

```text
projects/<project>/text/PAPER_ID.txt
```

Typical legacy path:

```text
data/text/PAPER_ID.txt
```

Sidecars should contain only text the user has the right to store locally. Do not add copyrighted full paper text to the repository.

## Discovery

The v0.7 file scanner reports top-level `.txt` files in the selected `text/` folder. A filename stem matching a registry `paper_id` is treated as a possible paper match.

```bash
paperwb files sidecars --project zis_photocatalysis
paperwb files sidecars --project zis_photocatalysis --out scratch/text_sidecars.md --force
```

## Search Integration

The existing indexed-search workflow can index sidecars:

```bash
paperwb index rebuild --project zis_photocatalysis --include-text
paperwb search photocorrosion --project zis_photocatalysis --indexed --text
```

The file scanner does not create text sidecars and does not extract text from PDFs.
