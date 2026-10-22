"""Offline teaching logic only. NOT Snowflake authorization enforcement."""
from __future__ import annotations
import csv
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_policy(path=ROOT / "security_model.json"):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def effective_actions(role, model):
    roles = model["roles"]
    visiting, visited, actions = set(), set(), set()

    def walk(name):
        if name not in roles:
            raise ValueError(f"Unknown role: {name}")
        if name in visiting:
            raise ValueError(f"Cycle in role inheritance: {name}")
        if name in visited:
            return
        visiting.add(name)
        actions.update(roles[name]["actions"])
        for parent in roles[name]["inherits"]:
            walk(parent)
        visiting.remove(name)
        visited.add(name)
    walk(role)
    return actions


def evaluate_matrix(model):
    return [(role, action, expected, action in effective_actions(role, model))
            for role, action, expected in model["approved_tests"]]


def accepted_energy(path=ROOT / "data" / "energy_fixture.csv"):
    with open(path, newline="", encoding="utf-8") as f:
        items = list(csv.DictReader(f))
    ids = [r["event_id"] for r in items]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate event ID")
    total = sum((Decimal(r["mwh"]) for r in items), Decimal("0"))
    if any(Decimal(r["mwh"]) < 0 for r in items):
        raise ValueError("Negative energy")
    return len(items), total


def usage_register(path=ROOT / "data" / "cost_register.csv"):
    with open(path, newline="", encoding="utf-8") as f:
        items = list(csv.DictReader(f))
    if not items:
        raise ValueError("Empty register")
    summary = {}
    for r in items:
        amount = Decimal(r["quantity"])
        if amount < 0:
            raise ValueError("Negative consumption")
        key = (r["category"], r["unit"])
        summary[key] = summary.get(key, Decimal("0")) + amount
    return summary


def projected_credits(summary):
    return sum((amount for (category, unit), amount in summary.items() if unit == "credit"), Decimal(0))


def warehouse_credits(summary):
    return sum((amount for (category, unit), amount in summary.items() if category == "warehouse_compute" and unit == "credit"), Decimal(0))


def format_report():
    model = load_policy()
    matrix = evaluate_matrix(model)
    assert all(expected == observed for _, _, expected, observed in matrix)
    count, energy = accepted_energy()
    usage = usage_register()
    return {"fixture_rows": count, "energy_mwh": str(energy),
            "warehouse_credits_assumed": str(warehouse_credits(usage)),
            "all_credit_categories_assumed": str(projected_credits(usage)),
            "denied_cases_offline": sum(not expected for _, _, expected, _ in matrix),
            "status": "OFFLINE simulation only; NOT a Snowflake access audit"}


if __name__ == "__main__":
    print(json.dumps(format_report(), indent=2))
