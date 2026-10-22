"""Run only on the included synthetic dataset; no Snowflake dependency."""
from pathlib import Path
import csv
from collections import defaultdict

path = Path(__file__).with_name("energy_sample.csv")
seen = set()
count = defaultdict(int)
values = defaultdict(list)
with path.open(encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        key = (row["scenario_id"], row["event_utc"], row["source"])
        if key in seen:
            raise ValueError(f"Duplicate synthetic key: {key}")
        seen.add(key)
        if int(row["minutes"]) != 15:
            raise ValueError(f"Unexpected synthetic interval: {row['minutes']}")
        count[row["source"]] += 1
        values[row["source"]].append(float(row["power_mw"]))

result = {source: (count[source], round(sum(vals)/len(vals), 1))
          for source, vals in sorted(values.items())}
assert result == {"SOLAR": (2, 0.0), "WIND": (2, 490.0)}, result
print("PASS: synthetic row counts and mean-power outputs")
for source, (n, mean) in result.items():
    print(f"{source}: intervals={n}, mean_power_mw={mean:.1f}")
