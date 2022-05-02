import tkinter as tk
import tkcalendar
import warnings
from secedgar.filings import FilingType
from tqdm import asyncio
import asyncio
from GUI_handler import GUI_handler
from functools import partial
import threading

# BNP Paribas Asset Management Holding
# susquehanna international group, LLP
# Citadel Investment Advisory, Inc.
# Melvin Capital Management LP
class SecGUI:
    def __init__(self, root):
        self.windowThreads = []
        self.handler = GUI_handler()
        tk.Grid.columnconfigure(root, 0, weight=1)
        tk.Grid.rowconfigure(root, 5, weight=1)
        tk.Grid.rowconfigure(root, 2, weight=1)
        warnings.filterwarnings("error")
        filings = self.getFilings()
        self.filling_dict = self.makeFilingDictionary()

        self.clicked = tk.StringVar(root)
        self.clicked.set(filings[5])

        # ------------MENU BAR---------------------------------
        self.menu_bar = tk.Menu(root, background='grey', foreground='black')

        self.menu_file = tk.Menu(self.menu_bar,background='white', foreground='black', tearoff=1 )
        self.menu_file.add_command(label='Set SEC ID')
        self.menu_file.add_command(label='clear database')
        self.menu_file.add_command(label='set temp file location')
        self.menu_file.add_command(label="Exit")
        self.menu_bar.add_cascade(label="File", menu=self.menu_file)
        root.config(menu=self.menu_bar)
        # ----------FILING TYPE COMBO BOX------------------------------------
        self.combo_box = tk.ttk.Combobox(root, textvariable=self.clicked)
        self.combo_box['values'] = filings
        self.combo_box['state'] = 'readonly'
        self.combo_box.grid(row=3, column=1, sticky=tk.S)

        # -------LABELS FOR FILING TYPE, START DATE, END DATE--------------------------------
        self.label_filingType = tk.Label(root, text="Filing type to search for")
        self.label_filingType.grid(row=3, column=1, sticky=tk.N)
        self.label_date_start = tk.Label(root, text="search from")
        self.label_date_start.grid(row=3, column=2, sticky=tk.N)
        self.label_date_end = tk.Label(root, text="Search until")
        self.label_date_end.grid(row=3, column=3, sticky=tk.N)

        # ------------------------CALENDERS------------------------------------------
        self.calander_start = tkcalendar.DateEntry(root, width=16, background="magenta3", foreground="white",
                                                   state=tk.DISABLED)
        self.calander_start.grid(row=3, column=2, sticky=tk.S)
        self.calander_end = tkcalendar.DateEntry(root, width=16, background="magenta3", foreground="white",
                                                 state=tk.DISABLED)
        self.calander_end.grid(row=3, column=3, sticky=tk.S)

        self.button_temp = tk.Button(root, text="temp", padx=10, pady=10, command=self.tempAction)
        self.button_temp.grid(row=3, column=4, sticky=tk.S)

        # ----------------CALANDER USAGE CHECK BOXES---------------------
        self.checkbox_start_variable = tk.BooleanVar()
        self.checkbox_end_variable = tk.BooleanVar()
        self.checkbox_start = tk.ttk.Checkbutton(root, text="use start date", command=self.checkButtonCommands,
                                                 variable=self.checkbox_start_variable, onvalue=True, offvalue=False)
        self.checkbox_end = tk.ttk.Checkbutton(root, text="use end date", command=self.checkButtonCommands,
                                               variable=self.checkbox_end_variable, onvalue=True, offvalue=False)
        self.checkbox_start.grid(row=4, column=2, sticky=tk.N)
        self.checkbox_end.grid(row=4, column=3, sticky=tk.N)

        self.label_last_checked = tk.Label(root, text="last checked: ")
        self.label_last_checked.grid(row=0, column=0)

        # -------------TRACKING LABELS, LIST, AND GRID PLACEMENT----------------------------------
        self.label_track_list_title = tk.Label(root, text="Institutions being tracked:")

        self.list_to_track = []

        self.list_box_track = tk.Listbox(root, width=35, exportselection=False, selectmode=tk.MULTIPLE)
        self.list_box_track.grid(row=2, column=0, rowspan=3, sticky="nsew")
        self.list_box_track.insert(1, "None")
        self.label_track_list_title.grid(row=1, column=0)

        self.list_box_results = tk.Listbox(root, width=35, exportselection=False, selectmode=tk.MULTIPLE)
        self.list_box_results.grid(row=5, column=0, sticky="nsew")
        self.list_box_results.insert(1, "search results will appear here")
        # --------------------------------------------------------------------------------------

        # ------------------SEARCH LABELS, INPUT, AND BUTTON----------------------------
        self.entry_institute_name = tk.Entry(root, width=50)
        self.entry_institute_name.grid(row=2, column=1, columnspan=3, sticky=tk.W + tk.E + tk.N)

        self.label_entry = tk.Label(root, text="please enter an institution")
        self.label_entry.grid(row=1, column=1, columnspan=3, sticky=tk.W + tk.E + tk.S)

        self.button_track = tk.Button(root, text="track this inst.", padx=10, pady=10, command=self.trackButtonActions)
        self.button_track.grid(row=5, column=3)

        action_with_arg = partial(self.openFilingsButtonActions, root)
        self.button_open_seperatly_search_selected = tk.Button(root, text="Open Filings", padx=10, pady=10,
                                                               command=action_with_arg)

        self.button_compare = tk.Button(root, text="Compare", padx=10, pady=10, command=self.compareButtonActions)
        self.button_compare.grid(row=5, column=1)
        self.button_track['state'] = tk.DISABLED

        self.button_open_seperatly_search_selected.grid(row=5, column=2)

        self.button_search = tk.Button(root, text="search", padx=10, pady=10, command=self.searchButtonAction)
        self.button_search.grid(row=2, column=4, stick=tk.N)

        self.button_manual_check = tk.Button(root, text="check for new filings", padx=10, pady=10,
                                             command=self.checkButtonActions)
        self.button_manual_check.grid(row=0, column=4)

    def compareButtonActions(self):
        self.handler.compareButtonActions()

    def openFilingsButtonActions(self, root):
        # Grab the items from the results list box and pass them into the handler
        first_res = self.list_box_results.get(0, 0)
        if "acc" in first_res[0]:
            # self.handler.openFilings(self.list_box_results.get(1,  tk.END), tk.Toplevel())
            self.windowThreads.append(threading.Thread(target=self.handler.openFilings,
                                                       args=(self.list_box_results.get(1, tk.END), tk.Toplevel())))
            self.windowThreads[len(self.windowThreads) - 1].start()
        else:
            # --------------CREATE A POP UP TO INDICATE THE ERROR----------
            # Filings must be found in order to open them
            i = 0
            i = i + 1

    def updateTrackList(self):
        self.list_box_track.delete(0, tk.END)
        count = 0
        self.list_box_track.insert(0, self.handler.getTrackedEntities())

    def trackButtonActions(self):
        if self.handler.foundEntity():
            # what this needs to do is get the name from the entry box (as an institute was found from the contents)
            # pass the name to the handler that will add it to the database and then simply reupdate the list
            # Pass the name as a list as multiple names can be selected as well
            self.handler.trackButtonActions([self.entry_institute_name.get()])

        else:
            selection = self.list_box_results.curselection()
            entities_to_track = []
            if 0 in selection:
                selection.remove(0)
            for index in selection:
                entities_to_track.append(self.list_box_results.get(index))
            # ------------------------------------------still gotta fix this method in the handler--------------------------------------------
            self.handler.trackButtonActions(entities_to_track)

            for x in range(len(entities_to_track)):
                self.list_box_track.insert(x, entities_to_track[x])

        # --------------from here call a method from the handler that generates the track list from the db---------------
        # ------------------------then clear and append the track box--------------------------------------

    def tempAction(self):
        # fv = FilingViewer()
        temp = tk.Toplevel()
        tl = tk.Label(temp, text="hello there")
        tl.pack()
        i = 0
        i = i + 1

    def checkButtonCommands(self):
        print(self.checkbox_end_variable)
        # if true then enable the date box
        if self.checkbox_end_variable.get():
            self.calander_end.config(state=tk.NORMAL)
        else:
            self.calander_end.config(state=tk.DISABLED)

        if self.checkbox_start_variable.get():
            self.calander_start.config(state=tk.NORMAL)
        else:
            self.calander_start.config(state=tk.DISABLED)
        return

    def getFilings(self):
        flist = ['FILING_10Q', 'FILING_10D', 'FILING_10K', 'FILING_11K',
                 'FILING_13H', 'FILING_13F', 'FILING_S11', 'FILING_144', 'FILING_18K',
                 'FILING_1A', 'FILING_1E', 'FILING_1K', 'FILING_1SA',
                 'FILING_1U', 'FILING_1Z', 'FILING_20F', 'FILING_25',
                 'FILING_2E', 'FILING_3', 'FILING_4', 'FILING_40F',
                 'FILING_8K', 'FILING_ABSEE', 'FILING_C', 'FILING_D',
                 'FILING_F1', 'FILING_F3', 'FILING_F4', 'FILING_F6',
                 'FILING_F7', 'FILING_F8', 'FILING_FX', 'FILING_MA',
                 'FILING_N14', 'FILING_N18F1', 'FILING_N1A', 'FILING_N2',
                 'FILING_N27D1', 'FILING_N3', 'FILING_N4', 'FILING_N5',
                 'FILING_N54A', 'FILING_N54C', 'FILING_N6', 'FILING_N6F',
                 'FILING_N8A', 'FILING_N8B2', 'FILING_N8B4', 'FILING_N8F',
                 'FILING_NCEN', 'FILING_NCR', 'FILING_NCSR', 'FILING_NCSRS',
                 'FILING_NLIQUID', 'FILING_NPORTEX', 'FILING_NPORTP', 'FILING_NPX',
                 'FILING_NQ', 'FILING_S1', 'FILING_S20', 'FILING_S3',
                 'FILING_S4', 'FILING_S6', 'FILING_S8', 'FILING_SC13D',
                 'FILING_SC13G', 'FILING_SD', 'FILING_SF1', 'FILING_SF3',
                 'FILING_T1', 'FILING_T2', 'FILING_T3', 'FILING_T6',
                 'FILING_TA1', 'FILING_TA2', 'FILING_TAW']
        return flist

    def searchButtonAction(self):

        t = threading.Thread(target=self.threadSearchButtonAction)
        t.start()
        # t.join()



        return

    def threadSearchButtonAction(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        # dates are passed to the handler as datetime objects, the heandler then converts them to integers for the edgar search
        if self.checkbox_start_variable.get():
            start_date = str(self.calander_start.get_date())
        else:
            start_date = ""
        if self.checkbox_end_variable.get():
            end_date = str(self.calander_end.get_date())
        else:
            end_date = ""

        # MAkE IT SO THIS RETURNS FALSE IF NO RESULTS ARE FOUND. 0 results because of diff file type gives a true result
        # After the call a function from getReults if True is returned
        print(self.filling_dict[self.combo_box.get()])
        self.list_box_results.delete(0, tk.END)
        box_index = 0
        if self.handler.searchForFiling(self.entry_institute_name.get(), self.filling_dict[self.combo_box.get()], start_date, end_date):

            for result in self.handler.getResultMessage():
                self.list_box_results.insert(box_index, result)
                box_index = box_index + 1

            self.button_track['state'] = tk.NORMAL
            if self.handler.foundEntity():
                self.button_open_seperatly_search_selected['state'] = tk.NORMAL
            else:
                self.button_open_seperatly_search_selected['state'] = tk.DISABLED

        else:

            for result in self.handler.getResultMessage():
                self.list_box_results.insert(box_index, result)
                box_index = box_index + 1

            if 'Please select one of' in self.list_box_results.get(0):
                self.button_track['state'] = tk.NORMAL
            else:
                self.button_track['state'] = tk.DISABLED
        self.handler.clearResultMessage()

    def checkButtonActions(self):
        temps = "hello"
        temps

    def makeFilingDictionary(self):
        filingType_dictionary = {
            'FILING_10Q': FilingType.FILING_10Q,
            'FILING_10D': FilingType.FILING_10D,
            'FILING_10K': FilingType.FILING_10K,
            'FILING_11K': FilingType.FILING_11K,
            'FILING_13F': FilingType.FILING_13F,
            'FILING_13H': FilingType.FILING_13H,
            'FILING_S11': FilingType.FILING_S11,
            'FILING_144': FilingType.FILING_144,
            'FILING_18K': FilingType.FILING_18K,
            'FILING_1A': FilingType.FILING_1A,
            'FILING_1E': FilingType.FILING_1E,
            'FILING_1K': FilingType.FILING_1K,
            'FILING_1SA': FilingType.FILING_1SA,
            'FILING_1U': FilingType.FILING_1U,
            'FILING_1Z': FilingType.FILING_1Z,
            'FILING_20F': FilingType.FILING_20F,
            'FILING_25': FilingType.FILING_25,
            'FILING_2E': FilingType.FILING_2E,
            'FILING_3': FilingType.FILING_3,
            'FILING_4': FilingType.FILING_4,
            'FILING_40F': FilingType.FILING_40F,
            'FILING_8K': FilingType.FILING_8K,
            'FILING_ABSEE': FilingType.FILING_ABSEE,
            'FILING_C': FilingType.FILING_C,
            'FILING_D': FilingType.FILING_D,
            'FILING_F1': FilingType.FILING_F1,
            'FILING_F3': FilingType.FILING_F3,
            'FILING_F4': FilingType.FILING_F4,
            'FILING_F6': FilingType.FILING_F6,
            'FILING_F7': FilingType.FILING_F7,
            'FILING_F8': FilingType.FILING_F8,
            'FILING_FX': FilingType.FILING_FX,
            'FILING_MA': FilingType.FILING_MA,
            'FILING_N14': FilingType.FILING_N14,
            'FILING_N18F1': FilingType.FILING_N18F1,
            'FILING_N1A': FilingType.FILING_N1A,
            'FILING_N2': FilingType.FILING_N2,
            'FILING_N27D1': FilingType.FILING_N27D1,
            'FILING_N3': FilingType.FILING_N3,
            'FILING_N4': FilingType.FILING_N4,
            'FILING_N5': FilingType.FILING_N5,
            'FILING_N54A': FilingType.FILING_N54A,
            'FILING_N54C': FilingType.FILING_N54C,
            'FILING_N6': FilingType.FILING_N6,
            'FILING_N6F': FilingType.FILING_N6F,
            'FILING_N8A': FilingType.FILING_N8A,
            'FILING_N8B2': FilingType.FILING_N8B2,
            'FILING_N8B4': FilingType.FILING_N8B4,
            'FILING_N8F': FilingType.FILING_N8F,
            'FILING_NCEN': FilingType.FILING_NCEN,
            'FILING_NCR': FilingType.FILING_NCR,
            'FILING_NCSR': FilingType.FILING_NCSR,
            'FILING_NCSRS': FilingType.FILING_NCSRS,
            'FILING_NLIQUID': FilingType.FILING_NLIQUID,
            'FILING_NPORTEX': FilingType.FILING_NPORTEX,
            'FILING_NPORTP': FilingType.FILING_NPORTP,
            'FILING_NPX': FilingType.FILING_NPX,
            'FILING_NQ': FilingType.FILING_NQ,
            'FILING_S1': FilingType.FILING_S1,
            'FILING_S20': FilingType.FILING_S20,
            'FILING_S3': FilingType.FILING_S3,
            'FILING_S4': FilingType.FILING_S4,
            'FILING_S6': FilingType.FILING_S6,
            'FILING_S8': FilingType.FILING_S8,
            'FILING_SC13D': FilingType.FILING_SC13D,
            'FILING_SC13G': FilingType.FILING_SC13G,
            'FILING_SD': FilingType.FILING_SD,
            'FILING_SF1': FilingType.FILING_SF1,
            'FILING_SF3': FilingType.FILING_SF3,
            'FILING_T1': FilingType.FILING_T1,
            'FILING_T2': FilingType.FILING_T2,
            'FILING_T3': FilingType.FILING_T3,
            'FILING_T6': FilingType.FILING_T6,
            'FILING_TA1': FilingType.FILING_TA1,
            'FILING_TA2': FilingType.FILING_TA2,
            'FILING_TAW': FilingType.FILING_TAW,
        }
        return filingType_dictionary


root = tk.Tk()
gui = SecGUI(root)

root.mainloop()
