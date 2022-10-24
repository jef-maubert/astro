# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 17:34:57 2022

@author: jef
"""
import os
import sys
import re
import logging
import logging.handlers
import configparser
from configparser import NoSectionError, DuplicateSectionError
import tkinter as tk
import datetime
import datetime
import platform

import constants
from waypoint import Waypoint, format_angle
from waypoint import INPUT_TYPE_LATITUDE, INPUT_TYPE_LONGITUDE, INPUT_TYPE_AZIMUT
from boat import Boat
from observation import Observation
from display_hat import DisplayHat
from course_speed_dlg import CourseSpeedDlg

PADX_STD = 2
PADY_STD = 4

class AstroTk(tk.Tk):

    def __init__(self, parent, data, app_logger):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.data = data
        self.app_logger = app_logger
        self.initialize()
        
    def initialize(self):
        self.title("Astro {}".format(constants.VERSION))
        self.grid()
        
        last_pos_frame = tk.LabelFrame(self, text="Last position", borderwidth=2, relief=tk.GROOVE)
        last_pos_frame.grid(column=0, row=0, sticky='ENWS', padx=PADX_STD, pady=PADY_STD)
        self.last_pos_dt = tk.Label(last_pos_frame)
        self.last_pos_dt.grid(row=0, column=0, padx=PADX_STD, sticky="W")
        self.last_pos = tk.Label(last_pos_frame)
        self.last_pos.grid(row=1, column=0, padx=PADX_STD, sticky="W")
        self.btn_modif_last_pos = tk.Button(last_pos_frame, text="Modify", command=self.on_button_modif_last_pos)
        self.btn_modif_last_pos.grid(row=0, column=1, padx=PADX_STD, sticky="NS")
 
        course_and_speed_frame = tk.LabelFrame(self, text="Course and speed", borderwidth=2, relief=tk.GROOVE)
        course_and_speed_frame.grid(column=0, row=1, sticky='ENWS', padx=PADX_STD, pady=PADY_STD)
        self.course = tk.Label(course_and_speed_frame)
        self.course.grid(row=0, column=0, padx=PADX_STD, sticky="W")
        self.speed= tk.Label(course_and_speed_frame)
        self.speed.grid(row=1, column=0, padx=PADX_STD, sticky="W")
        self.btn_modif_course_and_speed = tk.Button(course_and_speed_frame, text="Modify", command=self.on_button_modif_course_and_speed)
        self.btn_modif_course_and_speed.grid(row=0, column=1, padx=PADX_STD, sticky="NS")

        current_pos_frame = tk.LabelFrame(self, text="Current position", borderwidth=2, relief=tk.GROOVE)
        current_pos_frame.grid(column=0, row=2, sticky='ENWS', padx=PADX_STD, pady=PADY_STD)
        self.current_pos_dt = tk.Label(current_pos_frame)
        self.current_pos_dt.grid(row=0, column=0, padx=PADX_STD, sticky="W")
        self.current_pos = tk.Label(current_pos_frame)
        self.current_pos.grid(row=1, column=0, padx=PADX_STD, sticky="W")
        self.btn_modif_current_pos = tk.Button(current_pos_frame, text="Observation", command=self.on_button_new_obs)
        self.btn_modif_current_pos.grid(row=0, column=1, padx=PADX_STD, sticky="NS")

    def on_button_modif_last_pos(self):
        now = datetime.datetime.now().strftime(constants.DATE_FORMATTER)
        self.current_pos.configure(text=now)

    def on_button_modif_course_and_speed(self):
        self.app_logger.info('Click on button "Modif course and speed"')
        my_course_and_speed_dlg = CourseSpeedDlg(self, "Course and speed", 
                                                     self.data.my_boat.last_waypoint_datetime, 
                                                     self.data.my_boat.course, self.data.my_boat.speed)
        if my_course_and_speed_dlg.result:
            self.nMaxLogLines = my_course_and_speed_dlg.result[0]
            self.data.my_boat.course= my_course_and_speed_dlg.result[1]
            self.data.my_boat.speed = my_course_and_speed_dlg.result[2]
            self.update_display()

    def on_button_new_obs(self):
        self.app_logger.info('Click on button "New obs"')
     
    def update_display(self):
        self.display_last_position()
        self.display_course_and_speed()

    def display_course_and_speed(self):
        self.course.configure(text="Course : {}".format(format_angle(self.data.my_boat.course, INPUT_TYPE_AZIMUT)))
        self.speed.configure(text="Speed : {:.1f} Knots".format(self.data.my_boat.speed))
    
    def display_last_position(self):
        self.last_pos_dt.configure(text=self.data.my_boat.last_waypoint_datetime.strftime(constants.DATE_FORMATTER))
        last_position_str = "{}   {}".format(format_angle(self.data.my_boat.last_waypoint.latitude, INPUT_TYPE_LATITUDE), 
                                           format_angle(self.data.my_boat.last_waypoint.longitude, INPUT_TYPE_LONGITUDE))
        self.last_pos.configure(text=last_position_str)
