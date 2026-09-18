"""Lossless aircraft-model creation for RTW3's flattened AircraftTypes section."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .document import FIELD, Section, TextDocument
from .aircraft_game6_averages import FIELD_NAMES
from .aircraft_year_defaults import YEAR_DEFAULTS


ROLE_NAMES = {
    0: "Fighter", 1: "Dive bomber", 2: "Torpedo bomber",
    3: "Floatplane", 4: "Patrol aircraft", 5: "Medium bomber",
    10: "Light jet", 11: "Heavy jet", 12: "Attack jet", 13: "Helicopter",
}

EDITABLE_NUMERIC_FIELDS = (
    "Year", "BaseModelYear", "CruiseAltitude", "MaxFuel", "Ceiling", "Climb",
    "MaxSpeed", "CruiseSpeed", "LtEndurance",
    "MedEndurance", "HvyEndurance", "Firepower", "Maneuver", "Toughness",
    "Reliability", "LtBombLoadSize", "LtBombLoadNumber", "MedBombLoadSize",
    "MedBombLoadNumber", "HvyBombLoadSize", "HvyBombLoadNumber",
    "Torpedo1", "Torpedo2", "Missile2", "Radar", "Special", "Bombing",
    "Carrier", "Floatplane",
    "AvailableAircraft",
)

AT_KEY = re.compile(r"^AT(?P<slot>\d+)(?P<field>[A-Za-z].*)$")


@dataclass(frozen=True)
class AircraftType:
    slot: int
    fields: dict[str, str]

    @property
    def name(self) -> str:
        return f"{self.fields.get('Manufacturer', '')} {self.fields.get('Name', '')}".strip()

    @property
    def role(self) -> str:
        purpose = int(self.fields["Purpose"])
        return ROLE_NAMES.get(purpose, f"Role {purpose}")


def _aircraft_section(save) -> Section:
    sections = [section for section in save.documents[save.main_file].sections
                if section.name.casefold() == "aircrafttypes"]
    if len(sections) != 1:
        raise ValueError("This save needs exactly one [AircraftTypes] section")
    return sections[0]


def campaign_year(save) -> int:
    sections = [section for section in save.documents[save.main_file].sections
                if section.name.casefold() == "general"]
    if len(sections) != 1:
        raise ValueError("This save needs exactly one [General] section for aircraft design year")
    raw = sections[0].fields().get("Year", "")
    try:
        year = int(raw)
    except ValueError as error:
        raise ValueError("[General] has no valid Year field") from error
    if not 1800 <= year <= 2200:
        raise ValueError("Campaign year must be from 1800 to 2200")
    return year


def manufacturers_for_nation(types: list[AircraftType], nation_index: int) -> list[str]:
    names = {model.fields["Manufacturer"].strip() for model in types
             if int(model.fields["Nation"]) == nation_index and model.fields["Manufacturer"].strip()}
    return ["Privateer", *sorted((name for name in names if name.casefold() != "privateer"),
                                 key=str.casefold)]


def suggested_template(types: list[AircraftType], purpose: int, nation_index: int,
                       year: int) -> AircraftType:
    if not types:
        raise ValueError("This save has no aircraft models to use as a template")
    matching = [model for model in types if int(model.fields["Purpose"]) == purpose]
    candidates = matching or types
    return min(candidates, key=lambda model: (
        int(model.fields["Nation"]) != nation_index,
        abs(int(model.fields["Year"]) - year),
        -int(model.fields["Year"]),
        model.slot,
    ))


def aircraft_year_range(purpose: int) -> tuple[int, int]:
    """Return the available equivalent-year bounds for this aircraft type."""
    if purpose not in YEAR_DEFAULTS:
        raise ValueError("Choose a supported aircraft type")
    return min(YEAR_DEFAULTS[purpose]), max(YEAR_DEFAULTS[purpose])


def average_defaults(purpose: int, year: int) -> dict[str, str]:
    """Read the stored row for this aircraft type and exact campaign year."""
    if purpose not in YEAR_DEFAULTS:
        raise ValueError("Choose a supported aircraft type")
    try:
        row = YEAR_DEFAULTS[purpose][year]
    except KeyError as error:
        raise ValueError("Equivalent year is outside the table for this aircraft type") from error
    return dict(zip(FIELD_NAMES, map(str, row)))


def validate_aircraft_only_changes(save) -> None:
    """Prove that the loaded save differs from disk only by newly added models.

    Some real campaigns contain unrelated fleet-design validation issues. This
    check permits an aircraft-only write while retaining exact comparison of
    every other loaded file and save section.
    """
    main = save.documents[save.main_file]
    source = (save.folder / save.main_file).read_bytes()
    encoding = "utf-8-sig" if main.has_bom else main.encoding
    original = TextDocument.parse(
        source.decode(encoding), encoding=main.encoding, has_bom=main.has_bom)
    if original.preamble != main.preamble or len(original.sections) != len(main.sections):
        raise ValueError("Aircraft-only write cannot include other save changes")
    if any(document.to_bytes() != (save.folder / name).read_bytes()
           for name, document in save.documents.items() if name != save.main_file):
        raise ValueError("Aircraft-only write cannot include changes to other save files")
    old_general = new_general = old_aircraft = new_aircraft = None
    for before, after in zip(original.sections, main.sections):
        if before.name != after.name or before.header != after.header:
            raise ValueError("Aircraft-only write cannot change save sections")
        name = before.name.casefold()
        if name == "general":
            old_general, new_general = before, after
        elif name == "aircrafttypes":
            old_aircraft, new_aircraft = before, after
        else:
            if before.lines != after.lines:
                raise ValueError("Aircraft-only write cannot change non-aircraft save sections")
            continue
        if len(after.lines) < len(before.lines):
            raise ValueError("Aircraft-only write cannot remove existing fields")
        if name == "general" and len(after.lines) != len(before.lines):
            raise ValueError("Aircraft-only write cannot add general save fields")
        for old_line, new_line in zip(before.lines, after.lines):
            old_match, new_match = FIELD.match(old_line), FIELD.match(new_line)
            old_key = old_match.group(2).strip().casefold() if old_match else None
            new_key = new_match.group(2).strip().casefold() if new_match else None
            allowed = "idno" if name == "general" else "actypesno"
            if old_key == new_key == allowed:
                continue
            if old_line != new_line:
                raise ValueError("Aircraft-only write cannot modify existing save fields")
    if None in (old_general, new_general, old_aircraft, new_aircraft):
        raise ValueError("Aircraft-only write needs General and AircraftTypes sections")
    old_count = int(old_aircraft.fields()["ACTypesNo"])
    old_counter = int(old_general.fields()["IDNo"])
    new_count = int(new_aircraft.fields()["ACTypesNo"])
    new_counter = int(new_general.fields()["IDNo"])
    if new_count <= old_count:
        raise ValueError("Aircraft-only write has no new aircraft models")
    for line in new_aircraft.lines[len(old_aircraft.lines):]:
        match = FIELD.match(line)
        record = AT_KEY.fullmatch(match.group(2).strip()) if match else None
        if record is None or not old_count <= int(record.group("slot")) < new_count:
            raise ValueError("Aircraft-only write has an unexpected new aircraft field")
    models = aircraft_types(save)
    old_ids = [int(value) for key, value in old_aircraft.fields().items()
               if re.fullmatch(r"AT\d+Id", key)]
    first_id = max(old_counter, max(old_ids, default=-1) + 1)
    new_ids = [int(model.fields["Id"]) for model in models[old_count:]]
    if new_ids != list(range(first_id, first_id + new_count - old_count)):
        raise ValueError("New aircraft IDs do not follow the global allocation counter")
    if new_counter != first_id + new_count - old_count:
        raise ValueError("[General] IDNo does not match newly allocated aircraft IDs")


def aircraft_types(save) -> list[AircraftType]:
    """Read models and reject ambiguous or inconsistent flattened records."""
    section = _aircraft_section(save)
    count = section.fields().get("ACTypesNo")
    if count is None or not count.isdecimal():
        raise ValueError("[AircraftTypes] has no valid ACTypesNo count")
    records: dict[int, dict[str, str]] = {}
    seen: set[str] = set()
    for line in section.lines:
        match = FIELD.match(line)
        if not match:
            continue
        key = match.group(2).strip()
        record = AT_KEY.fullmatch(key)
        if not record:
            continue
        if key.casefold() in seen:
            raise ValueError(f"Duplicate aircraft field: {key}")
        seen.add(key.casefold())
        records.setdefault(int(record.group("slot")), {})[record.group("field")] = match.group(4).strip()
    expected = list(range(int(count)))
    if sorted(records) != expected:
        raise ValueError("Aircraft model slots do not match ACTypesNo")
    ids: set[int] = set()
    result = []
    for slot in expected:
        fields = records[slot]
        missing = {"Name", "Manufacturer", "Year", "Purpose", "Nation", "Id"} - fields.keys()
        if missing:
            raise ValueError(f"AT{slot} is missing {', '.join(sorted(missing))}")
        try:
            model_id = int(fields["Id"])
            int(fields["Purpose"])
            int(fields["Nation"])
        except ValueError as error:
            raise ValueError(f"AT{slot} has an invalid ID, purpose, or nation") from error
        if model_id in ids:
            raise ValueError(f"Duplicate aircraft model ID: {model_id}")
        ids.add(model_id)
        result.append(AircraftType(slot, fields))
    return result


def create_aircraft_type(save, nation, template_slot: int, changes: dict[str, str],
                         *, purpose: int | None = None) -> AircraftType:
    """Clone a model, edit known fields, and allocate a fresh slot and global ID."""
    target = save.nation(nation)
    types = aircraft_types(save)
    if type(template_slot) is not int or not 0 <= template_slot < len(types):
        raise ValueError("Choose an existing aircraft model as a template")
    template = types[template_slot]
    if purpose is not None and (type(purpose) is not int or purpose not in ROLE_NAMES):
        raise ValueError("Choose a supported aircraft type")
    if (purpose is not None and purpose != int(template.fields["Purpose"]) and
            not set(FIELD_NAMES).issubset(changes)):
        raise ValueError("Changing aircraft type requires a complete set of role-based stats")
    if "BaseModelYear" not in template.fields:
        raise ValueError("Template aircraft has no BaseModelYear field")
    required = {"Name", "Manufacturer", *EDITABLE_NUMERIC_FIELDS}
    if set(changes) - required:
        raise ValueError("Aircraft edit includes an unsupported field")
    fields = dict(template.fields)
    if purpose is not None:
        fields["Purpose"] = str(purpose)
    for key, raw in changes.items():
        value = str(raw).strip()
        if key in {"Name", "Manufacturer"}:
            if not value or any(char in value for char in "\r\n=;[]") or len(value) > 80:
                raise ValueError(f"{key} must be a non-empty single-line name (80 characters or fewer)")
            fields[key] = value
            continue
        try:
            number = int(value.replace(",", ""))
        except ValueError as error:
            raise ValueError(f"{key} must be a whole number") from error
        minimum = -1 if key == "Radar" else 0
        if not minimum <= number <= 2**31 - 1:
            raise ValueError(f"{key} must be between {minimum} and 2,147,483,647")
        if key in {"Carrier", "Floatplane"} and number not in (0, 1):
            raise ValueError(f"{key} must be 0 or 1")
        if key in {"Year", "BaseModelYear"} and not 1800 <= number <= 2200:
            raise ValueError(f"{key} must be a year from 1800 to 2200")
        fields[key] = str(number)
    if not fields["Name"].strip() or not fields["Manufacturer"].strip():
        raise ValueError("Aircraft name and manufacturer are required")
    if int(fields["Year"]) < int(fields["BaseModelYear"]):
        raise ValueError("Aircraft year cannot precede its base model year")
    if any(model.fields["Nation"] == str(target.index)
           and model.fields["Manufacturer"].casefold() == fields["Manufacturer"].casefold()
           and model.fields["Name"].casefold() == fields["Name"].casefold()
           for model in types):
        raise ValueError("That nation already has an aircraft model with this manufacturer and name")
    general = next((section for section in save.documents[save.main_file].sections
                    if section.name.casefold() == "general"), None)
    counter = None
    if general is not None and "IDNo" in general.fields():
        try:
            counter = int(general.fields()["IDNo"])
        except ValueError as error:
            raise ValueError("[General] IDNo is not a whole number") from error
    new_id = max(max(int(model.fields["Id"]) for model in types) + 1,
                 counter if counter is not None else 0)
    if not 0 <= new_id < 2**31 - 1:
        raise ValueError("No signed 32-bit aircraft model ID is available")
    fields["Nation"] = str(target.index)
    fields["Id"] = str(new_id)
    fields["Obsolete"] = "0"
    fields["DevelopmentTime"] = "0"
    section = _aircraft_section(save)
    newline = save.documents[save.main_file].newline
    with save.transaction():
        if general is not None and counter is not None:
            general.set("IDNo", new_id + 1, newline)
        section.set("ACTypesNo", len(types) + 1, newline)
        for key, value in fields.items():
            section.set(f"AT{len(types)}{key}", value, newline)
        created = aircraft_types(save)[-1]
        save.audit.append(
            f"Created {created.role} aircraft model {created.name} for {target.name} "
            f"(AT{created.slot}, ID {new_id})"
        )
        save.modified = True
    save._aircraft_changes = True
    return created
