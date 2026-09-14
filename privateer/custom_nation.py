"""Build self-contained RTW3 custom-nation packages from installed templates."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import shutil
import struct
import tempfile


SHIP_CLASSES = ("BB", "BC", "CA", "CL", "DD", "KE", "AMC", "CV", "CVL", "SS", "XX")
ERA_FILES = {"n00": "BNat1890.dat", "n20": "BNat1920.dat"}
TRAIT_FIELDS = (
    "Cautious", "GlobalNavalPower", "AttentionToDetail", "TechnicalExcellence",
    "LiberalDemocracy", "EfficientShipbuildingIndustry",
    "UndevelopedShipbuildingIndustry", "PoorEducation", "Autocracy",
    "Bombastic", "Isolationist", "HiddenFlaws", "Colonies",
)
INVALID_FILE_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
RESERVED_FILE_NAMES = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                       *(f"LPT{i}" for i in range(1, 10))}


@dataclass(frozen=True)
class NationTemplate:
    name: str
    fields: tuple[tuple[str, str], ...]

    def value(self, key, default=""):
        return next((value for field, value in self.fields if field == key), default)


@dataclass
class CustomNationConfig:
    name: str
    adjective: str
    template_name: str
    leader: str
    leader_fascist: str
    leader_communist: str
    leader_republic: str
    admiral_rank: str
    admiral_name: str
    air_unit_name: str
    trouble_region: str
    build_area: str
    parliament_name: str
    government_type: int
    dock_size: int
    base_resources: int
    budget_modifier: int
    treaty_tonnage_factor: int
    flag_code: str
    ship_names_per_class: int = 99
    custom_flag_path: str = ""
    traits: dict[str, bool] | None = None
    research_advantages: dict[int, bool] | None = None
    gun_quality: dict[int, int] | None = None

    def validate(self):
        for value, label in (
                (self.name, "Nation name"), (self.adjective, "Adjective"),
                (self.template_name, "Template nation"), (self.admiral_rank, "Admiral rank"),
                (self.admiral_name, "Admiral name"), (self.build_area, "Build area")):
            if not str(value).strip():
                raise ValueError(f"{label} is required")
        if INVALID_FILE_CHARS.search(self.name) or self.name.endswith((".", " ")):
            raise ValueError("Nation name contains a character Windows cannot use in a filename")
        if self.name.split(".", 1)[0].upper() in RESERVED_FILE_NAMES:
            raise ValueError("Nation name is reserved by Windows and cannot be used as a filename")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,12}", self.flag_code):
            raise ValueError("Flag code must contain 1–12 letters, numbers, underscores, or hyphens")
        if self.government_type not in (0, 1, 2):
            raise ValueError("Government type must be 0, 1, or 2")
        for value, low, high, label in (
                (self.dock_size, 1000, 200000, "Dock size"),
                (self.base_resources, 100, 1000000, "Base resources"),
                (self.budget_modifier, 1, 100, "Budget modifier"),
                (self.treaty_tonnage_factor, 1, 20, "Treaty tonnage factor"),
                (self.ship_names_per_class, 1, 999, "Ship names per class")):
            if type(value) is not int or not low <= value <= high:
                raise ValueError(f"{label} must be between {low:,} and {high:,}")
        if self.custom_flag_path and not Path(self.custom_flag_path).is_file():
            raise ValueError("The selected custom flag does not exist")
        if any(type(area) is not int or not 1 <= area <= 22 or type(enabled) is not bool
               for area, enabled in (self.research_advantages or {}).items()):
            raise ValueError("Research advantages must use areas 1–22 and true/false values")
        if any(type(caliber) is not int or not 2 <= caliber <= 18 or
               quality not in (-2, -1, 0, 1, 9)
               for caliber, quality in (self.gun_quality or {}).items()):
            raise ValueError("Gun quality must use calibers 2–18 and supported RTW3 values")
        try:
            json.dumps(asdict(self), ensure_ascii=False).encode("cp1252")
        except UnicodeEncodeError as exc:
            raise ValueError(
                "Nation text contains characters RTW3's Windows text format cannot store") from exc


def _read_game_text(path):
    return Path(path).read_text(encoding="cp1252")


def parse_nation_templates(path) -> list[NationTemplate]:
    """Read ordered Nation sections without discarding unfamiliar fields."""
    templates = []
    name = None
    fields = []
    for raw in _read_game_text(path).splitlines():
        line = raw.strip()
        header = re.fullmatch(r"\[Nation\d+\]", line, re.IGNORECASE)
        if header:
            if name is not None:
                templates.append(NationTemplate(name, tuple(fields)))
            name, fields = "", []
            continue
        if name is not None and "=" in raw:
            key, value = raw.split("=", 1)
            fields.append((key.strip(), value.strip()))
            if key.strip() == "Name":
                name = value.strip()
    if name is not None:
        templates.append(NationTemplate(name, tuple(fields)))
    return [template for template in templates if template.name]


def load_era_templates(install_directory) -> dict[str, dict[str, NationTemplate]]:
    data = Path(install_directory) / "Data"
    result = {}
    for era, filename in ERA_FILES.items():
        path = data / filename
        if not path.is_file():
            raise ValueError(f"Required RTW3 nation template is missing: {path}")
        result[era] = {template.name: template for template in parse_nation_templates(path)}
    if not result["n00"]:
        raise ValueError("No nation templates were found in BNat1890.dat")
    return result


def config_from_template(template: NationTemplate) -> CustomNationConfig:
    value = template.value
    name = value("Name")
    initials = "".join(part[0] for part in re.findall(r"[A-Za-z0-9]+", name))[:6] or "NAT"
    traits = {field: value(field, "0") == "1" for field in TRAIT_FIELDS}
    return CustomNationConfig(
        name=f"New {name}", adjective=f"New {value('Name2', name)}",
        template_name=name, leader=value("Leader", "Head of Government"),
        leader_fascist=value("LeaderF", "Leader"),
        leader_communist=value("LeaderC", "General Secretary"),
        leader_republic=value("LeaderR", value("Leader", "President")),
        admiral_rank=value("AdmiralRank", "Admiral"),
        admiral_name=value("AdmiralName", "Commander"),
        air_unit_name=value("AirUnitName", "Squadron"),
        trouble_region=value("TroubleRegion", "overseas"),
        build_area=value("BuildAreaName", "Northern Europe"),
        parliament_name=value("ParliamentName", "Parliament"),
        government_type=int(value("GovernmentType", "0")),
        dock_size=int(value("DockSize", "10000")),
        base_resources=int(value("BaseResources", "10000")),
        budget_modifier=int(value("BudgetModifier", "15")),
        treaty_tonnage_factor=int(value("TreatyTonnageFactor", "3")),
        flag_code=initials.upper(), traits=traits,
        research_advantages={area: value(f"Research{area}Advantage", "0") == "1"
                             for area in range(1, 23)},
        gun_quality={caliber: int(value(f"Guns{caliber}", "9"))
                     for caliber in range(2, 19)},
    )


def _replace_fields(template: NationTemplate, replacements: dict[str, str]) -> list[tuple[str, str]]:
    result = []
    remaining = dict(replacements)
    seen = set()
    for key, value in template.fields:
        if key in seen and key in replacements:
            continue
        seen.add(key)
        result.append((key, remaining.pop(key, value)))
    result.extend(remaining.items())
    return result


def render_nation_file(template: NationTemplate, config: CustomNationConfig) -> str:
    config.validate()
    flags = {
        "FlagFileName": f"{config.flag_code}.bmp",
        "FlagFileNameF": f"{config.flag_code}F.bmp",
        "FlagFileNameC": f"{config.flag_code}C.bmp",
        "FlagFileNameR": f"{config.flag_code}R.bmp",
    }
    replacements = {
        "Name": config.name, "Name2": config.adjective,
        "Leader": config.leader, "LeaderF": config.leader_fascist,
        "LeaderC": config.leader_communist, "LeaderR": config.leader_republic,
        "AdmiralRank": config.admiral_rank, "AdmiralName": config.admiral_name,
        "AirUnitName": config.air_unit_name, "TroubleRegion": config.trouble_region,
        "BuildAreaName": config.build_area, "ParliamentName": config.parliament_name,
        "GovernmentType": str(config.government_type), "DockSize": str(config.dock_size),
        "BaseResources": str(config.base_resources),
        "BudgetModifier": str(config.budget_modifier),
        "TreatyTonnageFactor": str(config.treaty_tonnage_factor),
        "ShipPrefix": (config.adjective[:1] or config.name[:1]).upper(),
        **flags,
    }
    replacements.update({field: "1" if enabled else "0"
                         for field, enabled in (config.traits or {}).items()
                         if field in TRAIT_FIELDS})
    replacements.update({f"Research{area}Advantage": "1" if enabled else "0"
                         for area, enabled in (config.research_advantages or {}).items()})
    replacements.update({f"Guns{caliber}": str(quality)
                         for caliber, quality in (config.gun_quality or {}).items()})
    lines = ["[Nation]"]
    lines.extend(f"{key}={value}" for key, value in _replace_fields(template, replacements))
    return "\r\n".join(lines) + "\r\n"


def render_ship_names(count=99) -> str:
    if type(count) is not int or not 1 <= count <= 999:
        raise ValueError("Ship names per class must be between 1 and 999")
    width = max(2, len(str(count)))
    blocks = []
    for ship_class in SHIP_CLASSES:
        names = [f"{ship_class}-{number:0{width}d}" for number in range(1, count + 1)]
        blocks.append(f"[{ship_class}]\r\n" + "\r\n".join(names))
    blocks.extend((
        "[SSPrefix]\r\nSS-",
        "[DDPrefix]\r\nDD-",
        "[Aircraft manufacturers]\r\nNational Aircraft Works;NAW",
        "[Helicopter manufacturers]\r\nNational Rotor Works;NRW",
        "[Aircraft names]\r\n" + "\r\n".join(
            f"Aircraft-{number:0{width}d}" for number in range(1, count + 1)),
    ))
    return "\r\n\r\n".join(blocks) + "\r\n"


def render_officer_names(count=200) -> str:
    return "\r\n".join(f"Officer-{number:03d}" for number in range(1, count + 1)) + "\r\n"


def write_placeholder_bmp(path, colors):
    """Write the 60x40, 24-bit BMP shape used by stock RTW3 flags."""
    width, height = 60, 40
    row_size = (width * 3 + 3) & ~3
    pixels = bytearray()
    for y in range(height):
        color = colors[min(2, (height - 1 - y) * 3 // height)]
        bgr = bytes((color[2], color[1], color[0]))
        pixels.extend(bgr * width)
        pixels.extend(b"\x00" * (row_size - width * 3))
    header = b"BM" + struct.pack("<IHHI", 54 + len(pixels), 0, 0, 54)
    header += struct.pack("<IIIHHIIIIII", 40, width, height, 1, 24, 0,
                          len(pixels), 2835, 2835, 0, 0)
    Path(path).write_bytes(header + pixels)


def validate_custom_flag(payload):
    if len(payload) < 54 or payload[:2] != b"BM":
        raise ValueError("Custom flag must be a Windows BMP file")
    width, height, planes, bits, compression = struct.unpack_from("<iiHHI", payload, 18)
    if (width, abs(height), planes, bits, compression) != (60, 40, 1, 24, 0):
        raise ValueError("Custom flag must be an uncompressed 60x40, 24-bit Windows BMP")


def _copy_war_info(data_directory: Path, template_name: str, destination: Path, stem: str):
    normal = data_directory / f"{template_name}WarInfo.dat"
    modern = data_directory / f"{template_name}WarInfo20.dat"
    if not normal.is_file():
        raise ValueError(f"WarInfo template is missing for {template_name}: {normal}")
    shutil.copy2(normal, destination / f"{stem}WarInfo.dat")
    shutil.copy2(modern if modern.is_file() else normal,
                 destination / f"{stem}WarInfo20.dat")


def export_custom_nation(config: CustomNationConfig, install_directory, output_parent) -> Path:
    """Create a ready-to-install package without modifying the game installation."""
    config.validate()
    install = Path(install_directory).resolve()
    output_parent = Path(output_parent).resolve()
    templates = load_era_templates(install)
    era_templates = {}
    for era, choices in templates.items():
        if config.template_name not in choices:
            raise ValueError(
                f"{config.template_name} is not available in {ERA_FILES[era]}")
        era_templates[era] = choices[config.template_name]
    package = output_parent / f"{config.name} - Privateer Nation"
    if package.exists():
        raise ValueError(f"Output folder already exists: {package}")
    output_parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".privateer-nation-", dir=output_parent))
    try:
        data = temporary / "Data"
        flags = temporary / "Flags"
        data.mkdir()
        flags.mkdir()
        stem = config.name
        for era, template in era_templates.items():
            (data / f"{stem}.{era}").write_text(
                render_nation_file(template, config), encoding="cp1252", newline="")
        names = render_ship_names(config.ship_names_per_class)
        (data / f"{stem}ShipNames.dat").write_text(names, encoding="cp1252", newline="")
        (data / f"{stem}ShipNames20.dat").write_text(names, encoding="cp1252", newline="")
        (data / f"{stem}Names.txt").write_text(
            render_officer_names(), encoding="cp1252", newline="")
        _copy_war_info(install / "Data", config.template_name, data, stem)

        palettes = {
            "": ((18, 48, 91), (238, 190, 52), (245, 245, 245)),
            "F": ((35, 35, 35), (145, 26, 26), (225, 225, 225)),
            "C": ((170, 18, 28), (235, 193, 35), (170, 18, 28)),
            "R": ((32, 79, 145), (245, 245, 245), (32, 79, 145)),
        }
        for suffix, colors in palettes.items():
            destination = flags / f"{config.flag_code}{suffix}.bmp"
            if suffix == "" and config.custom_flag_path:
                payload = Path(config.custom_flag_path).read_bytes()
                validate_custom_flag(payload)
                destination.write_bytes(payload)
            else:
                write_placeholder_bmp(destination, colors)

        manifest = {
            "format": 1, "generator": "Privateer Custom Nation Maker",
            "nation": config.name, "template_nation": config.template_name,
            "era_files": {"1890/1900": f"{stem}.n00", "1920/1935": f"{stem}.n20"},
            "inherited_map_identity": config.template_name,
        }
        (temporary / "privateer-nation.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        instructions = (
            f"{config.name} — RTW3 custom nation package\r\n\r\n"
            "1. Close Rule the Waves 3.\r\n"
            "2. Back up the game's Data and Flags folders.\r\n"
            "3. Copy this package's Data contents into the game's Data folder.\r\n"
            "4. Copy this package's Flags contents into the game's Flags folder.\r\n"
            "5. Start a NEW campaign and select the nation from the custom-nation list.\r\n\r\n"
            f"This nation inherits possessions, relationships, bonus technology, gun settings,\r\n"
            f"and WarInfo from {config.template_name}. Existing campaigns are not converted.\r\n"
            "Generated placeholder flags may be replaced with 60x40 24-bit BMP files using\r\n"
            "the same filenames. Keep this package as the uninstall/reinstall reference.\r\n"
        )
        (temporary / "INSTALL.txt").write_text(instructions, encoding="cp1252", newline="")
        temporary.replace(package)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return package

