"""Read-only campaign submarine inventory; local slots are not permanent IDs."""
from dataclasses import dataclass
import re

from .document import FIELD


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
        return 'Long range (3)' if value == '3' else f'Unverified type ({value or "missing"})'

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
