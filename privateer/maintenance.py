"""Provisional player-fleet maintenance rules from the supplied formula notes."""
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from .colonies import MAP_AREA_NAMES, map_area_name, possessions
from .document import TextDocument
from .economy import _field_integer, _records


@dataclass(frozen=True)
class MaintenanceModel:
    surface: int
    surface_all_active: int
    installations: int
    training_base: int
    training_points: int
    training_rate: Decimal


def ship_maintenance(fields, *, year, month, day, at_war, home_areas,
                     possession_areas, officers, installation=False, all_active=False):
    """Calculate a single hull; all-active applies only to surface ships."""
    needed = ('Maintenance', 'RepairTime', 'Status', 'ShipType', 'LocationAreaName')
    missing = [key for key in needed if key not in fields]
    if missing:
        raise ValueError('Ship maintenance is missing ' + ', '.join(missing))
    typ = fields['ShipType'].strip().upper()
    status = _field_integer(fields, 'Status')
    repair = _field_integer(fields, 'RepairTime')
    raw = _field_integer(fields, 'Maintenance')
    if repair >= 100: return 0
    cost = raw
    commander = _field_integer(fields, 'CommanderId', default=-1)
    officer = officers.get(commander, {})
    if commander >= 0 and commander not in officers:
        raise ValueError(f'Cannot resolve commander {commander} for ship maintenance')
    specials = {_field_integer(officer, 'Special'), _field_integer(officer, 'Special2')}
    if 17 in specials: cost = round(Decimal(cost) * Decimal('.75'))
    if 11 in specials: cost = round(Decimal(cost) * Decimal('1.1'))
    land_installation = installation and typ == 'LT'
    if repair > 0 and status != 2:
        cost = raw * (3 if land_installation else 2)
    if typ == 'KE':
        obsolete = _field_integer(fields, 'ObsoleteDate', default=None)
        if obsolete is None:
            raise ValueError('KE obsolete date is missing')
        # Saved dates appear to be days since 1900; month boundaries remain unverified.
        current = (year - 1900) * 365 + (month - 1) * 30 + day - 1
        if abs(current - obsolete) <= 31:
            raise ValueError('KE obsolete date is too close to an unverified date boundary')
        if obsolete < current: cost = round(Decimal(cost) * Decimal('1.1'))
    if not land_installation and status != 9:
        built = _field_integer(fields, 'YearBuilt', default=None)
        if built is None: raise ValueError('Ship build year is missing')
        age = year - built
        for threshold in (20, 25, 30, 35, 40, 45):
            if age > threshold: cost += int(Decimal(cost) * Decimal('.1')) + 1
    radar = _field_integer(fields, 'SearchRadarClass')
    cost += radar * (2 if typ in ('BB', 'BC', 'B', 'CA', 'CL', 'CV', 'CVL') else 1)
    if year > 1950 and not at_war and (typ in ('BB', 'BC') or
            (land_installation and _field_integer(fields, 'MainCalibre') > 8)):
        cost = round(Decimal(cost) * Decimal('1.05'))
    if all_active and not installation:
        return cost
    location = fields['LocationAreaName'].strip().casefold()
    if installation:
        location = possession_areas.get(location, location)
    known_areas = {name.casefold() for name in MAP_AREA_NAMES}
    if location not in known_areas:
        raise ValueError(f'Unknown ship location for maintenance: {fields["LocationAreaName"]}')
    outside = location not in home_areas
    if status in (1, 7): cost = round(Decimal(cost) * Decimal('.5'))
    elif status in (2, 9): cost = round(Decimal(cost) * Decimal('.2'))
    elif at_war: cost = round(Decimal(cost) * Decimal('1.4'))
    elif outside: cost = round(Decimal(cost) * Decimal('1.2'))
    name = fields.get('Classname', '').casefold()
    airbase = land_installation and ('airbase' in name or 'airship base' in name)
    if airbase and outside: cost = round(Decimal(cost) * Decimal('1.2'))
    if land_installation and not at_war: cost = round(Decimal(cost) * Decimal('.75'))
    return cost


def fleet_maintenance(save, nation, game, sections):
    """Read map and officer dependencies and calculate the player's fleet subtotal."""
    if nation.index != 0: raise ValueError('AI maintenance rules need further research')
    year = _field_integer(game, 'Year', default=None)
    month = _field_integer(game, 'Month', default=None)
    day = _field_integer(game, 'Day', default=None)
    if year is None or month is None or day is None or 'War' not in game:
        raise ValueError('Campaign date or war state is missing')
    owned = possessions(save)
    homes = {map_area_name(p.area).casefold() for p in owned
             if p.owner.casefold() == nation.name.casefold() and int(p.value) >= 200}
    if not homes: raise ValueError('Home areas for ship maintenance could not be identified')
    areas = {}
    for p in owned:
        key, area = p.name.casefold(), map_area_name(p.area).casefold()
        if key in areas and areas[key] != area:
            raise ValueError(f'Ambiguous possession location: {p.name}')
        areas[key] = area
    name = Path(save.main_file).with_suffix('.off').name
    doc = save.documents.get(name)
    if doc is None:
        try: data = (save.folder / name).read_bytes()
        except OSError as exc: raise ValueError('Officer file is unavailable for maintenance') from exc
        try: text = data.decode('utf-8-sig')
        except UnicodeDecodeError: text = data.decode('cp1252')
        doc = TextDocument.parse(text)
    matches = [section for section in doc.sections if section.name.casefold() == 'officers']
    if len(matches) != 1: raise ValueError('Officer section is missing or ambiguous')
    officers = {}
    for officer in _records(matches[0].fields(), 'Officer'):
        identity = _field_integer(officer, 'Id', default=None)
        if identity is None: continue
        if identity in officers: raise ValueError(f'Duplicate officer ID {identity}')
        officers[identity] = officer
    fort = sections.get(f'nation{nation.index}coastalartillery')
    if fort is None: raise ValueError('Installation roster is unavailable for maintenance')
    ships = [ship.section.fields() for ship in nation.ships]
    installations = _records(fort.fields(), 'Ship')
    at_war = _field_integer(game, 'War') > 0
    kwargs = dict(year=year, month=month, day=day, at_war=at_war,
                  home_areas=homes, possession_areas=areas, officers=officers)
    current = [f for f in ships if _field_integer(f, 'InPlay', default=1) == 1 and
               _field_integer(f, 'RepairTime') < 100]
    surface = sum(ship_maintenance(f, **kwargs) for f in current)
    active = sum(ship_maintenance(f, all_active=True, **kwargs) for f in current)
    installation_total = sum(ship_maintenance(f, installation=True, **kwargs)
        for f in installations if _field_integer(f, 'InPlay', default=1) == 1 and
        _field_integer(f, 'RepairTime') < 100)
    training_base = sum(ship_maintenance(f, **kwargs) for f in current
                       if _field_integer(f, 'RepairTime') == 0 and
                       _field_integer(f, 'Status') not in (7, 9))
    nf = nation.section.fields()
    programs = (('GunneryTraining', 'PendingGunneryTraining', 3),
                ('NightFighting', 'PendingNightFighting', 2),
                ('TorpedoWarfare', 'PendingTorpedoWarfare', 2),
                ('DamageControl', 'PendingDamageControl', 2))
    points = sum(value for current_key, pending_key, value in programs
                 if _field_integer(nf, current_key) or _field_integer(nf, pending_key))
    rate = (Decimal('.06') if _field_integer(nf, 'SurpriseAttack') and not _field_integer(nf, 'PoorEducation')
            else Decimal('.05') if at_war else Decimal('.08'))
    return MaintenanceModel(surface, active, installation_total, training_base, points, rate)

