-- Requires an authorized monitoring role. ACCOUNT_USAGE is not immediate.
SELECT query_id, query_tag, warehouse_name, warehouse_size,
       total_elapsed_time, execution_time, queued_overload_time,
       queued_provisioning_time, partitions_scanned, partitions_total,
       bytes_spilled_to_local_storage, bytes_spilled_to_remote_storage
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE query_tag = 'book_ch12_energy_benchmark_v1'
ORDER BY start_time DESC LIMIT 100;
