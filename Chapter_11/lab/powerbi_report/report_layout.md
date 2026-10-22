# Energy Analytics — suggested Power BI page specification

**Status:** design-only. No Power BI application or PBIX/PBIP export was used.

## Page 1: Overview (one synthetic UTC snapshot)
- Title: `SYNTHETIC Energy Generation and Consumption — interval 2026-03-01 10:00 UTC`.
- Four KPI cards with their full units: generation `66.000 MWh`, consumption `60.000 MWh`, net `+6.000 MWh`, expected technology coverage `6/6`.
- Horizontal bar chart: accepted generation by technology. Hydro 18; Nuclear 16; Wind 14; Bioenergy 8; Solar 6; Other 4 (all MWh).
- Wind share tile: `21.2121%` across all six technologies at the same interval, not national energy mix.
- Footer: `Synthetic demonstration; one interval only; consumption from separate illustrative data source; no real Finland national coverage claims`.
- Accessibility: sufficient contrast, descriptive alt text, no colour-only encoding, units in labels, optional keyboard-friendly slicers.

## Page 2: Data Quality and Lineage
- KPI catalogue contract version, acceptance status, selected technology, source interval, source-ready time, model refresh time (only after real implementation).
- A completeness indicator that distinguishes `0 MWh` from `no observed row` and unknown consumption from zero.
- A table of source/model/report owners and links to redacted documentation.
- Do not show fabricated live refresh timestamps. Model refresh times are placeholders until implementation.

## Acceptance scenarios
1. At the full filter context, generation = 66.000 MWh, consumption = 60.000 MWh, net = +6.000 MWh.
2. Wind bar = 14.000 MWh and share = 21.2121%.
3. Missing consumption displays unknown net (blank) and explains why.
4. Removing technology does not silently report fixture coverage as national coverage.
5. One interval must not be turned into a trend line.
6. Validate different source user identities and RLS in Power BI service before publishing.
