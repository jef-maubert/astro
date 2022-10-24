# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 17:34:57 2022

@author: jef
"""
import tkinter as tk
import constants
PADX_STD = 5

class AstroTk(tk.Tk):

    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.last_position = tk.StringVar()
        self.last_position_dt = tk.StringVar()
        self.current_position = tk.StringVar()
        self.current_position_dt = tk.StringVar()
        self.initialize()
        
    def initialize(self):
        self.title("Astro {}".format(constants.VERSION))
        self.grid()
        last_pos_frame = tk.LabelFrame(self, text="Last position", borderwidth=2, relief=tk.GROOVE)
        last_pos_frame.grid(column=0, row=0, sticky='ENWS', padx=PADX_STD, pady=2)
        self.last_pos_text = tk.Text(last_pos_frame, height=1)
        self.last_pos_text ["state"] = 'disabled'
        self.last_pos_text.grid(row=0, column=0, padx=PADX_STD, sticky="EW")

        self.btn_modif_last_pos = tk.Button(last_pos_frame, text="modify", command=self.on_button_modif_last_pos)
        self.btn_modif_last_pos.grid(row=0, column=1, padx=PADX_STD, sticky="EW")
 
        current_pos_frame = tk.LabelFrame(self, text="Current position", borderwidth=2, relief=tk.GROOVE)
        current_pos_frame.grid(column=0, row=1, sticky='ENWS', padx=PADX_STD, pady=2)
        self.btn_modif_current_pos = tk.Button(current_pos_frame, text="modify", command=self.on_button_modif_course_and_speed)
        self.btn_modif_current_pos.grid(row=0, column=1, padx=PADX_STD, sticky="EW")

    def on_button_modif_last_pos(self):
         return

    def on_button_modif_course_and_speed(self):
         return

def main () :
    my_app = AstroTk(None)
    my_app.mainloop()

if __name__ == "__main__":
    main()
