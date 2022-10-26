# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 21:35:57 2022

@author: jef
"""

import tkinter as tk
import re
from waypoint import format_angle, INPUT_TYPE_LATITUDE, INPUT_TYPE_LONGITUDE
import constants

class InitPosDlg(tk.Toplevel):

    def __init__(self, parent, title, last_modif_dt, waypoint):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)
        self.parent = parent
        self.app_logger = self.parent.app_logger
        self.result = None


        self.date_var = tk.StringVar()
        self.date_var.set(last_modif_dt.strftime(constants.DATE_DISPLAY_FORMATTER).split(" ")[0])
        self.time_var = tk.StringVar()
        self.time_var.set(last_modif_dt.strftime(constants.DATE_DISPLAY_FORMATTER).split(" ")[1])

        latitude_str = format_angle (waypoint.latitude,INPUT_TYPE_LATITUDE) 
        longitude_str = format_angle (waypoint.longitude,INPUT_TYPE_LONGITUDE) 
        self.app_logger.info('Input - lattitude : "%s", lattitude : "%s"', latitude_str, longitude_str)
        
        self.lat_deg_var = tk.StringVar()
        self.lat_deg_var.set(latitude_str.split("°")[0])
        self.lat_min_var = tk.StringVar()
        self.lat_min_var.set(latitude_str.split("°")[1].split("'")[0])
        self.lat_sign_var = tk.StringVar()
        if waypoint.latitude > 0 :
            self.lat_sign_var.set ("N")
        else:
            self.lat_sign_var.set ("S")

        self.long_deg_var = tk.StringVar()
        self.long_deg_var.set(longitude_str.split("°")[0])
        self.long_min_var = tk.StringVar()
        self.long_min_var.set(longitude_str.split("°")[1].split("'")[0])
        self.long_sign_var = tk.StringVar()
        if waypoint.longitude > 0 :
            self.long_sign_var.set ("E")
        else:
            self.long_sign_var.set ("W")

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
        self.date_wid.grid(row=next_prop_row, column=0, columnspan=3, **grid_dict)
        self.time_wid = tk.Entry(master, textvariable= self.time_var, width=TIME_WIDTH)
        self.time_wid.grid(row=next_prop_row, column=3, columnspan=3, **grid_dict)

        next_prop_row+=1
        tk.Label (master, text="Lat").grid (row=next_prop_row, column=0, rowspan=2, **grid_dict)
        self.lat_deg_wid = tk.Entry(master, textvariable= self.lat_deg_var, width=DEG_WIDTH)
        self.lat_deg_wid.grid(row=next_prop_row, column=1, rowspan=2, **grid_dict)
        tk.Label (master, text="°").grid (row=next_prop_row, column=2, rowspan=2, **grid_unit_dict)
        self.lat_min_wid = tk.Entry(master, textvariable= self.lat_min_var, width=MIN_WIDTH)
        self.lat_min_wid.grid(row=next_prop_row, column=3, rowspan=2, **grid_dict)
        tk.Label (master, text="'").grid (row=next_prop_row, column=4, rowspan=2, **grid_unit_dict)
        self.lat_sign_wid = tk.Radiobutton(master, text="N", variable = self.lat_sign_var, value = "N").grid (row=next_prop_row, column=5, **grid_unit_dict)
        next_prop_row+=1
        self.lat_sign_wid = tk.Radiobutton(master, text="S", variable = self.lat_sign_var, value = "S").grid (row=next_prop_row, column=5, **grid_unit_dict)
        next_prop_row+=1

        tk.Label (master, text="Long").grid (row=next_prop_row, column=0, rowspan=2, **grid_dict)
        self.long_deg_wid = tk.Entry(master, textvariable= self.long_deg_var, width=DEG_WIDTH)
        self.long_deg_wid.grid(row=next_prop_row, column=1, rowspan=2, **grid_dict)
        tk.Label (master, text="°").grid (row=next_prop_row, column=2, rowspan=2, **grid_unit_dict)
        self.long_min_wid = tk.Entry(master, textvariable= self.long_min_var, width=MIN_WIDTH)
        self.long_min_wid.grid(row=next_prop_row, column=3, rowspan=2, **grid_dict)
        tk.Label (master, text="'").grid (row=next_prop_row, column=4, rowspan=2, **grid_unit_dict)
        self.long_sign_wid = tk.Radiobutton(master, text="W", variable = self.long_sign_var, value = "W").grid (row=next_prop_row, column=5, **grid_unit_dict)
        next_prop_row+=1
        self.long_sign_wid = tk.Radiobutton(master, text="E", variable = self.long_sign_var, value = "E").grid (row=next_prop_row, column=5, **grid_unit_dict)
        next_prop_row+=1

        self.list_of_entry_validation.append({"category":"date", "variable":self.date_var, "widget":self.date_wid, "pattern":"^\d{1,2}\/\d{1,2}(\/\d{2,4})?$"})
        self.list_of_entry_validation.append({"category":"time", "variable":self.time_var, "widget":self.time_wid, "pattern":"^\d{1,2}:\d{1,2}:\d{1,2}$"})
        self.list_of_entry_validation.append({"category":"degre", "variable":self.lat_deg_var, "widget":self.lat_deg_wid, "pattern":"^\d{1,2}$", "max":90})
        self.list_of_entry_validation.append({"category":"minute", "variable":self.lat_min_var, "widget":self.lat_min_wid, "pattern":"^\d{1,2}\.?\d?$", "max":60})
        self.list_of_entry_validation.append({"category":"degre", "variable":self.long_deg_var, "widget":self.long_deg_wid, "pattern":"^\d{1,3}$", "max":180})
        self.list_of_entry_validation.append({"category":"minute", "variable":self.long_min_var, "widget":self.long_min_wid, "pattern":"^\d{1,2}\.?\d?$", "max":60})
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
        last_modif_dt = "{} {}".format(self.date_var.get(), self.time_var.get())
        latitude_str = "{:02d}°{:04.1f}'{}".format(int(self.lat_deg_var.get()), float(self.lat_min_var.get()), self.lat_sign_var.get())
        longitude_str = "{:03d}°{:04.1f}'{}".format(int(self.long_deg_var.get()), float(self.long_min_var.get()), self.long_sign_var.get())
        self.app_logger.info('Output - lattitude : "%s", lattitude : "%s"', latitude_str, longitude_str)
        self.result = last_modif_dt, latitude_str, longitude_str

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
