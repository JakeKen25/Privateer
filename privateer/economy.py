"""Read-only budget projection from verified RTW3 economy fields."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


def _whole(value) -> int:
    return int(Decimal(value).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def _field_integer(fields, *names, default=0):
    lookup = {key.casefold(): value for key, value in fields.items()}
    for name in names:
        try:
            return int(str(lookup[name.casefold()]).replace(",", ""))
        except (KeyError, ValueError):
            pass
    return default


@dataclass(frozen=True)
class BudgetProjection:
    yearly_budget: int
    monthly_budget: int
    maintenance: int
    construction: int
    naval_aircraft: int
    research: int
    extra_training: int
    intelligence: int
    total_expenses: int
    monthly_balance: int
    funds: int
    research_percent: int


def project_budget(nation, *, base_resources=None, funds=None) -> BudgetProjection:
    """Approximate the in-game budget panel without changing the save.

    The 2.4 annual factor and research calculation reproduce the supplied Game1
    screenshot exactly. Ship maintenance and construction use stored hull fields;
    RTW3 can add costs that are not represented by a verified save field.
    """
    resources = nation.base_resources if base_resources is None else base_resources
    available_funds = nation.funds if funds is None else funds
    resources = 0 if resources is None else resources
    available_funds = 0 if available_funds is None else available_funds
    fields = nation.section.fields()
    monthly = _whole(Decimal(resources) / Decimal(5))
    yearly = monthly * 12
    research_percent = _field_integer(fields, "ResearchPct")
    research = _whole(Decimal(monthly) * Decimal(research_percent) / Decimal(100))
    maintenance = 0
    construction = 0
    for ship in nation.ships:
        ship_fields = ship.section.fields()
        if ship.under_construction:
            construction += _field_integer(ship_fields, "MonthlyCost")
        else:
            maintenance += _field_integer(ship_fields, "Maintenance")
    naval_aircraft = _field_integer(fields, "NavalAircraftSpending", "AircraftSpending")
    extra_training = _field_integer(fields, "ExtraTrainingSpending", "TrainingSpending")
    intelligence = _field_integer(fields, "IntelligenceSpending")
    total = maintenance + construction + naval_aircraft + research + extra_training + intelligence
    return BudgetProjection(
        yearly, monthly, maintenance, construction, naval_aircraft, research,
        extra_training, intelligence, total, monthly - total, available_funds,
        research_percent,
    )
