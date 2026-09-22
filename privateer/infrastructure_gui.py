"""Dockyards and staged fortification editing."""
import tkinter as tk
from tkinter import messagebox, ttk
from .fortifications import (apply_infrastructure, available_types, base_sites,
                             owned_locations, records, status, type_for)
from .table_sort import heading_text, sorted_with_blanks


class InfrastructureWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        super().__init__(parent)
        self.save, self.nation = save, save.nation(nation_index)
        self.pending, self.additions = {}, []
        self.sort_column, self.sort_reverse = 'Name', False
        self.title(f'Infrastructure and Fortifications Manager — {self.nation.name}')
        self.geometry('1080x720')
        self.minsize(900, 600)
        self.transient(parent)
        self.problem = ''
        try:
            self.records = records(save, nation_index)
            self.types = available_types(save)
            self.locations = owned_locations(save, nation_index)
        except ValueError as exc:
            self.records, self.types, self.locations = {}, [], []
            self.problem = str(exc)
        install = getattr(getattr(parent, 'settings', None), 'rtw3_install_directory', '')
        try:
            self.sites = base_sites(install) if install else {}
        except (OSError, ValueError):
            self.sites = {}
        body = ttk.Frame(self, padding=16)
        body.pack(fill='both', expand=True)
        ttk.Label(body, text=f'Infrastructure and Fortifications — {self.nation.name}',
                  font=('Segoe UI', 13, 'bold')).pack(anchor='w')
        dock = ttk.Frame(body)
        dock.pack(fill='x', pady=12)
        ttk.Label(dock, text='Dockyard size (maximum displacement)').pack(side='left')
        self.dock_size = tk.StringVar(value='' if self.nation.dock_size is None else str(self.nation.dock_size))
        ttk.Entry(dock, textvariable=self.dock_size, width=18,
                  state='normal' if self.nation.dock_size is not None else 'disabled').pack(side='left', padx=12)
        toolbar = ttk.Frame(body)
        toolbar.pack(fill='x', pady=5)
        ttk.Label(toolbar, text='Fortifications — click a column heading to sort').pack(side='left')
        ttk.Button(toolbar, text='Add installation…', command=self.add,
                   state='disabled' if self.problem else 'normal').pack(side='right')
        ttk.Button(toolbar, text='Edit selected…', command=self.edit).pack(side='right', padx=8)
        frame = ttk.Frame(body)
        frame.pack(fill='both', expand=True)
        columns = ('Name', 'Classname', 'LocationAreaName', 'AircraftCapacity', 'State', 'Maintenance', 'Change')
        self.table = ttk.Treeview(frame, columns=columns, show='headings', selectmode='browse')
        self.labels = dict(zip(columns, ('Name', 'Type', 'Possession', 'Capacity', 'State', 'Maintenance', 'Pending')))
        for key in columns:
            self.table.heading(key, text=self.labels[key], command=lambda k=key: self.sort_by(k))
            self.table.column(key, width=190 if key in columns[:3] else 90, minwidth=60)
        scroll = ttk.Scrollbar(frame, command=self.table.yview)
        scroll.pack(side='right', fill='y')
        horizontal = ttk.Scrollbar(frame, orient='horizontal', command=self.table.xview)
        horizontal.pack(side='bottom', fill='x')
        self.table.configure(yscrollcommand=scroll.set, xscrollcommand=horizontal.set)
        self.table.pack(fill='both', expand=True)
        self.table.bind('<Double-1>', lambda e: self.edit() if self.table.identify_region(e.x, e.y) == 'cell' else None)
        self.status = tk.StringVar()
        ttk.Label(body, textvariable=self.status, wraplength=1000).pack(anchor='w', pady=8)
        ttk.Label(body, text='Additions are built immediately, with no funds deducted. Apply stages changes; Save writes them.',
                  wraplength=1000).pack(anchor='w')
        ttk.Label(body, text='Existing airbase sites and aircraft links are preserved. Construction and retired records are shown read-only.',
                  wraplength=1000).pack(anchor='w', pady=(3, 10))
        buttons = ttk.Frame(body)
        buttons.pack(fill='x')
        ttk.Button(buttons, text='Reset changes', command=self.reset).pack(side='left')
        ttk.Button(buttons, text='Cancel', command=self.destroy).pack(side='right')
        ttk.Button(buttons, text='Apply', command=self.apply).pack(side='right', padx=8)
        self.render()
        self.bind('<Escape>', lambda e: self.destroy())
        self.grab_set()

    def render(self):
        selection = self.table.selection()
        self.table.delete(*self.table.get_children())
        rows = []
        for slot, original in self.records.items():
            record = original | self.pending.get(slot, {})
            item = type_for(record['Classname'])
            if slot in self.pending and item and item != type_for(original['Classname']):
                record = record | {'AircraftCapacity': str(item.capacity), 'Maintenance': str(item.maintenance)}
            rows.append((str(slot), record | {'State': status(original), 'Change': 'Edited' if slot in self.pending else ''}))
        for index, addition in enumerate(self.additions):
            item = type_for(addition['Classname'])
            rows.append((f'new{index}', addition | {'AircraftCapacity': str(item.capacity),
                         'Maintenance': str(item.maintenance), 'State': 'Built', 'Change': 'New'}))
        rows = sorted_with_blanks(rows, lambda r: r[1][self.sort_column], reverse=self.sort_reverse,
                                 numeric=self.sort_column in ('AircraftCapacity', 'Maintenance'))
        for identity, record in rows:
            self.table.insert('', 'end', iid=identity, values=[record[k] for k in self.labels])
        if selection and self.table.exists(selection[0]):
            self.table.selection_set(selection[0])
        for key, label in self.labels.items():
            self.table.heading(key, text=heading_text(label, key == self.sort_column, self.sort_reverse))
        self.status.set(self.problem or f'{len(self.records)} installations; {len(self.pending)} edits and {len(self.additions)} additions staged.')

    def sort_by(self, column):
        self.sort_reverse = not self.sort_reverse if column == self.sort_column else False
        self.sort_column = column
        self.render()

    def add(self):
        FortificationDialog(self)

    def edit(self):
        selection = self.table.selection()
        if not selection:
            self.status.set('Select an installation first.')
            return
        identity = selection[0]
        if not identity.startswith('new'):
            record = self.records[int(identity)]
            if status(record) != 'Built' or type_for(record['Classname']) is None:
                self.status.set('This installation is read-only: it is not built or its type is not recognized.')
                return
        FortificationDialog(self, identity)

    def reset(self):
        self.pending.clear()
        self.additions.clear()
        self.dock_size.set('' if self.nation.dock_size is None else str(self.nation.dock_size))
        self.render()

    def apply(self):
        try:
            dock = None if self.nation.dock_size is None else int(self.dock_size.get().strip().replace(',', ''))
            apply_infrastructure(self.save, self.nation.index, dock, self.pending, self.additions, sites=self.sites)
        except (ValueError, TypeError) as exc:
            messagebox.showerror('Unable to apply infrastructure changes', str(exc), parent=self)
            return
        if self.save.modified:
            self.master.status.set('Unsaved changes')
        self.destroy()


class FortificationDialog(tk.Toplevel):
    def __init__(self, parent, identity=None):
        super().__init__(parent)
        self.identity = identity
        self.existing = identity is not None and not identity.startswith('new')
        if self.existing:
            record = parent.records[int(identity)] | parent.pending.get(int(identity), {})
        elif identity is not None:
            record = parent.additions[int(identity[3:])]
        else:
            record = {'Name': '', 'Classname': parent.types[0].name,
                      'LocationAreaName': parent.locations[0] if parent.locations else ''}
        self.title('Edit installation' if identity is not None else 'Add installation')
        self.transient(parent)
        self.resizable(False, False)
        body = ttk.Frame(self, padding=16)
        body.pack(fill='both', expand=True)
        self.kind = tk.StringVar(value=type_for(record['Classname']).name)
        self.location = tk.StringVar(value=record['LocationAreaName'])
        self.name = tk.StringVar(value=record['Name'])
        self.site = tk.StringVar()
        old_type = type_for(record['Classname'])
        types = [t.name for t in parent.types if not self.existing or t.family == old_type.family]
        if self.existing and old_type.name not in types:
            types.append(old_type.name)
        self.type_box = ttk.Combobox(body, textvariable=self.kind, values=types, state='readonly', width=42)
        self.location_box = ttk.Combobox(body, textvariable=self.location,
                                        values=sorted(set(parent.locations + [record['LocationAreaName']])), state='readonly', width=42)
        self.name_entry = ttk.Entry(body, textvariable=self.name, width=45)
        self.site_box = ttk.Combobox(body, textvariable=self.site, state='readonly', width=42)
        for row, (label, widget) in enumerate([('Type', self.type_box), ('Possession', self.location_box),
                                               ('Name', self.name_entry), ('Airbase site', self.site_box)]):
            ttk.Label(body, text=label).grid(row=row, column=0, sticky='w', padx=(0, 12), pady=6)
            widget.grid(row=row, column=1, sticky='ew', pady=6)
        self.note = tk.StringVar()
        ttk.Label(body, textvariable=self.note, wraplength=480).grid(row=4, column=0, columnspan=2, sticky='w', pady=10)
        buttons = ttk.Frame(body)
        buttons.grid(row=5, column=0, columnspan=2, sticky='e')
        ttk.Button(buttons, text='Cancel', command=self.close).pack(side='right')
        ttk.Button(buttons, text='Stage', command=self.stage).pack(side='right', padx=8)
        self.type_box.bind('<<ComboboxSelected>>', lambda e: self.update_fields())
        self.location_box.bind('<<ComboboxSelected>>', lambda e: self.update_fields())
        self.site_box.bind('<<ComboboxSelected>>', lambda e: self.update_name())
        self.update_fields()
        self.bind('<Escape>', lambda e: self.close())
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.grab_set()

    def update_fields(self):
        item = type_for(self.kind.get())
        air = item.family in ('airbase', 'airship')
        self.name_entry.configure(state='disabled' if air else 'normal')
        self.location_box.configure(state='disabled' if air and self.existing else 'readonly')
        self.site_box.configure(state='readonly' if air and not self.existing else 'disabled')
        choices = self.master.sites.get(self.location.get(), [])
        self.site_box.configure(values=choices)
        if self.site.get() not in choices:
            current = self.name.get()
            self.site.set(next((s for s in choices if current in ('Airbase ' + s, 'Airship base ' + s)), choices[0] if choices else ''))
        if air and not self.existing:
            self.update_name()
        elif not self.name.get():
            self.name.set(f'{"MTB squadron" if item.family == "mtb" else "Battery"} Privateer {len(self.master.records) + len(self.master.additions) + 1}')
        self.note.set('Choose a named site from the game installation configured in Settings.' if air and not self.existing else
                      'Existing base names, locations, IDs and assigned aircraft are preserved.' if air else
                      'Choose a possession owned by this nation. New installations are immediately available.')

    def update_name(self):
        prefix = 'Airbase ' if type_for(self.kind.get()).family == 'airbase' else 'Airship base '
        self.name.set(prefix + self.site.get() if self.site.get() else '')

    def stage(self):
        edit = {'Name': self.name.get().strip(), 'Classname': self.kind.get(), 'LocationAreaName': self.location.get()}
        if not edit['Name'] or not edit['LocationAreaName']:
            messagebox.showerror('Missing details', 'Select a possession and enter a name or choose a valid airbase site.', parent=self)
            return
        if self.identity is None:
            self.master.additions.append(edit)
        elif self.existing:
            slot = int(self.identity)
            original = self.master.records[slot]
            if (edit['Name'] == original['Name'] and edit['LocationAreaName'] == original['LocationAreaName']
                    and type_for(edit['Classname']) == type_for(original['Classname'])):
                self.master.pending.pop(slot, None)
            else:
                self.master.pending[slot] = edit
        else:
            self.master.additions[int(self.identity[3:])] = edit
        self.master.render()
        self.close()

    def close(self):
        self.master.grab_set()
        self.destroy()
