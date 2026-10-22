import csv
from collections import defaultdict

energy = defaultdict(float)
seen = set()
with open("energy_sample.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        key = (row["timestamp_utc"], row["source"])
        assert key not in seen, f"Duplicate: {key}"
        seen.add(key)
        minutes = int(row["minutes"])
        assert minutes > 0, "Invalid interval"
        energy[row["source"]] += float(row["power_mw"]) * minutes / 60
print({k: round(v, 2) for k, v in sorted(energy.items())})
