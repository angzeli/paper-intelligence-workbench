# v3.5 Recommended Patch Plan

Focus v3.5 on real-user feedback from the new documentation structure rather
than another feature subsystem.

## Recommended Work

1. Dogfood the v3.4 cookbook on a real local 10-15 paper project.
2. Record which recipes are confusing, missing flags, or too verbose.
3. Decide whether a static-site generator is worth the dependency and
   maintenance cost.
4. Add a README quickstart transcript test if the public quickstart changes.
5. Tighten report-gallery examples after users identify the most valuable
   reports.
6. Keep experimental command docs clearly labelled until real use confirms
   stable contracts.

## Not Recommended

- Do not add cloud sync.
- Do not add LLM summarization.
- Do not add publisher scraping.
- Do not turn the tool into a web app.
- Do not add more generated report families before dogfooding current ones.
