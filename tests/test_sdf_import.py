from pathlib import Path
import shutil

import pytest

from privateer.sdf_import import read_sdf, import_sdf, import_names, design_block
from privateer.sdf_schema import SCHEMA
from privateer.save import RTW3Save

EXAMPLE = Path(__file__).parents[1] / 'developmentResources/exampleSaves/Game5'


def write_design(path, ship_type='CL', mounts=2):
    """Synthetic design only: no installed game data in the test suite."""
    sections = {}
    for name, keys in SCHEMA.items():
        names = ([f'Superstructure{i}' for i in range(6)] if name == 'Superstructure0'
                 else [f'Turret{i}' for i in range(mounts)] if name == 'Turret0' else [name])
        for n in names:
            sections[n] = {key: '0' for key in keys}
    sections['Data'].update(ShipType=ship_type, Name='Synthetic', Displacement='12000', Cost='70000',
                            Maintenance='350', AircraftCapacity='1', Helipad='1', Speed='35', DesignSpeed='35',
                            LAA='7', MAA='9', DeckColor='clBlack')
    sections['Guns'].update(Main='6', Secondary='3', SecNo='4')
    for i in range(mounts):
        sections[f'Turret{i}']['Guns'] = '2'
    path.write_text('\n'.join(f'[{n}]\n' + '\n'.join(f'{k}={v}' for k,v in fields.items())
                              for n, fields in sections.items()), encoding='utf-8')
    return read_sdf(path)


@pytest.fixture
def target(tmp_path):
    shutil.copytree(EXAMPLE, tmp_path / 'target')
    return RTW3Save.load(tmp_path / 'target')


def payloads(save):
    return {name: doc.to_bytes() for name, doc in save.documents.items()}


def test_batch_roundtrip_names_class_and_no_aviation_changes(target, tmp_path):
    design = write_design(tmp_path/'test.sdf')
    before = payloads(target)
    old_hulls = {s.record_index: dict(s.section.fields()) for n in target.nations for s in n.ships}
    names, cls = import_sdf(target, design, 0, 3)
    assert names == ['Privateer CL 1', 'Privateer CL 2', 'Privateer CL 3']
    assert cls == 'Light Cruiser 1'
    added = [s for s in target.nation(0).ships if s.name in names]
    assert len({s.design_ref_id for s in added}) == 1
    for ship in added:
        f = ship.section.fields()
        assert f['AircraftCapacity'] == '1'
        assert f['CommanderId'] == '-1'
        assert f['MonthlyCost'] == '0'
        assert f['BuildProgress'] == f['Cost']
        assert f['NumberOfLogEntries'] == '0'
        assert f['BuildingNationIdx'] == '0'
        assert not ship.under_construction
    assert all(dict(s.section.fields()) == old_hulls[s.record_index]
               for n in target.nations for s in n.ships if s.record_index in old_hulls)
    assert {n for n,v in payloads(target).items() if v != before[n]} == {target.main_file,'DesignFiles0.des'}
    assert target._source_snapshot == target._folder_snapshot(target.folder)
    next_names, next_class = import_sdf(target, design, 0, 2)
    assert next_names == ['Privateer CL 4', 'Privateer CL 5']
    assert next_class == 'Light Cruiser 2'
    output = target.save_as(tmp_path/'roundtrip')
    loaded = RTW3Save.load(output)
    loaded.validate_or_raise()
    assert [s.name for s in loaded.nation(0).ships][-5:] == names + next_names


def test_numbering_uses_highest_and_design_only_classes(target, tmp_path):
    design = write_design(tmp_path/'test.sdf', 'DD')
    target.nation(0).ships[0].name = 'privateer DD 19'
    target.nation(0).ships[1].name = 'Privateer DD 2'
    target.nation(0).designs[0].class_name = 'Destroyer 7'
    assert import_names(target, 0, design, 2) == (['Privateer DD 20','Privateer DD 21'], 'Destroyer 8')


@pytest.mark.parametrize('count', [0, -1, 101, True, 1.5])
def test_invalid_count_atomic(target, tmp_path, count):
    design = write_design(tmp_path/'test.sdf')
    before = payloads(target)
    with pytest.raises(ValueError):
        import_sdf(target, design, 0, count)
    assert payloads(target) == before


@pytest.mark.parametrize('problem', ['sdf_changed', 'target_changed', 'bad_number', 'encoding'])
def test_failures_leave_no_partial_batch(target, tmp_path, problem):
    design = write_design(tmp_path/'test.sdf')
    if problem == 'sdf_changed':
        design.path.write_text('changed')
    elif problem == 'target_changed':
        (target.folder/'changed.txt').write_text('changed')
    elif problem == 'bad_number':
        design.sections['Turret0']['Guns'] = 'bad'
    else:
        target.documents['DesignFiles0.des'].encoding = 'cp1252'
        design.sections['Data']['MisidentifiedClassName'] = '\u2603'
    before = payloads(target)
    with pytest.raises((ValueError, UnicodeError)):
        import_sdf(target, design, 0, 3)
    assert payloads(target) == before


def test_serialization_counts_and_duplicate_helipad(target, tmp_path):
    design = write_design(tmp_path/'test.sdf', mounts=3)
    # LAA must not be omitted when the redundant exported Helipad is collapsed.
    block = [v.rstrip('\n') for v in design_block(design, 12, 400, 'Light Cruiser 9', 2, '\n')]
    assert block[:5] == ['ShipDesign12', 'Light Cruiser 9', '0', 'CL', '400']
    assert block[29:31] == ['2', '2']
    assert block[49:52] == ['0', '7', '9']
    assert block[129] == '3'
    assert block[129 + 1 + 3*7] == '1'
    text = design.path.read_text().replace('Helipad=1', 'Helipad=1\nHelipad=1')
    design.path.write_text(text)
    read_sdf(design.path)
    design.path.write_text(text.replace('Helipad=1\nHelipad=1','Helipad=1\nHelipad=0'))
    with pytest.raises(ValueError):
        read_sdf(design.path)


def test_unknown_schema_rejected(tmp_path):
    design = write_design(tmp_path/'test.sdf')
    design.path.write_text(design.path.read_text() + '\nUnknownEquipment=7')
    with pytest.raises(ValueError, match='Unsupported SDF layout'):
        read_sdf(design.path)
