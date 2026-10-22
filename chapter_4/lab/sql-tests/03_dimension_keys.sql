-- PASS iff zero rows returned. Checks required dimension membership.
SELECT f.raw_id FROM book_ch04.fact_energy_hourly f
LEFT JOIN book_ch04.dim_source s ON s.source_key=f.source_key
LEFT JOIN book_ch04.dim_metric m ON m.metric_key=f.metric_key
LEFT JOIN book_ch04.dim_date_utc d ON d.utc_date_key=f.utc_date_key
WHERE s.source_key IS NULL OR m.metric_key IS NULL OR d.utc_date_key IS NULL;
