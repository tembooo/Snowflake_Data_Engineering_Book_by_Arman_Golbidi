# Semantic model specification — chapter 11

**Model status:** design specification, not an actual `.pbix` file or published semantic model.

Star schema:
- `DimTime[interval_utc]` unique UTC key; optional local date/clock attributes with explicit IANA timezone rules; one-to-many to facts.
- `DimTechnology[technology_key]` stable unique technology identifier, one-to-many to FactGeneration.
- `DimGeography[geography_key]` unique region code, one-to-many to FactConsumption.
- `FactGeneration`: grain `(interval_utc, technology_key)`, additive `energy_mwh`, owner Analytics Engineering.
- `FactConsumption`: grain `(interval_utc, geography_key)`, additive `consumption_mwh`, owner Consumption Data Steward.

Relationships should be single-direction dimension-to-fact unless a verified business requirement calls for more. Do not join two facts directly. Percentages, averages, and ratios should be calculated from comparable, filtered base measures, not summed over rows.

Security: read-only BI role, only approved Gold views; separate BI workspace permission, semantic-model RLS review, and Snowflake authentication mode validation. Test both authorised and unauthorised identities.

Refresh: Import is baseline; set schedule by business-approved SLA and capacity/licence. Record ingest completion, Gold ready timestamp, model refresh success, and visual verification separately. DirectQuery is an alternative only after workload/cost/latency tests; every slicer can trigger source queries. Hybrid alternatives depend on available SKU/features.

Acceptance evidence: no missing expected technology, six accepted rows, total 66.000 MWh, separate consumption 60.000 MWh, net +6.000 MWh, blank when consumption absent, no fabricated performance numbers, source-to-dashboard lineage trace, verified RLS, Power BI manual screenshot once executed.
