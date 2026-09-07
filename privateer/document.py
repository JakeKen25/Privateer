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
class TextDocument:
    preamble: list[str]
    sections: list[Section]
    newline: str = "\n"

    @classmethod
    def parse(cls, text: str) -> "TextDocument":
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
        return cls(preamble, sections, newline)

    def render(self) -> str:
        return "".join(self.preamble + [part for section in self.sections for part in [section.header, *section.lines]])

    def add_section(self, section: Section) -> None:
        if self.sections and self.sections[-1].lines and not self.sections[-1].lines[-1].endswith(("\n", "\r")):
            self.sections[-1].lines[-1] += self.newline
        self.sections.append(section)
