from decimal import Decimal
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from wholefarm.climate import Direction, GHGFlux, GWPSet, Gas, aggregate_fluxes


class ClimateTests(unittest.TestCase):
    def setUp(self):
        # Deliberately illustrative factors: production configurations must cite
        # the selected assessment and provide its factors explicitly.
        self.gwp = GWPSet("test assessment", 100, {Gas.CO2: 1, Gas.CH4: 10, Gas.N2O: 100})

    def test_aggregation_keeps_gross_removals_and_net_separate(self):
        fluxes = (
            GHGFlux("enteric", "enteric", Gas.CH4, Decimal("2"), Direction.EMISSION, "2026", "calc:1"),
            GHGFlux("fertilizer", "soil", Gas.N2O, Decimal("0.5"), Direction.EMISSION, "2026", "calc:2"),
            GHGFlux("trees", "woody biomass", Gas.CO2, Decimal("15"), Direction.REMOVAL, "2026", "calc:3"),
        )
        result = aggregate_fluxes(fluxes, self.gwp, "2026")
        self.assertEqual(Decimal("70.0"), result.gross_emissions_kg_co2e)
        self.assertEqual(Decimal("15"), result.removals_kg_co2e)
        self.assertEqual(Decimal("55.0"), result.net_kg_co2e)
        self.assertEqual(Decimal("-15"), result.by_source_kg_co2e["woody biomass"])

    def test_gwp_set_must_be_complete(self):
        with self.assertRaisesRegex(ValueError, "exactly CO2, CH4, and N2O"):
            GWPSet("incomplete", 100, {Gas.CO2: 1, Gas.CH4: 10})

    def test_duplicate_flux_ids_are_rejected(self):
        flux = GHGFlux("same", "soil", Gas.N2O, 1, Direction.EMISSION, "2026", "calc")
        with self.assertRaisesRegex(ValueError, "duplicate flux_id"):
            aggregate_fluxes((flux, flux), self.gwp, "2026")
