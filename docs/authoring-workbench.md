# Authoring Workbench

The authoring workbench helps prepare literature-review sections from user-tracked evidence.

It may generate:

- evidence matrices
- claim banks
- citation banks
- paragraph plans
- subsection readiness reports
- writing packets

It must not generate final polished literature-review prose, invent claims, invent citations, or infer conclusions from papers.

## Example

```bash
paperwb report evidence-matrix --project zis_photocatalysis --theme photocorrosion --out scratch/evidence_matrix.md --force
paperwb report claim-bank --project zis_photocatalysis --theme photocorrosion --out scratch/claim_bank.md --force
paperwb report citation-bank --project zis_photocatalysis --theme photocorrosion --out scratch/citation_bank.md --force
paperwb report paragraph-plan --project zis_photocatalysis --theme photocorrosion --out scratch/paragraph_plan.md --force
paperwb report subsection-readiness --project zis_photocatalysis --theme photocorrosion --out scratch/readiness.md --force
paperwb writing-packet --project zis_photocatalysis --theme photocorrosion --out scratch/writing_packet.md --force
```

Detailed docs:

- [AUTHORING_WORKBENCH.md](AUTHORING_WORKBENCH.md)
- [EVIDENCE_MATRIX.md](EVIDENCE_MATRIX.md)
- [CLAIM_BANK.md](CLAIM_BANK.md)
- [CITATION_BANK.md](CITATION_BANK.md)
- [PARAGRAPH_PLANNER.md](PARAGRAPH_PLANNER.md)
- [SUBSECTION_READINESS.md](SUBSECTION_READINESS.md)
- [WRITING_PACKET.md](WRITING_PACKET.md)
