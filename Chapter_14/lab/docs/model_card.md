# Model Card — Seasonal Energy Baseline (Chapter 14)

**Status:** educational offline prototype; not suitable for deployment or autonomous grid operations.
**Version:** chapter14-draft-2026-10-22; **author:** Arman Golbidi.

## Intended use
Teach chronological evaluation of one-day-ahead daily energy forecasts and a simple residual-based anomaly alert. Not for real electricity production planning, asset safety, financial trades, or physical control.

## Provenance and scope
All **35 daily measurements** are generated in `ml_baseline.py`; none is from Finnish energy infrastructure or a Snowflake account. The earlier book's six accepted observations totaling 66.000 MWh are separate and **not extended or measured** here. Generated dates: 2026-01-01 through 2026-02-04 UTC, 35 days. An artificial +6 MWh outlier is added to day index 34.

## Methods
- Last-value baseline predicts $y_t$ with $y_{t-1}$.
- Seasonal naive baseline predicts $y_t$ with $y_{t-7}$.
- Split by time: training 0–20, validation 21–27, final test 28–34.
- Anomaly threshold = largest absolute seasonal residual on validation + 0.5 MWh (teaching heuristic, **not** a calibrated interval).
- Scoring: MAE in MWh; anomaly flag if held-out absolute seasonal residual exceeds validation threshold.

## Verified synthetic results
- Last-value test MAE = **3.2500 MWh**.
- Seasonal test MAE = **1.0643 MWh**.
- Validation residual threshold = **0.8500 MWh**.
- Injected anomaly at index 34 flagged. One artificial event does **not** support claims about real-world precision, recall or physical anomalies.
- 16 local Python unittest cases passed in the generated package.

## Limitations and review blockers
- Only 35 days; no measured seasonality, holidays, weather, curtailment, sensor outages or cross-device generalization.
- Single artificial outlier with known location; no unbiased anomaly benchmark.
- Actual-availability risk: a lag feature depends on when the earlier day's observation was published or corrected.
- No calibrated predictive uncertainty; validation threshold is not a statistical confidence interval.
- No live Snowflake ML function/Cortex invocation; billing, region and RBAC untested.

## Promotion checklist
☐ 1+ years approved real-world history with legal basis and owner approval.
☐ Frozen `as_of` reconstruction and chronological rolling-origin evaluation.
☐ Operational metric thresholds approved ahead of final holdout.
☐ Human review of false alarms and physical plausibility.
☐ Approved region/model route, least-privilege roles and data minimization.
☐ Measured cost by meter including inference and search serving where applicable.
☐ Owner, version, rollback, monitoring and incident runbook.
