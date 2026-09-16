from pathlib import Path

import pytest

from privateer.aircraft import aircraft_types
from privateer.save import RTW3Save


def aircraft_save(tmp_path: Path):
    folder = tmp_path / "Game6"
    folder.mkdir()
    contents = """[Nation0]\nName=USA\nShipCount=0\n[Nation1]\nName=Germany\nShipCount=0\n[AircraftTypes]\nACTypesNo=2\nAT0Name=Falcon\nAT0Manufacturer=Vought\nAT0Year=1940\nAT0BaseModelYear=1939\nAT0MaxSpeed=210\nAT0CruiseSpeed=125\nAT0LtEndurance=200\nAT0MedEndurance=160\nAT0HvyEndurance=130\nAT0Firepower=4\nAT0Maneuver=12\nAT0Toughness=5\nAT0Reliability=2\nAT0LtBombLoadSize=0\nAT0LtBombLoadNumber=0\nAT0MedBombLoadSize=0\nAT0MedBombLoadNumber=0\nAT0HvyBombLoadSize=0\nAT0HvyBombLoadNumber=0\nAT0Torpedo1=0\nAT0Torpedo2=0\nAT0Missile2=0\nAT0Carrier=1\nAT0Floatplane=0\nAT0Purpose=0\nAT0AvailableAircraft=7\nAT0Obsolete=1\nAT0DevelopmentTime=4\nAT0Nation=1\nAT0Id=100\nAT1Name=Seagull\nAT1Manufacturer=Grumman\nAT1Year=1941\nAT1BaseModelYear=1940\nAT1Purpose=3\nAT1Nation=0\nAT1Id=105\n[AirUnits]\nAirUnitNo=1\nAU0AircraftTypeId=100\nAU0Nation=1\n"""
    (folder / "RTWGame6.bcs").write_text(contents, encoding="utf-8")
    return RTW3Save.load(folder)


def test_create_aircraft_model_allocates_slot_id_and_nation_without_changing_squadrons(tmp_path):
    save = aircraft_save(tmp_path)
    original_units = save.documents[save.main_file].sections[-1].lines[:]
    created = save.create_aircraft_type(0, 0, {
        "Name": "Thunderhawk", "Manufacturer": "Vought", "Year": "1945",
        "BaseModelYear": "1944", "MaxSpeed": "350",
        "AvailableAircraft": "24", "Carrier": "1",
    })
    assert (created.slot, created.fields["Id"], created.fields["Nation"]) == (2, "106", "0")
    assert (created.name, created.role) == ("Vought Thunderhawk", "Fighter")
    assert created.fields["MaxSpeed"] == "350"
    assert created.fields["AvailableAircraft"] == "24"
    assert created.fields["Obsolete"] == "0"
    assert created.fields["DevelopmentTime"] == "0"
    assert save.documents[save.main_file].sections[-1].lines == original_units
    assert save.modified
    assert f"ACTypesNo=3{save.documents[save.main_file].newline}" in save.documents[save.main_file].render()
    save.save(create_backup=False)
    reloaded = RTW3Save.load(save.folder)
    assert aircraft_types(reloaded)[-1].fields == created.fields


@pytest.mark.parametrize("changes, error", [
    ({"Name": "Falcon", "Manufacturer": "Vought", "Year": "1945"}, "already has"),
    ({"Name": "Bad=Name"}, "single-line"),
    ({"Name": "New", "Year": "nineteen forty"}, "whole number"),
    ({"Name": "New", "Year": "3000"}, "year from 1800"),
    ({"Name": "New", "Carrier": "2"}, "0 or 1"),
    ({"Name": "New", "BaseModelYear": "1942", "Year": "1940"}, "cannot precede"),
    ({"Name": "New", "Id": "999"}, "unsupported field"),
])
def test_invalid_aircraft_creation_does_not_modify_save(tmp_path, changes, error):
    save = aircraft_save(tmp_path)
    original = save.documents[save.main_file].to_bytes()
    with pytest.raises(ValueError, match=error):
        save.create_aircraft_type(1, 0, changes)
    assert save.documents[save.main_file].to_bytes() == original
    assert not save.modified


def test_aircraft_parser_rejects_duplicate_model_ids(tmp_path):
    save = aircraft_save(tmp_path)
    section = next(section for section in save.documents[save.main_file].sections
                   if section.name == "AircraftTypes")
    section.set("AT1Id", 100)
    with pytest.raises(ValueError, match="Duplicate aircraft model ID"):
        aircraft_types(save)
