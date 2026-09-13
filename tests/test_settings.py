import tempfile
import unittest
from pathlib import Path

from privateer.save import RTW3Save
from privateer.settings import AppSettings


MAIN = b"[Nation0]\r\nName=Test Nation\r\nFunds=100\r\nBaseResources=50\r\n"


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_defaults_and_json_round_trip(self):
        path = self.root / "config" / "settings.json"
        self.assertEqual(AppSettings.load(path), AppSettings(True, ""))
        settings = AppSettings(False, str(self.root / "backups"))
        self.assertEqual(settings.save(path), path)
        self.assertEqual(AppSettings.load(path), settings)
        self.assertIn('"create_backups": false', path.read_text(encoding="utf-8"))

    def test_invalid_settings_are_rejected(self):
        path = self.root / "settings.json"
        path.write_text('{"create_backups": "yes"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Create backups"):
            AppSettings.load(path)

    def make_save(self):
        folder = self.root / "Game1"
        folder.mkdir()
        (folder / "RTWGame1.bcs").write_bytes(MAIN)
        return folder, RTW3Save.load(folder)

    def test_save_without_permanent_backup_keeps_atomic_recovery_temporary(self):
        folder, save = self.make_save()
        save.adjust_economy(0, funds=("Set value", "125"))
        self.assertIsNone(save.save(create_backup=False))
        self.assertIn(b"Funds=125", (folder / "RTWGame1.bcs").read_bytes())
        self.assertFalse(list(self.root.glob("Game1_backup_*")))
        self.assertFalse(list(self.root.glob(".Game1-privateer-recovery-*")))

    def test_custom_backup_contains_original_and_nested_location_is_rejected(self):
        folder, save = self.make_save()
        backup_root = self.root / "Backups"
        save.adjust_economy(0, funds=("Set value", "125"))
        backup = save.save(create_backup=True, backup_directory=backup_root)
        self.assertEqual(backup.parent, backup_root)
        self.assertEqual((backup / "RTWGame1.bcs").read_bytes(), MAIN)

        reloaded = RTW3Save.load(folder)
        with self.assertRaisesRegex(ValueError, "cannot be inside"):
            reloaded.save(backup_directory=folder / "Nested")


if __name__ == "__main__":
    unittest.main()
