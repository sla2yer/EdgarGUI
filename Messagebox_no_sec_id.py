import tkinter as tk


class Messagebox_noSecId:
    def __init__(self, root):
        self.toplevel = tk.Toplevel(root)
        self.stringVar_label_message = tk.StringVar(value=
                                                    "No SEC ID set!\n"
                                                    "Please set the SEC ID through the file menu before searching")
        self.label_message = tk.Label(self.toplevel, textvariable=self.stringVar_label_message)
        self.label_message.grid(row=0, column=0)

        self.button_ok = tk.Button(self.toplevel, text="ok", command=self.toplevel.destroy)
        self.button_ok.grid(row=1, column=0)

