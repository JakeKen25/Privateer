"""Air-wing inventory and staged ship-base reassignment."""

import tkinter as tk
from tkinter import messagebox, ttk

from .air_wings import AirWingDraft, air_wings, eligible_bases


class AirWingWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        self.draft = AirWingDraft(save, nation_index)
        self.save = self.draft.save
        self.nation_index = nation_index
        self.records = air_wings(self.save, nation_index)
        self.bases = eligible_bases(self.save, nation_index)
        super().__init__(parent)
        self.title(f"Air Wing Manager — {save.nation(nation_index).name}")
        self.geometry("1000x620")
        self.minsize(760, 440)
        self.transient(parent)

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Air wings", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(body, text=(
            "Review this nation’s saved air wings and reassign them to its aircraft-capable ships. "
            "Aircraft models and wing details are preserved. Changes stay pending until Apply."
        ), wraplength=950).pack(anchor="w", pady=(2, 10))

        filters = ttk.Frame(body)
        filters.pack(fill="x", pady=(0, 6))
        ttk.Label(filters, text="Search").pack(side="left")
        self.search = tk.StringVar()
        ttk.Entry(filters, textvariable=self.search, width=36).pack(side="left", padx=8)
        self.search.trace_add("write", lambda *_: self.render())

        table_frame = ttk.Frame(body)
        table_frame.pack(fill="both", expand=True)
        self.columns = ("Name", "aircraft", "Role", "AircraftNumber", "DesiredAircraftNumber",
                        "CarrierCapable", "base")
        labels = ("Air wing", "Aircraft model", "Role (saved)", "Aircraft", "Desired",
                  "Carrier capable", "Current base")
        self.table = ttk.Treeview(table_frame, columns=self.columns, show="headings", selectmode="browse")
        for column, label, width in zip(self.columns, labels, (180, 230, 105, 95, 95, 115, 180)):
            self.table.heading(column, text=label)
            self.table.column(column, width=width, minwidth=65, stretch=True)
        vertical = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        horizontal = ttk.Scrollbar(table_frame, orient="horizontal", command=self.table.xview)
        self.table.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.table.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        controls = ttk.Frame(body)
        controls.pack(fill="x", pady=(10, 0))
        ttk.Label(controls, text="Assign selected wing to").pack(side="left")
        self.base_choice = tk.StringVar()
        self.base_box = ttk.Combobox(controls, textvariable=self.base_choice, state="readonly", width=35)
        self.base_box.pack(side="left", padx=8)
        self.assign_button = ttk.Button(controls, text="Assign", command=self.assign)
        self.assign_button.pack(side="left")
        self.summary = tk.StringVar()
        ttk.Label(controls, textvariable=self.summary).pack(side="right")

        footer = ttk.Frame(body)
        footer.pack(fill="x", pady=(12, 0))
        self.status = tk.StringVar(value="Select an air wing to reassign it.")
        ttk.Label(footer, textvariable=self.status).pack(side="left", fill="x", expand=True)
        ttk.Button(footer, text="Apply", command=self.apply).pack(side="right", padx=(6, 0))
        ttk.Button(footer, text="Cancel", command=self.destroy).pack(side="right")

        self.table.bind("<<TreeviewSelect>>", self.selection_changed)
        self.bind("<Escape>", lambda _event: self.destroy())
        self._base_ids = {}
        self.refresh()
        self.grab_set()

    def refresh(self, selected=None):
        self.records = air_wings(self.save, self.nation_index)
        self.bases = eligible_bases(self.save, self.nation_index)
        self._base_ids = {f"{name} (ID {identity})": identity
                          for identity, name in self.bases.items()}
        self.base_box.configure(values=tuple(self._base_ids))
        self.render(selected)

    def render(self, selected=None):
        current = self.table.selection()
        if selected is None and current:
            selected = current[0]
        query = self.search.get().casefold()
        self.table.delete(*self.table.get_children())
        shown = 0
        for record in self.records:
            fields = record.fields
            carrier = fields.get("CarrierCapable", "")
            carrier = "Yes" if carrier == "1" else "No" if carrier == "0" else carrier
            values = (
                record.name, record.aircraft_name, fields.get("Role", ""),
                fields.get("AircraftNumber", ""), fields.get("DesiredAircraftNumber", ""),
                carrier, record.base_name,
            )
            if query and query not in " ".join(map(str, (record.slot, *values))).casefold():
                continue
            self.table.insert("", "end", iid=str(record.slot), values=values)
            shown += 1
        self.summary.set(f"{shown} shown / {len(self.records)} air wings · {len(self.bases)} eligible ships")
        if selected is not None and self.table.exists(str(selected)):
            self.table.selection_set(str(selected))
        self.selection_changed()

    def selection_changed(self, _event=None):
        selection = self.table.selection()
        self.assign_button.configure(state="normal" if selection and self._base_ids else "disabled")
        if selection:
            self.status.set("Assignment is pending until you choose Apply.")
        else:
            self.status.set("Select an air wing to reassign it.")

    def assign(self):
        selection = self.table.selection()
        base_id = self._base_ids.get(self.base_choice.get())
        if not selection or base_id is None:
            messagebox.showinfo("Choose a base", "Select an air wing and an aircraft-capable ship.", parent=self)
            return
        try:
            changed = self.draft.assign(int(selection[0]), base_id)
        except ValueError as error:
            messagebox.showerror("Unable to reassign air wing", str(error), parent=self)
            return
        self.status.set("Air wing reassigned in this pending draft." if changed else "Air wing already uses that base.")
        self.refresh(int(selection[0]))

    def apply(self):
        try:
            changed = self.draft.apply()
        except ValueError as error:
            messagebox.showerror("Unable to apply air-wing changes", str(error), parent=self)
            return
        if changed:
            self.master.status.set("Unsaved changes — air wings updated")
        self.destroy()
