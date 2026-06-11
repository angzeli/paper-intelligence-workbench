# Authoring Workbench

The v0.6 authoring workbench helps prepare literature-review sections from local, user-tracked evidence.

It generates planning artifacts:

- evidence matrices
- claim banks
- citation banks
- paragraph plans
- subsection readiness reports
- writing packets

It does not write final literature-review prose, invent claims, invent citations, invent quotes, or decide whether a scientific claim is true.

## Core Workflow

```bash
paperwb report evidence-matrix --project zis_photocatalysis --theme photocorrosion --out scratch/photocorrosion_evidence_matrix.md --force
paperwb report claim-bank --project zis_photocatalysis --theme photocorrosion --out scratch/photocorrosion_claim_bank.md --force
paperwb report citation-bank --project zis_photocatalysis --theme photocorrosion --out scratch/photocorrosion_citation_bank.md --force
paperwb report paragraph-plan --project zis_photocatalysis --theme photocorrosion --out scratch/photocorrosion_paragraph_plan.md --force
paperwb report subsection-readiness --project zis_photocatalysis --theme photocorrosion --out scratch/photocorrosion_readiness.md --force
paperwb writing-packet --project zis_photocatalysis --theme photocorrosion --out scratch/photocorrosion_writing_packet.md --force
```

Use these reports before drafting a subsection. They show what is supported, what is weak, which citations are linked, and which evidence gaps should be fixed first.

## Boundary

The authoring workbench is intentionally conservative. It reorganizes claims that already exist in structured notes. If a note has no claim, the tool does not infer one. If a paper lacks a BibTeX key, the citation bank reports that gap instead of guessing.
