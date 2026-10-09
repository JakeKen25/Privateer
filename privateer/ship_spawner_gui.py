"""Ship Spawner entry point and staged cross-save copying."""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .busy import run_background
from .save import RTW3Save
from .ship_spawner import copy_block_reason, copy_ships
from .ship_status import appears_in_transfer_window
from .ships_gui import ship_stats
from .table_sort import sorted_with_blanks


class ShipSpawnerWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        super().__init__(parent)
        self.save, self.nation_index = save, nation_index
        self.title('Ship Spawner')
        self.transient(parent)
        body = ttk.Frame(self, padding=20)
        body.pack(fill='both', expand=True)
        ttk.Label(body, text=f'Spawn ships for {save.nation(nation_index).name}',
                  font=('Segoe UI', 13, 'bold')).pack(anchor='w', pady=(0, 12))
        ttk.Button(body, text='Copy from another save', command=self.open_copy).pack(fill='x', pady=5)
        ttk.Button(body, text='Use built-in designs', state='disabled').pack(fill='x', pady=5)
        ttk.Label(body, text='Built-in designs are not available yet.').pack(anchor='w', pady=5)
        ttk.Button(body, text='Close', command=self.destroy).pack(anchor='e', pady=(12, 0))
        self.bind('<Escape>', lambda _: self.destroy())
        self.grab_set()

    def open_copy(self):
        parent, save, index = self.master, self.save, self.nation_index
        self.destroy()
        ShipCopyWindow(parent, save, index)


class ShipCopyWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        super().__init__(parent)
        self.save, self.nation_index = save, nation_index
        self.source_save = None
        self.ships, self.stats, self.blocks = {}, {}, {}
        self.pending = set()
        self.sort_column, self.reverse = 'name', False
        self.title(f'Ship Spawner — {save.nation(nation_index).name}')
        self.geometry('1050x650')
        self.minsize(780, 430)
        self.transient(parent)

        # Pack fixed controls first so the table absorbs shrinking space.
        footer = ttk.Frame(self, padding=12)
        footer.pack(side='bottom', fill='x')
        self.status = tk.StringVar(value='Choose a source campaign folder.')
        ttk.Label(footer, textvariable=self.status).pack(anchor='w')
        ttk.Label(footer, text='Apply accepts copies; Save or Save As writes them to the destination campaign.').pack(anchor='w', pady=5)
        buttons = ttk.Frame(footer)
        buttons.pack(fill='x')
        ttk.Button(buttons, text='Reset changes', command=self.reset).pack(side='left')
        ttk.Button(buttons, text='Cancel', command=self.destroy).pack(side='right')
        self.apply_button = ttk.Button(buttons, text='Apply', command=self.apply, state='disabled')
        self.apply_button.pack(side='right', padx=8)

        body = ttk.Frame(self, padding=(12, 12, 12, 0))
        body.pack(fill='both', expand=True)
        ttk.Label(body, text=f'Copy ships to {save.nation(nation_index).name}',
                  font=('Segoe UI', 13, 'bold')).pack(anchor='w')
        ttk.Label(body, text='Copies keep equipment, history and construction state. They arrive in the receiving nation’s home area without a commander.',
                  wraplength=950).pack(anchor='w', pady=(3, 8))
        source_bar = ttk.Frame(body)
        source_bar.pack(fill='x')
        self.source_path = tk.StringVar(value='No source selected')
        self.browse_button = ttk.Button(source_bar, text='Browse source…', command=self.browse)
        self.browse_button.pack(side='right')
        ttk.Label(source_bar, textvariable=self.source_path, wraplength=750).pack(side='left', fill='x', expand=True)

        filters = ttk.Frame(body)
        filters.pack(fill='x', pady=10)
        self.owner = tk.StringVar()
        self.search = tk.StringVar()
        ttk.Label(filters, text='Source nation').pack(side='left')
        self.owner_box = ttk.Combobox(filters, textvariable=self.owner, state='readonly', width=25)
        self.owner_box.pack(side='left', padx=8)
        ttk.Label(filters, text='Search').pack(side='left')
        ttk.Entry(filters, textvariable=self.search, width=28).pack(side='left', padx=8)
        ttk.Button(filters, text='Stage selected', command=self.stage).pack(side='left')
        ttk.Button(filters, text='Unstage selected', command=self.unstage).pack(side='left', padx=5)

        frame = ttk.Frame(body)
        frame.pack(fill='both', expand=True)
        columns = ('name', 'type', 'class', 'displacement', 'year', 'status', 'staged')
        self.table = ttk.Treeview(frame, columns=columns, show='headings', selectmode='extended')
        for key, title, width in [('name', 'Name', 170), ('type', 'Type', 55), ('class', 'Class', 170),
                                  ('displacement', 'Displacement', 95), ('year', 'Built', 60),
                                  ('status', 'Status', 160), ('staged', 'Pending copy', 100)]:
            self.table.heading(key, text=title, command=lambda c=key: self.sort(c))
            self.table.column(key, width=width, minwidth=45)
        vertical = ttk.Scrollbar(frame, orient='vertical', command=self.table.yview)
        horizontal = ttk.Scrollbar(frame, orient='horizontal', command=self.table.xview)
        self.table.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        vertical.pack(side='right', fill='y')
        horizontal.pack(side='bottom', fill='x')
        self.table.pack(fill='both', expand=True)
        self.table.bind('<<TreeviewSelect>>', self.details)
        self.owner.trace_add('write', lambda *_: self.render())
        self.search.trace_add('write', lambda *_: self.render())
        self.bind('<Escape>', lambda _: self.destroy())
        self.grab_set()

    def browse(self):
        if self.pending and not messagebox.askyesno('Change source', 'Discard the pending copies and choose another source?', parent=self):
            return
        folder = filedialog.askdirectory(parent=self, title='Choose the source Game folder', initialdir=str(self.save.folder.parent))
        if not folder:
            return
        def load():
            source = RTW3Save.load(folder)
            if source.folder == self.save.folder:
                raise ValueError('Choose a different source campaign folder')
            source.validate_or_raise()
            return source
        run_background(self, 'Reading source fleet…', load, self.loaded, self.load_failed)

    def load_failed(self, exc):
        self.grab_set()
        messagebox.showerror('Unable to load source', str(exc), parent=self)

    def loaded(self, source):
        self.source_save = source
        self.pending.clear()
        self.ships = {s.record_index: s for n in source.nations for s in n.ships
                      if appears_in_transfer_window(s.section.fields())}
        self.stats = {hull: ship_stats(ship) for hull, ship in self.ships.items()}
        self.blocks = {hull: copy_block_reason(ship) for hull, ship in self.ships.items()}
        self.source_path.set(str(source.folder))
        values = [f'{n.index}: {n.name}' for n in source.nations]
        self.owner_box.configure(values=values)
        self.owner.set(values[0])
        self.grab_set()

    def render(self):
        self.table.delete(*self.table.get_children())
        if not self.source_save or not self.owner.get():
            return
        owner = int(self.owner.get().split(':', 1)[0])
        needle = self.search.get().strip().casefold()
        rows = [h for h, s in self.ships.items() if s.owner_index == owner
                and needle in ' '.join(self.stats[h].values()).casefold()]
        rows = sorted_with_blanks(rows, lambda h: (h in self.pending if self.sort_column == 'staged'
                                  else self.stats[h][self.sort_column]), reverse=self.reverse,
                                  numeric=self.sort_column in {'year', 'displacement'})
        for h in rows:
            stats = self.stats[h]
            self.table.insert('', 'end', iid=str(h), values=tuple(stats[k] for k in
                ('name', 'type', 'class', 'displacement', 'year', 'status')) + ('Yes' if h in self.pending else '',))
        self.status.set(f'{len(rows)} shown; {len(self.pending)} pending copies across all source nations.')
        self.apply_button.configure(state='normal' if self.pending else 'disabled')

    def sort(self, column):
        self.reverse = not self.reverse if self.sort_column == column else False
        self.sort_column = column
        self.render()

    def details(self, _event=None):
        selected = self.table.selection()
        if selected:
            hull = int(selected[0])
            self.status.set(self.blocks[hull] or f'{self.ships[hull].name}: ready to stage. Duplicate names get a copy suffix.')

    def stage(self):
        failures = []
        for item in self.table.selection():
            hull = int(item)
            if self.blocks[hull]:
                failures.append(f'{self.ships[hull].name}: {self.blocks[hull]}')
            else:
                self.pending.add(hull)
        self.render()
        if failures:
            messagebox.showwarning('Some ships were not staged', '\n'.join(failures), parent=self)

    def unstage(self):
        self.pending.difference_update(int(i) for i in self.table.selection())
        self.render()

    def reset(self):
        self.pending.clear()
        self.render()

    def apply(self):
        if not self.pending:
            return
        try:
            copies = copy_ships(self.save, self.source_save, sorted(self.pending), self.nation_index)
        except (ValueError, KeyError, OSError, UnicodeError) as exc:
            messagebox.showerror('Unable to copy ships', str(exc), parent=self)
            return
        self.master.render_main_table()
        self.master.status.set(f'Unsaved changes — {len(copies)} ship copies added')
        self.destroy()
