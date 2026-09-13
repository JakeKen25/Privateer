"""Shared stable sorting for Tk tables with text and saved numeric values."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation


def sort_value(value):
    """Sort numbers numerically and all other populated values case-insensitively."""
    if isinstance(value, (int, float, Decimal)) and not isinstance(value, bool):
        return 0, Decimal(str(value))
    text = str(value).strip()
    try:
        return 0, Decimal(text.replace(",", ""))
    except InvalidOperation:
        return 1, text.casefold()


def sorted_with_blanks(items, value, *, reverse=False, numeric=False):
    """Sort populated values while keeping blank cells at the bottom."""
    populated, blank = [], []
    for item in items:
        raw = value(item)
        text = str(raw).strip()
        if numeric:
            try:
                Decimal(text.replace(",", ""))
            except InvalidOperation:
                blank.append(item)
                continue
        (blank if text == "" else populated).append(item)
    key = ((lambda item: Decimal(str(value(item)).strip().replace(",", "")))
           if numeric else (lambda item: str(value(item)).strip().casefold()))
    populated.sort(key=key, reverse=reverse)
    return populated + blank


def heading_text(label, active, reverse):
    if not active:
        return label
    return f"{label} {'▼' if reverse else '▲'}"
