# Power BI implementation guide (not a fabricated PBIX)

1. Obtain approved Snowflake account, BI warehouse, BI_READER role and read access only to audited Gold views.
2. In current Power BI Desktop: Get data > Snowflake. Supply server and warehouse, authenticate with the organisation-approved method, pick Import initially. Verify product versions and connector migration status (ADBC/ODBC).
3. Load distinct dimensions plus Gold generation; load separately authorised consumption if available. Validate query folding after any Power Query changes.
4. Establish one-to-many, single-direction relationships from dimensions to facts. Mark a Date table only when it meets its date-range/key requirements.
5. Create measures from `measures.dax`; verify expected totals against `metrics_validation.json`. Treat no-consumption as BLANK, never zero.
6. Build page: KPI cards (generation, consumption, net, coverage), six-bar technology comparison, event-time trend (needs more than one interval!), and provenance text.
7. Use Performance Analyzer, refresh history, Snowflake Query History to test with measured logs. No real performance claims are provided by this package.
8. Test dataset/report permissions, RLS and source credentials separately before publish. Record owner and rollback procedure.
9. Save actual `.pbix` or `.pbip` after manual authoring in Power BI Desktop; this package does not claim to include either.

**Visual warning:** one interval cannot produce a meaningful time trend. For a trend exercise generate additional explicitly synthetic intervals and extend acceptance tests before plotting.
