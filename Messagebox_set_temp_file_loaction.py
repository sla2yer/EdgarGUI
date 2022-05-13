import tkinter as tk
from functools import partial
from tkinter import filedialog
from Edgar_database import EdgarDatabase
from File_manager import FileManager

class Messagebox_setTempFileLocaiton:
    def __init__(self, root):
        self.db = EdgarDatabase(False)
        self.db.manualConnect()
        current_res = self.db.getTempFileLocation()
        current_string = 'current: '
        if len(current_res) == 0:
            current_string = current_string + 'None!'
        else:
            current_string = current_string + current_res[0]


        toplevel = tk.Toplevel(root)

        self.stringVar_label_current = tk.StringVar(value=current_string)
        self.label_current = tk.Label(toplevel, textvariable=self.stringVar_label_current)
        self.label_current.grid(row=0,column=1)
        partical_button_pick = partial(self.pickButtonCommand, toplevel)
        self.button_pick = tk.Button(toplevel, text='pick folder', command=partical_button_pick)
        self.button_pick.grid(row=1, column=1)
        partical_button_save = partial(self.saveButtonCommand, toplevel)
        self.button_save = tk.Button(toplevel, text='save', command=partical_button_save)
        self.button_save.grid(row=2, column=0)

        self.button_close = tk.Button(toplevel, text='cancel', command=toplevel.destroy)
        self.button_close.grid(row=2, column=2)



    def pickButtonCommand(self, toplevel):
        dirname =tk.filedialog.askdirectory(parent=toplevel, initialdir="/", title='Please select a directory')
        self.stringVar_label_current.set('current: ' + dirname)


    def saveButtonCommand(self, toplevel):
        print('save command')
        self.db.manualConnect()
        temp = self.stringVar_label_current.get()
        print(f'got from stringVar: {temp} ')
        with FileManager() as fm:
            temp = fm.cleanFiletypeString(temp)

        res = self.db.getTempFileLocation()
        if len(res) > 0:
            self.db.updateTempFileLocation(temp[9:len(temp)-1])
        else:
            self.db.insertTempFileLocation(temp[9:len(temp)-1])
        self.db.commit()
        print('inserted')
        self.db.close()
        toplevel.destroy()
