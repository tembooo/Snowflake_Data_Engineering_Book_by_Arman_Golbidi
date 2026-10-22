import copy
import csv
import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import security_lab as lab


class Chapter13OfflineTests(unittest.TestCase):
    def setUp(self):
        self.model = lab.load_policy()

    def test_01_fixture_has_six_rows(self):
        self.assertEqual(lab.accepted_energy()[0], 6)

    def test_02_fixture_total(self):
        self.assertEqual(lab.accepted_energy()[1], Decimal("66.000"))

    def test_03_roles_positive(self):
        self.assertIn("SELECT:GOLD.GENERATION_DAILY", lab.effective_actions("BOOK13_ANALYST", self.model))

    def test_04_roles_negative(self):
        self.assertNotIn("SELECT:RAW.METER_EVENT", lab.effective_actions("BOOK13_ANALYST", self.model))

    def test_05_writer_permission(self):
        self.assertIn("INSERT:RAW.METER_EVENT", lab.effective_actions("BOOK13_LOADER", self.model))

    def test_06_writer_not_admin(self):
        self.assertNotIn("CREATE:USER", lab.effective_actions("BOOK13_LOADER", self.model))

    def test_07_steward_unmask(self):
        self.assertIn("UNMASK:GOLD.CONTACT_CONTEXT.CONTACT_EMAIL", lab.effective_actions("BOOK13_STEWARD", self.model))

    def test_08_unknown_role_rejected(self):
        with self.assertRaises(ValueError): lab.effective_actions("GHOST", self.model)

    def test_09_cyclic_roles_rejected(self):
        m = copy.deepcopy(self.model)
        m["roles"]["BOOK13_GOLD_READER"]["inherits"].append("BOOK13_ANALYST")
        with self.assertRaisesRegex(ValueError, "Cycle"): lab.effective_actions("BOOK13_ANALYST", m)

    def test_10_all_matrix_cases(self):
        self.assertTrue(all(expected == observed for _, _, expected, observed in lab.evaluate_matrix(self.model)))

    def test_11_unexpected_role_inheritance_detected(self):
        m = copy.deepcopy(self.model)
        m["roles"]["BOOK13_ANALYST"]["inherits"].append("BOOK13_LOADER")
        self.assertIn("INSERT:RAW.METER_EVENT", lab.effective_actions("BOOK13_ANALYST", m))

    def test_12_register_categories(self):
        self.assertEqual(len(lab.usage_register()), 4)

    def test_13_warehouse_not_total(self):
        usage = lab.usage_register()
        self.assertEqual(lab.warehouse_credits(usage), Decimal("2.5"))
        self.assertEqual(lab.projected_credits(usage), Decimal("3.65"))

    def test_14_storage_different_unit(self):
        self.assertIn(("storage", "GB-month"), lab.usage_register())

    def test_15_money_not_invented(self):
        with open(lab.ROOT / "data" / "cost_register.csv", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertTrue(all(r["rate_status"] == "assumption" for r in rows))
        self.assertTrue(all(not r["rate_currency"] and not r["unit_rate"] for r in rows))

    def test_16_negative_cost_detected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "ledger.csv"
            path.write_text("category,unit,quantity\nwarehouse_compute,credit,-1\n")
            with self.assertRaises(ValueError): lab.usage_register(path)

    def test_17_invariant_report(self):
        self.assertEqual(lab.format_report()["status"], "OFFLINE simulation only; NOT a Snowflake access audit")


if __name__ == "__main__": unittest.main()
