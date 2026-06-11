# Paragraph Planner

The paragraph planner proposes an evidence-aware order for a theme subsection.

Default purposes are:

- opening context and scope
- key mechanism or problem
- primary evidence from tracked papers
- methods that explain how evidence was produced
- limitations, caveats, and competing interpretations
- gap leading to the next subsection

For each paragraph, the report lists claim IDs, papers to cite, claims to avoid, missing evidence, and caveats.

```bash
paperwb report paragraph-plan --project zis_photocatalysis --theme photocorrosion --out scratch/photocorrosion_paragraph_plan.md --force
```

The output is not polished prose. It is a planning checklist for the user.
