import tempfile
import unittest
from pathlib import Path
from privateer.save import RTW3Save
from privateer.guns import GUN_QUALITIES, gun_quality

class GunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name) / 'source'
        self.folder.mkdir()
        self.original = b'[Nation0]\r\nName=Test\r\nGuns2 = 9\r\nGuns3=-1\r\nGuns4=unrecognized\r\nResearch22CurrentLevel=7\r\nResearch0Level0=1\r\nUnknown=keep\r\n[Nation1]\r\nName=Other\r\nGuns2=0\r\n'
        (self.folder / 'game.bcs').write_bytes(self.original)
        self.save = RTW3Save.load(self.folder)

    def test_all_quality_values_and_unavailable(self):
        for value in GUN_QUALITIES:
            self.save.set_gun_qualities(0, {2: value})
            self.assertEqual(gun_quality(self.save.nation(0).section.fields(), 2), value)

    def test_roundtrip_changes_only_selected_guns(self):
        self.save.set_gun_qualities(0, {2: 2, 3: -3})
        output = self.save.save_as(Path(self.temp.name) / 'edited')
        expected = self.original.replace(b'Guns2 = 9', b'Guns2 = 2').replace(b'Guns3=-1', b'Guns3=-3')
        self.assertEqual((output / 'game.bcs').read_bytes(), expected)
        self.assertEqual((self.folder / 'game.bcs').read_bytes(), self.original)
        self.assertEqual(gun_quality(RTW3Save.load(output).nation(0).section.fields(), 2), 2)

    def test_invalid_batch_is_atomic_and_noop_stays_clean(self):
        self.save.set_gun_qualities(0, {2: 9})
        self.assertFalse(self.save.modified)
        for changes in ({2: 2, 3: 4}, {21: 1}, {True: 1}, {2: True}, {4: 1}, {5: 1}):
            with self.assertRaises(ValueError):
                self.save.set_gun_qualities(0, changes)
            self.assertEqual(self.save.documents['game.bcs'].to_bytes(), self.original)
            self.assertFalse(self.save.modified)

if __name__ == '__main__':
    unittest.main()
