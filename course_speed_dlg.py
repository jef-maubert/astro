# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 21:35:57 2022

@author: jef
"""

import tkinter as tk
class CourseSpeedDlg(tk.Toplevel):

    def __init__(self, parent, title, last_modif_dt, course, speed):
        self.last_modif_dt_var = tk.StringVar()
        self.last_modif_dt_var.set(last_modif_dt)
        self.course_var = tk.IntVar() 
        self.course_var.set(course)
        self.speed_var = tk.DoubleVar()
        self.speed_var.set(speed)

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)
        self.parent = parent
        self.result = None

        widBody = tk.Frame(self)
        self.initial_focus = self.CreateDlgBody(widBody)
        widBody.pack(padx=5, pady=5)

        self.buttonbox()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        self.initial_focus.focus_set()
        self.wait_window(self)

    #
    # construction hooks
    def CreateDlgBody(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden
        nextPropRow=0
        tk.Label (master, text="speed").grid (row=nextPropRow, sticky= "EW", padx=5, pady=5);
        self.wid_speeed = tk.Entry(master, textvariable= self.speed_var)
        self.wid_speeed.grid(row=nextPropRow, column=1, sticky= "W")
        nextPropRow+=1

        tk.Label (master, text="Course ").grid (row=nextPropRow, sticky= "EW", padx=5, pady=5);
        self.wid_course= tk.Entry(master, textvariable= self.course_var)
        self.wid_course.grid(row=nextPropRow, column=1, sticky= "W")
        nextPropRow+=1

        return self.wid_course
        
    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()
        self.cancel()

    def apply(self):
        course = self.course_var.get()
        speed = self.speed_var.get()
        last_modif_dt = self.last_modif_dt_var.get()
        self.result = last_modif_dt, course, speed

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):
        return 1 # override
