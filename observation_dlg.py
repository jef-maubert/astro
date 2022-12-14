# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 21:35:57 2022

@author: jef
"""

import tkinter as tk
import re
import datetime
import constants
class ObservationdDlg(tk.Toplevel):

    def __init__(self, parent, title):
        DEFAULT_ANGLE = "45°30"
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)
        self.parent = parent
        self.my_boat = self.parent.data.my_boat
        self.app_logger = self.parent.app_logger
        self.result = None

        now = datetime.datetime.now()
        self.date_var = tk.StringVar()
        self.date_var.set(now.strftime(constants.DATE_DISPLAY_FORMATTER).split(" ")[0])
        self.time_var = tk.StringVar()
        self.time_var.set(now.strftime(constants.DATE_DISPLAY_FORMATTER).split(" ")[1])

        self.eye_height_var = tk.StringVar()
        self.eye_height_var.set("{:.0f}".format(self.my_boat.eye_height))

        self.obs_height_deg_var = tk.StringVar()
        self.obs_height_deg_var.set(DEFAULT_ANGLE)
        self.obs_height_deg_var = tk.StringVar()
        self.obs_height_deg_var.set(DEFAULT_ANGLE.split("°")[0])
        self.obs_height_min_var = tk.StringVar()
        self.obs_height_min_var.set(DEFAULT_ANGLE.split("°")[1])

        self.list_of_entry_validation = []


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
        DATE_WIDTH = 10
        TIME_WIDTH = 8
        DEG_WIDTH = 4
        MIN_WIDTH = 5

        next_prop_row=0
        master.grid_columnconfigure(0, weight=1)
        for column_index in range (1,6) :
            master.grid_columnconfigure(column_index, weight=0)
        grid_dict = {"sticky":"EW", "padx":5, "pady":2}
        grid_unit_dict = {"sticky":"NSW", "padx":2, "pady":2}
        self.date_wid = tk.Entry(master, textvariable= self.date_var, width=DATE_WIDTH)
        self.date_wid.grid(row=next_prop_row, column=0, columnspan=2, **grid_dict)
        self.time_wid = tk.Entry(master, textvariable= self.time_var, width=TIME_WIDTH)
        self.time_wid.grid(row=next_prop_row, column=2, columnspan=2, **grid_dict)

        next_prop_row+=1
        tk.Label (master, text="Eye height\n(HH)").grid (row=next_prop_row, **grid_dict)
        self.eye_height_wid= tk.Entry(master, textvariable= self.eye_height_var, width=DEG_WIDTH)
        self.eye_height_wid.grid(row=next_prop_row, column=1, **grid_dict)
        tk.Label (master, text=" m").grid (row=next_prop_row, column=2, **grid_unit_dict)

        next_prop_row+=1
        tk.Label (master, text="Obs angle\n(DD.mm)").grid (row=next_prop_row, **grid_dict)

        self.obs_height_deg_wid = tk.Entry(master, textvariable= self.obs_height_deg_var, width=DEG_WIDTH)
        self.obs_height_deg_wid.grid(row=next_prop_row, column=1, **grid_dict)

        tk.Label (master, text=" °").grid (row=next_prop_row, column=2, **grid_unit_dict)

        self.obs_height_min_wid = tk.Entry(master, textvariable= self.obs_height_min_var, width=MIN_WIDTH)
        self.obs_height_min_wid.grid(row=next_prop_row, column=3, **grid_dict)

        tk.Label (master, text=" '").grid (row=next_prop_row, column=4, **grid_unit_dict)

        self.list_of_entry_validation.append({"category":"date", "variable":self.date_var, "widget":self.date_wid, "pattern":"^\d{1,2}\/\d{1,2}(\/\d{2,4})?$"})
        self.list_of_entry_validation.append({"category":"time", "variable":self.time_var, "widget":self.time_wid, "pattern":"^\d{1,2}:\d{1,2}:\d{1,2}$"})
        self.list_of_entry_validation.append({"category":"degre", "variable":self.obs_height_deg_var, "widget":self.obs_height_deg_wid, "pattern":"^\d{1,2}$", "max":90})
        self.list_of_entry_validation.append({"category":"minute", "variable":self.obs_height_min_var, "widget":self.obs_height_min_wid, "pattern":"^\d{1,2}$", "max":60})
        self.list_of_entry_validation.append({"category":"height", "variable":self.eye_height_var, "widget":self.eye_height_wid, "pattern":"^\d{1,2}$"})
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
        last_modif_dt = "{} {}".format(self.date_var.get(), self.time_var.get())
        eye_height = float(self.eye_height_var.get())
        obs_height = float(self.obs_height_deg_var.get())+float(self.obs_height_min_var.get())/60.0
        self.result = last_modif_dt, eye_height, obs_height

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
            elif max_value and float(value) >= max_value:
                self.app_logger.warning('%s is too high ( it should be < %d)', value, max_value)
                widget.configure(fg="red")
                all_entry_ok = False
            else:
                widget.configure(fg="black")

        if not all_entry_ok:
            return False

        return True
