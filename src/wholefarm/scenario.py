"""Baseline/intervention adoption schedules without embedded reduction claims."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .flows import _decimal


@dataclass(frozen=True)
class AdoptionSchedule:
    """Linearly phase a practice from zero to its target adoption."""

    start_year: int
    full_adoption_year: int
    target_fraction: Decimal | int | float | str = Decimal(1)

    def __post_init__(self) -> None:
        object.__setattr__(self, "target_fraction", _decimal(self.target_fraction))
        if self.full_adoption_year < self.start_year:
            raise ValueError("full_adoption_year cannot precede start_year")
        if not Decimal(0) <= self.target_fraction <= Decimal(1):
            raise ValueError("target_fraction must be between zero and one")

    def fraction(self, year: int) -> Decimal:
        if year < self.start_year:
            return Decimal(0)
        if year >= self.full_adoption_year:
            return self.target_fraction
        duration = Decimal(self.full_adoption_year - self.start_year)
        return self.target_fraction * Decimal(year - self.start_year) / duration


def interpolate(baseline: Decimal | int | float | str, intervention: Decimal | int | float | str, adoption: Decimal | int | float | str) -> Decimal:
    """Interpolate an activity value; this does not interpolate final emissions."""
    base = _decimal(baseline)
    target = _decimal(intervention)
    fraction = _decimal(adoption)
    if not Decimal(0) <= fraction <= Decimal(1):
        raise ValueError("adoption must be between zero and one")
    return base + fraction * (target - base)

