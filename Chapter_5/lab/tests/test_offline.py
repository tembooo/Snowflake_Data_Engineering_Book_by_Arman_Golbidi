import csv
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from validate_fixture import (evaluate, generate_manifest, verify_expected,
                              sha256_file)  # noqa: E402


class OfflineContractTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.tmp = Path(self.work.name)
        self.files = self.tmp / 'data'
        self.files.mkdir()
        for file in (ROOT / 'data').glob('*.csv'):
            (self.files / file.name).write_bytes(file.read_bytes())
        self.manifest = self.tmp / 'source_manifest.csv'
        generate_manifest(self.files, self.manifest)

    def tearDown(self):
        self.work.cleanup()

    def test_baseline(self):
        result = evaluate(self.files, self.manifest)
        verify_expected(result)
        self.assertEqual(result['numeric_valid_rows'], 7)
        self.assertEqual(result['accepted_total_mwh'], '97.500')

    def test_checksum_guard(self):
        f = self.files / 'energy_r1.csv'
        f.write_bytes(f.read_bytes().replace(b'10.000', b'10.001'))
        with self.assertRaisesRegex(ValueError, 'Checksum mismatch'):
            evaluate(self.files, self.manifest)

    def test_schema_drift_block(self):
        f = self.files / 'energy_r1.csv'
        f.write_bytes(f.read_bytes().replace(b'source_code,', b'unit_code,', 1))
        # Rebuild the manifest to isolate structural failure from checksum failure.
        with self.assertRaisesRegex(ValueError, 'Header mismatch'):
            generate_manifest(self.files, self.manifest)

    def test_revised_energy(self):
        f = self.files / 'energy_r2.csv'
        f.write_bytes(f.read_bytes().replace(b'13.000', b'15.000'))
        generate_manifest(self.files, self.manifest)
        result = evaluate(self.files, self.manifest)
        self.assertEqual(result['accepted_total_mwh'], '99.500')

    def test_manifest_row_count_detection(self):
        with self.manifest.open(newline='') as handle:
            rows = list(csv.DictReader(handle))
        rows[0]['expected_rows'] = '999'
        with self.manifest.open('w', newline='') as handle:
            w = csv.DictWriter(handle, fieldnames=rows[0].keys())
            w.writeheader(); w.writerows(rows)
        with self.assertRaisesRegex(ValueError, 'Row count mismatch'):
            evaluate(self.files, self.manifest)


if __name__ == '__main__':
    unittest.main()
