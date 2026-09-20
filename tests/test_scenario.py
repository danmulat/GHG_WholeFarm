from decimal import Decimal
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from wholefarm.scenario import AdoptionSchedule, interpolate


class ScenarioTests(unittest.TestCase):
    def test_linear_adoption_schedule(self):
        schedule = AdoptionSchedule(2026, 2030, "0.8")
        self.assertEqual(Decimal(0), schedule.fraction(2025))
        self.assertEqual(Decimal("0.4"), schedule.fraction(2028))
        self.assertEqual(Decimal("0.8"), schedule.fraction(2030))
        self.assertEqual(Decimal("0.8"), schedule.fraction(2035))

    def test_instant_adoption_has_no_division_by_zero(self):
        schedule = AdoptionSchedule(2026, 2026, "0.75")
        self.assertEqual(Decimal(0), schedule.fraction(2025))
        self.assertEqual(Decimal("0.75"), schedule.fraction(2026))

    def test_interpolation_changes_activity_not_reported_reduction(self):
        self.assertEqual(Decimal("15.0"), interpolate(10, 20, "0.5"))

    def test_invalid_adoption_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "between zero and one"):
            AdoptionSchedule(2026, 2030, "1.1")
