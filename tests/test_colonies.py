import tempfile
import unittest
from pathlib import Path
from privateer.save import RTW3Save
from privateer.colonies import possessions, map_document


class ColonyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.folder=Path(self.tmp.name)/'Game1';self.folder.mkdir()
        self.main=b'[Nation0]\r\nName=Italy\r\n[Nation1]\r\nName=France\r\n'
        (self.folder/'RTWGame1.bcs').write_bytes(self.main)
        (self.folder/'Autosave.bcs').write_bytes(b'[Nation0]\nName=Wrong autosave\n')
        self.map=(b'\xef\xbb\xbf[MapAreas]\r\nMapAreaCount=1\r\nMapArea0PossessionCount=2\r\n'
                  b'MapArea0Possession0Name=Test colony\r\nMapArea0Possession0Owner = Italy  \r\n'
                  b'MapArea0Possession0Invaded=1\r\nMapArea0Possession0TakenFrom=8\r\n'
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

if __name__=='__main__':unittest.main()
