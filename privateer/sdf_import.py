"""Experimental standalone SDF conversion and atomic, completed-hull spawning."""
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
import hashlib
import re

from .document import TextDocument
from .diplomacy import unique_section, unique_integer
from .sdf_schema import SCHEMA
from .ship_spawner import _next_hull_id
from .ship_transfers import library, roster, patch_field, positional_value

TYPE_NAMES = {'DD': 'Destroyer', 'BB': 'Battleship', 'BC': 'Battlecruiser',
              'B': 'Pre-Dreadnought', 'CA': 'Heavy Cruiser', 'CL': 'Light Cruiser',
              'CV': 'Aircraft Carrier', 'CVL': 'Light Aircraft Carrier',
              'AV': 'Seaplane Carrier', 'KE': 'Corvette', 'AMC': 'Armed Merchant Cruiser'}
FAMILIES = ('Turret', 'TorpedoMount', 'Equipment', 'Superstructure')


@dataclass
class SDFDesign:
    path: Path
    digest: str
    sections: dict

    @property
    def data(self):
        return self.sections['Data']

    @property
    def ship_type(self):
        return self.data['ShipType']

    def family(self, prefix):
        return [self.sections[key] for key in sorted(
            (k for k in self.sections if re.fullmatch(prefix + r'\d+', k)),
            key=lambda k: int(k[len(prefix):]))]


def read_sdf(path):
    path = Path(path)
    payload = path.read_bytes()
    if len(payload) > 2_000_000:
        raise ValueError('SDF file is too large')
    try:
        text = payload.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = payload.decode('cp1252')
    sections, section = {}, None
    for line in text.splitlines():
        if not line.strip():
            continue
        if line.startswith('[') and line.endswith(']'):
            section = line[1:-1]
            if section in sections:
                raise ValueError(f'Duplicate SDF section: {section}')
            sections[section] = {}
        elif '=' in line and section:
            key, value = line.split('=', 1)
            if key in sections[section]:
                if not (section == 'Data' and key == 'Helipad' and sections[section][key] == value):
                    raise ValueError(f'Duplicate SDF field: {section}/{key}')
            sections[section][key] = value
        else:
            raise ValueError('Unsupported SDF text format')
    for name, fields in sections.items():
        schema_name = next((f + '0' for f in FAMILIES if re.fullmatch(f + r'\d+', name)), name)
        expected = set(SCHEMA.get(schema_name, ()))
        if not expected or set(fields) != expected:
            raise ValueError(f'Unsupported SDF layout in {name}; export the design with the current RTW3 version')
        for key, value in fields.items():
            if any(ord(c) < 32 for c in value):
                raise ValueError(f'Invalid control character in {name}/{key}')
    required = set(SCHEMA) - {f + '0' for f in FAMILIES}
    if not required <= sections.keys():
        raise ValueError('SDF is missing required design sections')
    for prefix in FAMILIES:
        indices = sorted(int(k[len(prefix):]) for k in sections if re.fullmatch(prefix + r'\d+', k))
        if indices != list(range(len(indices))) or len(indices) > 100:
            raise ValueError(f'Invalid {prefix} section numbering')
        if prefix == 'Superstructure' and len(indices) != 6:
            raise ValueError('This importer requires six superstructure sections')
    design = SDFDesign(path, hashlib.sha256(payload).hexdigest(), sections)
    if design.ship_type not in TYPE_NAMES:
        raise ValueError(f'Unsupported ship type: {design.ship_type}')
    for key in ('Displacement', 'Cost', 'Maintenance', 'AircraftCapacity', 'DesignSpeed', 'Speed', 'ASWValue'):
        try:
            value = int(design.data[key])
        except ValueError as exc:
            raise ValueError(f'Invalid {key}') from exc
        if not 0 <= value <= 2147483647 or (key == 'Displacement' and value == 0):
            raise ValueError(f'Invalid {key}')
    return design


def next_series(values, prefix):
    pattern = re.compile(re.escape(prefix) + r' (\d+)$', re.I)
    return max((int(m[1]) for value in values if (m := pattern.fullmatch(value))), default=0) + 1


def import_names(save, nation_index, design, count):
    if type(count) is not int or not 1 <= count <= 100:
        raise ValueError('Choose between 1 and 100 copies')
    nation = save.nation(nation_index)
    prefix = f'Privateer {design.ship_type}'
    number = next_series((s.name for s in nation.ships), prefix)
    class_prefix = TYPE_NAMES[design.ship_type]
    classes = [s.class_name or '' for s in nation.ships] + [d.class_name or '' for d in nation.designs]
    class_name = f'{class_prefix} {next_series(classes, class_prefix)}'
    return [f'{prefix} {i}' for i in range(number, number + count)], class_name


def design_block(design, ordinal, design_id, class_name, nation_index, newline):
    """Serialize the observed current SDF layout to positional v10139.

    Campaign-only metadata uses neutral defaults; no saved hull/template is read.
    Duplicate Helipad is an SDF export artifact. Variable mount counts are explicit.
    """
    data = design.data
    out = [f'ShipDesign{ordinal}', class_name, '0', design.ship_type, str(design_id)]
    seen = set()
    for key in SCHEMA['Data']:
        if key in seen or key in {'ShipType', 'EnemyClassName', 'DeckColor'}:
            continue
        seen.add(key)
        value = data[key]
        if key == 'Name':
            value = class_name
        if key in {'Nation', 'BuildingNation'}:
            value = str(nation_index)
        out.append(value)
    # Campaign-only design metadata follows HighSpottingPos.
    out.extend(['8', '0', '', '-1', '0'])
    for section in ('Weights', 'Armor', 'Guns', 'Torpedoes'):
        out.extend(design.sections[section][key] for key in SCHEMA[section])
    for prefix in ('Turret', 'TorpedoMount', 'Equipment'):
        records = design.family(prefix)
        out.append(str(len(records)))
        for fields in records:
            out.extend(fields[key] for key in SCHEMA[prefix + '0'])
    for section in ('HullPoints', 'Sponsons', 'Funnels'):
        out.extend(design.sections[section][key] for key in SCHEMA[section])
    for fields in design.family('Superstructure'):
        out.extend(fields[key] for key in SCHEMA['Superstructure0'])
    for section in ('SecondaryTurrets', 'TertiaryTurrets'):
        out.extend(design.sections[section][key] for key in SCHEMA[section])
    out.extend([data['DeckColor'], '0', '0', '0'])
    return [value + newline for value in out]


def hull_fields(design, name, class_name, hull_id, design_id, nation_index, home, year):
    data = design.data
    fields = dict.fromkeys(('CrewQuality TimeToRefit Reinforcement TPS RepairTime Side Course Active Training '
        'Deployed Used Mines BattleStars PlayerIntel OldASW Halted Hurry Status OldStatus EAM Rebuild '
        'FCRadarClass SearchRadarClass NumberOfLogEntries MonthlyCost').split(), '0')
    fields.update(Id=str(hull_id), DesignRefId=str(design_id), Name=name, Classname=class_name,
        EnemyClassName=class_name, ShipType=design.ship_type, InPlay='1', Fate='XXX', CommanderId='-1',
        BuildingNationIdx=str(nation_index), LocationAreaName=home, DestinationAreaName='XXX',
        OrderedAreaName='XXX', YearBuilt=str(year), EngineYear=str(year), ObsoleteDate='29994',
        BuildProgress=data['Cost'], MainCalibre=design.sections['Guns']['Main'],
        AccomodationCramped=data['Accomodation'], FuelType=data['Fuel type'], MMP=data['MissileMaintenancePoints'],
        EnemySpeed=data['OSpeed'], EnemyBelt=data['OBelt'])
    for key in ('Displacement', 'ColonialService', 'EnginePriority', 'Mine capacity', 'ASWValue', 'RadarLimit',
                'MSG', 'EnhancedSonar', 'TowedArray', 'AircraftCapacity', 'FlightDeckCatapults', 'JetCapable',
                'AngledFlightDeck', 'Helipad', 'Cost', 'Maintenance', 'Speed', 'Range'):
        fields[key] = data[key]
    fields['CLAA'] = design.sections['Guns']['DP1']
    mounts = design.family('TorpedoMount')
    fields['HSSM'] = str(sum(int(m['Tubes']) for m in mounts if m['MT'] == '4'))
    fields['MSSM'] = '0'
    guns = sum(int(t['Guns']) for t in design.family('Turret'))
    fields['Description'] = f"Guns: {guns} x {fields['MainCalibre']}, {design.sections['Guns']['SecNo']} x {design.sections['Guns']['Secondary']}"
    return fields


def import_sdf(save, design, nation_index, count):
    """Accept a batch in memory only; any error leaves the original save untouched."""
    names, class_name = import_names(save, nation_index, design, count)
    if hashlib.sha256(design.path.read_bytes()).hexdigest() != design.digest:
        raise ValueError('SDF changed since selection; browse to it again')
    if save._source_snapshot != save._folder_snapshot(save.folder):
        raise ValueError('Destination changed on disk; reload the save first')
    save.validate_or_raise()
    working = deepcopy(save)
    nation = working.nation(nation_index)
    home = nation.section.fields().get('BuildAreaName', '').strip()
    if not home or home.casefold() == 'xxx':
        raise ValueError('The receiving nation has no home area')
    section, records, _ = roster(working, nation)
    filename, doc, lines, designs, counter = library(working, nation)
    design_id = max(counter, max((d.internal_design_id for d in designs), default=0)) + 1
    first_id = _next_hull_id(working)
    if max(design_id, first_id + count) > 2147483647:
        raise ValueError('ID allocation exceeds integer range')
    before = {s.record_index: dict(s.section.fields()) for n in working.nations for s in n.ships}
    year = unique_integer(unique_section(working, 'General'), 'Year')
    nl = working.documents[working.main_file].newline
    if section.lines and not section.lines[-1].endswith(('\r', '\n')):
        section.lines[-1] += nl
    expected = {}
    for offset, name in enumerate(names):
        fields = hull_fields(design, name, class_name, first_id + offset, design_id, nation_index, home, year)
        expected[first_id + offset] = fields
        section.lines.extend(f'Ship{len(records) + offset}{key}={value}{nl}' for key, value in fields.items())
    if lines and not lines[-1].endswith(('\r', '\n')):
        lines[-1] += doc.newline
    lines.extend(design_block(design, len(designs), design_id, class_name, nation_index, doc.newline))
    lines[1] = positional_value(lines[1], len(designs) + 1)
    working.documents[filename] = TextDocument.parse(''.join(lines), encoding=doc.encoding, has_bom=doc.has_bom)
    patch_field(nation.section, 'ShipCount', len(records) + count)
    patch_field(nation.section, 'DesignIDCount', design_id)
    patch_field(unique_section(working, 'General'), 'IDNo', first_id + count)
    working.nations = []
    working._build_model()
    working.validate_or_raise()
    roster(working, working.nation(nation_index))
    after = {s.record_index: dict(s.section.fields()) for n in working.nations for s in n.ships}
    if after != {**before, **expected}:
        raise ValueError('SDF hull preservation check failed')
    for document in working.documents.values():
        document.to_bytes()
    working.audit.append(f'Imported {count} completed {design.ship_type} ships from SDF as {class_name}; no aircraft assigned')
    save.documents, save.nations, save.audit = working.documents, working.nations, working.audit
    save.modified = save._ship_changes = True
    return names, class_name
