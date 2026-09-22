"""Coastal-artillery rosters, including land airbases and MTB squadrons.

Record layout and standard costs were checked against all nine Game6 nations.
IDs are shared with ships/air units; never renumber an existing installation.
"""
from dataclasses import dataclass
from pathlib import Path
import re

from .colonies import possessions
from .document import FIELD, TextDocument


@dataclass(frozen=True)
class FortificationType:
    name: str
    family: str
    cost: int
    maintenance: int
    capacity: int = 0


TYPES = {
    item.name: item for item in [
        *(FortificationType(f'{caliber} in coastal battery', 'battery', cost, maintenance)
          for caliber, cost, maintenance in
          [(4, 1200, 6), (5, 1600, 9), (6, 1920, 13), (7, 3200, 17),
           (8, 4800, 22), (9, 6000, 26), (10, 7200, 30), (11, 9600, 40), (12, 12000, 50)]),
        *(FortificationType(f'{caliber} in coastal battery in turrets', 'battery', cost, maintenance)
          for caliber, cost, maintenance in [(12, 19200, 76), (13, 24000, 84), (14, 26400, 92)]),
        FortificationType('Missile Battery', 'battery', 8000, 26),
        FortificationType('MTB squadron', 'mtb', 300, 20),
        FortificationType('Airship base', 'airship', 700, 43, 8),
        # Sizes 100/120 also exist in the installed Data/IDes templates.
        *(FortificationType(f'Airbase{size}', 'airbase', 700, size + 26, size)
          for size in (20, 40, 60, 80, 100, 120)),
    ]
}
_TYPES_BY_NAME = {name.casefold(): item for name, item in TYPES.items()}
_SHIP_FIELD = re.compile(r'Ship(\d+)(\D.*)')


def type_for(name):
    return _TYPES_BY_NAME.get(name.casefold())


def _section(save, name):
    found = [s for s in save.documents[save.main_file].sections if s.name.casefold() == name.casefold()]
    if len(found) != 1:
        raise ValueError(f'Missing or duplicate [{name}] section')
    return found[0]


def _fields(section):
    result = {}
    seen = set()
    for line in section.lines:
        match = FIELD.match(line)
        if not match:
            continue
        key, value = match.group(2).strip(), match.group(4).strip()
        if key.casefold() in seen:
            raise ValueError(f'Duplicate {key} in [{section.name}]')
        seen.add(key.casefold())
        result[key] = value
    return result


def number(value, label, maximum=2**31 - 1):
    if isinstance(value, bool) or not re.fullmatch(r'\d+', str(value)) or not 0 <= int(value) <= maximum:
        raise ValueError(f'{label} must be a whole number from 0 to {maximum:,}')
    return int(value)


def records(save, nation):
    section = _section(save, f'Nation{save.nation(nation).index}CoastalArtillery')
    fields = _fields(section)
    count = number(fields.get('CACount', ''), 'CACount', 10000)
    result = {}
    for key, value in fields.items():
        match = _SHIP_FIELD.fullmatch(key)
        if match:
            result.setdefault(int(match[1]), {})[match[2]] = value
    if set(result) != set(range(count)):
        raise ValueError('Fortification slots do not match CACount')
    ids = set()
    for slot, record in result.items():
        required = {'Id', 'Name', 'Classname', 'LocationAreaName', 'AircraftCapacity',
                    'InPlay', 'Fate', 'Cost', 'BuildProgress', 'Maintenance', 'Description', 'ShipType'}
        if required - record.keys():
            raise ValueError(f'Fortification {slot} is missing required fields')
        identity = number(record['Id'], 'Fortification ID')
        if identity in ids:
            raise ValueError('Duplicate fortification ID')
        ids.add(identity)
    return result


def status(record):
    if record['Fate'].strip().casefold() not in ('', 'xxx'):
        return record['Fate']
    return 'Built' if record['InPlay'] == '1' else 'Under construction'


def available_types(save):
    general = _fields(_section(save, 'General'))
    maximum = number(general.get('GameMaxAirbaseSize', '80'), 'Maximum airbase size', 10000)
    return [item for item in TYPES.values() if item.family != 'airbase' or item.capacity <= maximum]


def owned_locations(save, nation):
    name = save.nation(nation).name
    return sorted({p.name for p in possessions(save) if p.owner == name})


def base_sites(install_directory):
    """Read named sites by possession name, not by potentially scenario-specific slot."""
    path = Path(install_directory) / 'Data' / 'MapData.dat'
    if not path.is_file():
        return {}
    text = path.read_bytes().decode('cp1252')
    document = TextDocument.parse(text)
    fields = {k: v for section in document.sections for k, v in section.fields().items()}
    result = {}
    for key, value in fields.items():
        match = re.fullmatch(r'(MapArea\d+Possession\d+)BaseNames\d+', key)
        if match and value and value.casefold() not in ('xxx', 'error'):
            location = fields.get(match[1] + 'Name')
            if location:
                result.setdefault(location, set()).add(value)
    return {location: sorted(names) for location, names in result.items()}


def occupied_capacity(save, identity):
    sections = [s for s in save.documents[save.main_file].sections if s.name == 'AirUnits']
    if len(sections) > 1:
        raise ValueError('Duplicate air-unit roster')
    if not sections:
        return 0
    fields = _fields(sections[0])
    total = 0
    for key, value in fields.items():
        match = re.fullmatch(r'(AU\d+)HomeBase', key)
        if match and value == str(identity):
            prefix = match[1]
            total += max(number(fields.get(prefix + suffix, ''), suffix)
                         for suffix in ('AircraftNumber', 'DesiredAircraftNumber'))
    return total


def _text(value, label, encoding):
    if not isinstance(value, str) or not value.strip() or any(c in value for c in '\r\n\x00'):
        raise ValueError(f'{label} must be a non-empty single line')
    try:
        value.strip().encode(encoding)
    except UnicodeEncodeError as exc:
        raise ValueError(f'{label} contains characters this save cannot store') from exc
    return value.strip()


def _type_fields(item):
    return {'Classname': item.name, 'AircraftCapacity': str(item.capacity),
            'Description': f'{item.capacity} a/c' if item.family == 'airbase' else
                           f'{item.capacity} airships' if item.family == 'airship' else '',
            'ShipType': 'MTB' if item.family == 'mtb' else 'LT',
            'Cost': str(item.cost), 'Maintenance': str(item.maintenance)}


def _new_record(item, name, location, identity, nation, year):
    zero_fields = ('Displacement CrewQuality TimeToRefit ObsoleteDate Reinforcement AccomodationCramped '
                   'ColonialService CLAA TPS EnginePriority MainCalibre HSSM MSSM RepairTime Side Course '
                   'Active Training Deployed Used ASWValue Mines BattleStars FCRadarClass SearchRadarClass '
                   'RadarLimit MSG PlayerIntel EnhancedSonar OldASW TowedArray FlightDeckCatapults JetCapable '
                   'AngledFlightDeck Helipad FuelType BuildProgress MonthlyCost MMP Halted Hurry Status OldStatus '
                   'EngineYear EAM Speed EnemySpeed EnemyBelt Range Rebuild NumberOfLogEntries').split()
    record = dict.fromkeys(zero_fields, '0')
    record.update({'Id': str(identity), 'DesignRefId': '-1', 'Name': name, 'EnemyClassName': 'XXX',
                   'InPlay': '1', 'Fate': 'XXX', 'CommanderId': '-1', 'Mine capacity': '0',
                   'YearBuilt': str(year), 'BuildingNationIdx': str(nation), 'LocationAreaName': location,
                   'DestinationAreaName': 'XXX', 'OrderedAreaName': 'XXX'})
    record.update(_type_fields(item))
    return record


def apply_infrastructure(save, nation, dock_size, changes, additions, *, sites=None):
    """Validate the whole batch before changing the save; additions are built instantly.

    Changes are keyed by local roster slot, never by a displayed/sorted row index.
    Airbase families cannot be converted to another family or moved/renamed.
    """
    target = save.nation(nation)
    if dock_size is not None:
        number(dock_size, 'Dockyard size')
        if target.dock_size is None:
            raise ValueError('This nation has no dockyard size field')
    if not changes and not additions:
        if dock_size is not None:
            save.set_dock_size(nation, dock_size)
        return
    roster = records(save, nation)
    section = _section(save, f'Nation{target.index}CoastalArtillery')
    document = save.documents[save.main_file]
    locations = owned_locations(save, nation)
    allowed = {item.name for item in available_types(save)}
    patches = {}
    for slot, edit in changes.items():
        if type(slot) is not int or slot not in roster:
            raise ValueError('Unknown fortification slot')
        if set(edit) != {'Name', 'Classname', 'LocationAreaName'}:
            raise ValueError('Unsupported fortification edit')
        original = roster[slot]
        old_type = type_for(original['Classname'])
        item = type_for(edit['Classname'])
        if not old_type or not item or old_type.family != item.family:
            raise ValueError('Choose a supported type from the same installation family')
        if status(original) != 'Built':
            raise ValueError('Only built installations can be edited')
        name = _text(edit['Name'], 'Name', document.encoding)
        location = _text(edit['LocationAreaName'], 'Location', document.encoding)
        changed_type = item != old_type
        if changed_type and item.name not in allowed:
            raise ValueError('Airbase size exceeds this campaign limit')
        if location != original['LocationAreaName'] and location not in locations:
            raise ValueError('Select a possession owned by this nation')
        if old_type.family in ('airbase', 'airship'):
            if name != original['Name'] or location != original['LocationAreaName']:
                raise ValueError('Existing airbase names and locations are preserved to retain their site links')
            if changed_type and item.capacity < occupied_capacity(save, original['Id']):
                raise ValueError('This base has more assigned aircraft than the requested capacity')
        patch = {'Name': name, 'LocationAreaName': location}
        if changed_type:
            patch.update(_type_fields(item))
            # Built records use InPlay=1; a fresh scenario installation has zero progress/cost per month.
            patch.update(BuildProgress='0', MonthlyCost='0')
        patches[slot] = {k: v for k, v in patch.items() if original.get(k) != v}

    general = _section(save, 'General')
    fields = _fields(general)
    new_records = []
    next_id = None
    if additions:
        next_id = number(fields.get('IDNo', ''), 'Global ID counter')
        # Scan every stored identity, including aircraft, submarines and officers referenced in BCS.
        for source in document.sections:
            for key, value in source.fields().items():
                if key.endswith('Id') and re.fullmatch(r'\d+', value):
                    next_id = max(next_id, int(value) + 1)
        year = number(fields.get('Year', ''), 'Campaign year', 2200)
        existing_names = {r['Name'].casefold() for r in roster.values()}
        for addition in additions:
            if set(addition) != {'Name', 'Classname', 'LocationAreaName'}:
                raise ValueError('Unsupported fortification addition')
            item = type_for(addition['Classname'])
            if not item or item.name not in allowed:
                raise ValueError('Unsupported fortification type or airbase size')
            name = _text(addition['Name'], 'Name', document.encoding)
            location = _text(addition['LocationAreaName'], 'Location', document.encoding)
            if location not in locations:
                raise ValueError('Select a possession owned by this nation')
            if name.casefold() in existing_names:
                raise ValueError('An installation with this name already exists')
            existing_names.add(name.casefold())
            if item.family in ('airbase', 'airship'):
                prefix = 'Airbase ' if item.family == 'airbase' else 'Airship base '
                if name not in [prefix + site for site in (sites or {}).get(location, [])]:
                    raise ValueError('Select a named base site from the installed game map data')
                site = name[len(prefix):].casefold()
                for record in [*roster.values(), *new_records]:
                    if (record['LocationAreaName'] == location and type_for(record['Classname']) and
                        type_for(record['Classname']).family == item.family and
                        any(record['Name'].casefold() == label + site for label in
                            ('airbase ', 'naval air station ', 'airship base '))):
                        raise ValueError('This site already has an installation of that family')
            if next_id >= 2**31 - 1 or len(roster) + len(new_records) >= 10000:
                raise ValueError('No installation slot or ID is available')
            new_records.append(_new_record(item, name, location, next_id, target.index, year))
            next_id += 1
    if not any(patches.values()) and not new_records:
        if dock_size is not None:
            save.set_dock_size(nation, dock_size)
        return
    save._check_tension_source()
    with save.transaction():
        if dock_size is not None:
            save.set_dock_size(nation, dock_size)
        for slot, patch in patches.items():
            for key, value in patch.items():
                section.set(f'Ship{slot}{key}', value, document.newline)
        if new_records:
            if section.lines and not section.lines[-1].endswith(('\n', '\r')):
                section.lines[-1] += document.newline
            for slot, record in enumerate(new_records, len(roster)):
                section.lines.extend(f'Ship{slot}{key}={value}{document.newline}' for key, value in record.items())
            section.set('CACount', len(roster) + len(new_records), document.newline)
            general.set('IDNo', next_id, document.newline)
        records(save, nation)
        save.validate_or_raise()
        save.audit.append(f'Fortifications for {target.name}: {sum(bool(p) for p in patches.values())} edited, {len(new_records)} added')
        save.modified = True
    save._fortification_changes = True
