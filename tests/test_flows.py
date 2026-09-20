from decimal import Decimal
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from wholefarm.flows import Element, ElementQuantity, Flow, FlowLedger, StockChange


def carbon(kg: str) -> tuple[ElementQuantity, ...]:
    return (ElementQuantity(Element.CARBON, Decimal(kg)),)


class FlowLedgerTests(unittest.TestCase):
    def test_closed_manure_pathway_balances_each_compartment(self):
        ledger = FlowLedger()
        ledger.add_flow(Flow("excretion", "external", "housing", carbon("100"), "2026", "excretion"))
        ledger.add_flow(Flow("storage", "housing", "store", carbon("90"), "2026", "collection"))
        ledger.add_flow(Flow("housing_loss", "housing", "external", carbon("10"), "2026", "loss"))
        ledger.add_flow(Flow("application", "store", "soil", carbon("70"), "2026", "application"))
        ledger.add_flow(Flow("store_loss", "store", "external", carbon("20"), "2026", "loss"))
        ledger.add_stock_change(StockChange("soil", "2026", Element.CARBON, Decimal("70")))

        ledger.assert_balanced("2026")
        housing = next(
            balance for balance in ledger.balances("2026")
            if balance.compartment == "housing" and balance.element == Element.CARBON
        )
        self.assertEqual(Decimal("100"), housing.inflow_kg)
        self.assertEqual(Decimal("0"), housing.residual_kg)

    def test_unbalanced_pathway_reports_compartment_and_element(self):
        ledger = FlowLedger()
        ledger.add_flow(Flow("excretion", "external", "housing", carbon("100"), "2026", "excretion"))
        with self.assertRaisesRegex(ValueError, r"housing/carbon: 100 kg"):
            ledger.assert_balanced("2026")

    def test_duplicate_flow_is_rejected(self):
        ledger = FlowLedger()
        flow = Flow("same", "external", "soil", carbon("1"), "2026", "input")
        ledger.add_flow(flow)
        with self.assertRaisesRegex(ValueError, "duplicate flow_id"):
            ledger.add_flow(flow)

    def test_negative_quantity_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            ElementQuantity(Element.NITROGEN, Decimal("-1"))
