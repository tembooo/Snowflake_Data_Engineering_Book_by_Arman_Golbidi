"""Offline standard-library contract tests; NOT a live Snowflake integration test."""
import csv
import unittest
from decimal import Decimal
from pathlib import Path
from snowpark_pipeline import transform, validate
ROOT = Path(__file__).resolve().parent

def fixture():
    with (ROOT/'data'/'energy_revisions.csv').open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

class EnergyPipelineContractTests(unittest.TestCase):
    def test_input_count(self):
        self.assertEqual(len(fixture()), 12)
    def test_visible_rows(self):
        self.assertEqual(len(transform(fixture())[0]), 6)
    def test_total_is_correct(self):
        rows = transform(fixture())[0]
        self.assertEqual(sum((r['ENERGY_MWH'] for r in rows),Decimal(0)), Decimal('66.000'))
    def test_latest_revision_wins(self):
        rows = transform(fixture())[0]
        self.assertEqual(next(r for r in rows if r['TECHNOLOGY']=='Wind')['ENERGY_MWH'],Decimal('14'))
    def test_tombstone(self):
        self.assertNotIn('TEST',[r['TECHNOLOGY'] for r in transform(fixture())[0]])
    def test_duplicate_delivery(self):
        self.assertEqual(transform(fixture())[2]['replays'], 1)
    def test_invalid_rejected(self):
        self.assertEqual(transform(fixture())[2]['rejected'], 2)
    def test_replay_does_not_change_result(self):
        a = transform(fixture())[0]
        b = transform(fixture()+fixture())[0]
        self.assertEqual(a,b)
    def test_missing_field_rejected(self):
        with self.assertRaisesRegex(ValueError,'missing'):
            validate({'EVENT_ID':'x'})
    def test_conflicting_revision_rejected(self):
        rows = fixture()
        conflict = dict(rows[6]);conflict['EVENT_ID']='new-conflict';conflict['ENERGY_MWH']='29.0'
        result = transform(rows+[conflict])
        self.assertEqual(result[2]['conflicts'],1)
    def test_negative_rejected(self):
        with self.assertRaisesRegex(ValueError,'invalid nonnegative'):
            validate(dict(fixture()[0],ENERGY_MWH='-1'))
    def test_utc_required(self):
        with self.assertRaisesRegex(ValueError,'UTC'):
            validate(dict(fixture()[0],INTERVAL_UTC='2026-03-01T12:00:00'))

if __name__ == '__main__':
    unittest.main()
