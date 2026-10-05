import tempfile
import unittest
from pathlib import Path
from privateer.save import RTW3Save
from privateer.colonies import (
    MAP_AREA_NAMES,
    is_home_area_possession,
    is_home_province,
    map_area_name,
    map_document,
    nation_home_areas,
    possessions,
)


class ColonyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.folder=Path(self.tmp.name)/'Game1';self.folder.mkdir()
        self.main=(b'[Nation0]\r\nName=Italy\r\nBuildAreaName=The Mediterranean\r\n'
                   b'[Nation1]\r\nName=France\r\nBuildAreaName=Northern Europe\r\n')
        (self.folder/'RTWGame1.bcs').write_bytes(self.main)
        (self.folder/'Autosave.bcs').write_bytes(b'[Nation0]\nName=Wrong autosave\n')
        self.map=(b'\xef\xbb\xbf[MapAreas]\r\nMapAreaCount=1\r\nMapArea0PossessionCount=2\r\n'
                  b'MapArea0Possession0Name=Test colony\r\nMapArea0Possession0Owner = Italy  \r\n'
                  b'MapArea0Possession0Value=2\r\nMapArea0Possession1Value=3\r\nMapArea0Possession0Invaded=1\r\nMapArea0Possession0TakenFrom=8\r\n'
                  b'MapArea0Possession1Name=Neutral port\r\nMapArea0Possession1Owner=Neutral\r\nUnknown=keep\r\n')
        (self.folder/'MapData1.dat').write_bytes(self.map)
        (self.folder/'MapData2.dat').write_bytes(b'Unrelated map')
        self.save=RTW3Save.load(self.folder)

    def test_numbered_campaign_and_noop(self):
        self.assertEqual(self.save.main_file,'RTWGame1.bcs')
        self.assertEqual(len(possessions(self.save)),2)
        self.save.set_colony_owners({(0,0):'Italy'})
        self.assertFalse(self.save.modified)
        self.assertEqual(self.save.documents['MapData1.dat'].to_bytes(),self.map)

    def test_owner_only_roundtrip_and_backup(self):
        self.save.set_colony_owners({(0,0):'France',(0,1):'Italy'})
        expected=self.map.replace(b'Owner = Italy  ',b'Owner = France  ').replace(b'Owner=Neutral',b'Owner=Italy')
        output=self.save.save_as(Path(self.tmp.name)/'copy')
        self.assertEqual((output/'MapData1.dat').read_bytes(),expected)
        self.assertEqual((self.folder/'MapData1.dat').read_bytes(),self.map)
        backup=self.save.save()
        self.assertEqual((backup/'MapData1.dat').read_bytes(),self.map)
        for filename in ('RTWGame1.bcs','Autosave.bcs','MapData2.dat'):
            self.assertEqual((backup/filename).read_bytes(),(self.folder/filename).read_bytes())
        self.assertEqual([p.owner for p in possessions(RTW3Save.load(self.folder))],['France','Italy'])

    def test_validation_is_atomic(self):
        for changes in ({(0,0):'France',(0,1):'Missing country'},{(0,2):'France'},{(True,0):'France'},{(0,0):'France\nOther=1'}):
            with self.assertRaises(ValueError):self.save.set_colony_owners(changes)
            self.assertEqual(self.save.documents['MapData1.dat'].to_bytes(),self.map)
        section=map_document(self.save)[2]
        section.lines.append('MapArea0Possession0Owner=France\r\n')
        with self.assertRaisesRegex(ValueError,'Duplicate'):self.save.set_colony_owners({(0,0):'France'})

    def test_missing_map_counts_and_external_change(self):
        self.save.set_colony_owners({(0,0):'Neutral'})
        (self.folder/'MapData1.dat').write_bytes(self.map+b';game advanced\r\n')
        with self.assertRaisesRegex(ValueError,'changed on disk'):self.save.save()
        with self.assertRaisesRegex(ValueError,'changed on disk'):self.save.save_as(Path(self.tmp.name)/'copy')
        self.save.documents.pop('MapData1.dat')
        with self.assertRaisesRegex(ValueError,'Missing'):possessions(self.save)
        (self.folder/'MapData1.dat').write_bytes(self.map.replace(b'PossessionCount=2',b'PossessionCount=1'))
        with self.assertRaisesRegex(ValueError,'counts'):possessions(RTW3Save.load(self.folder))

    def test_renamed_folder_keeps_campaign_map_suffix(self):
        renamed=self.folder.with_name('Game1 backup')
        self.folder.rename(renamed)
        self.assertEqual(map_document(RTW3Save.load(renamed))[0],'MapData1.dat')

    def test_area_names_and_home_area_detection(self):
        self.assertEqual(len(MAP_AREA_NAMES), 16)
        self.assertEqual(map_area_name(0), 'Northern Europe')
        self.assertEqual(map_area_name(15), 'The Baltic')
        self.assertEqual(map_area_name(99), 'Unknown map area (99)')
        self.assertEqual(
            nation_home_areas(self.save),
            {'Italy': 1, 'France': 0},
        )
        test_colony = possessions(self.save)[0]
        self.assertFalse(is_home_area_possession(self.save, test_colony))

    def test_low_value_possession_in_home_area_can_transfer(self):
        data = self.map.replace(b'Owner = Italy', b'Owner = France')
        (self.folder/'MapData1.dat').write_bytes(data)
        save = RTW3Save.load(self.folder)
        self.assertTrue(is_home_area_possession(save, possessions(save)[0]))
        self.assertFalse(is_home_province(possessions(save)[0]))
        save.set_colony_owners({(0, 0): 'Italy'})
        self.assertEqual(possessions(save)[0].owner, 'Italy')

    def test_home_province_protection_is_owner_independent_and_atomic(self):
        for value in (200, 250):
            data = self.map.replace(b'Possession0Value=2', f'Possession0Value={value}'.encode())
            (self.folder/'MapData1.dat').write_bytes(data)
            save = RTW3Save.load(self.folder)
            self.assertTrue(is_home_province(possessions(save)[0]))
            with self.assertRaisesRegex(ValueError, 'home province.*cannot be transferred'):
                save.set_colony_owners({(0, 1): 'France', (0, 0): 'Neutral'})
            self.assertFalse(save.modified)
            self.assertEqual(save.documents['MapData1.dat'].to_bytes(), data)

    def test_invalid_value_blocks_transfer_without_writing(self):
        data = self.map.replace(b'Possession0Value=2', b'Possession0Value=?')
        (self.folder/'MapData1.dat').write_bytes(data)
        save = RTW3Save.load(self.folder)
        with self.assertRaisesRegex(ValueError, 'invalid possession Value'):
            save.set_colony_owners({(0, 0): 'France'})
        self.assertFalse(save.modified)

if __name__=='__main__':unittest.main()
