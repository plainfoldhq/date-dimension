import os, sys, unittest
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import retailcal as rc

class T(unittest.TestCase):
    def test_nrf(self):
        c = rc.Calendar(*rc.PRESETS["nrf-454"])
        self.assertEqual(c.bounds(2024), (date(2024, 2, 4), date(2025, 2, 1)))
        self.assertEqual([y for y in range(2000, 2030) if c.period_lengths(y)[1] == 53],
                         [2000, 2006, 2012, 2017, 2023, 2028])
    def test_last_sat_sep(self):
        c = rc.Calendar(*rc.PRESETS["445-sat-last-sep"])
        self.assertEqual(c.bounds(2023)[1], date(2023, 9, 30))
        self.assertEqual(c.bounds(2025)[1], date(2025, 9, 27))

if __name__ == "__main__":
    unittest.main()
