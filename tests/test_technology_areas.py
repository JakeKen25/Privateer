import tempfile
import unittest
from pathlib import Path
from privateer.technology import AreaTechnologyEdits, TechnologyDefinition
from privateer.save import RTW3Save


class AreaTechnologyTests(unittest.TestCase):
    def setUp(self):
        self.db = [TechnologyDefinition(1, 'Armour development', n, f'Tech {n + 1}',
                                       1900 + n, 100 + n, 'Effect', ())
                   for n in range(6)]
        self.fields = {t.key: '0' for t in self.db}
        self.fields.update({'Research1Level35': '1', 'Guns2': '9',
                            'Research1CurrentLevel': '7', 'Research1TSL': '2'})

    def test_cumulative_raise_lower_none_and_maximum(self):
        edits = AreaTechnologyEdits(self.db, self.fields)
        for level in (5, 2, 0, 6):
            edits.set_level(1, level)
            effective = self.fields | {k: str(v) for k, v in edits.pending.items()}
            self.assertEqual([effective[t.key] for t in self.db],
                             ['1'] * level + ['0'] * (6 - level))
            self.assertFalse({'Guns2', 'Research1Level35', 'Research1CurrentLevel',
                              'Research1TSL'} & edits.pending.keys())

    def test_existing_gaps_and_reset_are_lossless(self):
        self.fields['Research1Level4'] = '1'
        edits = AreaTechnologyEdits(self.db, self.fields)
        self.assertEqual(edits.current(1), 5)
        self.assertTrue(edits.mixed(1))
        self.assertEqual(edits.pending, {})
        edits.set_level(1, 5)
        self.assertEqual(len(edits.pending), 4)
        self.assertFalse(edits.mixed(1))
        edits.reset()
        self.assertEqual(edits.pending, {})
        self.assertTrue(edits.mixed(1))

    def test_invalid_or_missing_fields_and_ranges(self):
        edits = AreaTechnologyEdits(self.db, self.fields)
        for level in (-1, 7, True, 1.5):
            with self.assertRaises(ValueError):
                edits.set_level(1, level)
        self.fields.pop('Research1Level2')
        edits = AreaTechnologyEdits(self.db, self.fields)
        self.assertFalse(edits.editable(1))
        with self.assertRaises(ValueError):
            edits.set_level(1, 5)
        self.assertEqual(edits.pending, {})

    def test_area_save_roundtrip_only_changes_defined_flags(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / 'source'
            folder.mkdir()
            original = ('[Nation0]\r\nName=Test\r\n' +
                        ''.join(f'{k}={v}\r\n' for k, v in self.fields.items()) +
                        '[Nation1]\r\nName=Other\r\nResearch1Level0=0\r\n').encode()
            (folder / 'game.bcs').write_bytes(original)
            save = RTW3Save.load(folder)
            edits = AreaTechnologyEdits(self.db, save.nation(0).section.fields())
            edits.set_level(1, 5)
            save.set_technology_flags(0, self.db, edits.pending)
            output = save.save_as(Path(temp) / 'edited')
            expected = original
            for t in self.db[:5]:
                expected = expected.replace(f'{t.key}=0'.encode(), f'{t.key}=1'.encode(), 1)
            self.assertEqual((output / 'game.bcs').read_bytes(), expected)
            self.assertEqual((folder / 'game.bcs').read_bytes(), original)
            loaded = RTW3Save.load(output)
            edits = AreaTechnologyEdits(self.db, loaded.nation(0).section.fields())
            edits.set_level(1, 2)
            loaded.set_technology_flags(0, self.db, edits.pending)
            self.assertEqual([loaded.nation(0).section.fields()[t.key] for t in self.db],
                             ['1', '1', '0', '0', '0', '0'])

if __name__ == '__main__':
    unittest.main()
