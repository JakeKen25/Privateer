"""MapData possession ownership, keyed by map area and possession slot."""
from dataclasses import dataclass
import re
from .document import FIELD


MAP_AREA_NAMES = (
    'Northern Europe',
    'The Mediterranean',
    'West Africa',
    'Indian Ocean',
    'Southeast Asia',
    'Northeast Asia',
    'North American East Coast',
    'The Caribbean',
    'North American West Coast',
    'South American East Coast',
    'South American West Coast (no colonies)',
    'South Pacific',
    'Southern Africa',
    'Central Pacific',
    'Northern Pacific',
    'The Baltic',
)
_AREA_BY_NAME = {name.casefold(): index for index, name in enumerate(MAP_AREA_NAMES)}


def map_area_name(area):
    """Return the game's display name while remaining safe for future area IDs."""
    if type(area) is int and 0 <= area < len(MAP_AREA_NAMES):
        return MAP_AREA_NAMES[area]
    return f'Unknown map area ({area})'


def nation_home_areas(save):
    """Return each nation's canonical home area from its saved BuildAreaName."""
    result = {}
    for nation in save.nations:
        fields = {key.casefold(): value.strip() for key, value in nation.section.fields().items()}
        raw_name = fields.get('buildareaname', '')
        area = _AREA_BY_NAME.get(raw_name.casefold())
        result[nation.name] = area
    return result


def is_home_area_possession(save, possession):
    """Whether the current owner holds this possession in its saved home area."""
    return nation_home_areas(save).get(possession.owner) == possession.area


@dataclass(frozen=True)
class Possession:
    area: int
    index: int
    name: str
    owner: str
    value: str
    oil: str
    base: str

    @property
    def key(self):
        return f'MapArea{self.area}Possession{self.index}Owner'


def map_document(save):
    match = re.fullmatch(r'RTWGame(\d+)\.bcs', save.main_file, re.I)
    if not match:
        raise ValueError('Colony editing requires a numbered RTWGameX.bcs campaign.')
    expected = f'MapData{match.group(1)}.dat'
    matches = [(name, doc) for name, doc in save.documents.items() if name.casefold() == expected.casefold()]
    if len(matches) != 1:
        raise ValueError(f'Missing or ambiguous {expected} for this campaign.')
    filename, document = matches[0]
    sections = [s for s in document.sections if s.name.casefold() == 'mapareas']
    if len(sections) != 1:
        raise ValueError(f'Missing or duplicate [MapAreas] in {filename}')
    return filename, document, sections[0]


def possessions(save):
    _, _, section = map_document(save)
    fields = {}
    for line in section.lines:
        m = FIELD.match(line)
        if not m:
            continue
        key = m.group(2).strip().casefold()
        if key in fields and key.startswith('maparea'):
            raise ValueError(f'Duplicate map field: {m.group(2).strip()}')
        fields[key] = m.group(4).strip()

    def required(key):
        value = fields.get(key.casefold())
        if value is None or not value:
            raise ValueError(f'Missing map field: {key}')
        return value

    def count(key):
        raw = required(key)
        if not re.fullmatch(r'\d+', raw) or not 0 <= int(raw) <= 10000:
            raise ValueError(f'Invalid map count: {key}')
        return int(raw)

    result = []
    expected = set()
    for area in range(count('MapAreaCount')):
        for index in range(count(f'MapArea{area}PossessionCount')):
            prefix = f'MapArea{area}Possession{index}'
            result.append(Possession(area, index, required(prefix+'Name'), required(prefix+'Owner'),
                                     fields.get((prefix+'Value').lower(), '?'),
                                     fields.get((prefix+'Oil').lower(), '?'),
                                     fields.get((prefix+'BaseValue').lower(), '?')))
            expected.add((area, index))
    observed = {(int(m.group(1)), int(m.group(2))) for key in fields
                if (m := re.fullmatch(r'maparea(\d+)possession(\d+)(?:owner|name)', key))}
    if observed != expected:
        raise ValueError('Possession records do not match declared map counts')
    return result


def set_owners(save, changes):
    filename, document, section = map_document(save)
    records = {(p.area, p.index): p for p in possessions(save)}
    names = [n.name for n in save.nations]
    if len(names) != len(set(names)):
        raise ValueError('Ambiguous nation names in save')
    owners = set(names) | {'Neutral'}
    writes = []
    for pair, owner in changes.items():
        if not isinstance(pair, tuple) or len(pair) != 2 or any(type(i) is not int for i in pair) or pair not in records:
            raise ValueError('Unknown possession')
        if not isinstance(owner, str) or owner not in owners or any(c in owner for c in '\r\n'):
            raise ValueError('Choose a nation from the loaded save or Neutral')
        possession = records[pair]
        if possession.owner != owner:
            if is_home_area_possession(save, possession):
                raise ValueError(
                    f'{possession.name} is in {possession.owner}\'s home area '
                    f'({map_area_name(possession.area)}) and cannot be transferred'
                )
            writes.append((possession, owner))
    with save.transaction():
        for possession, owner in writes:
            for index, line in enumerate(section.lines):
                m = FIELD.match(line)
                if m and m.group(2).strip().casefold() == possession.key.casefold():
                    raw = m.group(4)
                    leading = raw[:len(raw)-len(raw.lstrip())]
                    trailing = raw[len(raw.rstrip()):]
                    start, end = m.span(4)
                    section.lines[index] = line[:start] + leading + owner + trailing + line[end:]
                    break
            save.audit.append(f'Changed {filename} {possession.name} ({map_area_name(possession.area)}/{possession.index}) owner: {possession.owner} -> {owner}')
        actual = {(p.area, p.index): p.owner for p in possessions(save)}
        if any(actual[(p.area, p.index)] != owner for p, owner in writes):
            raise ValueError('Ownership verification failed')
        if writes:
            save.modified = True
    if writes:
        save._colony_changes = True
