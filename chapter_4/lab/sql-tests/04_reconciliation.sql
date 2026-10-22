-- PASS iff zero rows returned (fixed synthetic fixture only).
SELECT COUNT(*) AS actual_n, SUM(energy_mwh) AS actual_mwh
FROM book_ch04.fact_energy_hourly
HAVING COUNT(*) <> 6 OR SUM(energy_mwh) <> 97.500;
