"""Verified slot-0 player / slots-1..8 AI diplomacy mapping."""
import re
from .document import FIELD

MAX_BASIC_TENSION = 20  # Editor guardrail, not an engine limit.


def unique_section(save, name):
    matches = [s for s in save.documents[save.main_file].sections if s.name.casefold() == name.casefold()]
    if len(matches) != 1:
        raise ValueError(f'Missing or duplicate [{name}] section')
    return matches[0]


def unique_integer(section, key):
    matches = [m for line in section.lines if (m := FIELD.match(line))
               and m.group(2).strip().casefold() == key.casefold()]
    if len(matches) != 1:
        raise ValueError(f'Missing or duplicate {section.name}/{key}')
    raw = matches[0].group(4).strip()
    if not re.fullmatch(r'[+-]?\d+', raw):
        raise ValueError(f'Invalid integer in {section.name}/{key}')
    return int(raw)


class Diplomacy:
    def __init__(self, save):
        self.save = save
        self.sections = {i: unique_section(save, f'Nation{i}') for i in range(9)}
        if [n.index for n in save.nations if n.is_player] != [0] or (save.player_detection_warning or '').startswith('Multiple'):
            raise ValueError('Unsupported diplomacy layout: expected player in Nation0')
        for i in range(1, 9):
            columns = {int(m.group(1)) for key in self.sections[i].fields()
                       if (m := re.fullmatch(r'AITension(\d+)', key, re.I))}
            if columns != set(range(1, 9)):
                raise ValueError(f'Unsupported diplomacy columns in Nation{i}; expected AITension1..8')
            if unique_integer(self.sections[i], f'AITension{i}') != 0:
                raise ValueError(f'Unsupported diplomacy diagonal in Nation{i}')

    def targets(self, a, b, alliance=False):
        if type(a) is not int or type(b) is not int or a not in self.sections or b not in self.sections:
            raise ValueError('Nation slot outside the supported diplomacy layout')
        if a == b:
            raise ValueError('Self-relations cannot be edited')
        if 0 in (a, b):
            return [(self.sections[b if a == 0 else a], 'Allied' if alliance else 'Tension')]
        prefix = 'AIAlliance' if alliance else 'AITension'
        return [(self.sections[a], f'{prefix}{b}'), (self.sections[b], f'{prefix}{a}')]

    def values(self, a, b, alliance=False):
        return tuple(unique_integer(s, k) for s, k in self.targets(a, b, alliance))

    def editable(self, a, b):
        return all(0 <= v <= MAX_BASIC_TENSION for v in self.values(a, b))

    def description(self, a, b):
        values = self.values(a, b)
        lines = [f'{s.name}/{k} = {v}' for (s, k), v in zip(self.targets(a, b), values)]
        if len(set(values)) > 1:
            lines.append('Reciprocal values differ. Editing this pair sets both to the chosen value.')
        if not self.editable(a, b):
            lines.append('Outside the basic editor range; preserved. War/peace transitions are separate operations.')
        if 0 in (a, b) and values == (50,):
            try:
                war = unique_integer(unique_section(self.save, 'General'), 'War')
            except ValueError:
                war = None
            lines.append('Matches the documented wartime pattern (raw 50, General/War=1).'
                         if war == 1 else 'Raw 50 is war-associated; full status is not decoded.')
        try:
            lines.append('Alliance values (read-only; meaning unconfirmed): ' +
                         ' / '.join(map(str, self.values(a, b, alliance=True))))
        except ValueError as exc:
            lines.append(f'Alliance data unavailable: {exc}')
        return '\n'.join(lines)


def set_tensions(save, changes):
    diplomacy = Diplomacy(save)
    writes, pairs = [], set()
    for pair, value in changes.items():
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise ValueError('Tension changes require a pair of nation slots')
        a, b = pair
        targets = diplomacy.targets(a, b)
        canonical = tuple(sorted(pair))
        if canonical in pairs:
            raise ValueError('Duplicate relationship in tension changes')
        pairs.add(canonical)
        if type(value) is not int or not 0 <= value <= MAX_BASIC_TENSION:
            raise ValueError('Basic tension edits accept integers 0-20 (editor guardrail, not an engine limit)')
        if not diplomacy.editable(a, b):
            raise ValueError('War-associated or out-of-range relationships are read-only')
        for section, key in targets:
            old = unique_integer(section, key)
            if old != value:
                writes.append((section, key, old, value))
    with save.transaction():
        for section, key, old, value in writes:
            for index, line in enumerate(section.lines):
                m = FIELD.match(line)
                if m and m.group(2).strip().casefold() == key.casefold():
                    start, end = m.span(4)
                    section.lines[index] = line[:start] + re.sub(r'[+-]?\d+', str(value), m.group(4), count=1) + line[end:]
                    break
            if unique_integer(section, key) != value:
                raise ValueError(f'Failed to verify {section.name}/{key}')
            save.audit.append(f'Changed {section.name} {key}: {old} -> {value}')
        if writes:
            save.modified = True
    if writes:
        save._tension_changes = True
