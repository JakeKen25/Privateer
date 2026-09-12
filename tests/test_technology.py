import tempfile
import unittest
from pathlib import Path
from privateer.technology import load_database, DEFAULT_DATABASE
from privateer.save import RTW3Save

class TechnologyTests(unittest.TestCase):
    @unittest.skipUnless(DEFAULT_DATABASE.is_file(), "Requires installed RTW3 data")
    def test_local_database_and_lossless_edits(self):
        db = load_database(DEFAULT_DATABASE)
        self.assertEqual(db[0].level, 0)
        self.assertEqual(db[0].internal_id, 30)
        self.assertEqual(db[0].year, 1891)
        self.assertEqual(len({t.area for t in db}), 22)
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / 'source'
            folder.mkdir()
            original = b';preserve\r\n[Nation0]\r\nName=Test\r\nResearch0Level0 = 0\r\nResearch0Level35=1\r\nResearch0TSL=unknown\r\nResearch0CurrentLevel=9\r\nGuns2=9\r\n[Nation1]\r\nName=Other\r\nResearch0Level0=0\r\n'
            (folder / 'game.bcs').write_bytes(original)
            save = RTW3Save.load(folder)
            save.set_technology_flags(0, db, {})
            self.assertFalse(save.modified)
            self.assertEqual(save.documents['game.bcs'].to_bytes(), original)
            with self.assertRaises(ValueError):
                save.set_technology_flags(0, db, {'Research0Level0': 1, 'Research0Level35': 1})
            self.assertEqual(save.documents['game.bcs'].to_bytes(), original)
            save.set_technology_flags(0, db, {'Research0Level0': 1})
            expected = original.replace(b'Research0Level0 = 0', b'Research0Level0 = 1')
            self.assertEqual(save.documents['game.bcs'].to_bytes(), expected)
            output = save.save_as(Path(temp) / 'edited')
            self.assertEqual((output / 'game.bcs').read_bytes(), expected)
            self.assertEqual((folder / 'game.bcs').read_bytes(), original)

    def test_missing_and_malformed_data(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'ResearchAreas3.dat'
            path.write_text('[Test 0]\nPicName=test.jpg\nExample;;Y;100;6;31;Effect\n')
            self.assertIsNone(load_database(path)[0].year)
            path.write_text('[Test 0]\ninvalid\n')
            with self.assertRaises(ValueError):
                load_database(path)

if __name__ == '__main__':
    unittest.main()
