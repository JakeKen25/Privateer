"""Lossless air-wing inventory and base reassignment for ``[AirUnits]``."""

from dataclasses import dataclass
import re

from .document import FIELD


@dataclass(frozen=True)
class AirWing:
    slot: int
    fields: dict[str, str]
    aircraft_name: str
    base_name: str

    @property
    def name(self):
        return self.fields.get("Name", f"Air wing {self.slot + 1}")

    def value(self, key):
        if key == "slot":
            return self.slot
        if key == "aircraft":
            return self.aircraft_name
        if key == "base":
            return self.base_name
        return self.fields.get(key, "")


def _unique_section(save, name):
    sections = [s for s in save.documents[save.main_file].sections
                if s.name.casefold() == name.casefold()]
    if len(sections) != 1:
        raise ValueError(f"Expected exactly one [{name}] section")
    return sections[0]


def _flat_records(section, prefix, count_key):
    values = {}
    seen = set()
    for line in section.lines:
        match = FIELD.match(line)
        if not match:
            continue
        key = match.group(2).strip()
        folded = key.casefold()
        if folded in seen:
            raise ValueError(f"Duplicate {key} in [{section.name}]")
        seen.add(folded)
        if folded == count_key.casefold():
            continue
        record = re.fullmatch(re.escape(prefix) + r"(\d+)(\D.+)", key, re.I)
        if record:
            values.setdefault(int(record[1]), {})[record[2]] = match.group(4).strip()
    declared = section.fields().get(count_key)
    if declared is None or not declared.isdigit() or int(declared) != len(values):
        raise ValueError(f"[{section.name}] {count_key} does not match its records")
    if sorted(values) != list(range(len(values))):
        raise ValueError(f"[{section.name}] record slots are not contiguous")
    return values


def _air_units_section(save):
    return _unique_section(save, "AirUnits")


def air_wings(save, nation_index):
    """Return a nation's wings with resolved names, without editing the save."""
    air_section = _air_units_section(save)
    raw_units = _flat_records(air_section, "AU", "AirUnitNo")
    type_sections = [s for s in save.documents[save.main_file].sections
                     if s.name.casefold() == "aircrafttypes"]
    if len(type_sections) != 1:
        raise ValueError("Expected exactly one [AircraftTypes] section")
    raw_types = _flat_records(type_sections[0], "AT", "ACTypesNo")
    model_names = {}
    for values in raw_types.values():
        identity = values.get("Id")
        if identity is not None:
            if identity in model_names:
                raise ValueError(f"Duplicate aircraft type ID {identity}")
            model_names[identity] = values.get("Name", f"Aircraft model {identity}")
    base_names = {}
    for ship in save.nation(nation_index).ships:
        identity = str(ship.record_index)
        base_names[identity] = ship.name
    result = []
    for slot, fields in raw_units.items():
        if fields.get("Nation") != str(nation_index):
            continue
        if "HomeBase" not in fields or "AircraftTypeId" not in fields:
            raise ValueError(f"Air wing {slot + 1} is missing its base or aircraft type reference")
        model_id = fields["AircraftTypeId"]
        result.append(AirWing(
            slot, fields, model_names.get(model_id, f"Unknown model ({model_id})"),
            base_names.get(fields["HomeBase"], f"Base {fields['HomeBase']}"),
        ))
    return tuple(result)


def eligible_bases(save, nation_index):
    """Return owned, live ships that have a positive aircraft capacity."""
    result = {}
    for ship in save.nation(nation_index).ships:
        fields = ship.section.fields()
        try:
            capacity = int(fields.get("AircraftCapacity", "0") or "0")
        except ValueError:
            continue
        fate = fields.get("Fate", "").strip().casefold()
        if capacity > 0 and fate in ("", "xxx") and fields.get("Status") != "9":
            result[str(ship.record_index)] = ship.name
    return result


def assign_air_wing(save, nation_index, slot, base_id):
    """Assign one existing wing to an eligible own ship; preserve all other fields."""
    if str(base_id) not in eligible_bases(save, nation_index):
        raise ValueError("Choose an active aircraft-capable ship owned by this nation.")
    section = _air_units_section(save)
    units = _flat_records(section, "AU", "AirUnitNo")
    if slot not in units or units[slot].get("Nation") != str(nation_index):
        raise ValueError("Select an existing air wing owned by this nation.")
    if "HomeBase" not in units[slot]:
        raise ValueError("The selected air wing has no HomeBase field.")
    if units[slot]["HomeBase"] == str(base_id):
        return False
    with save.transaction():
        section.set(f"AU{slot}HomeBase", base_id, save.documents[save.main_file].newline)
        save.modified = True
        save._aircraft_changes = True
        save.audit.append(f"Rebased air wing {slot + 1}: Nation{nation_index}, HomeBase {units[slot]['HomeBase']} -> {base_id}")
    return True


class AirWingDraft:
    """Isolated edits; Apply merges only the shared air-unit section."""

    def __init__(self, save, nation_index):
        from copy import deepcopy
        self.original = save
        self.nation_index = nation_index
        self.save = deepcopy(save)
        self.baseline = self._signature(save)
        self.audit_start = len(save.audit)

    @staticmethod
    def _signature(save):
        sections = [s for s in save.documents[save.main_file].sections
                    if s.name.casefold() == "airunits"]
        return [s.header + "".join(s.lines) for s in sections]

    def assign(self, slot, base_id):
        return assign_air_wing(self.save, self.nation_index, slot, base_id)

    def apply(self):
        from copy import deepcopy
        if self._signature(self.original) != self.baseline:
            raise ValueError("Air-wing data changed outside this window. Reopen the manager.")
        if self._signature(self.save) == self.baseline:
            return False
        source = _air_units_section(self.save)
        target = _air_units_section(self.original)
        with self.original.transaction():
            target.lines = deepcopy(source.lines)
            self.original.audit.extend(self.save.audit[self.audit_start:])
            self.original.modified = True
            self.original._aircraft_changes = True
        return True
