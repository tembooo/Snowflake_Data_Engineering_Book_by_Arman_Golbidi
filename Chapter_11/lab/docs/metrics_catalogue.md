# KPI catalogue — chapter 11 (synthetic only)

| KPI | Definition and grain | Unit | Owner | Empty-data policy | Fixture expected |
|---|---|---|---|---|---|
| Generation | Sum of accepted current production observations at timestamp + technology | MWh | Energy data steward | Blank when no observed data | 66.000 MWh |
| Consumption | Independent FI source measurement aligned at identical interval UTC | MWh | Grid consumption steward | Blank if unavailable | 60.000 MWh |
| Net position | Generation minus consumption only when both are available at same interval | MWh | Analytics engineering | Blank if one source absent | +6.000 MWh |
| Wind share | Wind generation / total generation, same filter context except technology | % | Analytics engineering | Blank when denominator is 0 | 21.2121% |
| Coverage | Number of expected production technologies with accepted values / 6 | ratio | Data quality owner | Incomplete is flagged; not silently 0 | 6/6 |

**Assumptions:** all data synthetic; snapshot 2026-03-01T10:00:00Z; the consumption source is a separate illustration created for this chapter. This is not a published fact about Finland. Power (MW) is not energy (MWh). A unit change needs contract versioning, test changes, report signoff, and an explicit effective date.

**KPI contract v0.1**: grain, numerator, denominator, unit, UTC interval alignment, source lineage, owner, correction policy, null/zero semantics, expected precision, classification, and change-control owner must be documented. Distinguish snapshot completeness from spatial/national grid coverage.
