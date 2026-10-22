# Power BI specification (NOT a .pbix; NOT run in Power BI)

Gold fact: `ENERGY_LAB.GOLD.FCT_ENERGY_HOURLY`.
Grain: one provider, technology, UTC interval. Measure: additive `ENERGY_MWH`.

DAX:
```
Generation MWh := SUM ( 'fct_energy_hourly'[energy_mwh] )
Visible Observations := COUNTROWS ( 'fct_energy_hourly' )
```

Fixture expected: Generation MWh 66.000; Visible Observations 6.
Choice: Import vs DirectQuery is conditional on evaluated freshness and workload.
No assumption about current connector SSO configuration; verify in the target tenant.
Mark report and refresh tests PENDING until a Power BI Desktop/Service check is logged.
Consumption is not in this base fixture; do NOT call 66.000 MWh net position.
