-- PASS iff zero rows returned: the corrected solar reading must win.
SELECT raw_id, energy_mwh FROM book_ch04.fact_energy_hourly
WHERE source_code='SOLAR_FI'
  AND interval_start_utc='2026-01-15 01:00:00'::TIMESTAMP_NTZ
  AND (raw_id<>7 OR energy_mwh<>13.000);
