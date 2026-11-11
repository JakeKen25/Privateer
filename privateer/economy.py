"""Read-only RTW3 budget estimates with explicit, adjustable empirical fallbacks."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
import re
from pathlib import Path

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
    possession_income: int | None = None
    income_multipliers: tuple[Decimal, ...] = ()
    year: int | None = None
    invasion_active: bool = False
    aircraft_cost: int | None = None
    maintenance_multiplier: Decimal = Decimal(1)
    maintenance_model: object | None = None


def _submarine_cost(fields, year, nation_fields, *, construction=False, at_war=False):
    """Calculate the documented submarine rate; unknown types require a fallback."""
    kind = _field_integer(fields, 'SubType', default=None)
    base = {0: 40, 1: 50, 2: 20, 3: 55, 4: 55}.get(kind)
    if base is None or year is None:
        return None
    if construction:
        if year > 1930: base += 2
        if year > 1940: base += 4
        for threshold in (1950, 1955, 1960):
            if year > threshold: base = int(base * Decimal('1.1'))
        if _field_integer(nation_fields, 'EfficientShipbuildingIndustry'): base += 2
        if _field_integer(nation_fields, 'PoorEducation'): base -= 2
        return base * 5
    if year > 1950: base += 2
    for threshold in (1955, 1960):
        if year > threshold: base = int(base * Decimal('1.1'))
    return round(Decimal(base) * Decimal('1.5')) if at_war else base


def _aircraft_cost(units, ships, installations, nation_index, nation_fields, year, at_war):
    if year > 1999: return None
    rates = {0:8, 1:8, 2:8, 3:6, 4:12, 5:12, 6:8, 7:8,
             8:8, 9:8, 10:10, 11:18, 12:18, 13:8, 14:12}
    bases = {}
    for fields in (*ships, *installations):
        identity = _field_integer(fields, 'Id', default=None)
        if identity is not None: bases[identity] = fields
    total = 0
    for unit in units:
        if _field_integer(unit, 'Nation', default=-1) != nation_index: continue
        role = _field_integer(unit, 'Role', default=None)
        if role not in rates: return None
        rate = 14 if role == 5 and year >= 1952 else rates[role]
        cost = _field_integer(unit, 'AircraftNumber') * rate
        if _field_integer(nation_fields, 'AirSeaRescue'): cost = round(Decimal(cost) * Decimal('1.06'))
        if _field_integer(nation_fields, 'PilotTraining'):
            cost = round(Decimal(cost) * (Decimal('1.02') if _field_integer(nation_fields, 'Kamikaze') else Decimal('1.1')))
        if not at_war:
            cost = round(Decimal(cost) * Decimal('.8'))
            factor = (Decimal('1.01') if 1950 <= year <= 1956 else
                      Decimal('1.02') if 1957 <= year <= 1964 else
                      Decimal('1.03') if 1965 <= year <= 1968 else
                      Decimal('1.04') if 1969 <= year <= 1975 else
                      Decimal('1.05') if 1976 <= year <= 1999 else Decimal(1))
            cost = round(Decimal(cost) * factor)
        if _field_integer(unit, 'CarrierCapable'): cost = round(Decimal(cost) * Decimal('1.5'))
        if _field_integer(unit, 'NightCapable'):
            cost = round(Decimal(cost) * (Decimal('1.3') if role in (10,11,12) else Decimal('1.5')))
        home = _field_integer(unit, 'HomeBase', default=-1)
        base = bases.get(home)
        if home >= 0 and base is None: return None
        if (base and _field_integer(base, 'Status') in (1,2)) or (home < 0 and not at_war):
            cost = round(Decimal(cost) * Decimal('.8'))
        total += cost
    for ship in ships:
        if _field_integer(ship, 'InPlay', default=1) != 1 or _field_integer(ship, 'RepairTime') >= 100: continue
        if ship.get('ShipType', '').strip().upper() not in ('CV','CVL'):
            capacity = _field_integer(ship, 'AircraftCapacity')
            total += capacity * ((10 if at_war else 8) if _field_integer(ship, 'Helipad') else (8 if at_war else 6))
    for installation in installations:
        if _field_integer(installation, 'InPlay', default=1) != 1 or _field_integer(installation, 'RepairTime') >= 100: continue
        capacity = _field_integer(installation, 'AircraftCapacity')
        if 0 < capacity <= 16:
            total += capacity * (20 if year < 1939 else 25 if year <= 1945 else 30)
    return total


def _possession_income(save, nation, year, install_directory):
    from .colonies import possessions
    from .document import TextDocument
    if not install_directory:
        raise ValueError('Set the game installation directory to calculate possession income.')
    path = Path(install_directory) / 'Data' / 'MapData.dat'
    try:
        data = path.read_bytes()
        try: text = data.decode('utf-8-sig')
        except UnicodeDecodeError: text = data.decode('cp1252')
    except OSError as exc:
        raise ValueError(f'Cannot read the game map data: {path}') from exc
    natural = {}
    names = {}
    for section in TextDocument.parse(text).sections:
        for key, value in section.fields().items():
            m = re.fullmatch(r'MapArea(\d+)Possession(\d+)(NaturalOwnerName|Name)', key, re.I)
            if m:
                target = natural if m.group(3).casefold() == 'naturalownername' else names
                target[(int(m.group(1)), int(m.group(2)))] = value
    brackets = ((1899,29),(1904,28),(1906,27),(1908,26),(1910,25),(1912,24),
                (1914,23),(1918,22),(1925,21),(1930,20),(1936,19),(1940,18),
                (1944,17),(1945,16),(1946,15),(1947,14),(1948,13),(1949,12),
                (1950,10),(1951,8),(1952,6),(1999,4))
    rate = next((value for end,value in brackets if year <= end), None)
    if rate is None: raise ValueError('Possession income is not specified after 1999.')
    owned = [p for p in possessions(save) if p.owner.casefold() == nation.name.casefold()]
    homes = {p.area for p in owned if int(p.value) >= 200}
    total = 0
    for p in owned:
        value = int(p.value)
        if p.area in homes:
            if value < 200: total += value * 25
            continue
        key = (p.area, p.index)
        if names.get(key, '').casefold() != p.name.casefold():
            matches = [k for k, name in names.items()
                       if k[0] == p.area and name.casefold() == p.name.casefold()]
            if len(matches) != 1:
                raise ValueError(f'Cannot uniquely match {p.name} in game map data.')
            key = matches[0]
        if key not in natural:
            raise ValueError(f'Cannot match natural ownership for {p.name} in game map data.')
        total += value * (25 if natural[key].casefold() == nation.name.casefold() else rate)
    return total


def budget_context(save, nation, assumptions=None, install_directory=None):
    """Read campaign-level inputs once when opening the modal editor."""
    assumptions = assumptions or BudgetAssumptions()
    sections = {s.name.casefold(): s for s in save.documents[save.main_file].sections}
    general = sections.get("general")
    fleet = _field_integer(general.fields(), "FleetSize", default=None) if general else None
    game = general.fields() if general else {}
    year = _field_integer(game, 'Year', default=None)
    nf = nation.section.fields()
    income_warning = None
    try:
        income = _possession_income(save, nation, year, install_directory) if year is not None else None
    except (ValueError, KeyError) as exc:
        income = None
        income_warning = str(exc)
    factors = []
    if fleet is not None and fleet <= 3: factors.append(Decimal('1.08'))
    if _field_integer(game, 'ArmyOffensive') > 0: factors.append(Decimal('0.9'))
    if _field_integer(game, 'CRI') > 0: factors.append(Decimal('0.99'))
    gov = _field_integer(nf, 'GovernmentType', default=-1)
    if _field_integer(game, 'TotalWar') and gov in (4,5): factors.append(Decimal('1.05'))
    if year is not None and year > 1920 and _field_integer(game, 'War') < -6 and gov in (0,1): factors.append(Decimal('0.97'))
    maintenance_multiplier = Decimal(1)
    if year is not None and _field_integer(game, 'War') <= 0 and gov not in (3, 5):
        maintenance_multiplier = next((Decimal(factor) for start,end,factor in
            ((1922,1949,'1.02'),(1950,1955,'1.05'),(1956,1960,'1.1'),
             (1961,1965,'1.15'),(1966,1970,'1.2'),(1971,1999,'1.25'))
            if start <= year <= end), Decimal(1))
    intelligence = None
    # The target-nation spending fields describe the player's intelligence only.
    if nation.index == 0:
        levels = [_field_integer(n.section.fields(), "IntelligenceSpending", default=None)
                  for n in save.nations if n.index != 0]
        if all(level in (0, 1, 2, 3) for level in levels):
            intelligence = sum(levels) * 10 * fleet if fleet is not None else None
    construction, maintenance, notes = [], [], []
    if income_warning: notes.append(income_warning)
    additional_construction = additional_maintenance = 0
    submarine_maintenance = 0
    if fleet is not None:
        try:
            from .colonies import map_document, possessions
            map_fields = map_document(save)[2].fields()
            for p in possessions(save):
                if p.owner.casefold() != nation.name.casefold(): continue
                key = f'MapArea{p.area}Possession{p.index}BuildingBase'
                if _field_integer(map_fields, key) > 0:
                    additional_construction += (fleet + 1) * (150 if int(p.base) >= 20 else 100)
        except (ValueError, KeyError) as exc:
            notes.append(f'Base expansion unavailable: {exc}')
    if _field_integer(nation.section.fields(), "DockBuilding") > 0:
        size = _field_integer(nf, 'DockSize', default=None)
        if fleet is None or size is None:
            additional_construction += _whole(assumptions.dock_construction)
            notes.append('Dock expansion uses the reference fallback because fleet size or dock size is missing.')
        else:
            dock = (fleet + 1) * 150
            for condition, factor in ((size < 15000, Decimal('.9')),
                                      (size < 10000, Decimal('.9'))):
                if condition: dock = int(dock * factor)
            for threshold in (30000, 40000, 50000, 60000, 65000):
                if size >= threshold: dock = int(dock * Decimal('1.1'))
            if _field_integer(nf, 'UndevelopedShipbuildingIndustry'):
                dock = int(dock * Decimal('.8'))
            additional_construction += dock
            notes.append(f'Dock expansion: {dock:,}/month from the supplied rule; under validation.')
    for suffix, prefix, label in (("Submarines", "Sub", "submarines"),
                                   ("CoastalArtillery", "Ship", "fortifications")):
        section = sections.get(f"nation{nation.index}{suffix}".casefold())
        if section is None:
            maintenance.append(label + " (roster unavailable)")
            construction.append(label + " (roster unavailable)")
            continue
        for fields in _records(section.fields(), prefix):
            if (prefix != 'Sub' and not appears_in_transfer_window(fields)) or _field_integer(fields, "Sunk"):
                continue
            if _field_integer(fields, "InPlay", default=1):
                raw = _field_integer(fields, "Maintenance", default=None)
                if prefix == "Sub":
                    cost = _submarine_cost(fields, year, nf, at_war=_field_integer(game, 'War') > 0)
                    if cost is None:
                        cost = raw if raw is not None else _whole(assumptions.submarine_maintenance)
                        notes.append('Unknown submarine type or year uses a maintenance fallback.')
                    additional_maintenance += cost
                    submarine_maintenance += cost
                elif raw is not None:
                    factor = Decimal(1) if "mtb" in fields.get("Classname", "").casefold() else assumptions.infrastructure_factor
                    additional_maintenance += int((Decimal(raw) * factor).quantize(Decimal(1), rounding=ROUND_HALF_EVEN))
                else:
                    maintenance.append("installation with no Maintenance (0 fallback)")
            else:
                cost = (_submarine_cost(fields, year, nf, construction=True)
                        if prefix == 'Sub' else _field_integer(fields, "MonthlyCost", default=None))
                if cost is None:
                    cost = _whole(assumptions.submarine_construction) if prefix == "Sub" else 0
                    notes.append(f"{label.capitalize()} construction: missing MonthlyCost uses {cost:,} per unit; reference fallback, not a verified formula.")
                if _field_integer(fields, "Halted"):
                    raw = _field_integer(fields, "Maintenance", default=_whole(assumptions.submarine_maintenance) if prefix == "Sub" else 0)
                    cost = raw // 2
                    notes.append("Halted submarine/installation construction borrows the surface half-maintenance rule (unverified).")
                elif prefix != 'Sub' and _field_integer(fields, "Hurry"):
                    cost = _whole(Decimal(cost) * Decimal("1.15"))
                    notes.append("Hurried submarine/installation construction borrows the surface 1.15 multiplier (unverified).")
                additional_construction += cost
    maintenance_model = None
    if year is not None and nation.index == 0:
        try:
            from .maintenance import fleet_maintenance
            maintenance_model = fleet_maintenance(save, nation, game, sections)
            additional_maintenance = submarine_maintenance + maintenance_model.installations
            notes.append('Ship maintenance follows the supplied rules; KE date interpretation and unusual cases remain under validation.')
        except (ValueError, KeyError) as exc:
            notes.append(f'Ship maintenance uses earlier estimates: {exc}')
    units = sections.get("airunits")
    models = sections.get("aircrafttypes")
    aircraft = sum(max(0, _field_integer(f, "AircraftNumber")) for f in _records(units.fields(), "AU")
                   if _field_integer(f, "Nation", default=-1) == nation.index) if units else 0
    available = sum(max(0, _field_integer(f, "AvailableAircraft")) for f in _records(models.fields(), "AT")
                    if _field_integer(f, "Nation", default=-1) == nation.index) if models else 0
    if units is None:
        notes.append("Air-unit roster unavailable: aircraft count falls back to 0.")
    aircraft_cost = None
    if units is not None and year is not None:
        fort_section = sections.get(f'nation{nation.index}coastalartillery')
        if fort_section is not None:
            aircraft_cost = _aircraft_cost(_records(units.fields(), 'AU'),
                tuple(ship.section.fields() for ship in nation.ships),
                _records(fort_section.fields(), 'Ship'), nation.index, nf, year,
                _field_integer(game, 'War') > 0)
            if aircraft_cost is None: notes.append('Unknown air-unit role, base or year uses the aircraft fallback.')
    return BudgetContext(fleet, intelligence, tuple(dict.fromkeys(construction)),
                         tuple(dict.fromkeys(maintenance)), additional_construction,
                         additional_maintenance, aircraft, available, tuple(dict.fromkeys(notes)), income, tuple(factors), year,
                         game.get('InvasionTargetName', '').strip().casefold() not in ('', 'xxx'), aircraft_cost,
                         maintenance_multiplier, maintenance_model)


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
    invasion: int = 0


def project_budget(nation, *, context=None, base_resources=None, funds=None, assumptions=None):
    """Return numeric estimates; disclose reference-rate and zero fallbacks."""
    assumptions = assumptions or BudgetAssumptions()
    context = context or BudgetContext()
    resources = nation.base_resources if base_resources is None else base_resources
    available_funds = nation.funds if funds is None else funds
    fields = nation.section.fields()
    modifier = _field_integer(fields, "BudgetModifier", default=None)
    notes = ["Income follows the supplied formula when possession and campaign data are available; other budget lines remain estimates."]
    if resources is None or modifier is None or context.fleet_size is None:
        yearly = monthly = 0
        notes.append("Income inputs missing: income and research use a 0 fallback.")
    else:
        if context.possession_income is None:
            yearly = _whole(Decimal(resources) * modifier * context.fleet_size / 10 * assumptions.income_factor)
            notes.append('Possession data unavailable: income uses the earlier estimate.')
        else:
            yearly = round(Decimal(resources + context.possession_income) / 101 * max(3, modifier)) * context.fleet_size
            for factor in context.income_multipliers:
                yearly = round(Decimal(yearly) * factor)
            yearly *= 10
        monthly = round(Decimal(yearly) / 12)
    research_percent = _field_integer(fields, "ResearchPct")
    research_yearly = round(Decimal(yearly) * research_percent / 100)
    if _field_integer(fields, 'HFR') == 3 and context.fleet_size is not None:
        research_yearly += 1200 * context.fleet_size
    research = round(Decimal(research_yearly) / 12)
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
    if context.maintenance_model is not None:
        maintenance = context.maintenance_model.surface
        all_active = context.maintenance_model.surface_all_active
    naval_aircraft = _field_integer(fields, "NavalAircraftSpending", "AircraftSpending", default=None)
    extra_training = _field_integer(fields, "ExtraTrainingSpending", "TrainingSpending", default=None)
    intelligence = context.intelligence
    if naval_aircraft is None:
        if context.aircraft_cost is not None:
            naval_aircraft = context.aircraft_cost
            notes.append('Aircraft use the supplied role and modifier rules; the result is under validation.')
        else:
            naval_aircraft = _whole(context.aircraft_count * assumptions.aircraft_rate)
            notes.append(f"Aircraft: {context.aircraft_count:,} assigned × {assumptions.aircraft_rate:.6f}; reference average 18,194 / 1,956. Pools ({context.aircraft_available:,}), development, role, pilot and carrier-readiness effects are not separately priced.")
    else:
        notes.append("Aircraft: explicit saved spending field.")
    if context.maintenance_model is not None:
        academy = (round(Decimal(yearly // 95) / 12) // 10 * 10) if _field_integer(fields, 'NavalAcademy') else 0
        model = context.maintenance_model
        extra_training = round(Decimal(model.training_base * model.training_points) * model.training_rate) + academy
        notes.append('Training uses eligible ship maintenance, current and pending priorities, and the academy rule; under validation.')
    elif extra_training is None:
        percent = sum(rate for name, rate in (("GunneryTraining", 30), ("NightFighting", 20),
                      ("TorpedoWarfare", 20), ("DamageControl", 20)) if _field_integer(fields, name))
        academy = (round(Decimal(yearly // 95) / 12) // 10 * 10) if _field_integer(fields, "NavalAcademy") else 0
        extra_training = _whole(Decimal(maintenance) * assumptions.training_base_factor * percent / 100) + academy
        notes.append(f"Training: {percent}% × {assumptions.training_base_factor} × estimated surface maintenance + academy {academy:,} derived from yearly budget. The training factor and pending timing remain unverified.")
    else:
        notes.append("Training: explicit saved spending field.")
    if intelligence is None:
        intelligence = 0
        notes.append("Intelligence: 0 fallback; AI-owned spending or invalid target levels cannot be inferred from the player's target fields.")
    maintenance += context.additional_maintenance
    all_active += context.additional_maintenance
    maintenance = round(Decimal(maintenance) * context.maintenance_multiplier)
    all_active = round(Decimal(all_active) * context.maintenance_multiplier)
    notes.extend(context.estimate_notes)
    if context.construction_notes:
        notes.append("Construction uses 0 for " + ", ".join(context.construction_notes) + ".")
    if context.maintenance_notes:
        notes.append("Maintenance uses 0 for " + ", ".join(context.maintenance_notes) + ".")
    notes.append(f"Infrastructure: saved maintenance × {assumptions.infrastructure_factor}, nearest-even; MTB uses full value. Cross-save applicability unverified. Missile storage is not added separately because its accounting is unresolved.")
    notes.append("Ship maintenance includes observed class-2 search radar charges for DD/CL/CV; other equipment, repair and officer modifiers remain unverified.")
    invasion = yearly // 300 + 100 if context.invasion_active else 0
    total = maintenance + construction + invasion + sum(v for v in
        (naval_aircraft, research, extra_training, intelligence) if v is not None)
    return BudgetProjection(yearly, monthly, maintenance, construction, naval_aircraft,
        research, extra_training, intelligence, total, monthly - total, available_funds or 0,
        research_percent, tuple(notes), True, all_active, invasion)

