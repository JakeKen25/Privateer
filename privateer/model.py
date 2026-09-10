from __future__ import annotations

from dataclasses import dataclass, field
from copy import deepcopy
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

from .document import PrefixedRecord, Section


ECONOMY_ADJUSTMENTS = ("Set value", "Adjust by amount", "Adjust by percentage")


def adjusted_integer(current: int | None, operation: str, amount: str) -> int:
    """Return an economy value after applying a user-facing adjustment."""
    cleaned = amount.strip().replace(",", "")
    if operation == "Adjust by percentage":
        cleaned = cleaned.removesuffix("%").strip()
        try:
            percentage = Decimal(cleaned)
        except InvalidOperation as error:
            raise ValueError("Percentage must be a number") from error
        if current is None:
            raise ValueError("Cannot adjust a value that is missing from the save")
        result = (Decimal(current) * (Decimal(100) + percentage) / Decimal(100)).quantize(
            Decimal(1), rounding=ROUND_HALF_UP
        )
        return int(result)

    try:
        value = int(cleaned)
    except ValueError as error:
        raise ValueError("Amount must be a whole number") from error
    if operation == "Set value":
        return value
    if operation == "Adjust by amount":
        if current is None:
            raise ValueError("Cannot adjust a value that is missing from the save")
        return current + value
    raise ValueError(f"Unknown adjustment: {operation}")


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
    section: Section | None
    source_file: str
    positional_record: tuple[str, ...] | None = None

    @classmethod
    def from_section(cls, record_index: int, section: Section, source_file: str) -> "ShipDesign":
        values = section.fields()
        internal = _integer(values, "DesignId", "ShipDesignId", "Id")
        return cls(record_index, record_index if internal is None else internal,
                   values.get("Type") or values.get("ShipType"),
                   values.get("Class") or values.get("ClassName"), section, source_file)

    @classmethod
    def from_positional_record(
        cls, record_index: int, lines: list[str], source_file: str
    ) -> "ShipDesign":
        """Build a design from the confirmed v10139 positional record prefix."""
        if len(lines) < 5:
            raise ValueError(
                f"Malformed design record ShipDesign{record_index} in {source_file}: "
                "expected at least five lines"
            )
        try:
            internal_id = int(lines[4].strip())
        except ValueError as error:
            raise ValueError(
                f"Malformed design record ShipDesign{record_index} in {source_file}: "
                f"internal design ID is not an integer: {lines[4].strip()!r}"
            ) from error
        return cls(
            record_index,
            internal_id,
            lines[3].strip(),
            lines[1].strip(),
            None,
            source_file,
            tuple(lines),
        )

    def clone(self, new_id: int, newline: str) -> "ShipDesign":
        if self.section is None:
            raise NotImplementedError("Positional RTW3 design cloning is not implemented")
        section = deepcopy(self.section)
        section.name = f"ShipDesign{new_id}"
        section.header = f"[{section.name}]{newline}"
        values = section.fields()
        id_key = next((key for key in values if key.casefold() in {"designid", "shipdesignid", "id"}), "DesignId")
        section.set(id_key, new_id, newline)
        return ShipDesign.from_section(new_id, section, self.source_file)

    def signature(self) -> tuple[tuple[str, str], ...]:
        if self.section is None:
            raise NotImplementedError("Positional RTW3 design equivalence is not defined")
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
