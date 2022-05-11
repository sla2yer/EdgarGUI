import tkinter as tk
from Edgar_database import EdgarDatabase


class Messagebox_setSecId:
    def __init__(self, root):
        self.toplevel = tk.Toplevel(root)
        self.toplevel.title("Set SEC Search ID")
        self.toplevel.geometry("230x100")
        self.db = EdgarDatabase(False)
        self.db.manualConnect()
        current_sec_id = self.db.getSecID()
        self.db.close()
        if len(current_sec_id) > 1:
            temp_string = f'The ID is currently set with the following\n' \
                          f'Name:{current_sec_id[0]}\n' \
                          f'Email:{current_sec_id[1]}\n' \
                          f'Please insert any changes and press ok to submit, or cancel or close the window'
        else:
            temp_string = 'There is no user_agent ID set\n' \
                          'This information is placed as part of the HTTP header in the search requests\n' \
                          'The inforation is part of header in the format of "name (email)"\n' \
                          'This must be given as per the SEC fair access'
        label_current = tk.Label(self.toplevel, text=temp_string)
        label_current.grid(column=0, row=0, columnspan=2, sticky=tk.E)
        label_name = tk.Label(self.toplevel, text="Name:")
        label_name.grid(column=0, row=1)

        label_email = tk.Label(self.toplevel, text='Email:')
        label_email.grid(column=0, row=2)

        self.entry_name = tk.Entry(self.toplevel, width=30)
        self.entry_name.grid(column=1, row=1, columnspan=3)

        self.entry_email = tk.Entry(self.toplevel, width=30)
        self.entry_email.grid(column=1, row=2, columnspan=3)

        self.button_submit = tk.Button(self.toplevel, text='submit', command=self.insertSecId)
        self.button_submit.grid(column=0, row=3)

        self.button_cancel = tk.Button(self.toplevel, text='Cancel', command=self.toplevel.destroy)
        self.button_cancel.grid(column=1, row=3)

    def insertSecId(self):
        self.db.manualConnect()
        name = self.entry_name.get()
        email = self.entry_email.get()
        self.db.insertSecId(name, email)
        self.db.commit()
        self.db.close()
        self.toplevel.destroy()
