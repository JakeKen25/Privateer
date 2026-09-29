"""Read-only RTW3 budget estimates with explicit, adjustable empirical fallbacks."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
import re

from .ship_status import appears_in_transfer_window

BUDGET_DISCLAIMER = (
    "Estimated budget: every amount is numeric, but unresolved formulas use the "
    "assumptions below. Total expenses and balance are estimates, not verified game costs."
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
class BudgetAssumptions:
    # Reference averages, NOT decoded RTW3 formulas. See BUDGET_ESTIMATES.md.
    aircraft_rate: Decimal = Decimal(18194) / Decimal(1956)
    submarine_maintenance: Decimal = Decimal(55)
    submarine_construction: Decimal = Decimal(295)
    infrastructure_factor: Decimal = Decimal("0.75")
    training_base_factor: Decimal = Decimal("0.8")
    academy_cost: Decimal = Decimal(340)
    dock_construction: Decimal = Decimal(324)
    income_factor: Decimal = Decimal(1)

    def __post_init__(self):
        for name, value in self.__dict__.items():
            value = Decimal(str(value))
            if not value.is_finite() or not 0 <= value <= 1_000_000:
                raise ValueError(f"{name.replace('_', ' ').capitalize()} must be between 0 and 1,000,000.")
            object.__setattr__(self, name, value)


@dataclass(frozen=True)
class BudgetContext:
    fleet_size: int | None = None
    intelligence: int | None = None
    construction_notes: tuple[str, ...] = ()
    maintenance_notes: tuple[str, ...] = ()
    additional_construction: int = 0
    additional_maintenance: int = 0
    aircraft_count: int = 0
    aircraft_available: int = 0
    estimate_notes: tuple[str, ...] = ()


def budget_context(save, nation, assumptions=None):
    """Read campaign-level inputs once when opening the modal editor."""
    assumptions = assumptions or BudgetAssumptions()
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
    construction, maintenance, notes = [], [], []
    additional_construction = additional_maintenance = 0
    if _field_integer(nation.section.fields(), "DockBuilding") > 0:
        additional_construction += _whole(assumptions.dock_construction)
        notes.append(f"Dock expansion: {assumptions.dock_construction:,.0f}/month fallback from the Game8 observation; not a general formula.")
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
                raw = _field_integer(fields, "Maintenance", default=None)
                if prefix == "Sub":
                    additional_maintenance += raw if raw is not None else _whole(assumptions.submarine_maintenance)
                    if raw is None:
                        notes.append(f"Submarine maintenance fallback: {assumptions.submarine_maintenance:,.0f} each, from Game3 long-range boats; other types/eras unverified.")
                elif raw is not None:
                    factor = Decimal(1) if "mtb" in fields.get("Classname", "").casefold() else assumptions.infrastructure_factor
                    additional_maintenance += int((Decimal(raw) * factor).quantize(Decimal(1), rounding=ROUND_HALF_EVEN))
                else:
                    maintenance.append("installation with no Maintenance (0 fallback)")
            else:
                cost = _field_integer(fields, "MonthlyCost", default=None)
                if cost is None:
                    cost = _whole(assumptions.submarine_construction) if prefix == "Sub" else 0
                    notes.append(f"{label.capitalize()} construction: missing MonthlyCost uses {cost:,} per unit; reference fallback, not a verified formula.")
                if _field_integer(fields, "Halted"):
                    raw = _field_integer(fields, "Maintenance", default=_whole(assumptions.submarine_maintenance) if prefix == "Sub" else 0)
                    cost = raw // 2
                    notes.append("Halted submarine/installation construction borrows the surface half-maintenance rule (unverified).")
                elif _field_integer(fields, "Hurry"):
                    cost = _whole(Decimal(cost) * Decimal("1.15"))
                    notes.append("Hurried submarine/installation construction borrows the surface 1.15 multiplier (unverified).")
                additional_construction += cost
    units = sections.get("airunits")
    models = sections.get("aircrafttypes")
    aircraft = sum(max(0, _field_integer(f, "AircraftNumber")) for f in _records(units.fields(), "AU")
                   if _field_integer(f, "Nation", default=-1) == nation.index) if units else 0
    available = sum(max(0, _field_integer(f, "AvailableAircraft")) for f in _records(models.fields(), "AT")
                    if _field_integer(f, "Nation", default=-1) == nation.index) if models else 0
    if units is None:
        notes.append("Air-unit roster unavailable: aircraft count falls back to 0.")
    return BudgetContext(fleet, intelligence, tuple(dict.fromkeys(construction)),
                         tuple(dict.fromkeys(maintenance)), additional_construction,
                         additional_maintenance, aircraft, available, tuple(dict.fromkeys(notes)))


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
    all_active_maintenance: int = 0


def project_budget(nation, *, context=None, base_resources=None, funds=None, assumptions=None):
    """Return numeric estimates; disclose reference-rate and zero fallbacks."""
    assumptions = assumptions or BudgetAssumptions()
    context = context or BudgetContext()
    resources = nation.base_resources if base_resources is None else base_resources
    available_funds = nation.funds if funds is None else funds
    fields = nation.section.fields()
    modifier = _field_integer(fields, "BudgetModifier", default=None)
    notes = ["Income: BaseResources × BudgetModifier × FleetSize / 10, with the adjustable income factor. Possession and other adjustments remain unresolved."]
    if resources is None or modifier is None or context.fleet_size is None:
        yearly = monthly = 0
        notes.append("Income inputs missing: income and research use a 0 fallback.")
    else:
        yearly = _whole(Decimal(resources) * modifier * context.fleet_size / 10 * assumptions.income_factor)
        monthly = _whole(Decimal(yearly) / 12)
    research_percent = _field_integer(fields, "ResearchPct")
    research = _whole(Decimal(monthly) * research_percent / 100)
    maintenance = 0
    all_active = 0
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
            all_active += charge
            maintenance += int((Decimal(charge) / divisor).quantize(
                Decimal(1), rounding=ROUND_HALF_EVEN))
    naval_aircraft = _field_integer(fields, "NavalAircraftSpending", "AircraftSpending", default=None)
    extra_training = _field_integer(fields, "ExtraTrainingSpending", "TrainingSpending", default=None)
    intelligence = context.intelligence
    if naval_aircraft is None:
        naval_aircraft = _whole(context.aircraft_count * assumptions.aircraft_rate)
        notes.append(f"Aircraft: {context.aircraft_count:,} assigned × {assumptions.aircraft_rate:.6f}; reference average 18,194 / 1,956. Pools ({context.aircraft_available:,}), development, role, pilot and carrier-readiness effects are not separately priced.")
    else:
        notes.append("Aircraft: explicit saved spending field.")
    if extra_training is None:
        percent = sum(rate for name, rate in (("GunneryTraining", 30), ("NightFighting", 20),
                      ("TorpedoWarfare", 20), ("DamageControl", 20)) if _field_integer(fields, name))
        academy = _whole(assumptions.academy_cost) if _field_integer(fields, "NavalAcademy") else 0
        extra_training = _whole(Decimal(maintenance) * assumptions.training_base_factor * percent / 100) + academy
        notes.append(f"Training: {percent}% × {assumptions.training_base_factor} × estimated surface maintenance + academy {academy:,}. The 0.8 base factor and 340 academy default are Game3 approximations; current flags only, pending timing unresolved.")
    else:
        notes.append("Training: explicit saved spending field.")
    if intelligence is None:
        intelligence = 0
        notes.append("Intelligence: 0 fallback; AI-owned spending or invalid target levels cannot be inferred from the player's target fields.")
    maintenance += context.additional_maintenance
    all_active += context.additional_maintenance
    notes.extend(context.estimate_notes)
    if context.construction_notes:
        notes.append("Construction uses 0 for " + ", ".join(context.construction_notes) + ".")
    if context.maintenance_notes:
        notes.append("Maintenance uses 0 for " + ", ".join(context.maintenance_notes) + ".")
    notes.append(f"Infrastructure: saved maintenance × {assumptions.infrastructure_factor}, nearest-even; MTB uses full value. Cross-save applicability unverified. Missile storage is not added separately because its accounting is unresolved.")
    notes.append("Ship maintenance includes observed class-2 search radar charges for DD/CL/CV; other equipment, repair and officer modifiers remain unverified.")
    total = maintenance + construction + sum(v for v in
        (naval_aircraft, research, extra_training, intelligence) if v is not None)
    return BudgetProjection(yearly, monthly, maintenance, construction, naval_aircraft,
        research, extra_training, intelligence, total, monthly - total, available_funds or 0,
        research_percent, tuple(notes), True, all_active)
