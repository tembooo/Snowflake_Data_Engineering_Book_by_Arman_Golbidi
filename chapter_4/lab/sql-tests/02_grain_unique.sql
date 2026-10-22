-- PASS iff zero rows returned.
SELECT source_code,metric_code,interval_start_utc,COUNT(*) AS n
FROM book_ch04.fact_energy_hourly
GROUP BY source_code,metric_code,interval_start_utc
HAVING COUNT(*) > 1;
