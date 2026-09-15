"""Verified display and transfer rules for RTW3 ship lifecycle status."""

FLEET_STATUS_NAMES = {
    "0": "Active Fleet",
    "1": "Reserve",
    "2": "Mothballed",
    "6": "Foreign Service",
}
_LIVE_FATES = {"", "xxx"}
MUSEUM_STATUS = "9"


def has_final_fate(fields) -> bool:
    return str(fields.get("Fate", "")).strip().casefold() not in _LIVE_FATES


def ship_status_label(ship, fields=None) -> str:
    """Translate verified statuses and distinguish construction from final fates."""
    fields = ship.section.fields() if fields is None else fields
    fate = str(fields.get("Fate", "")).strip()
    normalized_fate = fate.casefold()
    if str(fields.get("Status", "")).strip() == MUSEUM_STATUS:
        return "Museum Ship"
    if normalized_fate not in _LIVE_FATES:
        if "broken up on slipway" in normalized_fate:
            return "Scrapped on slipway"
        if "scrapped" in normalized_fate:
            return "Scrapped"
        if "sunk" in normalized_fate:
            return "Sunk"
        if "mined" in normalized_fate:
            return "Sunk (mined)"
        if "scuttled" in normalized_fate:
            return "Scuttled"
        return "Lost / unavailable"

    in_play = str(fields.get("InPlay", "1")).strip().casefold()
    if in_play in {"0", "false", "no"}:
        return "Under construction"
    raw_status = str(fields.get("Status", "")).strip()
    if raw_status in FLEET_STATUS_NAMES:
        return FLEET_STATUS_NAMES[raw_status]
    return f"Unknown status ({raw_status or '?'})"


def appears_in_transfer_window(fields) -> bool:
    """Return whether a hull is current and should appear in Transfer Ships."""
    return not has_final_fate(fields) and str(fields.get("Status", "")).strip() != MUSEUM_STATUS


def final_fate_transfer_block_reason(ship, fields=None) -> str | None:
    """Block historical hull records while allowing live construction transfers."""
    fields = ship.section.fields() if fields is None else fields
    if appears_in_transfer_window(fields):
        return None
    status = ship_status_label(ship, fields)
    if status == "Museum Ship":
        return "Museum ships cannot be transferred."
    return f"{status} ships cannot be transferred."
