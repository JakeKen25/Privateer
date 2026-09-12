from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
from pathlib import Path
import hashlib
import random
import re
import shutil
import tempfile

from .document import FIELD, PrefixedRecord, Section, TextDocument
from .model import Nation, Ship, ShipDesign, TechnologyState, _integer, adjusted_integer
from .guns import GUN_CALIBERS, GUN_QUALITIES, gun_quality
from .validation import SaveValidationError, ValidationReport

NATION = re.compile(r"^Nation(\d+)$", re.I)
NATION_SHIP = re.compile(r"^Nation(\d+)Ship(\d+)$", re.I)
NATION_SHIPS = re.compile(r"^Nation(\d+)Ships$", re.I)
FLAT_SHIP_KEY = re.compile(r"^Ship(?P<slot>\d+)(?P<field>.+)$")
SHIP = re.compile(r"^Ship(\d+)$", re.I)
DESIGN = re.compile(r"^ShipDesign(\d+)$", re.I)
POSITIONAL_DESIGN = re.compile(r"^ShipDesign(\d+)\s*$", re.I)
TECH_PREFIXES = ("tech", "research", "unlock")


class RTW3Save:
    """In-memory save folder and structured mutation API."""

    def __init__(self, folder: Path, documents: dict[str, TextDocument], main_file: str):
        self.folder, self.documents, self.main_file = folder, documents, main_file
        self.nations: list[Nation] = []
        self.modified = False
        self.audit: list[str] = []
        self.player_detection_warning: str | None = None
        self._tension_changes = False
        self._colony_changes = False
        self._source_snapshot = None
        self._build_model()

    @classmethod
    def load(cls, folder: str | Path) -> "RTW3Save":
        path = Path(folder).expanduser().resolve()
        if not path.is_dir():
            raise ValueError(f"Save folder does not exist: {path}")
        source_snapshot = cls._folder_snapshot(path)
        candidates = sorted(path.glob("*.bcs"))
        if not candidates:
            raise ValueError("Folder is not an RTW3 save: no .bcs main save was found")
        numbered = [f for f in candidates if re.fullmatch(r"RTWGame\d+\.bcs", f.name, re.I)]
        preferred = [f for f in numbered if f.stem.casefold() == f"rtw{path.name}".casefold()]
        if len(preferred) == 1:
            main = preferred[0]
        elif len(numbered) == 1:
            main = numbered[0]
        elif not numbered and len(candidates) == 1:
            main = candidates[0]
        else:
            raise ValueError("Ambiguous campaign files: select a folder with one numbered RTWGameX.bcs")
        documents: dict[str, TextDocument] = {}
        text_files = [main, *sorted(path.glob("*.des"))]
        slot = re.fullmatch(r"RTWGame(\d+)\.bcs", main.name, re.I)
        if slot:
            maps = [f for f in path.iterdir() if f.is_file() and f.name.casefold() == f"mapdata{slot.group(1)}.dat"]
            if len(maps) > 1:
                raise ValueError("Ambiguous map data files")
            text_files.extend(maps)
        for file in dict.fromkeys(text_files):
            payload = file.read_bytes()
            has_bom = payload.startswith(b"\xef\xbb\xbf")
            try:
                text = payload.decode("utf-8-sig" if has_bom else "utf-8")
                encoding = "utf-8"
            except UnicodeDecodeError:
                text = payload.decode("cp1252")
                encoding = "cp1252"
                has_bom = False
            documents[file.name] = TextDocument.parse(
                text, encoding=encoding, has_bom=has_bom
            )
        save = cls(path, documents, main.name)
        if not save.nations:
            raise ValueError("Unsupported RTW3 save: no [NationN] sections were found")
        save._source_snapshot = source_snapshot
        if cls._folder_snapshot(path) != source_snapshot:
            raise ValueError("Save files changed while loading; reload the save")
        return save

    @staticmethod
    def _folder_snapshot(folder):
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in folder.iterdir() if p.is_file()}

    def _check_tension_source(self):
        if (self._tension_changes or self._colony_changes) and self._source_snapshot != self._folder_snapshot(self.folder):
            raise ValueError("Save files changed on disk since loading. Reload before saving relations or colony edits.")

    def set_colony_owners(self, changes):
        from .colonies import set_owners
        set_owners(self, changes)

    def set_tensions(self, changes):
        from .diplomacy import set_tensions
        set_tensions(self, changes)

    def _build_model(self) -> None:
        main = self.documents[self.main_file]
        for section in main.sections:
            match = NATION.match(section.name)
            if not match:
                continue
            index = int(match.group(1)); values = section.fields()
            tech = {k: self._coerce(v) for k, v in values.items() if k.casefold().startswith(TECH_PREFIXES)}
            self.nations.append(Nation(index, values.get("Name", f"Nation{index}"), section,
                _integer(values, "Funds"), _integer(values, "BaseResources"),
                _integer(values, "BudgetModifier"), TechnologyState(tech)))
        by_index = {nation.index: nation for nation in self.nations}
        for section in main.sections:
            roster = NATION_SHIPS.match(section.name)
            if roster:
                owner = int(roster.group(1))
                if owner in by_index:
                    self._parse_flat_ship_roster(section, by_index[owner])
                continue
            match = NATION_SHIP.match(section.name) or SHIP.match(section.name)
            if not match:
                continue
            values = section.fields()
            if len(match.groups()) == 2:
                owner, record = map(int, match.groups())
            else:
                record = int(match.group(1)); owner = _integer(values, "OwnerNationIdx", "NationIdx")
            if owner not in by_index:
                continue
            design = _integer(values, "ShipDesignRefId", "DesignId")
            build = _integer(values, "BuildingNationIdx")
            uc = str(values.get("UnderConstruction", values.get("Status", "0"))).casefold() in {"1", "true", "yes", "building", "under construction"}
            by_index[owner].ships.append(Ship(record, owner, values.get("Name", f"Ship{record}"),
                values.get("Type") or values.get("ShipType"), values.get("Class") or values.get("ClassName"),
                design, build, uc, section))
        # A DesignFilesN-style filename assigns the library; otherwise use NationIdx.
        for filename, document in self.documents.items():
            file_owner = self._file_nation_index(filename)
            if file_owner in by_index and filename.casefold().endswith(".des"):
                positional = self._parse_positional_designs(filename, document)
                if positional is not None:
                    by_index[file_owner].designs.extend(positional)
                    continue
            for section in document.sections:
                match = DESIGN.match(section.name)
                if not match:
                    continue
                fields = section.fields()
                owner = file_owner if file_owner is not None else _integer(fields, "NationIdx", "OwnerNationIdx")
                if owner in by_index:
                    by_index[owner].designs.append(ShipDesign.from_section(int(match.group(1)), section, filename))
        self._detect_player()

    @staticmethod
    def _parse_positional_designs(
        filename: str, document: TextDocument
    ) -> list[ShipDesign] | None:
        """Parse a v10139 design library without normalizing its source text."""
        lines = document.render().splitlines(keepends=True)
        if not lines or lines[0].strip().casefold() != "v10139":
            return None
        if len(lines) < 2:
            raise ValueError(f"Malformed design library {filename}: missing record count")
        try:
            declared_count = int(lines[1].strip())
        except ValueError as error:
            raise ValueError(
                f"Malformed design library {filename}: record count is not an integer"
            ) from error

        starts: list[tuple[int, int]] = []
        for line_index, line in enumerate(lines[2:], start=2):
            match = POSITIONAL_DESIGN.fullmatch(line)
            if match:
                starts.append((line_index, int(match.group(1))))
        if len(starts) != declared_count:
            raise ValueError(
                f"Malformed design library {filename}: declares {declared_count} records "
                f"but contains {len(starts)}"
            )
        expected_ordinals = list(range(declared_count))
        ordinals = [ordinal for _, ordinal in starts]
        if ordinals != expected_ordinals:
            raise ValueError(
                f"Malformed design library {filename}: expected ShipDesign ordinals "
                f"0..{declared_count - 1}, found {ordinals}"
            )

        designs: list[ShipDesign] = []
        for position, (start, ordinal) in enumerate(starts):
            end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
            designs.append(
                ShipDesign.from_positional_record(ordinal, lines[start:end], filename)
            )
        return designs

    @staticmethod
    def _parse_flat_ship_roster(section: Section, nation: Nation) -> None:
        """Parse every ``ShipN`` record in a real ``[NationNShips]`` section."""
        slots: dict[int, dict[str, str]] = {}
        for key, value in section.fields().items():
            match = FLAT_SHIP_KEY.match(key)
            if match:
                slots.setdefault(int(match.group("slot")), {})[match.group("field")] = value

        for slot in sorted(slots):
            values = slots[slot]
            ship_id = _integer(values, "Id")
            if ship_id is None:
                raise ValueError(
                    f"Unsupported RTW3 ship record: [{section.name}] Ship{slot} "
                    "has fields but no integer Id"
                )
            design = _integer(values, "DesignRefId")
            build = _integer(values, "BuildingNationIdx")
            in_play = str(values.get("InPlay", "1")).casefold() in {"1", "true", "yes"}
            record = PrefixedRecord(section, f"Ship{slot}")
            nation.ships.append(Ship(
                ship_id,
                nation.index,
                values.get("Name", f"Ship{ship_id}"),
                values.get("ShipType") or values.get("Type"),
                values.get("Classname") or values.get("ClassName") or values.get("Class"),
                design,
                build,
                not in_play,
                record,
                local_slot=slot,
                flattened_record=True,
            ))

    @staticmethod
    def _file_nation_index(filename: str) -> int | None:
        match = re.search(r"(?:DesignFiles|Nation)(\d+)", filename, re.I)
        return int(match.group(1)) if match else None

    @staticmethod
    def _coerce(value: str):
        if value.casefold() in {"true", "false"}: return value.casefold() == "true"
        try: return int(value)
        except ValueError: return value

    def _detect_player(self) -> None:
        explicit: list[Nation] = []
        for nation in self.nations:
            fields = {k.casefold(): v.casefold() for k, v in nation.section.fields().items()}
            if any(fields.get(key) in {"1", "true", "yes"} for key in ("isplayer", "player", "playernation")):
                explicit.append(nation)
        if len(explicit) == 1:
            explicit[0].is_player = True
        else:
            fallback = next((n for n in self.nations if n.index == 0), None)
            if fallback: fallback.is_player = True
            self.player_detection_warning = ("Multiple player flags found; Nation0 fallback used" if explicit
                                              else "No explicit player field found; Nation0 fallback used")

    def nation(self, value: str | int | Nation) -> Nation:
        if isinstance(value, Nation): return value
        found = next((n for n in self.nations if n.index == value or n.name.casefold() == str(value).casefold()), None)
        if not found: raise KeyError(f"Unknown nation: {value}")
        return found

    def get_ships(self, owner=None, ship_type: str | None = None) -> list[Ship]:
        nations = [self.nation(owner)] if owner is not None else self.nations
        return [ship for nation in nations for ship in nation.ships
                if ship_type is None or (ship.ship_type or "").casefold() == ship_type.casefold()]

    @contextmanager
    def transaction(self):
        snapshot = deepcopy((self.documents, self.nations, self.modified, self.audit))
        try:
            yield self
        except Exception:
            self.documents, self.nations, self.modified, self.audit = snapshot
            raise

    def transfer_ships(self, ships: list[Ship], destination, *, force_building_nation_to_owner: bool = True) -> None:
        if any(ship.flattened_record for ship in ships):
            raise NotImplementedError(
                "Transfers for flattened [NationNShips] records are disabled until "
                "physical roster movement and positional .des cloning are implemented"
            )
        destination = self.nation(destination)
        with self.transaction():
            for ship in list(dict.fromkeys(id(s) for s in ships)):
                actual = next(s for s in ships if id(s) == ship)
                source = self.nation(actual.owner_index)
                if source is destination: continue
                design = next((d for d in source.designs if d.record_index == actual.design_ref_id and d.internal_design_id == actual.design_ref_id), None)
                if design is None:
                    raise ValueError(f'Ship "{actual.name}" references unresolved design ID {actual.design_ref_id} in {source.name}')
                existing = next((d for d in destination.designs if d.signature() == design.signature()), None)
                if existing is None:
                    new_id = max((d.record_index for d in destination.designs), default=-1) + 1
                    copied = design.clone(new_id, self.documents[design.source_file].newline)
                    target_file = destination.designs[0].source_file if destination.designs else design.source_file
                    copied.source_file = target_file
                    self.documents[target_file].add_section(copied.section)
                    destination.designs.append(copied); existing = copied
                    self.audit.append(f"Copied design {design.record_index} from {source.name} to {destination.name} as {new_id}")
                actual.set_design(existing.record_index, self.documents[self.main_file].newline)
                source.ships.remove(actual); destination.ships.append(actual); actual.owner_index = destination.index
                actual.section.set("OwnerNationIdx", destination.index, self.documents[self.main_file].newline)
                if force_building_nation_to_owner:
                    actual.building_nation_index = destination.index
                    actual.section.set("BuildingNationIdx", destination.index, self.documents[self.main_file].newline)
                self.audit.append(f"Transferred {actual.name}: {source.name} -> {destination.name}")
            for nation in self.nations: nation.sync_ship_count(self.documents[self.main_file].newline)
            report = self.validate()
            if not report.valid: raise SaveValidationError(report)
            self.modified = True

    def distribute_randomly(self, ships: list[Ship], eligible_nations: list[Nation], seed: int) -> None:
        rng = random.Random(seed)
        self.audit.append(f"Random distribution seed: {seed}")
        for ship in ships: self.transfer_ships([ship], rng.choice(eligible_nations))

    def copy_technology(self, source, destination) -> None:
        source, destination = self.nation(source), self.nation(destination)
        for key, value in source.technology.fields.items(): destination.section.set(key, value, self.documents[self.main_file].newline)
        destination.technology = deepcopy(source.technology); self.modified = True

    def adjust_economy(
        self,
        nation,
        *,
        funds: tuple[str, str] | None = None,
        base_resources: tuple[str, str] | None = None,
    ) -> None:
        """Apply optional funds/resource edits as one in-memory transaction."""
        target = self.nation(nation)
        newline = self.documents[self.main_file].newline
        with self.transaction():
            if funds is not None:
                previous = target.funds
                target.set_funds(adjusted_integer(previous, *funds), newline)
                self.audit.append(f"Changed {target.name} Funds: {previous} -> {target.funds}")
            if base_resources is not None:
                previous = target.base_resources
                target.set_base_resources(adjusted_integer(previous, *base_resources), newline)
                self.audit.append(
                    f"Changed {target.name} BaseResources: {previous} -> {target.base_resources}"
                )
            self.validate_or_raise()
            self.modified = True

    def set_gun_qualities(self, nation, changes):
        """Validate the complete batch before editing existing gun fields only."""
        target = self.nation(nation)
        fields = target.section.fields()
        for caliber, quality in changes.items():
            if type(caliber) is not int or caliber not in GUN_CALIBERS:
                raise ValueError(f"Unsupported gun caliber: {caliber}")
            if type(quality) is not int or quality not in GUN_QUALITIES:
                raise ValueError(f"Unsupported gun quality: {quality}")
            if gun_quality(fields, caliber) is None:
                raise ValueError(f"Missing or invalid Guns{caliber} field")
        with self.transaction():
            for caliber, quality in changes.items():
                key = f"Guns{caliber}"
                if gun_quality(fields, caliber) == quality:
                    continue
                target.section.set(key, quality, self.documents[self.main_file].newline)
                self.audit.append(f"Changed {target.name} {key}: {fields[key]} -> {quality}")
                self.modified = True

    def set_technology_flags(self, nation, database, changes):
        """Apply only explicitly edited, defined possession flags atomically."""
        target = self.nation(nation)
        allowed = {tech.key for tech in database}
        fields = target.section.fields()
        for key, value in changes.items():
            if key not in allowed:
                raise ValueError(f"Undefined technology: {key}")
            if type(value) is not int or value not in (0, 1):
                raise ValueError(f"Technology possession must be 0 or 1: {key}")
            if fields.get(key) not in ("0", "1"):
                raise ValueError(f"Missing or unsupported save field: {key}")
        with self.transaction():
            for key, value in changes.items():
                if fields[key] == str(value):
                    continue
                target.section.set(key, value, self.documents[self.main_file].newline)
                target.technology.fields[key] = value
                self.audit.append(f"Changed {target.name} {key}: {fields[key]} -> {value}")
                self.modified = True

    def set_maximum_technology(self, nation, maximum: int = 100) -> None:
        raise NotImplementedError(
            "Maximum technology is disabled until an RTW3 format profile defines "
            "all required fields, valid ranges, and unlock dependencies"
        )

    def validate(self) -> ValidationReport:
        report = ValidationReport(sum(len(n.ships) for n in self.nations))
        seen: set[int] = set()
        for nation in self.nations:
            count = _integer(nation.section.fields(), "ShipCount")
            if count is not None and count != len(nation.ships): report.add("ship_count", f"{nation.name}: stored {count}, actual {len(nation.ships)}")
            design_ids: dict[int, ShipDesign] = {}
            for design in nation.designs:
                if design.positional_record is None and design.record_index != design.internal_design_id:
                    report.add("internal_design_id", f"{nation.name} design {design.record_index} internally identifies as {design.internal_design_id}")
                    # A mismatched record cannot resolve a reference merely because
                    # its external section label happens to match.
                    continue
                if design.internal_design_id in design_ids: report.add("duplicate_design_id", f"{nation.name} has duplicate design {design.internal_design_id}")
                design_ids[design.internal_design_id] = design
            for ship in nation.ships:
                if ship.record_index in seen: report.add("duplicate_ship_id", f"Duplicate ship ID {ship.record_index}")
                seen.add(ship.record_index)
                design = design_ids.get(ship.design_ref_id)
                if design is None: report.add("missing_design", f'{nation.name} ship "{ship.name}" references design {ship.design_ref_id}')
                else:
                    report.resolved_design_refs += 1
                    if ship.ship_type and design.ship_type and ship.ship_type.casefold() != design.ship_type.casefold(): report.add("type_mismatch", f'{ship.name}: {ship.ship_type} ship uses {design.ship_type} design')
            for key, value in nation.section.fields().items():
                if re.fullmatch(r"Research\d+Level\d+", key, re.I) and value not in ("0", "1"):
                    report.add("technology_flag", f"{nation.name} {key} must be 0 or 1")
            for label, value in (("Funds", nation.funds), ("BaseResources", nation.base_resources)):
                if value is not None and not -(2**31) <= value <= 2**31 - 1: report.add("integer_range", f"{nation.name} {label} exceeds signed 32-bit range")
        return report

    def validate_or_raise(self) -> None:
        report = self.validate()
        if not report.valid: raise SaveValidationError(report)

    def save_as(self, destination: str | Path) -> Path:
        self._check_tension_source()
        self.validate_or_raise(); destination = Path(destination).resolve()
        if destination.exists(): raise FileExistsError(f"Destination already exists: {destination}")
        temporary = Path(tempfile.mkdtemp(prefix=f".{destination.name}-", dir=destination.parent))
        try:
            shutil.copytree(self.folder, temporary, dirs_exist_ok=True)
            self._write_documents(temporary)
            RTW3Save.load(temporary).validate_or_raise()
            self._check_tension_source()
            temporary.replace(destination)
        except Exception:
            shutil.rmtree(temporary, ignore_errors=True); raise
        return destination

    def save(self) -> Path:
        self._check_tension_source()
        self.validate_or_raise()
        stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S_%f")
        backup = self.folder.with_name(f"{self.folder.name}_backup_{stamp}")
        shutil.copytree(self.folder, backup)
        temporary = Path(tempfile.mkdtemp(prefix=".privateer-", dir=self.folder.parent))
        try:
            shutil.copytree(self.folder, temporary, dirs_exist_ok=True); self._write_documents(temporary)
            RTW3Save.load(temporary).validate_or_raise()
            self._check_tension_source()
            for name in self.documents: (temporary / name).replace(self.folder / name)
            (temporary / "RTW3_SAVE_EDITOR_LOG.txt").replace(self.folder / "RTW3_SAVE_EDITOR_LOG.txt")
        finally: shutil.rmtree(temporary, ignore_errors=True)
        self.modified = False
        self._source_snapshot = self._folder_snapshot(self.folder)
        return backup

    def _write_documents(self, folder: Path) -> None:
        for name, document in self.documents.items():
            payload = document.to_bytes()
            (folder / name).write_bytes(payload)
            if (folder / name).read_bytes() != payload:
                raise ValueError(f"Written save verification failed: {name}")
        (folder / "RTW3_SAVE_EDITOR_LOG.txt").write_text("RTW3 Save Editor\n\n" + "\n".join(self.audit), encoding="utf-8")
