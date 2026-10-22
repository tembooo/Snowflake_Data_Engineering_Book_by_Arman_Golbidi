-- PASS iff zero rows returned; valid for generation_mwh metric.
SELECT raw_id FROM book_ch04.fact_energy_hourly
WHERE source_code IS NULL OR metric_code IS NULL
   OR interval_start_utc IS NULL OR energy_mwh IS NULL
   OR energy_mwh < 0;
