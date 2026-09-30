"""Searchable submarine inventory with explicit raw-data boundaries."""
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from .submarines import submarine_roster
from .table_sort import sorted_with_blanks, heading_text


class SubmarineWindow(tk.Toplevel):
    def __init__(self, parent, save, nation_index):
        records, warnings = submarine_roster(save, nation_index)
        super().__init__(parent)
        self.title(f'Submarine Manager — {save.nation(nation_index).name}')
        self.geometry('1100x620')
        self.transient(parent)
        self.records = records
        self.by_slot = {str(r.slot): r for r in records}
        self.sort_column, self.reverse = 'slot', False
        self.search, self.filter = tk.StringVar(), tk.StringVar(value='All')
        body = ttk.Frame(self, padding=12)
        body.pack(fill='both', expand=True)
        ttk.Label(body, text='Submarine inventory — read-only', font=('Segoe UI', 13, 'bold')).pack(anchor='w')
        ttk.Label(body, text='View saved records and history. Creation, transfer and editing need further validation.').pack(anchor='w', pady=(2, 8))
        bar = ttk.Frame(body); bar.pack(fill='x')
        ttk.Label(bar, text='Search').pack(side='left')
        ttk.Entry(bar, textvariable=self.search, width=35).pack(side='left', padx=8)
        ttk.Combobox(bar, textvariable=self.filter, state='readonly', width=24,
                     values=('All', 'In service', 'Under construction', 'Construction halted', 'Historical / sunk', 'Unknown')).pack(side='left')
        self.summary = tk.StringVar()
        ttk.Label(bar, textvariable=self.summary).pack(side='right')
        self.columns = {'slot':'Save slot', 'Name':'Name', 'type':'Type', 'status':'State',
                        'YearBuilt':'Built', 'RemainingBuildTime':'Build time (raw)',
                        'LocationAreaName':'Location', 'DestinationAreaName':'Destination',
                        'OrderedAreaName':'Ordered area', 'Availability':'Availability (raw)', 'Accuracy':'Accuracy (raw)'}
        table_frame = ttk.Frame(body); table_frame.pack(fill='both', expand=True, pady=8)
        self.table = ttk.Treeview(table_frame, columns=tuple(self.columns), show='headings', selectmode='browse')
        for key, label in self.columns.items():
            self.table.heading(key, text=label, command=lambda c=key:self.sort(c))
            self.table.column(key, width=145 if key in ('Name','type','status') or 'AreaName' in key else 100, stretch=False)
        self.table.grid(row=0, column=0, sticky='nsew')
        sy=ttk.Scrollbar(table_frame, orient='vertical', command=self.table.yview);sy.grid(row=0,column=1,sticky='ns')
        sx=ttk.Scrollbar(table_frame, orient='horizontal', command=self.table.xview);sx.grid(row=1,column=0,sticky='ew')
        self.table.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        table_frame.rowconfigure(0,weight=1);table_frame.columnconfigure(0,weight=1)
        ttk.Label(body, text='Selected record — exact saved fields (slot is not a permanent ID)').pack(anchor='w')
        self.details=ScrolledText(body,height=7,wrap='word');self.details.pack(fill='x',pady=4)
        self.details.configure(state='disabled')
        if warnings:
            ttk.Label(body,text='\n'.join(warnings),wraplength=1000).pack(anchor='w')
        ttk.Button(body,text='Close',command=self.destroy).pack(anchor='e')
        self.search.trace_add('write',lambda *_:self.render())
        self.filter.trace_add('write',lambda *_:self.render())
        self.table.bind('<<TreeviewSelect>>',self.show_details)
        self.bind('<Escape>',lambda _:self.destroy())
        self.render();self.grab_set()

    def sort(self, column):
        self.reverse = not self.reverse if self.sort_column == column else False
        self.sort_column = column
        self.render()

    def render(self):
        selected=self.table.selection()
        query=self.search.get().casefold();state=self.filter.get()
        rows=[r for r in self.records if (state=='All' or r.status==state or
              state=='Historical / sunk' and r.status in ('Historical','Sunk')) and
              query in ' '.join([str(r.slot),r.type_label,r.status,*r.fields.values()]).casefold()]
        numeric=self.sort_column in ('slot','YearBuilt','RemainingBuildTime','Availability','Accuracy')
        rows=sorted_with_blanks(rows,lambda r:r.value(self.sort_column),reverse=self.reverse,numeric=numeric)
        self.table.delete(*self.table.get_children())
        for r in rows:
            self.table.insert('', 'end', iid=str(r.slot), values=[r.value(k) for k in self.columns])
        for key,label in self.columns.items():
            self.table.heading(key,text=heading_text(label,key==self.sort_column,self.reverse))
        self.summary.set(f'{len(rows)} shown / {len(self.records)} records')
        if selected and self.table.exists(selected[0]):
            self.table.selection_set(selected[0])
        self.show_details()

    def show_details(self, _event=None):
        selection=self.table.selection()
        text='Select a submarine to inspect its saved fields.'
        if selection:
            record=self.by_slot[selection[0]]
            text='\n'.join(f'Sub{record.slot}{key}={value}' for key,value in record.fields.items())
        self.details.configure(state='normal');self.details.delete('1.0','end')
        self.details.insert('1.0',text);self.details.configure(state='disabled')
