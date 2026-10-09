from copy import deepcopy
from pathlib import Path
import shutil

import pytest

from privateer.save import RTW3Save
from privateer.ship_spawner import copy_ships
from privateer.diplomacy import unique_section


EXAMPLE = Path(__file__).parents[1] / 'developmentResources/exampleSaves/Game5'


@pytest.fixture
def campaigns(tmp_path):
    shutil.copytree(EXAMPLE, tmp_path / 'source')
    shutil.copytree(EXAMPLE, tmp_path / 'target')
    return RTW3Save.load(tmp_path / 'source'), RTW3Save.load(tmp_path / 'target')


def payloads(save):
    return {name: doc.to_bytes() for name, doc in save.documents.items()}


def test_copy_preserves_source_and_existing_hulls_roundtrip(campaigns, tmp_path):
    source, target = campaigns
    ship = source.nation(0).ships[0]
    old_source, old_target = payloads(source), payloads(target)
    existing = {s.record_index: dict(s.section.fields()) for n in target.nations for s in n.ships}
    # Copies use the receiver even when nation slots differ.
    target.nation(0).section.set('Name', source.nation(1).name)
    target.nation(1).section.set('Name', source.nation(0).name)
    target.nations = []
    target._build_model()
    source_fields = dict(ship.section.fields())
    result = copy_ships(target, source, [ship.record_index], 0)
    added = next(s for s in target.nation(0).ships if s.record_index == result[0]['id'])
    fields = added.section.fields()
    assert fields['BuildingNationIdx'] == '0'
    assert fields['CommanderId'] == '-1'
    assert fields['LocationAreaName'] == target.nation(0).section.fields()['BuildAreaName']
    assert fields['DestinationAreaName'] == fields['OrderedAreaName'] == 'XXX'
    assert added.name.endswith('(copy 2)')
    changed = {'Id', 'DesignRefId', 'Name', 'BuildingNationIdx', 'CommanderId',
               'LocationAreaName', 'DestinationAreaName', 'OrderedAreaName'}
    assert {k: v for k, v in fields.items() if k not in changed} == {
        k: v for k, v in source_fields.items() if k not in changed}
    assert payloads(source) == old_source
    assert source._folder_snapshot(source.folder) == source._source_snapshot
    assert target._folder_snapshot(target.folder) == target._source_snapshot
    assert set(name for name, doc in payloads(target).items() if doc != old_target[name]) == {
        target.main_file, 'DesignFiles0.des'}
    output = target.save_as(tmp_path / 'output')
    reloaded = RTW3Save.load(output)
    reloaded.validate_or_raise()
    after = {s.record_index: dict(s.section.fields()) for n in reloaded.nations for s in n.ships}
    assert all(after[h] == f for h, f in existing.items())
    assert after[added.record_index] == fields
    assert int(unique_section(reloaded, 'General').fields()['IDNo']) > added.record_index


def test_shared_design_copied_once_and_repeated_copies_get_unique_ids(campaigns):
    source, target = campaigns
    groups = {}
    for s in source.nation(1).ships:
        groups.setdefault(s.design_ref_id, []).append(s)
    ships = next(g for g in groups.values() if len(g) >= 2)
    original = next(d for d in source.nation(1).designs if d.internal_design_id == ships[0].design_ref_id)
    count = len(target.nation(0).designs)
    first = copy_ships(target, source, [s.record_index for s in ships[:2]], 0)
    assert len(target.nation(0).designs) == count + 1
    block = target.nation(0).designs[-1].positional_record
    assert [v for i, v in enumerate(block) if i not in (0, 4)] == [v for i, v in enumerate(original.positional_record) if i not in (0, 4)]
    second = copy_ships(target, source, [ships[0].record_index], 0)
    assert second[0]['id'] not in {m['id'] for m in first}
    assert second[0]['name'].endswith('(copy 2)')


def test_construction_state_and_assigned_commander(campaigns):
    source, target = campaigns
    ship = next(s for s in source.nation(1).ships if s.under_construction)
    ship.section.set('CommanderId', 98765)
    fields = dict(ship.section.fields())
    result = copy_ships(target, source, [ship.record_index], 0)
    copied = next(s for s in target.nation(0).ships if s.record_index == result[0]['id'])
    assert copied.under_construction
    assert copied.section.fields()['CommanderId'] == '-1'
    for key in ('BuildProgress', 'Cost', 'MonthlyCost', 'Maintenance', 'Halted', 'Hurry'):
        assert copied.section.fields()[key] == fields[key]


@pytest.mark.parametrize('problem', ['carrier', 'overflow', 'duplicate', 'missing', 'source_changed'])
def test_rejected_batch_leaves_target_unchanged(campaigns, problem):
    source, target = campaigns
    ships = source.nation(1).ships[:2]
    ids = [s.record_index for s in ships]
    if problem == 'carrier':
        ships[1].section.set('AircraftCapacity', 20)
    elif problem == 'overflow':
        unique_section(target, 'General').set('IDNo', 2147483647)
    elif problem == 'duplicate':
        ids = [ids[0], ids[0]]
    elif problem == 'missing':
        ids.append(999999)
    elif problem == 'source_changed':
        (source.folder / 'changed.txt').write_text('changed')
    before = payloads(target)
    with pytest.raises((ValueError, KeyError)):
        copy_ships(target, source, ids, 0)
    assert payloads(target) == before
    assert not target.modified


def test_same_folder_refused(campaigns):
    source, _ = campaigns
    with pytest.raises(ValueError, match='different source'):
        copy_ships(source, deepcopy(source), [source.nation(0).ships[0].record_index], 0)


def test_copy_uses_receiver_when_source_builder_is_absent(campaigns):
    source, target = campaigns
    ship = source.nation(1).ships[0]
    source.nation(1).name = 'Nation absent from destination'
    original_builder = ship.section.fields()['BuildingNationIdx']
    result = copy_ships(target, source, [ship.record_index], 2)
    copied = next(s for s in target.nation(2).ships if s.record_index == result[0]['id'])
    assert copied.section.fields()['BuildingNationIdx'] == '2'
    assert ship.section.fields()['BuildingNationIdx'] == original_builder
