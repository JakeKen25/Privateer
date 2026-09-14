import struct
import tempfile
import unittest
from pathlib import Path

from privateer.custom_nation import (
    SHIP_CLASSES, config_from_template, export_custom_nation,
    load_era_templates, parse_nation_templates, render_nation_file,
    render_ship_names, validate_custom_flag, write_placeholder_bmp,
)


TEMPLATE = """[Nation0]
Name=Germany
Name2=German
Leader=Kaiser
LeaderF=Leader
LeaderC=Secretary
LeaderR=Chancellor
AdmiralRank=Admiral
AdmiralName=von Test
AirUnitName=Gruppe
TroubleRegion=in the Balkans
BuildAreaName=Northern Europe
ParliamentName=the Reichstag
GovernmentType=1
DockSize=12000
BaseResources=12500
BudgetModifier=13
TreatyTonnageFactor=4
TechnicalExcellence=1
PoorEducation=0
Possession0=Germany
UnknownFutureField=preserve me
[Nation1]
Name=France
Name2=French
"""


class CustomNationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.install = self.root / "Rule the Waves 3"
        data = self.install / "Data"
        data.mkdir(parents=True)
        (data / "BNat1890.dat").write_text(TEMPLATE, encoding="cp1252")
        (data / "BNat1920.dat").write_text(TEMPLATE, encoding="cp1252")
        (data / "GermanyWarInfo.dat").write_bytes(b"normal war data")
        (data / "GermanyWarInfo20.dat").write_bytes(b"modern war data")

    def config(self):
        template = load_era_templates(self.install)["n00"]["Germany"]
        config = config_from_template(template)
        config.name = "Test Republic"
        config.adjective = "Test"
        config.flag_code = "TR"
        return config

    def test_parse_and_render_preserve_unknown_template_fields(self):
        path = self.install / "Data" / "BNat1890.dat"
        templates = parse_nation_templates(path)
        self.assertEqual([item.name for item in templates], ["Germany", "France"])
        rendered = render_nation_file(templates[0], self.config())
        self.assertIn("[Nation]\r\n", rendered)
        self.assertIn("Name=Test Republic\r\n", rendered)
        self.assertIn("FlagFileName=TR.bmp\r\n", rendered)
        self.assertIn("Possession0=Germany\r\n", rendered)
        self.assertIn("UnknownFutureField=preserve me\r\n", rendered)
        self.assertIn("Research1Advantage=0\r\n", rendered)
        self.assertIn("Guns2=9\r\n", rendered)

    def test_default_ship_names_cover_every_class_and_use_class_number(self):
        names = render_ship_names(30)
        for ship_class in SHIP_CLASSES:
            self.assertIn(f"[{ship_class}]", names)
            self.assertIn(f"{ship_class}-01", names)
            self.assertIn(f"{ship_class}-30", names)
        self.assertIn("KE-05", names)
        self.assertIn("CV-30", names)

    def test_export_creates_complete_two_era_package_and_flags(self):
        output = self.root / "Exports"
        package = export_custom_nation(self.config(), self.install, output)
        data = package / "Data"
        flags = package / "Flags"
        expected_data = {
            "Test Republic.n00", "Test Republic.n20",
            "Test RepublicShipNames.dat", "Test RepublicShipNames20.dat",
            "Test RepublicNames.txt", "Test RepublicWarInfo.dat",
            "Test RepublicWarInfo20.dat",
        }
        self.assertEqual({path.name for path in data.iterdir()}, expected_data)
        self.assertEqual((data / "Test RepublicWarInfo.dat").read_bytes(), b"normal war data")
        self.assertEqual((data / "Test RepublicWarInfo20.dat").read_bytes(), b"modern war data")
        self.assertTrue((package / "INSTALL.txt").is_file())
        self.assertTrue((package / "privateer-nation.json").is_file())
        for filename in ("TR.bmp", "TRF.bmp", "TRC.bmp", "TRR.bmp"):
            payload = (flags / filename).read_bytes()
            self.assertEqual(payload[:2], b"BM")
            self.assertEqual(struct.unpack_from("<ii", payload, 18), (60, 40))

    def test_export_refuses_to_overwrite_existing_package(self):
        output = self.root / "Exports"
        export_custom_nation(self.config(), self.install, output)
        with self.assertRaisesRegex(ValueError, "already exists"):
            export_custom_nation(self.config(), self.install, output)

    def test_validation_rejects_invalid_filename_and_unencodable_text(self):
        config = self.config()
        config.name = "Bad/Name"
        with self.assertRaisesRegex(ValueError, "filename"):
            config.validate()
        config.name = "Good Name"
        config.adjective = "Unsupported \U0001f680"
        with self.assertRaisesRegex(ValueError, "Windows text format"):
            config.validate()

    def test_custom_flag_validation_requires_stock_dimensions_and_format(self):
        flag = self.root / "flag.bmp"
        write_placeholder_bmp(flag, ((1, 2, 3), (4, 5, 6), (7, 8, 9)))
        validate_custom_flag(flag.read_bytes())
        payload = bytearray(flag.read_bytes())
        struct.pack_into("<i", payload, 18, 61)
        with self.assertRaisesRegex(ValueError, "60x40"):
            validate_custom_flag(payload)


if __name__ == "__main__":
    unittest.main()

