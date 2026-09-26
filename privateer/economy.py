"""Read-only, explicitly incomplete RTW3 budget estimates."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
import re

from .ship_status import appears_in_transfer_window

BUDGET_DISCLAIMER = (
    "Under development: calculator estimates may differ from the amounts shown in-game. "
    "Uncalculated costs are not zero and are excluded from the subtotal."
)


def _whole(value):
    return int(Decimal(value).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def _field_integer(fields, *names, default=0):
    lookup = {key.casefold(): value for key, value in fields.items()}
    for name in names:
        try:
            return int(str(lookup[name.casefold()]).replace(",", ""))
        except (KeyError, ValueError):
            pass
    return default


def _records(fields, prefix):
    records = {}
    for key, value in fields.items():
        match = re.fullmatch(prefix + r"(\d+)(\D.*)", key, re.I)
        if match:
            records.setdefault(match[1], {})[match[2]] = value
    return tuple(records.values())


@dataclass(frozen=True)
class BudgetContext:
    fleet_size: int | None = None
    intelligence: int | None = None
    construction_notes: tuple[str, ...] = ()
    maintenance_notes: tuple[str, ...] = ()
    additional_construction: int = 0


def budget_context(save, nation):
    """Read campaign-level inputs once when opening the modal editor."""
    sections = {s.name.casefold(): s for s in save.documents[save.main_file].sections}
    general = sections.get("general")
    fleet = _field_integer(general.fields(), "FleetSize", default=None) if general else None
    intelligence = None
    # The target-nation spending fields describe the player's intelligence only.
    if nation.index == 0:
        levels = [_field_integer(n.section.fields(), "IntelligenceSpending", default=None)
                  for n in save.nations if n.index != 0]
        if all(level in (0, 1, 2, 3) for level in levels):
            intelligence = sum(levels) * 80
    construction, maintenance = [], []
    additional_construction = 0
    if _field_integer(nation.section.fields(), "DockBuilding") > 0:
        construction.append("dock expansion")
    for suffix, prefix, label in (("Submarines", "Sub", "submarines"),
                                   ("CoastalArtillery", "Ship", "fortifications")):
        section = sections.get(f"nation{nation.index}{suffix}".casefold())
        if section is None:
            maintenance.append(label + " (roster unavailable)")
            construction.append(label + " (roster unavailable)")
            continue
        for fields in _records(section.fields(), prefix):
            if not appears_in_transfer_window(fields) or _field_integer(fields, "Sunk"):
                continue
            if _field_integer(fields, "InPlay", default=1):
                maintenance.append(label)
            else:
                # Submarine records often have no MonthlyCost. Do not substitute
                # the single observed Game3 cost for all eras and submarine types.
                cost = _field_integer(fields, "MonthlyCost", default=None)
                if cost is None or (prefix == "Sub" and _field_integer(fields, "Halted")):
                    construction.append(label)
                elif prefix == "Ship" and (_field_integer(fields, "Halted") or
                                            _field_integer(fields, "Hurry")):
                    construction.append(label + " (halted/accelerated)")
                else:
                    additional_construction += cost
    return BudgetContext(fleet, intelligence, tuple(dict.fromkeys(construction)),
                         tuple(dict.fromkeys(maintenance)), additional_construction)


@dataclass(frozen=True)
class BudgetProjection:
    yearly_budget: int | None
    monthly_budget: int | None
    maintenance: int
    construction: int
    naval_aircraft: int | None
    research: int | None
    extra_training: int | None
    intelligence: int | None
    total_expenses: int
    monthly_balance: int | None
    funds: int
    research_percent: int
    notes: tuple[str, ...] = ()
    incomplete: bool = True


def project_budget(nation, *, context=None, base_resources=None, funds=None):
    """Estimate supported components; never turn missing expense fields into zero.

    Income uses an explicitly provisional domestic-income estimate. Possession
    effects are unresolved. Construction/status rules are based on the nine-save
    comparison, not a claim of exact agreement with the game engine.
    """
    context = context or BudgetContext()
    resources = nation.base_resources if base_resources is None else base_resources
    available_funds = nation.funds if funds is None else funds
    fields = nation.section.fields()
    modifier = _field_integer(fields, "BudgetModifier", default=None)
    notes = ["Income excludes unverified possession and other game adjustments."]
    if resources is None or modifier is None or context.fleet_size is None:
        yearly = monthly = None
    else:
        yearly = _whole(Decimal(resources) * modifier * context.fleet_size / 10)
        monthly = _whole(Decimal(yearly) / 12)
    research_percent = _field_integer(fields, "ResearchPct")
    research = (None if monthly is None else
                _whole(Decimal(monthly) * research_percent / 100))
    maintenance = 0
    construction = context.additional_construction
    for ship in nation.ships:
        f = ship.section.fields()
        if not appears_in_transfer_window(f):
            continue
        charge = _field_integer(f, "Maintenance")
        if ship.under_construction:
            if _field_integer(f, "Halted"):
                construction += charge // 2
            else:
                cost = _field_integer(f, "MonthlyCost")
                construction += (_whole(Decimal(cost) * Decimal("1.15"))
                                 if _field_integer(f, "Hurry") else cost)
        else:
            status = str(f.get("Status", "0")).strip()
            # Controlled Game3 observations: class-2 search radar adds 2 on
            # destroyers and 4 on cruisers/carriers, before status reductions.
            if _field_integer(f, "SearchRadarClass") == 2:
                charge += {"DD": 2, "CL": 4, "CV": 4}.get(str(f.get("ShipType", "")).strip(), 0)
            divisor = 2 if status == "1" else 5 if status == "2" else 1
            maintenance += int((Decimal(charge) / divisor).quantize(
                Decimal(1), rounding=ROUND_HALF_EVEN))
    naval_aircraft = _field_integer(fields, "NavalAircraftSpending", "AircraftSpending", default=None)
    extra_training = _field_integer(fields, "ExtraTrainingSpending", "TrainingSpending", default=None)
    intelligence = context.intelligence
    for value, label in ((naval_aircraft, "aircraft"), (extra_training, "training"),
                         (intelligence, "intelligence")):
        if value is None:
            notes.append(f"{label.capitalize()} costs are not yet calculated.")
    if context.construction_notes:
        notes.append("Construction excludes " + ", ".join(context.construction_notes) + ".")
    if context.maintenance_notes:
        notes.append("Maintenance excludes " + ", ".join(context.maintenance_notes) + ".")
    notes.append("Ship maintenance includes observed class-2 search radar charges for DD/CL/CV; other equipment, repair and officer modifiers remain unverified.")
    total = maintenance + construction + sum(v for v in
        (naval_aircraft, research, extra_training, intelligence) if v is not None)
    # A balance from incomplete expenses would look like money available to spend.
    return BudgetProjection(yearly, monthly, maintenance, construction, naval_aircraft,
        research, extra_training, intelligence, total, None, available_funds or 0,
        research_percent, tuple(notes))
