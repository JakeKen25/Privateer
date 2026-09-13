import unittest

from privateer.document import PrefixedRecord, Section
from privateer.save import RTW3Save
from pathlib import Path


class ShipFieldCacheTests(unittest.TestCase):
    def test_cached_fields_avoid_parent_roster_rescan_and_track_set(self):
        section = Section("Nation0Ships", "[Nation0Ships]\n", ["Ship0Name=Original\n"])
        record = PrefixedRecord(section, "Ship0", {"Name": "Original"})
        section.lines[0] = "Ship0Name=Changed behind cache\n"
        self.assertEqual(record.fields(), {"Name": "Original"})
        record.set("Name", "Updated")
        self.assertEqual(record.fields(), {"Name": "Updated"})
        self.assertEqual(section.lines, ["Ship0Name=Updated\n"])

    def test_real_flattened_records_retain_their_parsed_fields(self):
        save = RTW3Save.load(Path(__file__).parents[1] / "exampleSaves" / "Game5")
        records = [ship.section for nation in save.nations for ship in nation.ships]
        self.assertTrue(records)
        self.assertTrue(all(record.cached_fields is not None for record in records))
        self.assertEqual(records[0].fields()["Id"], str(save.nations[0].ships[0].record_index))


if __name__ == "__main__":
    unittest.main()
