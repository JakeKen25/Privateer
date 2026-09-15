import hashlib
import tempfile
import unittest
from pathlib import Path

from privateer.save import RTW3Save
from privateer.ship_status import ship_status_label
from privateer.ships_gui import ship_details, ship_stats, transfer_block_reason


SOURCE = Path(__file__).parents[1] / "developmentResources" / "exampleSaves" / "Game5"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ShipTransferTests(unittest.TestCase):
    def setUp(self):
        self.save = RTW3Save.load(SOURCE)

    def test_single_transfer_preserves_hull_and_only_touches_required_files(self):
        ship = self.save.nation(1).ships[0]
        hull = ship.record_index
        original_fields = dict(ship.section.fields())
        source_design = next(
            design for design in self.save.nation(1).designs
            if design.internal_design_id == ship.design_ref_id
        )
        source_payload = source_design.positional_record
        total = sum(len(nation.ships) for nation in self.save.nations)

        self.save.transfer_ship_batch({hull: 0})

        moved = next(candidate for candidate in self.save.nation(0).ships if candidate.record_index == hull)
        fields = moved.section.fields()
        self.assertEqual(moved.owner_index, 0)
        self.assertEqual(moved.record_index, hull)
        self.assertEqual(sum(len(nation.ships) for nation in self.save.nations), total)
        self.assertEqual(fields["BuildingNationIdx"], original_fields["BuildingNationIdx"])
        self.assertNotEqual(fields["DesignRefId"], original_fields["DesignRefId"])
        for key, value in original_fields.items():
            if key != "DesignRefId":
                self.assertEqual(fields[key], value, key)
        self.assertEqual(source_design.positional_record, source_payload)
        copied_design = next(
            design for design in self.save.nation(0).designs
            if design.internal_design_id == moved.design_ref_id
        )
        self.assertEqual(len(copied_design.positional_record), len(source_payload))
        for line_index, line in enumerate(source_payload):
            if line_index not in {0, 4}:
                self.assertEqual(copied_design.positional_record[line_index], line)
        self.assertTrue(self.save.validate().valid)

        with tempfile.TemporaryDirectory() as temporary:
            output = self.save.save_as(Path(temporary) / "Game5Transfer")
            reloaded = RTW3Save.load(output)
            self.assertTrue(reloaded.validate().valid)
            self.assertTrue(any(candidate.record_index == hull for candidate in reloaded.nation(0).ships))
            changed = {
                path.name for path in SOURCE.iterdir() if path.is_file()
                and digest(path) != digest(output / path.name)
            }
            self.assertEqual(changed, {"RTWGame5.bcs", "DesignFiles0.des"})

    def test_batch_reuses_one_design_for_matching_source_design(self):
        source = self.save.nation(1)
        groups = {}
        for ship in source.ships:
            groups.setdefault(ship.design_ref_id, []).append(ship)
        ships = next(group for group in groups.values() if len(group) >= 2)
        before = len(self.save.nation(0).designs)
        self.save.transfer_ship_batch({ships[0].record_index: 0, ships[1].record_index: 0})
        moved = [next(ship for ship in self.save.nation(0).ships if ship.record_index == item.record_index)
                 for item in ships[:2]]
        self.assertEqual(moved[0].design_ref_id, moved[1].design_ref_id)
        self.assertEqual(len(self.save.nation(0).designs), before + 1)

    def test_same_design_sent_to_two_destinations_creates_two_valid_mappings(self):
        source = self.save.nation(1)
        groups = {}
        for ship in source.ships:
            groups.setdefault(ship.design_ref_id, []).append(ship)
        ships = next(group for group in groups.values() if len(group) >= 2)
        self.save.transfer_ship_batch({ships[0].record_index: 0, ships[1].record_index: 2})
        self.assertTrue(self.save.validate().valid)
        self.assertTrue(any(ship.record_index == ships[0].record_index for ship in self.save.nation(0).ships))
        self.assertTrue(any(ship.record_index == ships[1].record_index for ship in self.save.nation(2).ships))

    def test_player_commander_is_cleared_but_other_state_is_preserved(self):
        ship = next(ship for ship in self.save.nation(0).ships
                    if ship.section.fields().get("CommanderId") != "-1")
        fields = dict(ship.section.fields())
        self.save.transfer_ship_batch({ship.record_index: 1})
        moved = next(candidate for candidate in self.save.nation(1).ships
                     if candidate.record_index == ship.record_index)
        self.assertEqual(moved.section.fields()["CommanderId"], "-1")
        for key, value in fields.items():
            if key not in {"DesignRefId", "CommanderId"}:
                self.assertEqual(moved.section.fields()[key], value, key)

    def test_under_construction_ship_keeps_progress_and_cost_state(self):
        ship = next(ship for ship in self.save.nation(1).ships if ship.under_construction)
        fields = dict(ship.section.fields())
        self.save.transfer_ship_batch({ship.record_index: 2})
        moved = next(candidate for candidate in self.save.nation(2).ships
                     if candidate.record_index == ship.record_index)
        self.assertTrue(moved.under_construction)
        self.assertEqual(moved.section.fields()["BuildingNationIdx"], fields["BuildingNationIdx"])
        for key in ("BuildProgress", "Cost", "MonthlyCost", "Maintenance", "Halted", "Hurry"):
            self.assertEqual(moved.section.fields()[key], fields[key], key)

    def test_failed_batch_is_atomic(self):
        ship = self.save.nation(1).ships[0]
        before = {name: document.to_bytes() for name, document in self.save.documents.items()}
        with self.assertRaisesRegex(ValueError, "existing hull"):
            self.save.transfer_ship_batch({ship.record_index: 999})
        self.assertEqual(before, {name: document.to_bytes() for name, document in self.save.documents.items()})
        self.assertFalse(self.save.modified)

    def test_ui_helpers_explain_state_and_carrier_gate(self):
        ship = self.save.nation(1).ships[0]
        self.assertIsNone(transfer_block_reason(ship))
        details = ship_details(self.save, ship)
        self.assertIn(ship.name, details)
        self.assertIn(str(ship.record_index), details)
        self.assertIn("Eligible", details)
        stats = ship_stats(ship)
        self.assertEqual(stats["type"], ship.ship_type)
        self.assertEqual(stats["speed"], ship.section.fields()["Speed"])
        self.assertEqual(stats["main_gun"], ship.section.fields()["MainCalibre"])
        self.assertEqual(stats["description"], ship.section.fields()["Description"])
        ship.section.set("AircraftCapacity", 20)
        self.assertIn("Carrier", transfer_block_reason(ship))

    def test_verified_fleet_status_labels_and_construction(self):
        ship = self.save.nation(1).ships[0]
        fields = dict(ship.section.fields())
        fields.update({"Fate": "XXX", "InPlay": "1"})
        expected = {
            "0": "Active Fleet",
            "1": "Reserve",
            "2": "Mothballed",
            "6": "Foreign Service",
            "10": "Unknown status (10)",
        }
        for raw, label in expected.items():
            fields["Status"] = raw
            self.assertEqual(ship_status_label(ship, fields), label)
        fields["InPlay"] = "0"
        self.assertEqual(ship_status_label(ship, fields), "Under construction")
        self.assertIsNone(transfer_block_reason(ship, fields))

    def test_final_fates_are_labelled_and_blocked_atomically(self):
        ship = self.save.nation(1).ships[0]
        cases = {
            "Scrapped": "Scrapped",
            "Broken up on slipway": "Scrapped on slipway",
            "Torpedoed and sunk by enemy submarine": "Sunk",
            "Mined": "Sunk (mined)",
            "Scuttled": "Scuttled",
        }
        for fate, label in cases.items():
            fields = dict(ship.section.fields())
            fields["Fate"] = fate
            self.assertEqual(ship_status_label(ship, fields), label)
            self.assertIn("cannot be transferred", transfer_block_reason(ship, fields))

        ship.section.set("Fate", "Scrapped")
        original = {name: document.to_bytes() for name, document in self.save.documents.items()}
        with self.assertRaisesRegex(ValueError, "Scrapped ships cannot be transferred"):
            self.save.transfer_ship_batch({ship.record_index: 0})
        self.assertEqual(original, {name: document.to_bytes() for name, document in self.save.documents.items()})
        self.assertFalse(self.save.modified)

    def test_scrapped_slipway_record_is_not_under_construction(self):
        ship = next(ship for ship in self.save.nation(1).ships if ship.under_construction)
        hull = ship.record_index
        ship.section.set("Fate", "Broken up on slipway")
        self.save.nations = []
        self.save._build_model()
        reparsed = next(candidate for nation in self.save.nations for candidate in nation.ships
                        if candidate.record_index == hull)
        self.assertFalse(reparsed.under_construction)
        self.assertEqual(ship_status_label(reparsed), "Scrapped on slipway")


if __name__ == "__main__":
    unittest.main()
