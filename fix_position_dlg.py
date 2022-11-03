# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 21:35:57 2022

@author: jef
"""

import tkinter as tk
import re
import datetime
import constants
class FixPositionDlg(tk.Toplevel):

    def __init__(self, parent, title, azimut, distance):
        new_position_dt=datetime.datetime.now()
        self.date_var = tk.StringVar()
        self.date_var.set(new_position_dt.strftime(constants.DATE_DISPLAY_FORMATTER).split(" ")[0])
        self.time_var = tk.StringVar()
        self.time_var.set(new_position_dt.strftime(constants.DATE_DISPLAY_FORMATTER).split(" ")[1])
        self.azimut_var = tk.StringVar()
        self.azimut_var.set("{:03.0f}".format(azimut))
        self.distance_var = tk.StringVar()
        self.distance_var.set("{:.1f}".format(distance))
        self.list_of_entry_validation = []

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)
        self.parent = parent
        self.app_logger = self.parent.app_logger
        self.result = None

        dlg_body = tk.Frame(self)
        self.initial_focus = self.create_dlg_body(dlg_body)
        dlg_body.pack(padx=5, pady=5)

        self.add_cancel_ok_buttons()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.initial_focus.focus_set()
        self.wait_window(self)

    #
    # construction hooks
    def create_dlg_body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        next_prop_row=0
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=0)
        master.grid_columnconfigure(2, weight=0)
        grid_dict = {"sticky":"EW", "padx":5, "pady":2}
        grid_unit_dict = {"sticky":"NSW", "padx":2, "pady":2}
        grid_note_dict = {"sticky":"NSW", "padx":5, "pady":2, "columnspan":4}
        entry_dict ={"width":8}
        tk.Label (master, text="from").grid (row=next_prop_row, **grid_dict)
        self.date_wid = tk.Entry(master, textvariable= self.date_var, width=10)
        self.date_wid.grid(row=next_prop_row, column=1, **grid_dict)
        self.time_wid = tk.Entry(master, textvariable= self.time_var, **entry_dict)
        self.time_wid.grid(row=next_prop_row, column=2, **grid_dict)

        next_prop_row+=1
        tk.Label (master, text="Distance\n(DD.d)").grid (row=next_prop_row, **grid_dict)
        self.distance_wid = tk.Entry(master, textvariable= self.distance_var, **entry_dict)
        self.distance_wid.grid(row=next_prop_row, column=1, **grid_dict)
        tk.Label (master, text=" NM").grid (row=next_prop_row, column=2, **grid_unit_dict)

        next_prop_row+=1
        tk.Label (master, text="Azimut\n(CCC)").grid (row=next_prop_row, **grid_dict)
        self.azimut_wid= tk.Entry(master, textvariable= self.azimut_var, **entry_dict)
        self.azimut_wid.grid(row=next_prop_row, column=1, **grid_dict)
        tk.Label (master, text=" °").grid (row=next_prop_row, column=2, **grid_unit_dict)

        next_prop_row+=1
        tk.Label (master, text="""
NOTE : pressing 'OK' will : 
* move the boat to (azimut,distance) and,
* will erase all the sun observations""", justify=tk.LEFT, anchor="w").grid (row=next_prop_row, **grid_note_dict)

        self.list_of_entry_validation.append({"category":"date", "variable":self.date_var, "widget":self.date_wid, "pattern":"^\d{1,2}\/\d{1,2}(\/\d{2,4})?$"})
        self.list_of_entry_validation.append({"category":"time", "variable":self.time_var, "widget":self.time_wid, "pattern":"^\d{1,2}:\d{1,2}:\d{1,2}$"})
        self.list_of_entry_validation.append({"category":"distance", "variable":self.distance_var, "widget":self.distance_wid, "pattern":"^\d{1,3}\.?\d?$"})
        self.list_of_entry_validation.append({"category":"azimut", "variable":self.azimut_var, "widget":self.azimut_wid, "pattern":"^\d{1,3}$", "max":360})
        next_prop_row+=1
        return self.time_wid

    def add_cancel_ok_buttons(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = tk.Frame(self)

        ok_button = tk.Button(box, text="OK", width=10, command=self.on_ok_button, default=tk.ACTIVE)
        ok_button.pack(side=tk.LEFT, padx=5, pady=5)
        cancel_button = tk.Button(box, text="Cancel", width=10, command=self.on_cancel_button)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.on_ok_button)
        self.bind("<Escape>", self.on_cancel_button)

        box.pack()

    #
    # standard button semantics

    def on_ok_button(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()
        self.on_cancel_button()

    def apply(self):
        azimut = float(self.azimut_var.get())
        distance = float(self.distance_var.get())
        new_position_dt = "{} {}".format(self.date_var.get(), self.time_var.get())
        self.result = new_position_dt, azimut, distance

    def on_cancel_button(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):
        all_entry_ok = True
        for entry_validation in self.list_of_entry_validation:
            pattern = entry_validation["pattern"]
            value = entry_validation["variable"].get()
            widget = entry_validation["widget"]
            max_value = entry_validation.get("max")
            if re.fullmatch(pattern, value) is None:
                category = entry_validation["category"]
                self.app_logger.warning('%s is a not correct value for "%s". it should match "%s"', value, pattern, category)
                widget.configure(fg="red")
                all_entry_ok = False
            elif max_value and int(value) >= max_value:
                self.app_logger.warning('%s is too high ( it should be < %d)', value, max_value)
                widget.configure(fg="red")
                all_entry_ok = False
            else:
                widget.configure(fg="black")

        if not all_entry_ok:
            return False

        return True
