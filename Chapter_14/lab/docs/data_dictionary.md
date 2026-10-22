# Data dictionary and guarantees

`synthetic_daily_energy.csv` (actual file: `data/synthetic_daily_energy.csv`):
- `date_utc`: unique contiguous UTC date, daily grain.
- `generation_mwh`: numeric 3-decimal synthetic daily energy amount, MWh, nonnegative and finite.
- `source`: constant `synthetic`, rejects unsanctioned provenance.

`data/baseline_results.json`:
- `test_mae_seasonal_mwh`: held-out absolute-error average for lag 7.
- `test_mae_last_value_mwh`: held-out absolute-error average for lag 1.
- `validation_residual_threshold_mwh`: maximum validation seasonal residual + 0.5 MWh, not a calibrated interval.
- `flagged_test_indices`: zero-based indices satisfying the configured threshold.

`ai_eval_cases.csv`: manually authored evaluation prompts, with expected behaviours; not a scored AI model result, not machine inference outputs, and no private content.
