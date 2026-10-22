"""Run with 'python -m unittest discover -s tests -v' from the lab directory."""
import unittest
from copy import deepcopy
from decimal import Decimal
from validate_fixture import read_rows, choose_accepted, validate


class AcceptedEnergyTests(unittest.TestCase):
    def setUp(self):
        self.rows = read_rows()

    def test_golden_fixture(self):
        self.assertEqual(validate(self.rows)["accepted_mwh"], "97.500")

    def test_later_correction_supersedes_prior_value(self):
        actual = choose_accepted(self.rows)
        key = ("SOLAR_FI", "generation_mwh", "2026-01-15 01:00:00")
        self.assertEqual(actual[key]["energy_mwh"], Decimal("13.000"))

    def test_reject_negative(self):
        faulty = deepcopy(self.rows)
        faulty[1]["mwh_text"] = "-9.000"
        with self.assertRaises(AssertionError):
            choose_accepted(faulty)

    def test_reject_invalid_decimal(self):
        faulty = deepcopy(self.rows)
        faulty[0]["mwh_text"] = "not_a_number"
        with self.assertRaises(AssertionError):
            choose_accepted(faulty)

    def test_reject_wrong_expected_cardinality(self):
        with self.assertRaises(AssertionError):
            validate(self.rows[:5])


if __name__ == "__main__":
    unittest.main()
