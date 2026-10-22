-- This function covers the last 14 days, subject to privileges and context.
SELECT file_name, status, row_count, row_parsed,
       error_count, last_load_time
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
  TABLE_NAME => 'BRONZE_ENERGY',
  START_TIME => DATEADD('day',-1,CURRENT_TIMESTAMP())
))
ORDER BY last_load_time DESC;
