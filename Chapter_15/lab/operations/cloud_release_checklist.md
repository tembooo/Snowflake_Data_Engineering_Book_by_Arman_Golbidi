# Cloud integration: PENDING, not a completed deployment

[ ] Confirm account, region, edition and test scope.
[ ] Obtain role-grant approval and check negative access tests with actual restricted role.
[ ] Approve a small auto-suspending warehouse and non-warehouse spend guardrails.
[ ] Verify Snowflake COPY syntax and CSV parsing using a fresh test account.
[ ] Run SQL quality checks; collect query IDs and compare 6-row/66.000 fixture output.
[ ] Verify true row-source provenance, replay and same-revision conflict blocking.
[ ] Measure actual query latency, partition pruning and credit records.
[ ] Connect an authorised Power BI workspace and capture actual refresh evidence.
[ ] Test failure recovery, delayed correction and role revocation.
[ ] Peer review security, costs, permissions, licences and safe cleanup.
[ ] Record tag SHA, software versions, reviewer, evidence and outstanding risks.

Never assert production readiness based solely on the shipped offline tests.
