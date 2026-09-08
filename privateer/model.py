from __future__ import annotations

from dataclasses import dataclass, field
from copy import deepcopy
from typing import Any

from .document import PrefixedRecord, Section


def _integer(fields: dict[str, str], *names: str) -> int | None:
    lookup = {key.casefold(): value for key, value in fields.items()}
    for name in names:
        try:
            return int(lookup[name.casefold()].replace(",", ""))
        except (KeyError, ValueError):
            pass
    return None


@dataclass
class TechnologyState:
    fields: dict[str, int | bool | str] = field(default_factory=dict)


@dataclass
class ShipDesign:
    record_index: int
    internal_design_id: int
    ship_type: str | None
    class_name: str | None
    section: Section
    source_file: str

    @classmethod
    def from_section(cls, record_index: int, section: Section, source_file: str) -> "ShipDesign":
        values = section.fields()
        internal = _integer(values, "DesignId", "ShipDesignId", "Id")
        return cls(record_index, record_index if internal is None else internal,
                   values.get("Type") or values.get("ShipType"),
                   values.get("Class") or values.get("ClassName"), section, source_file)

    def clone(self, new_id: int, newline: str) -> "ShipDesign":
        section = deepcopy(self.section)
        section.name = f"ShipDesign{new_id}"
        section.header = f"[{section.name}]{newline}"
        values = section.fields()
        id_key = next((key for key in values if key.casefold() in {"designid", "shipdesignid", "id"}), "DesignId")
        section.set(id_key, new_id, newline)
        return ShipDesign.from_section(new_id, section, self.source_file)

    def signature(self) -> tuple[tuple[str, str], ...]:
        ignored = {"designid", "shipdesignid", "id", "nationidx", "ownernationidx"}
        return tuple(sorted((k.casefold(), v) for k, v in self.section.fields().items() if k.casefold() not in ignored))


@dataclass
class Ship:
    record_index: int
    owner_index: int
    name: str
    ship_type: str | None
    class_name: str | None
    design_ref_id: int | None
    building_nation_index: int | None
    under_construction: bool
    section: Section | PrefixedRecord
    local_slot: int | None = None
    flattened_record: bool = False

    def set_design(self, design_id: int, newline: str) -> None:
        self.design_ref_id = design_id
        self.section.set("ShipDesignRefId", design_id, newline)


@dataclass
class Nation:
    index: int
    name: str
    section: Section
    funds: int | None
    base_resources: int | None
    budget_modifier: int | None
    technology: TechnologyState
    ships: list[Ship] = field(default_factory=list)
    designs: list[ShipDesign] = field(default_factory=list)
    is_player: bool = False

    def set_funds(self, value: int, newline: str = "\n") -> None:
        if not isinstance(value, int):
            raise TypeError("Funds must be an integer")
        self.funds = value
        self.section.set("Funds", value, newline)

    def set_base_resources(self, value: int, newline: str = "\n") -> None:
        if not isinstance(value, int):
            raise TypeError("BaseResources must be an integer")
        self.base_resources = value
        self.section.set("BaseResources", value, newline)

    def sync_ship_count(self, newline: str = "\n") -> None:
        self.section.set("ShipCount", len(self.ships), newline)
