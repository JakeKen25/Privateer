"""Basic tension management for a selected nation."""
import tkinter as tk
from tkinter import ttk, messagebox
from .diplomacy import Diplomacy


class TensionWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        super().__init__(parent)
        self.save, self.nation_index = save, nation_index
        self.entries, self.original = {}, {}
        self.title(f'Manage Relations - {save.nation(nation_index).name}')
        self.geometry('870x700')
        self.minsize(760, 570)
        self.transient(parent)
        try:
            self.diplomacy = Diplomacy(save)
            if nation_index not in self.diplomacy.sections:
                raise ValueError('This stored nation is outside the supported relations matrix (slots 0-8).')
        except ValueError as exc:
            messagebox.showerror('Unsupported diplomacy layout', str(exc), parent=parent)
            self.destroy()
            return
        body = ttk.Frame(self, padding=14)
        body.pack(fill='both', expand=True)
        ttk.Label(body, text=f'Relations for {save.nation(nation_index).name}', font=('Segoe UI', 13, 'bold')).pack(anchor='w')
        ttk.Label(body, text='Enter a new Tension Level for each pair to change; leave other entries blank.').pack(anchor='w')
        ttk.Label(body, text='Basic editor range: 0-20. This is an editor guardrail, not a known game limit.').pack(anchor='w')
        rows = ttk.Frame(body)
        rows.pack(fill='x', pady=10)
        for col, text in enumerate(('Other nation', 'Current Tension Level', 'New Tension Level', '')):
            ttk.Label(rows, text=text).grid(row=0, column=col, sticky='w', padx=8, pady=6)
        rows.columnconfigure(0, weight=1)
        for row, other in enumerate((i for i in range(9) if i != nation_index), 1):
            ttk.Label(rows, text=save.nation(other).name).grid(row=row, column=0, sticky='w', padx=8, pady=8)
            try:
                values = self.diplomacy.values(nation_index, other)
                editable = self.diplomacy.editable(nation_index, other)
                self.original[other] = values
                label = ' / '.join(map(str, values)) if len(set(values)) > 1 else str(values[0])
                if len(set(values)) > 1:
                    label += ' (differs)'
                if not editable:
                    label += ' (read-only)'
            except ValueError:
                label, editable = 'Missing/invalid', False
            ttk.Label(rows, text=label).grid(row=row, column=1, sticky='w', padx=8)
            variable = tk.StringVar()
            self.entries[other] = variable
            entry = ttk.Entry(rows, textvariable=variable, width=12, state='normal' if editable else 'disabled')
            entry.grid(row=row, column=2, padx=8)
            entry.bind('<FocusIn>', lambda e, o=other: self.show_details(o))
            ttk.Button(rows, text='Details', command=lambda o=other: self.show_details(o)).grid(row=row, column=3, padx=8)
        self.details = tk.Text(body, height=8, wrap='word', state='disabled')
        self.details.pack(fill='both', expand=True)
        ttk.Label(body, text='War and alliance state are preserved. Apply stages edits; Save writes them with a backup.').pack(anchor='w', pady=8)
        buttons = ttk.Frame(body)
        buttons.pack(fill='x')
        ttk.Button(buttons, text='Reset changes', command=self.reset_changes).pack(side='left')
        ttk.Button(buttons, text='Cancel', command=self.destroy).pack(side='right')
        ttk.Button(buttons, text='Apply', command=self.apply).pack(side='right', padx=8)
        self.show_details(next(iter(self.entries)))
        self.bind('<Escape>', lambda e: self.destroy())
        self.grab_set()
        messagebox.showwarning(
            "Manage Relations - Under Development",
            "This section is under development.\n\nOnly numerical Tension Levels can be edited. War and alliance values are preserved.",
            parent=self,
        )

    def show_details(self, other):
        try:
            text = self.diplomacy.description(self.nation_index, other)
        except ValueError as exc:
            text = str(exc)
        self.details.configure(state='normal')
        self.details.delete('1.0', 'end')
        self.details.insert('1.0', f'{self.save.nation(self.nation_index).name} / {self.save.nation(other).name}\n\n{text}')
        self.details.configure(state='disabled')

    def reset_changes(self):
        for variable in self.entries.values():
            variable.set('')

    def apply(self):
        try:
            changes = {}
            for other, variable in self.entries.items():
                raw = variable.get().strip()
                if raw:
                    value = int(raw)
                    if any(v != value for v in self.original[other]):
                        changes[(self.nation_index, other)] = value
            self.save.set_tensions(changes)
        except (ValueError, KeyError) as exc:
            messagebox.showerror('Unable to apply tensions', str(exc), parent=self)
            return
        if changes:
            self.master.status.set('Unsaved changes')
        self.destroy()
