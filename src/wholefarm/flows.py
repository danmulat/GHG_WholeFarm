"""Mass-balanced carbon and nitrogen flows between farm compartments.

The ledger stores physical quantities only. It deliberately does not calculate
emission factors: calculation engines create flows, while this module verifies
that the resulting farm system conserves carbon and nitrogen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from typing import Iterable


EXTERNAL = "external"


class Element(StrEnum):
    CARBON = "carbon"
    NITROGEN = "nitrogen"


def _decimal(value: Decimal | int | float | str) -> Decimal:
    """Convert user values without introducing binary floating-point noise."""
    return value if isinstance(value, Decimal) else Decimal(str(value))


@dataclass(frozen=True)
class ElementQuantity:
    """An elemental mass in the ledger's canonical unit, kg per period."""

    element: Element
    kg: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "kg", _decimal(self.kg))
        if self.kg < 0:
            raise ValueError("element quantity cannot be negative")


@dataclass(frozen=True)
class Flow:
    """A uniquely identified transfer from one compartment to another."""

    flow_id: str
    source: str
    destination: str
    quantities: tuple[ElementQuantity, ...]
    period: str
    process: str
    evidence_id: str | None = None

    def __post_init__(self) -> None:
        if not self.flow_id.strip():
            raise ValueError("flow_id is required")
        if not self.source.strip() or not self.destination.strip():
            raise ValueError("source and destination are required")
        if self.source == self.destination:
            raise ValueError("a flow cannot have the same source and destination")
        if not self.period.strip() or not self.process.strip():
            raise ValueError("period and process are required")
        if not self.quantities:
            raise ValueError("at least one element quantity is required")
        elements = [quantity.element for quantity in self.quantities]
        if len(elements) != len(set(elements)):
            raise ValueError("an element may occur only once in a flow")

    def quantity(self, element: Element) -> Decimal:
        return next((item.kg for item in self.quantities if item.element == element), Decimal(0))


@dataclass(frozen=True)
class StockChange:
    """Closing minus opening elemental stock for a compartment and period."""

    compartment: str
    period: str
    element: Element
    kg: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "kg", _decimal(self.kg))
        if not self.compartment.strip() or self.compartment == EXTERNAL:
            raise ValueError("stock change requires an internal compartment")


@dataclass(frozen=True)
class Balance:
    compartment: str
    period: str
    element: Element
    inflow_kg: Decimal
    outflow_kg: Decimal
    stock_change_kg: Decimal
    residual_kg: Decimal

    def is_balanced(self, tolerance_kg: Decimal | int | float | str = "0.000001") -> bool:
        return abs(self.residual_kg) <= _decimal(tolerance_kg)


@dataclass
class FlowLedger:
    """Collection of transfers with compartment-level conservation checks."""

    _flows: dict[str, Flow] = field(default_factory=dict, init=False, repr=False)
    _stock_changes: dict[tuple[str, str, Element], StockChange] = field(
        default_factory=dict, init=False, repr=False
    )

    @property
    def flows(self) -> tuple[Flow, ...]:
        return tuple(self._flows.values())

    def add_flow(self, flow: Flow) -> None:
        if flow.flow_id in self._flows:
            raise ValueError(f"duplicate flow_id: {flow.flow_id}")
        self._flows[flow.flow_id] = flow

    def add_stock_change(self, change: StockChange) -> None:
        key = (change.compartment, change.period, change.element)
        if key in self._stock_changes:
            raise ValueError(
                "duplicate stock change for "
                f"{change.compartment}/{change.period}/{change.element.value}"
            )
        self._stock_changes[key] = change

    def balances(self, period: str) -> tuple[Balance, ...]:
        flows = [flow for flow in self._flows.values() if flow.period == period]
        compartments = {
            endpoint
            for flow in flows
            for endpoint in (flow.source, flow.destination)
            if endpoint != EXTERNAL
        }
        compartments.update(
            change.compartment
            for change in self._stock_changes.values()
            if change.period == period
        )
        results: list[Balance] = []
        for compartment in sorted(compartments):
            for element in Element:
                inflow = sum(
                    (flow.quantity(element) for flow in flows if flow.destination == compartment),
                    Decimal(0),
                )
                outflow = sum(
                    (flow.quantity(element) for flow in flows if flow.source == compartment),
                    Decimal(0),
                )
                stock_change = self._stock_changes.get((compartment, period, element))
                stock_kg = stock_change.kg if stock_change else Decimal(0)
                results.append(
                    Balance(
                        compartment, period, element, inflow, outflow, stock_kg,
                        inflow - outflow - stock_kg,
                    )
                )
        return tuple(results)

    def assert_balanced(
        self,
        period: str,
        tolerance_kg: Decimal | int | float | str = "0.000001",
        *,
        exclude: Iterable[str] = (),
    ) -> None:
        """Raise with all failing balances; useful as a reporting gate."""
        exclusions = set(exclude)
        failures = [
            balance for balance in self.balances(period)
            if balance.compartment not in exclusions and not balance.is_balanced(tolerance_kg)
        ]
        if failures:
            details = "; ".join(
                f"{item.compartment}/{item.element.value}: {item.residual_kg} kg"
                for item in failures
            )
            raise ValueError(f"unbalanced ledger for {period}: {details}")

