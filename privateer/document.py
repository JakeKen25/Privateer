"""Lossless-enough line document used instead of configparser.

Only changed values are rewritten; unrecognised text is never normalized.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re

SECTION = re.compile(r"^\s*\[([^]]+)]")
FIELD = re.compile(r"^(\s*)([^=;#]+?)(\s*[=:]\s*)(.*?)(\r?\n)?$")


@dataclass
class Section:
    name: str
    header: str
    lines: list[str] = field(default_factory=list)

    def fields(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for line in self.lines:
            match = FIELD.match(line)
            if match:
                result[match.group(2).strip()] = match.group(4).strip()
        return result

    def set(self, key: str, value: object, newline: str = "\n") -> None:
        for index, line in enumerate(self.lines):
            match = FIELD.match(line)
            if match and match.group(2).strip().casefold() == key.casefold():
                end = match.group(5) or ""
                self.lines[index] = f"{match.group(1)}{match.group(2)}{match.group(3)}{value}{end}"
                return
        self.lines.append(f"{key}={value}{newline}")


@dataclass
class PrefixedRecord:
    """A field view over one flattened record in a section.

    RTW3 stores ships as ``ShipNField=value`` lines inside a nation roster.
    Keeping the parent section and prefix here means reads retain every unknown
    field and can still point back to the exact source container. Parsed fields
    may be retained so repeated table reads do not rescan the complete roster.
    """

    parent: Section
    prefix: str
    cached_fields: dict[str, str] | None = None

    def fields(self) -> dict[str, str]:
        if self.cached_fields is not None:
            return dict(self.cached_fields)
        result: dict[str, str] = {}
        for line in self.parent.lines:
            match = FIELD.match(line)
            if not match:
                continue
            key = match.group(2).strip()
            if key.startswith(self.prefix) and len(key) > len(self.prefix) and not key[len(self.prefix)].isdigit():
                result[key[len(self.prefix):]] = match.group(4).strip()
        return result

    def set(self, key: str, value: object, newline: str = "\n") -> None:
        target = f"{self.prefix}{key}"
        self.parent.set(target, value, newline)
        if self.cached_fields is not None:
            actual = next((name for name in self.cached_fields
                           if name.casefold() == key.casefold()), key)
            self.cached_fields[actual] = str(value)


@dataclass
class TextDocument:
    preamble: list[str]
    sections: list[Section]
    newline: str = "\n"
    encoding: str = "utf-8"
    has_bom: bool = False

    @classmethod
    def parse(
        cls, text: str, *, encoding: str = "utf-8", has_bom: bool = False
    ) -> "TextDocument":
        newline = "\r\n" if "\r\n" in text else "\n"
        preamble: list[str] = []
        sections: list[Section] = []
        current: Section | None = None
        for line in text.splitlines(keepends=True):
            match = SECTION.match(line)
            if match:
                current = Section(match.group(1).strip(), line)
                sections.append(current)
            elif current is None:
                preamble.append(line)
            else:
                current.lines.append(line)
        return cls(preamble, sections, newline, encoding, has_bom)

    def render(self) -> str:
        return "".join(self.preamble + [part for section in self.sections for part in [section.header, *section.lines]])

    def to_bytes(self) -> bytes:
        payload = self.render().encode(self.encoding)
        if self.has_bom and self.encoding.casefold().replace("_", "-") == "utf-8":
            return b"\xef\xbb\xbf" + payload
        return payload

    def add_section(self, section: Section) -> None:
        if self.sections and self.sections[-1].lines and not self.sections[-1].lines[-1].endswith(("\n", "\r")):
            self.sections[-1].lines[-1] += self.newline
        self.sections.append(section)
