"""Relationship editing and a shared nation-by-nation overview."""
import tkinter as tk
from tkinter import ttk, messagebox
from .diplomacy import Diplomacy, RELATION_ACTIONS, relation_plan, apply_relations


class TensionWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        super().__init__(parent)
        self.save, self.nation_index = save, nation_index
        self.entries, self.original, self.actions = {}, {}, {}
        self.title(f'Relationship Manager — {save.nation(nation_index).name}')
        self.geometry(f'{min(1240, self.winfo_screenwidth()-80)}x{min(1000, self.winfo_screenheight()-100)}')
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
        viewport = ttk.Frame(self)
        viewport.pack(fill='both', expand=True)
        canvas = tk.Canvas(viewport, highlightthickness=0)
        vertical = ttk.Scrollbar(viewport, orient='vertical', command=canvas.yview)
        horizontal = ttk.Scrollbar(viewport, orient='horizontal', command=canvas.xview)
        canvas.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        vertical.pack(side='right', fill='y')
        horizontal.pack(side='bottom', fill='x')
        canvas.pack(fill='both', expand=True)
        body = ttk.Frame(canvas, padding=14)
        content = canvas.create_window((0, 0), window=body, anchor='nw')
        body.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>', lambda e: canvas.itemconfigure(content, width=max(1120, e.width)))
        self.bind('<MouseWheel>', lambda e: canvas.yview_scroll(-int(e.delta / 120), 'units'))
        ttk.Label(body, text=f'Relations for {save.nation(nation_index).name}', font=('Segoe UI', 13, 'bold')).pack(anchor='w')
        self.build_matrix(body)
        ttk.Label(body, text='Enter a new Tension Level for each pair to change; leave other entries blank.').pack(anchor='w')
        ttk.Label(body, text='Tension: 0–20. Use the actions below to manage wars and alliances.').pack(anchor='w')
        rows = ttk.Frame(body)
        rows.pack(fill='x', pady=10)
        for col, text in enumerate(('Other nation', 'Current Tension Level', 'New Tension Level', 'Action', '', 'Status')):
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
            try:
                state = self.diplomacy.status(nation_index, other)
            except ValueError:
                state = 'Unknown'
            ttk.Label(rows, text=state, font=('Segoe UI', 9, 'bold')).grid(row=row, column=5, sticky='w', padx=8)
            ttk.Label(rows, text=label).grid(row=row, column=1, sticky='w', padx=8)
            variable = tk.StringVar()
            self.entries[other] = variable
            entry = ttk.Entry(rows, textvariable=variable, width=12, state='normal' if editable else 'disabled')
            entry.grid(row=row, column=2, padx=8)
            entry.bind('<FocusIn>', lambda e, o=other: self.show_details(o))
            action = tk.StringVar()
            self.actions[other] = action
            ttk.Combobox(rows, textvariable=action, values=('',) + RELATION_ACTIONS, state='readonly', width=20).grid(row=row, column=3, padx=8)
            action.trace_add('write', lambda *_, o=other: self.show_details(o))
            ttk.Button(rows, text='Details', command=lambda o=other: self.show_details(o)).grid(row=row, column=4, padx=8)
        self.details = tk.Text(body, height=5, wrap='word', state='disabled')
        self.details.pack(fill='both', expand=True)
        ttk.Label(body, text='Choose a tension edit OR action per pair. Apply changes memory; Save writes with backups.').pack(anchor='w', pady=8)
        buttons = ttk.Frame(self, padding=10)
        buttons.pack(side='bottom', fill='x', before=viewport)
        ttk.Button(buttons, text='Reset changes', command=self.reset_changes).pack(side='left')
        ttk.Button(buttons, text='Cancel', command=self.destroy).pack(side='right')
        ttk.Button(buttons, text='Apply', command=self.apply).pack(side='right', padx=8)
        self.show_details(next(iter(self.entries)))
        self.bind('<Escape>', lambda e: self.destroy())
        self.grab_set()

    def build_matrix(self, body):
        ttk.Label(body, text='All nations — current relations', font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(12, 4))
        ttk.Label(body, text='Rows relate to columns. Numbers are tension; War and Allied mark status. Pending edits appear after Apply.').pack(anchor='w')
        table = ttk.Frame(body)
        table.pack(fill='x', pady=(6, 12))
        self.matrix_labels = {}
        names = [self.save.nation(i).name for i in range(9)]
        for col, name in enumerate(['Nation'] + names):
            tk.Label(table, text=name, bg='#d2d2d2', fg='#202020',
                     font=('Segoe UI', 9, 'bold'), wraplength=105, padx=4, pady=6).grid(row=0, column=col, sticky='nsew', padx=1, pady=1)
            table.columnconfigure(col, weight=1)
        shades = (('#fafafa', '#ededed'), ('#e5e5e5', '#d8d8d8'))
        for row, name in enumerate(names):
            tk.Label(table, text=name, bg='#d2d2d2', fg='#202020', anchor='w',
                     font=('Segoe UI', 9, 'bold'), padx=6, pady=5).grid(row=row+1, column=0, sticky='nsew', padx=1, pady=1)
            for col in range(9):
                cell = tk.Label(table, text=self.diplomacy.matrix_cell(row, col),
                                bg=shades[row % 2][col % 2], fg='#202020',
                                font=('Segoe UI', 9), wraplength=100, padx=4, pady=5)
                cell.grid(row=row+1, column=col+1, sticky='nsew', padx=1, pady=1)
                self.matrix_labels[row, col] = cell

    def show_details(self, other):
        try:
            text = self.diplomacy.description(self.nation_index, other)
            action = self.actions[other].get()
            if action:
                plan = relation_plan(self.save, self.nation_index, other, action)
                text += '\n\n' + action + ':\n' + '\n'.join(f'{s.name}/{k}: {old} -> {new}' for s, k, old, new in plan)
                text += '\nFinances and territory remain unchanged.'
        except ValueError as exc:
            text = str(exc)
        self.details.configure(state='normal')
        self.details.delete('1.0', 'end')
        self.details.insert('1.0', f'{self.save.nation(self.nation_index).name} / {self.save.nation(other).name}\n\n{text}')
        self.details.configure(state='disabled')

    def reset_changes(self):
        for variable in list(self.entries.values()) + list(self.actions.values()):
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
            actions = {(self.nation_index, other): v.get() for other, v in self.actions.items() if v.get()}
            apply_relations(self.save, changes, actions)
        except (ValueError, KeyError) as exc:
            messagebox.showerror('Unable to apply relations', str(exc), parent=self)
            return
        if changes or actions:
            self.master.status.set('Unsaved changes')
        self.destroy()
