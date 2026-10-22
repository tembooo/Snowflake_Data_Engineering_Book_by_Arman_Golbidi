"""Standard-library tests; synthetic correctness and honest measurement labels."""
import csv, tempfile, unittest
from decimal import Decimal
import offline_validate as v
class TestChapter12Lab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=v.validate_expanded()
    def test_01_seed_count(self):self.assertEqual(len(v.validate_seed()),6)
    def test_02_seed_values(self):self.assertEqual({r['technology']:Decimal(r['energy_mwh']) for r in v.validate_seed()},v.EXPECTED)
    def test_03_seed_sum(self):self.assertEqual(sum(v.EXPECTED.values()),Decimal('66'))
    def test_04_fixture_count(self):self.assertEqual(len(self.data),42)
    def test_05_seven_days(self):self.assertEqual(len({r['interval_utc'] for r in self.data}),7)
    def test_06_unique_grain(self):self.assertEqual(len({(r['interval_utc'],r['technology']) for r in self.data}),42)
    def test_07_fixture_total(self):self.assertEqual(sum(Decimal(r['energy_mwh']) for r in self.data),Decimal('462'))
    def test_08_daily_sum(self):self.assertEqual(sum(v.by_range(self.data,'2026-10-04').values()),Decimal('66'))
    def test_09_filter_equivalence(self):
        for i in range(1,8):
            day=f'2026-10-{i:02d}'
            self.assertEqual(v.by_date_expression(self.data,day),v.by_range(self.data,day))
    def test_10_end_exclusive(self):self.assertFalse(v.by_range(self.data,'2026-10-08'))
    def test_11_no_negative(self):self.assertTrue(all(Decimal(r['energy_mwh'])>=0 for r in self.data))
    def test_12_manifest(self):self.assertTrue(v.verify_manifest())
    def test_13_no_query_ids(self):self.assertTrue(all(not x['query_id'] for x in v.rows('benchmark_results.csv')))
    def test_14_no_fabricated_credits(self):self.assertTrue(all(not x['warehouse_credits'] for x in v.rows('benchmark_results.csv')))
    def test_15_illustrative_labels(self):self.assertEqual({r['status'] for r in v.rows('benchmark_results.csv')},{'synthetic_illustration'})
    def test_16_percentile_rule(self):self.assertAlmostEqual(v.percentile([1,2,3,4,5],95),4.8)
if __name__=='__main__':unittest.main()
