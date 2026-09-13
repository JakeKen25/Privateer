"""Fleet browser and staged, transactional ship ownership transfers."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .table_sort import heading_text, sorted_with_blanks


def transfer_block_reason(ship) -> str | None:
    """Return a user-facing reason for a dependency we cannot migrate safely."""
    fields = ship.section.fields()
    try:
        aircraft_capacity = int(fields.get("AircraftCapacity", "0") or "0")
    except ValueError:
        return "Aircraft capacity is malformed."
    if aircraft_capacity > 0 or (ship.ship_type or "").upper() in {"CV", "CVL", "AV"}:
        return "Carrier and air-group transfers are not supported yet."
    missing = [key for key in ("DesignRefId", "BuildingNationIdx", "CommanderId") if key not in fields]
    if missing:
        return "Missing required field(s): " + ", ".join(missing)
    return None


def ship_details(save, ship) -> str:
    fields = ship.section.fields()
    owner = save.nation(ship.owner_index).name
    builder_index = ship.building_nation_index
    try:
        builder = save.nation(builder_index).name if builder_index is not None else "Unknown"
    except KeyError:
        builder = f"Nation{builder_index}"
    lifecycle = "Under construction" if ship.under_construction else "In service"
    location = fields.get("LocationAreaName") or "Unknown"
    commander = fields.get("CommanderId", "Unknown")
    progress = fields.get("BuildProgress", "Unknown")
    reason = transfer_block_reason(ship)
    eligibility = f"Blocked: {reason}" if reason else "Eligible for an ownership transfer"
    return (
        f"{ship.name} (hull ID {ship.record_index})\n"
        f"Owner: {owner}    Type: {ship.ship_type or 'Unknown'}    Class: {ship.class_name or 'Unknown'}\n"
        f"State: {lifecycle}    Location: {location}    Build progress: {progress}\n"
        f"Design reference: {ship.design_ref_id}    Builder: {builder}    Commander ID: {commander}\n"
        f"{eligibility}"
    )


def ship_stats(ship) -> dict[str, str]:
    """Return lossless display values for the saved per-hull statistics."""
    fields = ship.section.fields()
    displacement = fields.get("Displacement", "")
    try:
        displacement = f"{int(displacement):,}" if displacement else ""
    except ValueError:
        pass
    search_radar = fields.get("SearchRadarClass", "")
    fire_control_radar = fields.get("FCRadarClass", "")
    if search_radar == fire_control_radar:
        radar = search_radar
    else:
        radar = f"S:{search_radar or '-'} / FC:{fire_control_radar or '-'}"
    return {
        "type": ship.ship_type or "",
        "name": ship.name,
        "class": ship.class_name or "",
        "displacement": displacement,
        "speed": fields.get("Speed", ""),
        "main_gun": fields.get("MainCalibre", ""),
        "radar": radar,
        "asw": fields.get("ASWValue", ""),
        "year": fields.get("YearBuilt", ""),
        "location": fields.get("LocationAreaName", ""),
        "status": fields.get("Status", ""),
        "crew": fields.get("CrewQuality", ""),
        "maintenance": fields.get("Maintenance", ""),
        "description": fields.get("Description", ""),
    }


class ShipTransfersWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        super().__init__(parent)
        self.save = save
        self.pending: dict[int, int] = {}
        self.sort_column: str | None = None
        self.sort_reverse = False
        self.ships = {ship.record_index: ship for nation in save.nations for ship in nation.ships}
        self.nation_values = [f"{nation.index}: {nation.name}" for nation in save.nations]
        self.title("Manage Ship Transfers")
        self.geometry("1120x740")
        self.minsize(900, 600)
        self.transient(parent)

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Ship ownership transfers", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(
            body,
            text=("Transfers keep the hull, original building nation, and all saved state while "
                  "copying its design to the receiver. Carrier/air-group transfers are currently blocked."),
            wraplength=1050,
        ).pack(anchor="w")

        filters = ttk.Frame(body)
        filters.pack(fill="x", pady=10)
        self.source = tk.StringVar(value=self.nation_values[self._nation_position(nation_index)])
        self.search = tk.StringVar()
        self.type_filter = tk.StringVar(value="All types")
        ship_types = sorted({ship.ship_type for ship in self.ships.values() if ship.ship_type})
        ttk.Label(filters, text="Current owner").pack(side="left")
        ttk.Combobox(filters, textvariable=self.source, values=self.nation_values,
                     state="readonly", width=25).pack(side="left", padx=8)
        ttk.Label(filters, text="Type").pack(side="left")
        ttk.Combobox(filters, textvariable=self.type_filter, values=["All types", *ship_types],
                     state="readonly", width=12).pack(side="left", padx=8)
        ttk.Label(filters, text="Search").pack(side="left")
        ttk.Entry(filters, textvariable=self.search, width=25).pack(side="left", padx=8)
        self.count = tk.StringVar()
        ttk.Label(filters, textvariable=self.count).pack(side="right")

        frame = ttk.Frame(body)
        frame.pack(fill="both", expand=True)
        columns = ("type", "name", "class", "displacement", "speed", "main_gun", "radar",
                   "asw", "year", "location", "status", "crew", "maintenance",
                   "description", "destination")
        self.table = ttk.Treeview(frame, columns=columns, show="tree headings", selectmode="extended")
        self.heading_labels = {"hull": "Hull ID"}
        self.table.heading("#0", text="Hull ID", command=lambda: self.sort_by("hull"))
        self.table.column("#0", width=70, minwidth=55, stretch=False)
        specs = [
            ("type", "Type", 50), ("name", "Name", 150), ("class", "Class", 145),
            ("displacement", "Displacement", 90), ("speed", "Speed", 55),
            ("main_gun", "Main gun", 65), ("radar", "Radar", 90), ("asw", "ASW", 50),
            ("year", "Year", 55), ("location", "Location", 145),
            ("status", "Status (raw)", 75), ("crew", "Crew quality (raw)", 105),
            ("maintenance", "Maintenance", 85), ("description", "Description", 220),
            ("destination", "Staged destination", 150),
        ]
        for key, label, width in specs:
            self.heading_labels[key] = label
            self.table.heading(key, text=label, command=lambda column=key: self.sort_by(column))
            self.table.column(key, width=width, minwidth=45)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.table.yview)
        horizontal = ttk.Scrollbar(frame, orient="horizontal", command=self.table.xview)
        self.table.configure(yscrollcommand=scroll.set, xscrollcommand=horizontal.set)
        scroll.pack(side="right", fill="y")
        horizontal.pack(side="bottom", fill="x")
        self.table.pack(fill="both", expand=True)

        editor = ttk.Frame(body)
        editor.pack(fill="x", pady=(10, 6))
        ttk.Label(editor, text="Transfer selected ships to").pack(side="left")
        initial_destination = next((value for value in self.nation_values
                                    if self._nation_index(value) != nation_index), self.nation_values[0])
        self.destination = tk.StringVar(value=initial_destination)
        ttk.Combobox(editor, textvariable=self.destination, values=self.nation_values,
                     state="readonly", width=25).pack(side="left", padx=8)
        ttk.Button(editor, text="Stage transfer", command=self.stage).pack(side="left")
        ttk.Button(editor, text="Unstage selected", command=self.unstage).pack(side="left", padx=6)

        details = ttk.LabelFrame(body, text="Selected ship", padding=8)
        details.pack(fill="x", pady=(0, 8))
        self.details = tk.StringVar(value="Select a ship to see its saved state and transfer eligibility.")
        ttk.Label(details, textvariable=self.details, justify="left", wraplength=1040).pack(anchor="w")

        self.status = tk.StringVar(value="No changes")
        ttk.Label(body, textvariable=self.status).pack(anchor="w")
        ttk.Label(body, text="Apply stages the transfers in memory. Use Save or Save As in the main window to write them.").pack(anchor="w", pady=(3, 8))
        buttons = ttk.Frame(body)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Reset changes", command=self.reset_changes).pack(side="left")
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text="Apply", command=self.apply).pack(side="right", padx=8)

        self.search.trace_add("write", lambda *_: self.render())
        self.source.trace_add("write", lambda *_: self.render())
        self.type_filter.trace_add("write", lambda *_: self.render())
        self.table.bind("<<TreeviewSelect>>", self.show_details)
        self.bind("<Escape>", lambda _event: self.destroy())
        self.render()
        self.grab_set()

    def _nation_position(self, nation_index):
        return next(index for index, nation in enumerate(self.save.nations) if nation.index == nation_index)

    @staticmethod
    def _nation_index(value):
        return int(value.split(":", 1)[0])

    def render(self):
        self.table.delete(*self.table.get_children())
        source_index = self._nation_index(self.source.get())
        needle = self.search.get().strip().casefold()
        source_ships = self.save.nation(source_index).ships
        rows = []
        for ship in source_ships:
            fields = ship.section.fields()
            stats = ship_stats(ship)
            if self.type_filter.get() not in ("All types", ship.ship_type):
                continue
            haystack = f"{ship.record_index} {ship.name} {ship.class_name} {ship.ship_type} {fields.get('LocationAreaName', '')}".casefold()
            if needle not in haystack:
                continue
            pending = self.pending.get(ship.record_index)
            destination = self.save.nation(pending).name if pending is not None else ""
            rows.append((ship, stats, destination))
        if self.sort_column:
            column = self.sort_column
            rows = sorted_with_blanks(
                rows,
                lambda row: (row[0].record_index if column == "hull"
                             else row[2] if column == "destination"
                             else row[1][column]),
                reverse=self.sort_reverse,
                numeric=column in {"hull", "displacement", "speed", "main_gun", "asw",
                                   "year", "status", "crew", "maintenance"},
            )
        for ship, stats, destination in rows:
            self.table.insert("", "end", iid=str(ship.record_index), text=str(ship.record_index),
                              values=tuple(stats[key] for key in (
                                  "type", "name", "class", "displacement", "speed", "main_gun",
                                  "radar", "asw", "year", "location", "status", "crew",
                                  "maintenance", "description")) + (destination,))
        self.count.set(f"{len(rows)} / {len(source_ships)} ships")
        self.status.set(f"{len(self.pending)} staged ship transfer(s)")
        self.details.set("Select a ship to see its saved state and transfer eligibility.")

    def sort_by(self, column):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        self.table.heading("#0", text=heading_text(
            self.heading_labels["hull"], column == "hull", self.sort_reverse))
        for key, label in self.heading_labels.items():
            if key != "hull":
                self.table.heading(key, text=heading_text(
                    label, key == column, self.sort_reverse))
        self.render()

    def show_details(self, _event=None):
        selected = self.table.selection()
        if selected:
            self.details.set(ship_details(self.save, self.ships[int(selected[0])]))

    def stage(self):
        selected = self.table.selection()
        if not selected:
            self.status.set("Select one or more ships first.")
            return
        destination = self._nation_index(self.destination.get())
        failures = []
        for item in selected:
            ship = self.ships[int(item)]
            reason = transfer_block_reason(ship)
            if reason:
                failures.append(f"{ship.name}: {reason}")
            elif destination == ship.owner_index:
                self.pending.pop(ship.record_index, None)
            else:
                self.pending[ship.record_index] = destination
        self.render()
        if failures:
            messagebox.showwarning("Some ships were not staged", "\n".join(failures), parent=self)

    def unstage(self):
        for item in self.table.selection():
            self.pending.pop(int(item), None)
        self.render()

    def reset_changes(self):
        self.pending.clear()
        self.render()

    def apply(self):
        if not self.pending:
            self.destroy()
            return
        try:
            self.save.transfer_ship_batch(self.pending)
        except (ValueError, KeyError) as exc:
            messagebox.showerror("Unable to transfer ships", str(exc), parent=self)
            return
        for nation in self.save.nations:
            if self.master.table.exists(str(nation.index)):
                self.master.table.set(str(nation.index), "ships", len(nation.ships))
        self.master.status.set("Unsaved changes")
        self.destroy()
