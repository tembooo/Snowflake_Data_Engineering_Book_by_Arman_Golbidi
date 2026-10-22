-- SPECIFIC TO THIS SYNTHETIC TEACHING FIXTURE ONLY. Not for production data.
SELECT COALESCE(SUM(energy_mwh),0) AS observed
FROM {{ ref('fct_energy_hourly') }}
HAVING ABS(COALESCE(SUM(energy_mwh),0) - 66.000) > 0.0001
