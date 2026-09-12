from dataclasses import dataclass
from pathlib import Path
import re

DEFAULT_DATABASE = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Rule the Waves 3\Data\ResearchAreas3.dat')

@dataclass(frozen=True)
class TechnologyDefinition:
    area: int
    area_name: str
    level: int
    name: str
    year: int | None
    internal_id: int
    description: str
    raw_fields: tuple[str, ...]

    @property
    def key(self):
        return f'Research{self.area}Level{self.level}'


def load_database(path):
    """Levels are zero-based row positions within each area, not internal IDs."""
    payload = Path(path).read_bytes()
    try:
        text = payload.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = payload.decode('cp1252')
    result = []
    area = None
    seen = set()
    for line_number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith((';', '#', '//')):
            continue
        header = re.fullmatch(r'\[(.+?)\s+(\d+)\]', line)
        if header:
            area_name, area = header.group(1), int(header.group(2))
            if area in seen:
                raise ValueError(f'Duplicate research area {area}')
            seen.add(area)
            level = 0
            continue
        if '=' in line and ';' not in line:
            continue
        fields = tuple(part.strip() for part in line.split(';'))
        if area is None or len(fields) < 7:
            raise ValueError(f'Unsupported technology data at line {line_number}')
        try:
            year = int(fields[1]) if fields[1] else None
            internal_id = int(fields[5])
        except ValueError as exc:
            raise ValueError(f'Invalid technology data at line {line_number}') from exc
        result.append(TechnologyDefinition(area, area_name, level, fields[0], year,
                                           internal_id, fields[6], fields))
        level += 1
    if not result:
        raise ValueError('No technologies found in ResearchAreas3.dat')
    return result

class AreaTechnologyEdits:
    """Stage cumulative area levels; opening the editor never fills save gaps."""
    def __init__(self, database, fields):
        self.original = dict(fields)
        self.areas = {}
        for tech in database:
            self.areas.setdefault(tech.area, []).append(tech)
        for technologies in self.areas.values():
            technologies.sort(key=lambda tech: tech.level)
        self.selected = {}
        self.pending = {}

    def editable(self, area):
        return all(self.original.get(t.key) in ('0', '1') for t in self.areas[area])

    def current(self, area):
        if area in self.selected:
            return self.selected[area]
        return max((i for i, t in enumerate(self.areas[area], 1)
                    if self.original.get(t.key) == '1'), default=0)

    def mixed(self, area):
        return area not in self.selected and any(
            self.original.get(t.key) != '1' for t in self.areas[area][:self.current(area)])

    def set_level(self, area, level):
        technologies = self.areas[area]
        if type(level) is not int or not 0 <= level <= len(technologies):
            raise ValueError('Technology level is outside this research area')
        if not self.editable(area):
            raise ValueError('This area has missing or invalid save fields')
        self.selected[area] = level
        for i, tech in enumerate(technologies, 1):
            value = int(i <= level)
            if str(value) == self.original[tech.key]:
                self.pending.pop(tech.key, None)
            else:
                self.pending[tech.key] = value

    def reset(self):
        self.selected.clear()
        self.pending.clear()
