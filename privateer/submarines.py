"""Campaign submarine inventory and construction from observed saved templates."""
from dataclasses import dataclass
import re

from .document import FIELD, Section


SUBMARINE_TYPES = {
    '0': 'SS — Submarine',
    '1': 'SSM — Minelaying submarine',
    '2': 'SSC — Coastal submarine',
    '3': 'SSL — Long range submarine',
    '4': 'SSG — Missile submarine',
}


@dataclass(frozen=True)
class Submarine:
    slot: int
    fields: dict[str, str]

    @property
    def status(self):
        f = self.fields
        fate = f.get('Fate', '').strip()
        if f.get('Sunk') == '1':
            return 'Sunk'
        if fate.casefold() not in ('', 'xxx'):
            return 'Historical'
        if f.get('Sunk') not in ('0', '1'):
            return 'Unknown'
        if f.get('InPlay') == '0':
            if f.get('Halted') == '1':
                return 'Construction halted'
            return 'Under construction' if f.get('Halted') == '0' else 'Unknown'
        if f.get('InPlay') == '1':
            return 'In service'
        return 'Unknown'

    @property
    def type_label(self):
        value = self.fields.get('SubType', '')
        return SUBMARINE_TYPES.get(value, f'Unverified type ({value or "missing"})')

    def value(self, column):
        if column == 'slot':
            return self.slot
        if column == 'status':
            return self.status
        if column == 'type':
            return self.type_label
        return self.fields.get(column, '')


def submarine_roster(save, nation_index):
    """Return records plus layout warnings without touching the document."""
    name = f'Nation{nation_index}Submarines'
    sections = [s for s in save.documents[save.main_file].sections if s.name.casefold() == name.casefold()]
    if not sections:
        return (), (f'[{name}] is missing; this is not a confirmed empty roster.',)
    if len(sections) != 1:
        raise ValueError(f'Duplicate [{name}] sections; submarine inventory is ambiguous.')
    section = sections[0]
    seen = set()
    for line in section.lines:
        match = FIELD.match(line)
        if match:
            key = match.group(2).strip().casefold()
            if key in seen:
                raise ValueError(f'Duplicate submarine field: {key}')
            seen.add(key)
    grouped = {}
    for key, value in section.fields().items():
        match = re.fullmatch(r'Sub(\d+)(\D.+)', key)
        if match:
            grouped.setdefault(int(match[1]), {})[match[2]] = value
    records = tuple(Submarine(slot, fields) for slot, fields in sorted(grouped.items()))
    warnings = []
    try:
        count = int(section.fields()['SubCount'])
        if count != len(records) or sorted(grouped) != list(range(count)):
            warnings.append('SubCount or slot sequence differs from parsed records; all parsed entries are retained.')
    except (KeyError, ValueError):
        warnings.append('SubCount is missing or invalid; all parsed entries are retained.')
    return records, tuple(warnings)


# Completed Game6 references, S-120 through S-125, inspected 2026-10-08.
# Only reusable type/stat values are bundled, never save identities or locations.
SUBMARINE_REFERENCES = {
    'SSC': ('2', '135', '0', 'SSC — Coastal submarine'),
    'SS': ('0', '135', '0', 'SS — Submarine'),
    'SSM-122': ('1', '135', '1', 'SSM — Minelaying submarine (S-122 reference)'),
    'SSM-123': ('1', '135', '0', 'SSM — Minelaying submarine (S-123 reference)'),
    'SSL': ('3', '135', '0', 'SSL — Long range submarine'),
    'SSG': ('4', '135', '1', 'SSG — Missile submarine'),
}


def create_submarine(save, nation_index, *, submarine_type, name, location):
    """Append a completed same-nation submarine at an observed service location."""
    nation = save.nation(nation_index)
    records, warnings = submarine_roster(save, nation.index)
    missing_roster = not any(sec.name.casefold() == f'nation{nation.index}submarines'
                             for sec in save.documents[save.main_file].sections)
    if warnings and not missing_roster:
        raise ValueError('Cannot create submarines with an incomplete or inconsistent roster.')
    name = name.strip()
    if not name or any(ord(c) < 32 for c in name) or any(c in name for c in '=[]'):
        raise ValueError('Enter a name without control characters, brackets or equals signs.')
    if any(r.fields.get('Name', '').casefold() == name.casefold() for r in records):
        raise ValueError('A submarine with this name already exists in this nation.')
    if submarine_type not in SUBMARINE_REFERENCES:
        raise ValueError('Select a supported submarine type.')
    kind, availability, accuracy, label = SUBMARINE_REFERENCES[submarine_type]
    fields = dict(SubType=kind, Availability=availability, Accuracy=accuracy)
    if location not in spawn_locations(save, nation.index):
        raise ValueError('Select a valid home or submarine service location for this nation.')
    document = save.documents[save.main_file]
    generals = [s for s in document.sections if s.name.casefold() == 'general']
    try:
        if len(generals) != 1:
            raise ValueError()
        year = int(generals[0].fields()['Year'])
        if not 1 <= year <= 9999:
            raise ValueError()
    except (KeyError, ValueError) as error:
        raise ValueError('Campaign year is missing or invalid.') from error
    nations = [s for s in document.sections if s.name.casefold() == f'nation{nation.index}']
    if len(nations) != 1:
        raise ValueError('Nation section is missing or ambiguous.')
    counter_lines = [FIELD.match(line) for line in nations[0].lines]
    counter_values = [m.group(4).strip() for m in counter_lines
                      if m and m.group(2).strip().casefold() == 'subnumber']
    try:
        if len(counter_values) != 1:
            raise ValueError()
        counter = int(counter_values[0])
        if not 0 <= counter < 2**31 - 1:
            raise ValueError()
    except ValueError as error:
        raise ValueError('Nation SubNumber counter is missing or invalid.') from error
    section = next((s for s in document.sections
                    if s.name.casefold() == f'nation{nation.index}submarines'), None)
    fields.update(Name=name, Fate='', YearBuilt=str(year), RemainingBuildTime='0', Halted='0', Sunk='0',
                  Active='0', InPlay='1', DestinationAreaName='XXX', OrderedAreaName='XXX')
    fields['LocationAreaName'] = location
    slot = len(records)
    with save.transaction():
        if section is None:
            section = Section(f'Nation{nation.index}Submarines',
                              f'[Nation{nation.index}Submarines]{document.newline}')
            document.add_section(section)
        if section.lines and not section.lines[-1].endswith(('\n', '\r')):
            section.lines[-1] += document.newline
        for key, value in fields.items():
            section.set(f'Sub{slot}{key}', value, document.newline)
        section.set('SubCount', slot + 1, document.newline)
        nations[0].set('SubNumber', counter + 1, document.newline)
        save.modified = True
        save.audit.append(f'Spawned {name} ({SUBMARINE_TYPES[fields["SubType"]]}) for '
                          f'{nation.name} using Game6 reference {submarine_type}')
    return Submarine(slot, fields)


def spawn_locations(save, nation_index):
    records, _ = submarine_roster(save, nation_index)
    locations = {r.fields['LocationAreaName'] for r in records
                 if r.status == 'In service' and
                 r.fields.get('LocationAreaName', '').strip() not in ('', 'XXX')}
    home = save.nation(nation_index).section.fields().get('BuildAreaName', '').strip()
    if home and home != 'XXX':
        locations.add(home)
    return tuple(sorted(locations))


def next_submarine_name(save, nation_index):
    """First unused positive Privateer number, including historical names."""
    records, _ = submarine_roster(save, nation_index)
    used = {r.fields.get('Name', '').strip().casefold() for r in records}
    number = 1
    while f'privateer {number}' in used:
        number += 1
    return f'Privateer {number}'
