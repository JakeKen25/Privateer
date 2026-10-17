import unittest
from pathlib import Path

from privateer.air_wings import AirWingDraft, air_wings, assign_air_wing
from privateer.save import RTW3Save


SAVE = Path(__file__).parents[1] / "developmentResources" / "exampleSaves" / "Game5"


class AirWingTests(unittest.TestCase):
    def setUp(self):
        self.save = RTW3Save.load(SAVE)
        self.source = self.save.nation(1).ships[0]
        self.target = self.save.nation(1).ships[1]
        self.source.section.set("AircraftCapacity", 20)
        self.target.section.set("AircraftCapacity", 20)
        sections = self.save.documents[self.save.main_file].sections
        self.air = next(s for s in sections if s.name == "AirUnits")
        self.types = next(s for s in sections if s.name == "AircraftTypes")
        self.air.set("AirUnitNo", 1)
        self.types.set("ACTypesNo", 1)
        self.types.set("AT0Name", "Test aircraft")
        self.types.set("AT0Id", 800)
        for key, value in {
            "AU0Id": 900, "AU0AircraftTypeId": 800, "AU0AircraftNumber": 8,
            "AU0DesiredAircraftNumber": 10, "AU0Role": 14, "AU0Nation": 1,
            "AU0HomeBase": self.source.record_index, "AU0CarrierCapable": 1,
        }.items():
            self.air.set(key, value)

    def test_air_wings_resolve_models_and_bases(self):
        wing, = air_wings(self.save, 1)
        self.assertEqual(wing.aircraft_name, "Test aircraft")
        self.assertEqual(wing.base_name, self.source.name)
        self.assertEqual(wing.value("AircraftNumber"), "8")

    def test_reassignment_is_staged_then_applies_only_to_wing_base(self):
        before = dict(self.air.fields())
        draft = AirWingDraft(self.save, 1)
        self.assertTrue(draft.assign(0, self.target.record_index))
        self.assertEqual(self.air.fields(), before)
        self.assertTrue(draft.apply())
        after = self.air.fields()
        for key, value in before.items():
            self.assertEqual(after[key], str(self.target.record_index) if key == "AU0HomeBase" else value)
        self.assertTrue(self.save.modified)
        self.assertTrue(self.save._aircraft_changes)

    def test_duplicate_assignment_is_a_noop(self):
        self.assertFalse(assign_air_wing(self.save, 1, 0, self.source.record_index))
        self.assertFalse(self.save.modified)

    def test_rejects_foreign_base_and_stale_draft(self):
        draft = AirWingDraft(self.save, 1)
        with self.assertRaisesRegex(ValueError, "active aircraft-capable"):
            draft.assign(0, self.save.nation(2).ships[0].record_index)
        draft.assign(0, self.target.record_index)
        self.air.set("AU0Role", 15)
        with self.assertRaisesRegex(ValueError, "changed outside"):
            draft.apply()


if __name__ == "__main__":
    unittest.main()
