import unittest
import sys
from pathlib import Path
from decimal import Decimal
sys.path.insert(0,str(Path(__file__).parents[1]))
from metrics import read_csv,calculate,ROOT

class TestMetrics(unittest.TestCase):
    def setUp(self):
        self.g=read_csv(ROOT/'data/gold_generation.csv')
        self.c=read_csv(ROOT/'data/consumption.csv')
    def test_total(self): self.assertEqual(calculate(self.g,self.c)['generation_mwh'],Decimal('66.000'))
    def test_consumption(self):self.assertEqual(calculate(self.g,self.c)['consumption_mwh'],Decimal('60.000'))
    def test_net(self):self.assertEqual(calculate(self.g,self.c)['net_mwh'],Decimal('6.000'))
    def test_wind_share(self):self.assertAlmostEqual(calculate(self.g,self.c)['wind_share_pct'],Decimal('21.212121'),places=5)
    def test_six_technologies(self):self.assertEqual(calculate(self.g,self.c)['generation_coverage'],'6/6')
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):calculate(self.g+[dict(self.g[0])],self.c)
    def test_negative_rejected(self):
        g=[dict(x) for x in self.g];g[0]['energy_mwh']='-1'
        with self.assertRaises(ValueError):calculate(g,self.c)
    def test_missing_technology_rejected(self):
        with self.assertRaises(ValueError):calculate(self.g[:-1],self.c)
    def test_unknown_technology_rejected(self):
        g=[dict(x) for x in self.g];g[0]['technology']='Geothermal'
        with self.assertRaises(ValueError):calculate(g,self.c)
    def test_timezone_rejected(self):
        g=[dict(x) for x in self.g];g[0]['interval_utc']='2026-03-01T10:00:00+02:00'
        with self.assertRaises(ValueError):calculate(g,self.c)
    def test_duplicate_consumption_rejected(self):
        with self.assertRaises(ValueError):calculate(self.g,self.c+self.c)
    def test_unavailable_consumption_not_zero(self):
        result=calculate(self.g,[])
        self.assertIsNone(result['consumption_mwh']);self.assertIsNone(result['net_mwh'])
    def test_nonnumeric_rejected(self):
        g=[dict(x) for x in self.g];g[0]['energy_mwh']='NaN'
        with self.assertRaises(ValueError):calculate(g,self.c)
    def test_snapshot_grain(self):
        g=[dict(x) for x in self.g];g[0]['interval_utc']='2026-03-01T10:15:00Z'
        with self.assertRaises(ValueError):calculate(g,self.c)
    def test_output_row_count(self):self.assertEqual(calculate(self.g,self.c)['row_count'],6)
if __name__=='__main__':unittest.main()
