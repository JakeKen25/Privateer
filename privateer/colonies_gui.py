"""Searchable possession ownership editor with staged transfers."""
import tkinter as tk
from tkinter import ttk, messagebox
from .colonies import (
    is_home_area_possession,
    map_area_name,
    map_document,
    nation_home_areas,
    possessions,
)
from .table_sort import heading_text, sorted_with_blanks


class ColoniesWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        super().__init__(parent)
        self.save = save
        self.pending = {}
        self.sort_column = None
        self.sort_reverse = False
        self.title(f'Colony Manager — {save.nation(nation_index).name}')
        self.geometry('1000x700')
        self.minsize(800, 550)
        self.transient(parent)
        try:
            self.records = {(p.area, p.index): p for p in possessions(save)}
            self.home_areas = nation_home_areas(save)
            self.locked = {
                pair for pair, possession in self.records.items()
                if is_home_area_possession(save, possession)
            }
            filename = map_document(save)[0]
        except ValueError as exc:
            messagebox.showerror('Colony data unavailable', str(exc), parent=parent)
            self.destroy()
            return
        body = ttk.Frame(self, padding=12)
        body.pack(fill='both', expand=True)
        ttk.Label(body, text=f'Possession ownership - {filename}', font=('Segoe UI', 13, 'bold')).pack(anchor='w')
        ttk.Label(body, text='Home-area possessions are shown but cannot be transferred. Ownership changes do not settle wars or move ships.').pack(anchor='w')
        filters = ttk.Frame(body)
        filters.pack(fill='x', pady=10)
        self.search = tk.StringVar()
        self.owner_filter = tk.StringVar(value=save.nation(nation_index).name)
        owners = sorted({n.name for n in save.nations} | {'Neutral'})
        ttk.Label(filters, text='Current owner').pack(side='left')
        ttk.Combobox(filters, textvariable=self.owner_filter, values=['All owners']+sorted(set(owners)|{p.owner for p in self.records.values()}), state='readonly', width=23).pack(side='left', padx=8)
        ttk.Label(filters, text='Search').pack(side='left')
        ttk.Entry(filters, textvariable=self.search, width=28).pack(side='left', padx=8)
        self.count = tk.StringVar()
        ttk.Label(filters, textvariable=self.count).pack(side='right')
        frame = ttk.Frame(body)
        frame.pack(fill='both', expand=True)
        self.columns = ('name','area','owner','new','status','value','oil','base')
        self.table = ttk.Treeview(frame, columns=self.columns, show='headings', selectmode='extended')
        self.heading_labels = {}
        for key, label, width in [('name','Possession',190),('area','Map area',190),('owner','Current owner',120),('new','New owner',120),('status','Transfer status',135),('value','Value',55),('oil','Oil',40),('base','Base',55)]:
            self.heading_labels[key] = label
            self.table.heading(key,text=label,command=lambda column=key:self.sort_by(column)); self.table.column(key,width=width,minwidth=40)
        self.table.tag_configure('home', foreground='#777777')
        scroll=ttk.Scrollbar(frame,orient='vertical',command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right',fill='y'); self.table.pack(fill='both',expand=True)
        editor=ttk.Frame(body); editor.pack(fill='x',pady=12)
        ttk.Label(editor,text='New owner for selected possessions').pack(side='left')
        self.new_owner=tk.StringVar(value=save.nation(nation_index).name)
        ttk.Combobox(editor,textvariable=self.new_owner,values=owners,state='readonly',width=23).pack(side='left',padx=8)
        ttk.Button(editor,text='Stage transfer',command=self.stage).pack(side='left')
        self.status=tk.StringVar(value='No changes')
        ttk.Label(body,textvariable=self.status).pack(anchor='w')
        ttk.Label(body,text='Apply stages ownership edits in memory. Use Save or Save As to write them.').pack(anchor='w',pady=6)
        buttons=ttk.Frame(body);buttons.pack(fill='x')
        ttk.Button(buttons,text='Reset changes',command=self.reset_changes).pack(side='left')
        ttk.Button(buttons,text='Cancel',command=self.destroy).pack(side='right')
        ttk.Button(buttons,text='Apply',command=self.apply).pack(side='right',padx=8)
        self.search.trace_add('write',lambda *_: self.render())
        self.owner_filter.trace_add('write',lambda *_: self.render())
        self.render();self.bind('<Escape>',lambda e:self.destroy());self.grab_set()

    def render(self):
        self.table.delete(*self.table.get_children())
        rows=[]
        for pair,p in self.records.items():
            if self.owner_filter.get() not in ('All owners',p.owner):continue
            area_name = map_area_name(p.area)
            transfer_status = 'Home area (locked)' if pair in self.locked else 'Transferable'
            if self.search.get().strip().casefold() not in f'{p.name} {p.owner} {area_name} {transfer_status}'.casefold():continue
            values={'name':p.name,'area':area_name,'owner':p.owner,'new':self.pending.get(pair,''),
                    'status':transfer_status,
                    'value':p.value,'oil':p.oil,'base':p.base}
            rows.append((pair,values))
        if self.sort_column:
            rows=sorted_with_blanks(rows,lambda row:row[1][self.sort_column],
                                   reverse=self.sort_reverse,
                                   numeric=self.sort_column in {'value','oil','base'})
        for pair,values in rows:
            self.table.insert('','end',iid=f'{pair[0]}:{pair[1]}',
                              values=tuple(values[key] for key in self.columns),
                              tags=('home',) if pair in self.locked else ())
        self.count.set(f'{len(self.table.get_children())} / {len(self.records)} possessions')
        self.status.set(f'{len(self.pending)} staged ownership change(s)')

    def sort_by(self,column):
        if self.sort_column==column:self.sort_reverse=not self.sort_reverse
        else:self.sort_column,self.sort_reverse=column,False
        for key,label in self.heading_labels.items():
            self.table.heading(key,text=heading_text(label,key==column,self.sort_reverse))
        self.render()

    def stage(self):
        if not self.table.selection():
            self.status.set('Select one or more possessions first.');return
        skipped = 0
        for item in self.table.selection():
            pair=tuple(map(int,item.split(':')))
            if pair in self.locked:
                self.pending.pop(pair, None)
                skipped += 1
                continue
            owner=self.new_owner.get()
            if owner==self.records[pair].owner:self.pending.pop(pair,None)
            else:self.pending[pair]=owner
        self.render()
        if skipped:
            self.status.set(
                f'{len(self.pending)} staged ownership change(s); '
                f'{skipped} home-area possession(s) skipped'
            )

    def reset_changes(self):
        self.pending.clear();self.render()

    def apply(self):
        try:self.save.set_colony_owners(self.pending)
        except ValueError as exc:
            messagebox.showerror('Unable to apply ownership changes',str(exc),parent=self);return
        if self.pending:self.master.status.set('Unsaved changes')
        self.destroy()
