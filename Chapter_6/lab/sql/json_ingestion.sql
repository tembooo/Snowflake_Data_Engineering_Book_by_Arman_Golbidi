-- Chapter 6: run ONLY in a disposable, authorized database/schema.
-- No credentials, real datasets, or external stages. Temporary table is session-scoped.
CREATE OR REPLACE TEMPORARY TABLE CH06_BRONZE_JSON (
    SOURCE_LINE NUMBER(10,0),
    RAW_LINE VARCHAR
);
INSERT INTO CH06_BRONZE_JSON (SOURCE_LINE, RAW_LINE)
SELECT COLUMN1, COLUMN2 FROM VALUES
  (1, '{"schema_version":1,"provider":"synthetic-fi","envelope_id":"demo-2026-01-15T10Z","observed_at_utc":"2026-01-15T10:00:00Z","unit":"MWh","observations":[{"tech":"wind","mwh":21.25},{"tech":"solar","mwh":12.50},{"tech":"hydro","mwh":18.00}]}'),
  (2, '{"schema_version":2,"provider":"synthetic-fi","envelope_id":"demo-2026-01-15T11Z","observed_at_utc":"2026-01-15T11:00:00Z","unit":"MWh","measurements":[{"tech":"wind","mwh":19.00},{"tech":"solar","mwh":13.00},{"tech":"hydro","mwh":13.75}],"source":{"system":"book-fixture"}}'),
  (3, '{"schema_version":2,"provider":"synthetic-fi","envelope_id":"demo-reject-missing","observed_at_utc":"2026-01-15T12:00:00Z","unit":"MWh","measurements":[{"tech":"wind","mwh":null},{"tech":"solar","mwh":2.00},{"tech":"hydro","mwh":3.00}]}'),
  (4, '{"schema_version":2,"provider":"synthetic-fi","envelope_id":"broken","measurements":[');

SELECT COUNT(*) AS physical_lines FROM CH06_BRONZE_JSON;
-- Expected (fixture): 4
