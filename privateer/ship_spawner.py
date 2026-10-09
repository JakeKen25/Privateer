"""Atomic cross-campaign copies of flattened hulls and positional designs."""
from copy import deepcopy
from pathlib import Path
import re

from .document import FIELD, TextDocument
from .diplomacy import unique_integer, unique_section
from .ship_transfers import library, patch_field, positional_value, roster, SHIP_KEY, replace_line_value
from .ships_gui import transfer_block_reason


def copy_block_reason(ship):
    reason = transfer_block_reason(ship)
    return reason.replace('transferred', 'copied').replace('transfers', 'copies') if reason else None


def _next_hull_id(save):
    counter = unique_integer(unique_section(save, 'General'), 'IDNo')
    if counter < 0:
        raise ValueError('Invalid destination ID counter')
    documents = list(save.documents.values())
    officer_path = save.folder / Path(save.main_file).with_suffix('.off').name
    if not officer_path.is_file():
        raise ValueError('The destination officer file is required to check ID allocation')
    payload = officer_path.read_bytes()
    try:
        text = payload.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = payload.decode('cp1252')
    documents.append(TextDocument.parse(text))
    ids = [int(value) for doc in documents for section in doc.sections
           for key, value in section.fields().items()
           if 'id' in key.casefold() and re.fullmatch(r'\d+', value)]
    return max(counter, max(ids, default=0) + 1)


def copy_ships(target, source, hull_ids, nation_index):
    """Copy one of each selected hull; never modify or save the source campaign."""
    hull_ids = list(hull_ids)
    if not hull_ids:
        return []
    if source is target or source.folder.resolve() == target.folder.resolve():
        raise ValueError('Choose a different source campaign folder')
    if len(hull_ids) != len(set(hull_ids)):
        raise ValueError('A ship can only be selected once per batch')
    source.validate_or_raise()
    target.validate_or_raise()
    if source._source_snapshot != source._folder_snapshot(source.folder):
        raise ValueError('Source files changed since loading; browse to the source again')
    if target._source_snapshot != target._folder_snapshot(target.folder):
        raise ValueError('Destination files changed since loading; reload before copying')
    working = deepcopy(target)
    nation = working.nation(nation_index)
    home = nation.section.fields().get('BuildAreaName', '').strip()
    if not home or home.casefold() == 'xxx':
        raise ValueError('The destination nation has no home area')
    section, records, _ = roster(working, nation)
    filename, doc, lines, designs, counter = library(working, nation)
    next_id = _next_hull_id(working)
    if next_id + len(hull_ids) > 2147483647:
        raise ValueError('Hull ID allocation exceeds integer range')
    ships = {s.record_index: s for n in source.nations for s in n.ships}
    before = {s.record_index: (n.index, dict(s.section.fields()))
              for n in working.nations for s in n.ships}
    source_rosters, source_libraries = {}, {}
    blocks, design_map, expected, manifest = [], {}, {}, []
    names = {s.name.casefold() for s in nation.ships}
    design_counter = max(counter, max((d.internal_design_id for d in designs), default=0))
    for offset, hull in enumerate(hull_ids):
        if type(hull) is not int or hull not in ships:
            raise ValueError('Choose an existing source hull ID')
        ship = ships[hull]
        if not ship.flattened_record:
            raise ValueError('Only flattened ship rosters are supported')
        if reason := copy_block_reason(ship):
            raise ValueError(f'{ship.name}: {reason}')
        owner = source.nation(ship.owner_index)
        if owner.index not in source_rosters:
            source_rosters[owner.index] = roster(source, owner)
            source_libraries[owner.index] = library(source, owner)
        builder = nation.index
        key = (owner.index, ship.design_ref_id)
        if key not in design_map:
            matches = [d for d in source_libraries[owner.index][3]
                       if d.internal_design_id == ship.design_ref_id]
            if len(matches) != 1:
                raise ValueError(f'{ship.name}: missing or ambiguous source design')
            design_counter += 1
            if design_counter > 2147483647:
                raise ValueError('Design ID allocation exceeds integer range')
            block = list(matches[0].positional_record)
            block[0] = positional_value(block[0], f'ShipDesign{len(designs) + len(blocks)}')
            block[4] = positional_value(block[4], design_counter)
            blocks.append(block)
            design_map[key] = design_counter
        name = ship.name
        suffix = 2
        while name.casefold() in names:
            name = f'{ship.name} (copy {suffix})'
            suffix += 1
        names.add(name.casefold())
        edits = {'Id': str(next_id + offset), 'DesignRefId': str(design_map[key]),
                 'BuildingNationIdx': str(builder), 'CommanderId': '-1', 'Name': name,
                 'LocationAreaName': home, 'DestinationAreaName': 'XXX', 'OrderedAreaName': 'XXX'}
        fields = dict(ship.section.fields())
        if not edits.keys() <= fields.keys():
            raise ValueError(f'{ship.name}: missing required copy fields')
        for line in source_rosters[owner.index][1][ship.local_slot]:
            match = FIELD.match(line)
            field = SHIP_KEY.fullmatch(match.group(2).strip()).group(2)
            if field in edits:
                line = replace_line_value(line, edits[field])
                match = FIELD.match(line)
            start, end = match.span(2)
            line = line[:start] + f'Ship{len(records) + offset}{field}' + line[end:]
            if section.lines and not section.lines[-1].endswith(('\n', '\r')):
                section.lines[-1] += working.documents[working.main_file].newline
            section.lines.append(line)
        expected[next_id + offset] = (nation.index, dict(fields, **edits))
        manifest.append({'source_id': hull, 'id': next_id + offset, 'name': name})
    patch_field(nation.section, 'ShipCount', len(records) + len(hull_ids))
    patch_field(nation.section, 'DesignIDCount', design_counter)
    patch_field(unique_section(working, 'General'), 'IDNo', next_id + len(hull_ids))
    lines[1] = positional_value(lines[1], len(designs) + len(blocks))
    for block in blocks:
        if lines and not lines[-1].endswith(('\n', '\r')):
            lines[-1] += doc.newline
        lines.extend(block)
    working.documents[filename] = TextDocument.parse(''.join(lines), encoding=doc.encoding, has_bom=doc.has_bom)
    working.nations = []
    working._build_model()
    working.validate_or_raise()
    roster(working, working.nation(nation_index))
    after = {s.record_index: (n.index, dict(s.section.fields()))
             for n in working.nations for s in n.ships}
    if after != {**before, **expected}:
        raise ValueError('Copied hull preservation check failed')
    for document in working.documents.values():
        document.to_bytes()
    working.audit.append(f'Copied {len(manifest)} ships from {source.folder} to {nation.name}; source unchanged')
    target.documents, target.nations, target.audit = working.documents, working.nations, working.audit
    target.modified = True
    target._ship_changes = True
    return manifest
