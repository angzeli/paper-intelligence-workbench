# Workspace Health Report

| Severity | Code | Identifier | Message | Suggestion |
| --- | --- | --- | --- | --- |
| warning | note_parse_warning | synth_photo_2023 | example_note_2.md: Claim 1 is missing evidence location. | Review the note against the structured note format. |
| warning | missing_bibtex_key | synth_finance_2021 | synth_finance_2021 is not linked to a BibTeX key. | Add bibtex_key once a citation entry is available. |
| error | duplicate_doi | 10.0000/synthetic.charge.2024 | DOI 10.0000/synthetic.charge.2024 appears in papers: synth_charge_2024, synth_charge_dup_2024. | Merge duplicate records or correct the DOI. |
| warning | duplicate_title | synthetic charge separation in layered photocatalyst films | Normalized title 'synthetic charge separation in layered photocatalyst films' appears in papers: synth_charge_2024, synth_charge_dup_2024. | Confirm whether these rows represent the same paper. |
| error | duplicate_bibtex_doi | 10.0000/synthetic.charge.2024 | DOI 10.0000/synthetic.charge.2024 appears in BibTeX keys: syntheticCharge2024, syntheticChargeDuplicate2024. | Confirm whether these entries are duplicates. |
| error | missing_author | syntheticPhoto2023 | syntheticPhoto2023 is missing author. | Add the author field if known. |
| error | missing_journal | syntheticPhoto2023 | syntheticPhoto2023 is missing journal. | Add the journal field if known. |
| warning | missing_venue | syntheticPhoto2023 | syntheticPhoto2023 is missing expected venue field(s): journal. | Add journal, booktitle, publisher, school, or venue data when available. |
| warning | empty_field | syntheticPhoto2023 | syntheticPhoto2023 has an empty author field. | Remove empty fields or fill them with user-verified data. |
| warning | empty_field | syntheticPhoto2023 | syntheticPhoto2023 has an empty journaltitle field. | Remove empty fields or fill them with user-verified data. |
| warning | inconsistent_field_name | syntheticPhoto2023 | syntheticPhoto2023 uses journaltitle; expected journal. | Consider renaming journaltitle to journal. |
| warning | empty_field | syntheticPhoto2023 | syntheticPhoto2023 has an empty doi field. | Remove empty fields or fill them with user-verified data. |
| warning | missing_doi | syntheticPhoto2023 | syntheticPhoto2023 has no DOI. | Add a DOI only if you have verified one locally. |
| warning | suspiciously_incomplete | syntheticPhoto2023 | syntheticPhoto2023 looks sparse. | Review the entry for missing author, venue, DOI, or URL fields. |
| error | missing_journal | syntheticAdsorb2022 | syntheticAdsorb2022 is missing journal. | Add the journal field if known. |
| warning | missing_venue | syntheticAdsorb2022 | syntheticAdsorb2022 is missing expected venue field(s): journal. | Add journal, booktitle, publisher, school, or venue data when available. |
| warning | empty_field | syntheticAdsorb2022 | syntheticAdsorb2022 has an empty journal field. | Remove empty fields or fill them with user-verified data. |
| error | invalid_year | syntheticAdsorb2022 | syntheticAdsorb2022 has invalid year '20X2'; expected YYYY. | Use a four-digit publication year. |
| warning | missing_doi | syntheticAdsorb2022 | syntheticAdsorb2022 has no DOI. | Add a DOI only if you have verified one locally. |
| warning | suspiciously_incomplete | syntheticAdsorb2022 | syntheticAdsorb2022 looks sparse. | Review the entry for missing author, venue, DOI, or URL fields. |
| warning | suspiciously_incomplete | extraUnlinked2020 | extraUnlinked2020 looks sparse. | Review the entry for missing author, venue, DOI, or URL fields. |
| warning | bibtex_not_linked_to_registry | extraUnlinked2020 | BibTeX entry extraUnlinked2020 is not linked to any registry paper. | Add the key to a paper row or keep it as an intentional extra reference. |
| warning | registry_missing_bibtex_key | synth_finance_2021 | synth_finance_2021 has no BibTeX key. | Link the paper to a verified BibTeX entry when available. |
| warning | registry_paper_without_notes | synth_adsorb_2022 | synth_adsorb_2022 has no parsed note and no notes_path. | Generate a note template or update notes_path. |
| warning | registry_paper_without_notes | synth_charge_dup_2024 | synth_charge_dup_2024 has no parsed note and no notes_path. | Generate a note template or update notes_path. |
| warning | theme_under_supported | charge-separation | charge separation has 1 supporting claim(s); target is 2. | Add more verified claims or adjust the theme threshold. |
| warning | theme_too_few_papers | charge-separation | charge separation has evidence from 1 paper(s); target is 2. | Add evidence from more papers or adjust the theme threshold. |
| warning | theme_under_supported | photocorrosion | photocorrosion has 1 supporting claim(s); target is 2. | Add more verified claims or adjust the theme threshold. |
| warning | theme_too_few_papers | photocorrosion | photocorrosion has evidence from 1 paper(s); target is 2. | Add evidence from more papers or adjust the theme threshold. |
| warning | theme_under_supported | catalyst-stability | catalyst stability has 1 supporting claim(s); target is 2. | Add more verified claims or adjust the theme threshold. |
| warning | theme_too_few_papers | catalyst-stability | catalyst stability has evidence from 1 paper(s); target is 2. | Add evidence from more papers or adjust the theme threshold. |
| warning | theme_under_supported | co2-adsorption | CO2 adsorption has 0 supporting claim(s); target is 1. | Add more verified claims or adjust the theme threshold. |
| warning | theme_too_few_papers | co2-adsorption | CO2 adsorption has evidence from 0 paper(s); target is 1. | Add evidence from more papers or adjust the theme threshold. |
| warning | theme_under_supported | finance-valuation | finance valuation has 1 supporting claim(s); target is 2. | Add more verified claims or adjust the theme threshold. |
| warning | theme_under_supported | ml-methodology | ML methodology has 0 supporting claim(s); target is 1. | Add more verified claims or adjust the theme threshold. |
| warning | theme_too_few_papers | ml-methodology | ML methodology has evidence from 0 paper(s); target is 1. | Add evidence from more papers or adjust the theme threshold. |
| error | claim_missing_evidence_location | synth_photo_2023:c1 | synth_photo_2023:c1 has no section/page evidence location. | Add a section, page, figure, table, or appendix location. |
