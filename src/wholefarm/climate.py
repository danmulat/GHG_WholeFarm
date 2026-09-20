"""Transparent conversion and aggregation of greenhouse-gas quantities."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Mapping

from .flows import _decimal


class Gas(StrEnum):
    CO2 = "CO2"
    CH4 = "CH4"
    N2O = "N2O"


class Direction(StrEnum):
    EMISSION = "emission"
    REMOVAL = "removal"


@dataclass(frozen=True)
class GWPSet:
    """Explicit GWP values; the caller must supply the assessment identity."""

    assessment: str
    horizon_years: int
    factors: Mapping[Gas, Decimal | int | float | str]

    def __post_init__(self) -> None:
        if not self.assessment.strip() or self.horizon_years <= 0:
            raise ValueError("assessment and positive time horizon are required")
        normalized = {gas: _decimal(value) for gas, value in self.factors.items()}
        if set(normalized) != set(Gas):
            raise ValueError("GWP factors must contain exactly CO2, CH4, and N2O")
        if any(value <= 0 for value in normalized.values()):
            raise ValueError("GWP factors must be positive")
        if normalized[Gas.CO2] != 1:
            raise ValueError("CO2 GWP must equal one")
        object.__setattr__(self, "factors", normalized)


@dataclass(frozen=True)
class GHGFlux:
    flux_id: str
    source_category: str
    gas: Gas
    kg_gas: Decimal
    direction: Direction
    period: str
    evidence_id: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "kg_gas", _decimal(self.kg_gas))
        for name in ("flux_id", "source_category", "period", "evidence_id"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} is required")
        if self.kg_gas < 0:
            raise ValueError("kg_gas must be non-negative; use direction for sign")

    def kg_co2e(self, gwp: GWPSet) -> Decimal:
        sign = Decimal(1) if self.direction == Direction.EMISSION else Decimal(-1)
        return sign * self.kg_gas * gwp.factors[self.gas]


@dataclass(frozen=True)
class ClimateResult:
    gross_emissions_kg_co2e: Decimal
    removals_kg_co2e: Decimal
    net_kg_co2e: Decimal
    by_source_kg_co2e: Mapping[str, Decimal]
    gwp_assessment: str
    gwp_horizon_years: int


def aggregate_fluxes(fluxes: tuple[GHGFlux, ...], gwp: GWPSet, period: str) -> ClimateResult:
    selected = [flux for flux in fluxes if flux.period == period]
    ids = [flux.flux_id for flux in selected]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate flux_id in reporting period")
    gross = sum(
        (flux.kg_co2e(gwp) for flux in selected if flux.direction == Direction.EMISSION),
        Decimal(0),
    )
    removals = -sum(
        (flux.kg_co2e(gwp) for flux in selected if flux.direction == Direction.REMOVAL),
        Decimal(0),
    )
    by_source: dict[str, Decimal] = {}
    for flux in selected:
        by_source[flux.source_category] = by_source.get(flux.source_category, Decimal(0)) + flux.kg_co2e(gwp)
    return ClimateResult(gross, removals, gross - removals, by_source, gwp.assessment, gwp.horizon_years)

