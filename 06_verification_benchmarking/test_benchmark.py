"""Tests for benchmark reporting, log decoding, and solver configuration."""
import tempfile
import unittest
from pathlib import Path
from benchmark import parse_log, decode_process_output, make_limited_model, write_reports


class BenchmarkTests(unittest.TestCase):
    def test_summary(self):
        self.assertEqual(parse_log('SUMMARY,1363,151\nOBJECTIVE: 478564\n', 350),
                         {'weighted_tardiness':1363,'makespan':151,'objective':478564})

    def test_bad_objective(self):
        with self.assertRaises(ValueError):
            parse_log('SUMMARY,1363,151\nOBJECTIVE: 3\n', 350)

    def test_duplicate_summary(self):
        with self.assertRaises(ValueError):
            parse_log('SUMMARY,1,2\nSUMMARY,1,2\n', 350)

    def test_powershell_utf16(self):
        self.assertEqual(decode_process_output('SUMMARY,1,2\n'.encode('utf-16')), 'SUMMARY,1,2\n')

    def test_model_limit_replacement(self):
        with tempfile.TemporaryDirectory() as folder:
            src = Path(folder) / 'model.mod'
            dst = Path(folder) / 'copy.mod'
            src.write_text('execute { cp.param.TimeLimit = 30; cp.param.Workers = 4; }')
            make_limited_model(src, dst, 5, 2)
            self.assertIn('TimeLimit = 5;', dst.read_text())
            self.assertIn('Workers = 2;', dst.read_text())
            self.assertIn('TimeLimit = 30;', src.read_text())

    def test_report_generation(self):
        with tempfile.TemporaryDirectory() as folder:
            sample = dict(method='monolithic', budget_seconds=5, trial=1,
                          actual_wall_seconds=5.3, weighted_tardiness=1363,
                          makespan=151, objective=478564, verified=True,
                          status='PASS', log='mono.log')
            write_reports([sample], Path(folder), 350)
            self.assertTrue((Path(folder) / 'results.csv').exists())
            self.assertIn('478564', (Path(folder) / 'results.md').read_text())


if __name__ == '__main__':
    unittest.main()
