from pathlib import Path

import pytest

from privateer.save import RTW3Save
from privateer.validation import SaveValidationError


MAIN = """; keep me\r
[Nation0]\r
Name=Britain\r
Funds=100\r
BaseResources=200\r
ShipCount=0\r
TechGuns=2\r
Unknown = untouched\r
[Nation1]\r
Name=Germany\r
Funds=300\r
BaseResources=400\r
ShipCount=1\r
TechGuns=8\r
[Nation1Ship7]\r
Name=Fawn\r
Type=DD\r
Class=Fawn\r
ShipDesignRefId=10\r
OwnerNationIdx=1\r
BuildingNationIdx=1\r
UnderConstruction=1\r
"""
DES0 = """[ShipDesign2]\nDesignId=2\nType=BB\nClass=Old\n"""
DES1 = """[ShipDesign10]\nDesignId=10\nType=DD\nClass=Fawn\nGun=4\n"""


def fixture(tmp_path: Path) -> Path:
    folder = tmp_path / "Game7"; folder.mkdir()
    (folder / "game.bcs").write_bytes(MAIN.encode())
    (folder / "DesignFiles0.des").write_text(DES0)
    (folder / "DesignFiles1.des").write_text(DES1)
    (folder / "unknown.off").write_bytes(b"opaque\x00data")
    return folder


def test_load_player_economy_and_unknown_formatting(tmp_path):
    save = RTW3Save.load(fixture(tmp_path))
    assert save.nation("Britain").is_player
    assert save.player_detection_warning
    save.nation(0).set_funds(1_000, save.documents[save.main_file].newline)
    assert "Unknown = untouched\r\n" in save.documents[save.main_file].render()
    assert "Funds=1000\r\n" in save.documents[save.main_file].render()


def test_atomic_transfer_clones_and_remaps_design(tmp_path):
    save = RTW3Save.load(fixture(tmp_path)); donor = save.nation(1); ship = donor.ships[0]
    save.transfer_ships([ship], "Britain")
    assert donor.designs[0].record_index == 10  # donor copy is retained
    assert ship.owner_index == 0 and ship.building_nation_index == 0
    assert ship.design_ref_id == 3
    copied = save.nation(0).designs[-1]
    assert copied.record_index == copied.internal_design_id == 3
    assert save.validate().valid


def test_validator_catches_external_internal_mismatch(tmp_path):
    folder = fixture(tmp_path)
    (folder / "DesignFiles1.des").write_text(DES1.replace("DesignId=10", "DesignId=36"))
    report = RTW3Save.load(folder).validate()
    assert not report.valid
    assert {issue.code for issue in report.issues} >= {"internal_design_id", "missing_design"}


def test_failed_transfer_rolls_back(tmp_path):
    save = RTW3Save.load(fixture(tmp_path)); ship = save.nation(1).ships[0]
    ship.design_ref_id = 999
    with pytest.raises(ValueError): save.transfer_ships([ship], 0)
    assert ship in save.nation(1).ships


def test_save_as_preserves_unknown_files_and_round_trips(tmp_path):
    folder = fixture(tmp_path); save = RTW3Save.load(folder)
    destination = tmp_path / "Copy"; save.save_as(destination)
    assert (destination / "unknown.off").read_bytes() == b"opaque\x00data"
    assert RTW3Save.load(destination).validate().valid


def test_technology_and_seeded_distribution(tmp_path):
    save = RTW3Save.load(fixture(tmp_path))
    save.copy_technology(1, 0); assert save.nation(0).technology.fields["TechGuns"] == 8
    with pytest.raises(NotImplementedError, match="format profile"):
        save.set_maximum_technology(0)


@pytest.mark.parametrize(
    ("game", "counts"),
    [
        ("Game4", [52, 91, 74, 147, 100, 111, 136, 34, 33, 0]),
        ("Game5", [36, 51, 46, 37, 50, 40, 49, 22, 26, 0]),
    ],
)
def test_real_rosters_parse_all_stored_ships(game, counts):
    folder = Path(__file__).parents[1] / "exampleSaves" / game
    save = RTW3Save.load(folder)
    assert [len(nation.ships) for nation in save.nations] == counts
    assert all(ship.record_index != ship.local_slot for ship in save.nations[0].ships)
    assert any("Mine capacity" in ship.section.fields() for ship in save.nations[0].ships)


def test_real_flattened_transfer_is_safely_disabled():
    folder = Path(__file__).parents[1] / "exampleSaves" / "Game5"
    save = RTW3Save.load(folder)
    with pytest.raises(NotImplementedError, match="physical roster movement"):
        save.transfer_ships([save.nation(1).ships[0]], 0)


def test_malformed_flattened_record_is_not_silently_ignored(tmp_path):
    folder = fixture(tmp_path)
    main = (folder / "game.bcs").read_text()
    main += "[Nation0Ships]\nShip0Name=Missing identifier\n"
    (folder / "game.bcs").write_text(main)
    with pytest.raises(ValueError, match="fields but no integer Id"):
        RTW3Save.load(folder)
