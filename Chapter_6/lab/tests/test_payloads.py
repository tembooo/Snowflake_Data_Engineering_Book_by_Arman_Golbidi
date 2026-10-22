"""No Snowflake account required: python -m unittest discover -s tests -v"""
import json
from decimal import Decimal
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_payloads import FIXTURE, inspect_lines, validate_envelope


class ChapterSixLabTests(unittest.TestCase):
    def test_fixture_counts(self):
        r = inspect_lines(FIXTURE.read_text().splitlines())
        self.assertEqual((r["physical_lines"], r["accepted_envelopes"], r["syntax_rejected"], r["contract_rejected"]), (4, 2, 1, 1))
        self.assertEqual(r["accepted_readings"], 6)

    def test_reconciled_total(self):
        r = inspect_lines(FIXTURE.read_text().splitlines())
        self.assertEqual(r["accepted_total_mwh"], "97.500")

    def test_v2_renamed_array(self):
        line = FIXTURE.read_text().splitlines()[1]
        doc = json.loads(line, parse_float=Decimal)
        self.assertEqual({r["technology"] for r in validate_envelope(doc, 2)}, {"wind", "solar", "hydro"})

    def test_json_null_rejected_not_zero(self):
        lines = FIXTURE.read_text().splitlines()
        r = inspect_lines([lines[2]])
        self.assertEqual(r["contract_rejected"], 1)
        self.assertEqual(r["accepted_readings"], 0)

    def test_duplicate_technology_fails_contract(self):
        doc = json.loads(FIXTURE.read_text().splitlines()[0], parse_float=Decimal)
        doc["observations"][1]["tech"] = "wind"
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_envelope(doc, 1)

    def test_duplicate_business_key_across_envelopes(self):
        lines = FIXTURE.read_text().splitlines()
        r = inspect_lines([lines[0], lines[0]])
        self.assertEqual(r["accepted_envelopes"], 1)
        self.assertEqual(r["contract_rejected"], 1)


if __name__ == "__main__":
    unittest.main()
