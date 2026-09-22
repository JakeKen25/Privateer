"""Synthetic fixtures: never depend on or modify installed game/save files."""
import tempfile
import unittest
from pathlib import Path

from privateer.fortifications import (apply_infrastructure, available_types, base_sites,
                                     occupied_capacity, records, status)
from privateer.save import RTW3Save


def fixture(folder):
    def installation(slot, identity, name, kind, capacity):
        data = {'Id': identity, 'Name': name, 'Classname': kind, 'AircraftCapacity': capacity,
                'LocationAreaName': 'Home', 'InPlay': 1, 'Fate': 'XXX', 'Cost': 700,
                'BuildProgress': 702, 'Maintenance': 86, 'MonthlyCost': 350,
                'Description': '60 a/c' if capacity else '', 'ShipType': 'LT',
                'MysteryField': 'preserve exactly', 'BuildingNationIdx': 0}
        return ''.join(f'Ship{slot}{k}={v}\r\n' for k, v in data.items())
    payload = ('[General]\r\nYear=1950\r\nIDNo=10\r\nGameMaxAirbaseSize=100\r\n'
               '[Nation0]\r\nName=Test\r\nDockSize=30000\r\n'
               '[Nation0CoastalArtillery]\r\nCACount=2\r\n' +
               installation(0, 12, 'Airbase Port', 'Airbase60', 60) +
               installation(1, 13, 'Battery 2', '6 in Coastal Battery', 0) +
               '[Nation1]\r\nName=Other\r\nDockSize=20000\r\n'
               '[Nation1CoastalArtillery]\r\nCACount=0\r\n'
               '[AirUnits]\r\nAirUnitNo=1\r\nAU0Id=90\r\nAU0HomeBase=12\r\n'
               'AU0AircraftNumber=18\r\nAU0DesiredAircraftNumber=30\r\n')
    (folder / 'RTWGame6.bcs').write_bytes(payload.encode())
    (folder / 'MapData6.dat').write_text('[MapAreas]\nMapAreaCount=1\nMapArea0PossessionCount=2\n'
                                      'MapArea0Possession0Name=Home\nMapArea0Possession0Owner=Test\n'
                                      'MapArea0Possession1Name=Other land\nMapArea0Possession1Owner=Other\n')
    return RTW3Save.load(folder)


class FortificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name) / 'source'
        self.folder.mkdir()
        self.save = fixture(self.folder)

    def edit(self, slot, **changes):
        record = records(self.save, 0)[slot]
        return {k: changes.get(k, record[k]) for k in ('Name', 'Classname', 'LocationAreaName')}

    def test_parse_and_noop_preserve_bytes(self):
        before = self.save.documents[self.save.main_file].to_bytes()
        apply_infrastructure(self.save, 0, 30000, {1: self.edit(1)}, [])
        self.assertEqual(self.save.documents[self.save.main_file].to_bytes(), before)
        self.assertFalse(self.save.modified)
        self.assertEqual(occupied_capacity(self.save, 12), 30)

    def test_upgrade_and_add_roundtrip_preserves_links_and_other_nation(self):
        before = self.save.documents[self.save.main_file].to_bytes()
        air = next(s for s in self.save.documents[self.save.main_file].sections if s.name == 'AirUnits')
        air_before = list(air.lines)
        additions = [{'Name': 'Battery New', 'Classname': 'Missile Battery', 'LocationAreaName': 'Home'},
                     {'Name': 'Airbase New Port', 'Classname': 'Airbase100', 'LocationAreaName': 'Home'}]
        apply_infrastructure(self.save, 0, 40000, {0: self.edit(0, Classname='Airbase80')}, additions,
                             sites={'Home': ['New Port']})
        result = records(self.save, 0)
        self.assertEqual(result[0]['Id'], '12')
        self.assertEqual(result[0]['AircraftCapacity'], '80')
        self.assertEqual(result[0]['Description'], '80 a/c')
        self.assertEqual(result[0]['MysteryField'], 'preserve exactly')
        self.assertEqual([result[i]['Id'] for i in (2, 3)], ['91', '92'])
        self.assertEqual(air.lines, air_before)
        self.assertEqual(records(self.save, 1), {})
        output = self.save.save_as(Path(self.temp.name) / 'edited')
        reloaded = RTW3Save.load(output)
        self.assertEqual(records(reloaded, 0), result)
        self.assertEqual(reloaded.nation(0).dock_size, 40000)
        self.assertEqual((self.folder / self.save.main_file).read_bytes(), before)

    def test_invalid_batch_does_not_apply_dockyard_or_any_other_edits(self):
        before = self.save.documents[self.save.main_file].to_bytes()
        for invalid in (self.edit(0, Classname='Airbase20'), self.edit(0, Name='Airbase Elsewhere'),
                        self.edit(0, Classname='Missile Battery'), self.edit(0, Classname='Airbase120')):
            with self.assertRaises(ValueError):
                apply_infrastructure(self.save, 0, 99999, {1: self.edit(1, Name='Renamed'), 0: invalid}, [])
            self.assertEqual(self.save.documents[self.save.main_file].to_bytes(), before)
            self.assertFalse(self.save.modified)

    def test_unowned_duplicate_or_unknown_base_site_is_rejected(self):
        for name, location in [('Airbase Port', 'Home'), ('Airbase Unknown', 'Home'), ('Airbase New', 'Other land')]:
            with self.assertRaises(ValueError):
                apply_infrastructure(self.save, 0, None, {},
                    [{'Name': name, 'LocationAreaName': location, 'Classname': 'Airbase40'}],
                    sites={'Home': ['Port', 'New'], 'Other land': ['New']})
        self.assertFalse(self.save.modified)

    def test_stale_source_refuses_save(self):
        apply_infrastructure(self.save, 0, None, {1: self.edit(1, Name='Renamed')}, [])
        with (self.folder / self.save.main_file).open('ab') as stream:
            stream.write(b'; external modification\r\n')
        with self.assertRaisesRegex(ValueError, 'changed on disk'):
            self.save.save_as(Path(self.temp.name) / 'edited')

    def test_invalid_roster_and_readonly_construction(self):
        section = next(s for s in self.save.documents[self.save.main_file].sections if s.name == 'Nation0CoastalArtillery')
        section.set('Ship1InPlay', 0)
        self.assertEqual(status(records(self.save, 0)[1]), 'Under construction')
        with self.assertRaises(ValueError):
            apply_infrastructure(self.save, 0, None, {1: self.edit(1, Name='No')}, [])
        section.set('CACount', 3)
        with self.assertRaises(ValueError):
            records(self.save, 0)

    def test_type_limits_and_map_sites_use_names(self):
        kinds = {t.name for t in available_types(self.save)}
        self.assertIn('Airbase100', kinds)
        self.assertNotIn('Airbase120', kinds)
        install = Path(self.temp.name) / 'install'
        (install / 'Data').mkdir(parents=True)
        (install / 'Data' / 'MapData.dat').write_text('[MapArea6]\nMapArea6Possession8Name=Home\n'
            'MapArea6Possession8BaseNames0=Port\nMapArea6Possession8BaseNames1=New Port\n')
        self.assertEqual(base_sites(install), {'Home': ['New Port', 'Port']})


if __name__ == '__main__':
    unittest.main()
