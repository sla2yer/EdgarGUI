
import tkinter as tk
from functools import partial

from Edgar_filingviewer_handler import FilingViewerHandler


class FilingViewer:
    def __init__(self,  filings,  root_parent):
        self.root = root_parent
        
        tk.Grid.rowconfigure(self.root,  5,  weight=1)
        self.handler = FilingViewerHandler(filings)
        self.stringvar_sortby = tk.StringVar(self.root)
        self.cbox_sortby = tk.ttk.Combobox(self.root, textvariable=self.stringvar_sortby)
        self.cbox_sortby['values'] = ["alphabetical", "shrs/prn amount",  "shrs/prn change", "value", "value change"]
        self.cbox_sortby['state'] = 'readonly'
        self.stringvar_sortby.set('alphabetical')

        self.stringvar_pcl = tk.StringVar(self.root)
        self.cbox_pcl = tk.ttk.Combobox(self.root, textvariable=tk.StringVar(self.root))
        self.cbox_pcl['values'] = ['All', 'Put', 'Call', 'Long']
        self.cbox_pcl['state'] = 'readonly'
        self.cbox_pcl.current(0)

        self.stringvar_asc_desc = tk.StringVar(self.root)
        self.cbox_asc_desc = tk.ttk.Combobox(self.root, textvariable=tk.StringVar(self.root))
        self.cbox_asc_desc['values'] = ["ascending",  "descending"]
        self.cbox_asc_desc['state'] = 'readonly'
        self.cbox_asc_desc.current(0)
        
        self.cbox_date_from = tk.ttk.Combobox(self.root, textvariable=tk.StringVar(self.root))
        self.cbox_date_from['values'] = self.handler.getFilingDates()
        self.cbox_date_from['state'] = 'readonly'
        self.cbox_date_from.current(len(self.cbox_date_from['values'])-2)
        
        self.cbox_date_until= tk.ttk.Combobox(self.root, textvariable=tk.StringVar(self.root))
        self.cbox_date_until['values'] = self.handler.getFilingDates()
        self.cbox_date_until['state'] = 'readonly'
        self.cbox_date_until.current(len(self.cbox_date_until['values'])-1)
        
        self.label_search = tk.Label(self.root,  text="Enter a company name to search the holdings")
        self.entry_search = tk.Entry(self.root,  width=60)
        
        self.label_company_details = tk.Label(self.root,  text=self.handler.getCompanyDetailsString(),  justify=tk.LEFT)
        self.label_company_details.grid(row=0,  column=0,  columnspan=5,  sticky='w')
        self.label_search.grid(row=1,  column=0)
        self.entry_search.grid(row=2,  column=0,  columnspan=3)

        self.button_search = tk.Button(self.root,  text="search",  command=self.searchButtonActions)
        self.button_search.grid(row=2,  column=3)
        
        self.button_clear = tk.Button(self.root,  text="clear",  command=self.clearSearchButtonActions)
        self.button_clear.grid(row=2,  column=4)

        self.button_sort = tk.Button(self.root, text='sort', command=self.sortButtonActions)
        self.button_sort.grid(row=2, column=5)
        
        self.label_date = tk.Label(self.root,  text='Showing change from: ')
        self.label_date.grid(row=4,  column=0)
        
        self.cbox_date_until.grid(row=4,  column=3)
        self.label_date_until = tk.Label(self.root,  text='until: ')
        self.label_date_until.grid(row=4,  column=2)
        self.cbox_date_from.grid(row=4,  column=1)
        
        self.label_sort = tk.Label(self.root,  text="Sort results by:")
        self.label_sort.grid(row=4,  column=4)
        self.cbox_pcl.grid(row=4,  column=5)
        self.cbox_sortby.grid(row=4,  column=6)
        self.cbox_asc_desc.grid(row=4,  column=7)
        
        self.label_other_managers = tk.Label(self.root,  text="check to only show holding for the selected manager")
        self.label_other_managers.grid(row=1,  column=6,  columnspan=2)
        self.bool_other_manager = tk.IntVar()
        self.checkbutton_other_managager = tk.Checkbutton(self.root,  text="",  variable=self.bool_other_manager,  onvalue=1,  offvalue=0,  command=self.otherManagerCheckActions)
        self.checkbutton_other_managager.grid(row=2,  column=6,sticky="e")
        self.cbox_other_managers = tk.ttk.Combobox(self.root, textvariable=tk.StringVar(self.root))
        self.cbox_other_managers['values'] = ["Other manager 1", "Other manager 2"]
        self.cbox_other_managers['state'] = 'readonly'
        self.cbox_other_managers.current(0)
        self.cbox_other_managers.grid(row=2,  column=7)
        lbox_font = ("courier",  9)
        self.list_box_results = tk.Listbox(self.root, font=lbox_font, width=90,  exportselection=False,  selectmode=tk.MULTIPLE)
        self.list_box_results.grid(row=5, column=0, columnspan=8,  sticky="nsew")
        self.list_box_results.insert(0, self.handler.generateResultHeader())
        
        for result in self.handler.getResults( {'page': 0, 'start date': self.cbox_date_from.get(),  'end date': self.cbox_date_until.get(), 'asc or desc':self.cbox_asc_desc.get(),  'sort by':self.cbox_sortby.get(),   'other manager': self.cbox_other_managers.get(),  'bool only managers':self.bool_other_manager.get(),  'res per page':50 } ):
            self.list_box_results.insert(tk.END, result)
        
        
        self.button_back_res_page = tk.Button(self.root,  text="back",  command=self.backButtonActions)
        self.button_back_res_page.grid(row=6,  column=2)
        
        self.button_next_res_page = tk.Button(self.root,  text="next",  command=self.nextButtonActions)
        self.button_next_res_page.grid(row=6,  column=6)
        #-----------------------------GET THE NUMBER OF PAGES IN THE HANDLER-----------------------
        #-------------------------ACTUALLY JUST MAKE A METHOD THAT RETURNS THE RES PAGE NUMBER STRING------------
        #action_with_arg = partial(self.hander.getPageNumberString,  root)
        self.label_res_page_1 = tk.Label(self.root,  text="Page")
        self.label_res_page_1.grid(row=6, column=3, sticky=tk.E)
        
        self.stringVar_res_page = tk.StringVar(self.root)
        self.entry_res_page = tk.Entry(self.root,  width=4,  textvariable=self.stringVar_res_page)
        self.entry_res_page.grid(row=6, column=4)
        self.stringVar_res_page.set("1")
        # ----------the method for the page number string is needed  to be used for all page changes as itll grab the search parameteres each time-----------------------------------------
        # -----------it does not need to return the page number, just the number of pages and results.---------------------------------------------------------------------------------
        
        # -----------------------------still need to add the other manager and if the box is checked------------------
        value_dict = {'from date': self.cbox_date_from.get(),  'until date': self.cbox_date_until.get(), 'next page':(-1),  'other manager': self.cbox_other_managers.get(),  'bool only managers':self.bool_other_manager.get(),  'res per page':50}
        self.label_res_page_2 = tk.Label(self.root,  text=self.handler.getPageNumberString())
        self.label_res_page_2.grid(row=6,  column=5, sticky=tk.W)
        
        # self.root.grab_set()
    
    def nextButtonActions(self):
        pagenum = int(self.stringVar_res_page.get()) + 1
        self.stringVar_res_page.set(str(pagenum))
        self.list_box_results.delete(1, tk.END)
        for result in self.handler.getResults({'page': pagenum}):
            self.list_box_results.insert(tk.END, result)
        return

    def sortButtonActions(self):
        self.handler.sortResults(self.cbox_pcl.get(), self.stringvar_sortby.get(), 'desc' in self.cbox_asc_desc.get(), 50)
        return
    
    def backButtonActions(self):
        pagenum = int(self.stringVar_res_page.get()) - 1
        self.stringVar_res_page.set(str(pagenum))
        self.list_box_results.delete(1, tk.END)
        for result in self.handler.getResults({'page': pagenum}):
            self.list_box_results.insert(tk.END, result)
        return
    
    def otherManagerCheckActions(self):
        i = 0
        i = i + 1
    
    def clearSearchButtonActions(self):
        i = 0
        i = i + 1
    
    def searchButtonActions(self):
        i = 0
        i = i +1
