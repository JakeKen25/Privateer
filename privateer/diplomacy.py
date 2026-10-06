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

    def status(self, a, b):
        """Summarize a pair without concealing asymmetric or conflicting records."""
        tensions = self.values(a, b)
        alliances = self.values(a, b, alliance=True)
        war = all(v == 50 for v in tensions)
        if 0 in (a, b):
            war = war and unique_integer(unique_section(self.save, 'General'), 'War') > 0
        allied = all(v > 0 for v in alliances)
        if war and allied:
            return 'War / Allied (conflict)'
        if len(set(tensions)) > 1 or len(set(alliances)) > 1:
            return 'Mixed relations'
        if war:
            return 'War'
        if allied:
            return 'Allied'
        if any(v < 0 or v > MAX_BASIC_TENSION for v in tensions) or any(v < 0 for v in alliances):
            return 'Special state'
        return 'Peace'

    def matrix_cell(self, a, b):
        """Display row-to-column values; retain directional AI differences."""
        if a == b:
            return '—'
        try:
            tension = self.values(a, b)[0]
            alliance = self.values(a, b, alliance=True)[0]
            war = tension == 50
            if 0 in (a, b):
                war = war and unique_integer(unique_section(self.save, 'General'), 'War') > 0
            labels = []
            if war:
                labels.append('War')
            if alliance > 0:
                labels.append('Allied')
            if labels:
                return f'{tension} · ' + ' / '.join(labels)
            return str(tension)
        except ValueError:
            return 'Unknown'

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
            lines.append('At war (tension 50 and positive war counter).'
                         if war is not None and war > 0 else 'Raw 50 is war-associated; full status is not decoded.')
        try:
            lines.append('Alliance values (60 observed; duration unconfirmed): ' +
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


RELATION_ACTIONS = ('Create Alliance', 'Break Treaty', 'Reset Tension to 0', 'Start War', 'Ceasefire')


def relation_plan(save, a, b, action):
    """Validate an action and return exact writes without mutation."""
    d = Diplomacy(save)
    targets = d.targets(a, b)
    if action not in RELATION_ACTIONS:
        raise ValueError('Unknown relationship action')
    if action == 'Reset Tension to 0':
        if not d.editable(a, b):
            raise ValueError('Use Ceasefire for active war; special tensions cannot be reset')
        writes = [(s, k, 0) for s, k in targets]
    elif action in ('Create Alliance', 'Break Treaty'):
        if action == 'Create Alliance' and not d.editable(a, b):
            raise ValueError('Cannot ally with a war-associated opponent')
        writes = [(s, k, 60 if action == 'Create Alliance' else 0) for s, k in d.targets(a, b, True)]
    else:
        if 0 not in (a, b):
            raise ValueError('War and ceasefire support player relationships only')
        general = unique_section(save, 'General')
        war = unique_integer(general, 'War')
        opponents = [i for i in range(1, 9) if d.values(0, i) == (50,)]
        if action == 'Start War':
            if war > 0 or opponents or not d.editable(a, b):
                raise ValueError('Start War requires peace and no existing war-associated opponents')
            if any(d.values(a, b, True)):
                raise ValueError('Break Treaty before starting war with this nation')
            writes = [(general, 'War', 1), (targets[0][0], targets[0][1], 50)]
        else:
            if war <= 0 or opponents != [b if a == 0 else a]:
                raise ValueError('Ceasefire requires exactly one matching active player opponent')
            writes = [(general, 'War', -1), (targets[0][0], targets[0][1], 3),
                      (d.sections[0], 'VP', 0), (general, 'EnemyVP', 0)]
    return [(s, k, unique_integer(s, k), v) for s, k, v in writes]


def apply_relations(save, tensions, actions):
    """Preflight the dialog batch before atomic in-memory application."""
    from copy import deepcopy
    pairs = set()
    for pair in list(tensions) + list(actions):
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise ValueError('Choose a pair of nation slots')
        Diplomacy(save).targets(*pair)
        canonical = tuple(sorted(pair))
        if canonical in pairs:
            raise ValueError('Choose either a tension edit or an action for each pair')
        pairs.add(canonical)
    if sum(a in ('Start War', 'Ceasefire') for a in actions.values()) > 1:
        raise ValueError('Apply one war or ceasefire operation at a time')
    def apply(target):
        set_tensions(target, tensions)
        for (a, b), action in actions.items():
            for section, key, old, value in relation_plan(target, a, b, action):
                if old == value:
                    continue
                section.set(key, value)
                if unique_integer(section, key) != value:
                    raise ValueError('Relationship write verification failed')
                target.audit.append(f'{action}: {section.name}/{key}: {old} -> {value}')
                target.modified = True
                target._tension_changes = True
    apply(deepcopy(save))
    with save.transaction():
        apply(save)
