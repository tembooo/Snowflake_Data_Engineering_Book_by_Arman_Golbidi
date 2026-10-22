"""Chapter 14: deterministic, offline energy forecasting/anomaly baseline.
All values are synthetic; no Snowflake or network access required.
"""
from __future__ import annotations
import csv
import json
import statistics
import math
from pathlib import Path
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'synthetic_daily_energy.csv'
BASE_PATTERN = (9.0, 11.0, 10.0, 8.0, 12.0, 7.0, 9.0)

def make_fixture(n=35, inject_anomaly=True):
    assert n >= 35
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    result = []
    for i in range(n):
        # Small deterministic noise prevents a conveniently perfect baseline.
        value = BASE_PATTERN[i % 7] + (i // 7) * 0.15 + (-0.10 if i % 3 == 0 else 0.10)
        if inject_anomaly and i == 34:
            value += 6.0
        result.append({'date_utc': (start + timedelta(days=i)).date().isoformat(),
                       'generation_mwh': round(value, 3), 'source': 'synthetic'})
    return result

def write_fixture(rows, path=DATA):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as file:
        writer=csv.DictWriter(file, fieldnames=['date_utc','generation_mwh','source'])
        writer.writeheader();writer.writerows(rows)

def load_fixture(path=DATA):
    with Path(path).open(newline='', encoding='utf-8') as file:
        rows=list(csv.DictReader(file))
    if len(rows) < 35: raise ValueError('At least 35 dates required for fixed holdouts')
    dates=[datetime.strptime(r['date_utc'],'%Y-%m-%d').date() for r in rows]
    if len(set(dates)) != len(dates): raise ValueError('Duplicate daily business key')
    if any((b-a).days != 1 for a,b in zip(dates,dates[1:])):
        raise ValueError('Daily UTC series must be contiguous and sorted')
    if any(r['source'] != 'synthetic' for r in rows): raise ValueError('Unexpected provenance')
    values=[float(r['generation_mwh']) for r in rows]
    if any(not math.isfinite(v) or v < 0 for v in values):
        raise ValueError('Negative or non-finite energy')
    return values

def predict(values, idx, method='seasonal'):
    lag={'seasonal':7,'last':1}[method]
    if idx < lag: raise ValueError('Not enough history')
    return values[idx-lag]

def mae(actual,pred):
    if len(actual)!=len(pred) or not actual:raise ValueError('bad paired arrays')
    return statistics.mean(abs(a-p) for a,p in zip(actual,pred))

def evaluate(values):
    """Chronological train [0,21), validation [21,28), test [28,35).
    No future outcome is used to predict its own time step.
    """
    if len(values) != 35: raise ValueError('This teaching split requires 35 days')
    val_index=range(21,28);test_index=range(28,35)
    val_errors=[abs(values[i]-predict(values,i,'seasonal')) for i in val_index]
    # Conservative baseline-only heuristic; not a calibrated confidence interval.
    threshold=max(val_errors)+0.5
    actual=[values[i] for i in test_index]
    seasonal=[predict(values,i,'seasonal') for i in test_index]
    last=[predict(values,i,'last') for i in test_index]
    flags=[abs(a-p)>threshold for a,p in zip(actual,seasonal)]
    return {
        'training_days':21,'validation_days':7,'test_days':7,
        'test_mae_seasonal_mwh':round(mae(actual,seasonal),4),
        'test_mae_last_value_mwh':round(mae(actual,last),4),
        'validation_residual_threshold_mwh':round(threshold,4),
        'flagged_test_indices':[28+i for i,v in enumerate(flags) if v],
        'predictions':[{'date_index':i,'actual_mwh':actual[i-28],
                        'seasonal_prediction_mwh':seasonal[i-28],
                        'is_flagged':flags[i-28]} for i in test_index]
    }

if __name__=='__main__':
    write_fixture(make_fixture())
    print(json.dumps(evaluate(load_fixture()), indent=2))
