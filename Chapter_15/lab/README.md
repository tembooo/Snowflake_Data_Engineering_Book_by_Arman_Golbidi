# Chapter 15 Companion: Finland Energy Analytics Capstone

**Book:** Snowflake Data Engineering: From Fundamentals to Production-Ready Data Pipelines  
**Chapter:** 15, printed pages 265–288  
**Author:** Arman Golbidi  
**Status:** offline teaching capstone accepted; real Snowflake/Power BI deployment NOT EXECUTED.

## Run safely, with no account and no network

From the directory containing `project/`, `operations/` and `architecture_decisions/`:

```bash
python -m unittest discover -s project/tests -v
python project/python/capstone.py
```

Requires Python 3.10+ standard library; no third-party dependencies, account secrets or
network connections. Results are in `project/output/` and `test_results/`.

### Verified offline fixture result

- Original 12 deliveries, one identical duplicate, two quarantined records.
- One tombstoned business key; six current gold observations.
- Generation total **66.000 MWh**. Wind corrected to **14.000 MWh**.
- **21/21 local unit tests PASSED** in the chapter build environment.
- Fixture SHA-256 is recorded in `project/contracts/energy_event_v1.yml` and outputs.

All observations, provider names and credits are **synthetic illustrations**;
this repository does not include or fetch real Fingrid or Statistics Finland data.

## Cloud extension (NOT tested)

Inspect SQL in `project/sql/` in sequence. **No live Snowflake SQL was executed.**
Requires a designated test account, approved small warehouse, secure upload method,
permissions and a named reviewer. SQL contains sample object names and may require
adaptation to current account edition / permissions / file format behaviour.
The cleanup file keeps all destructive commands commented. See
`operations/cloud_release_checklist.md` before any cloud action.

Power BI `project/bi/semantic_model.md` specifies measures only; no `.pbix` was made.
For real source access, check API registration, rate limits, dataset metadata,
licences and required attribution before collecting or redistributing any data.

## Evidence and rights

- `test_results/offline_tests.txt`: independent unittest execution record.
- `test_results/offline_run.json`: acceptance output.
- `architecture_decisions/`: rationale and alternative designs.
- `operations/`: incident response and cloud release gates.
- `references/source_register.md`: documentation and external references.

Editorial release tag suggestion: `ch15-capstone-review-v1`; NOT claimed published.
Project source code is originally authored for this chapter; referenced GitHub
repositories are reading references and not bundled or implied licensed.
