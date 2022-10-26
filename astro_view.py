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
        self.grid_columnconfigure(0, weight=1)
        next_row = 0
        title = tk.Label(self, text="Astro {}".format (constants.VERSION), background="green")
        title.grid(row=next_row, column=0, columnspan=2, padx=PADX_STD, sticky="NSEW")
        next_row += 1

        grid_dict =  {"padx": 5, "pady": 2, "sticky": "nsew"}

        last_pos_frame = tk.LabelFrame(self, text="Last position", borderwidth=2, relief=tk.GROOVE)
        last_pos_frame.grid(row=next_row, column=0, **grid_dict)
        last_pos_frame.grid_columnconfigure(0, weight=1)
        last_pos_frame.grid_columnconfigure(1, weight=0)
        self.last_pos_dt = tk.Label(last_pos_frame)
        self.last_pos_dt.grid(row=0, column=0, **grid_dict)
        self.last_pos = tk.Label(last_pos_frame)
        self.last_pos.grid(row=1, column=0, **grid_dict)
        self.btn_modif_last_pos = tk.Button(last_pos_frame, text="Modify", command=self.on_button_modif_last_pos)
        self.btn_modif_last_pos.grid(row=0, column=1, rowspan=2, **grid_dict)

        next_row += 1
        course_and_speed_frame = tk.LabelFrame(self, text="Course and speed", borderwidth=2, relief=tk.GROOVE)
        course_and_speed_frame.grid(column=0, row=next_row, **grid_dict)
        course_and_speed_frame.grid_columnconfigure(0, weight=1)
        course_and_speed_frame.grid_columnconfigure(1, weight=0)
        self.course = tk.Label(course_and_speed_frame)
        self.course.grid(row=0, column=0, **grid_dict)
        self.speed= tk.Label(course_and_speed_frame)
        self.speed.grid(row=1, column=0, **grid_dict)
        self.btn_modif_course_and_speed = tk.Button(course_and_speed_frame, text="Modify", command=self.on_button_modif_course_and_speed)
        self.btn_modif_course_and_speed.grid(row=0, column=1, rowspan=2, **grid_dict)

        next_row += 1
        current_pos_frame = tk.LabelFrame(self, text="Current position", borderwidth=2, relief=tk.GROOVE)
        current_pos_frame.grid(column=0, row=next_row, **grid_dict)
        current_pos_frame.grid_columnconfigure(0, weight=1)
        current_pos_frame.grid_columnconfigure(1, weight=0)
        self.current_pos_dt = tk.Label(current_pos_frame)
        self.current_pos_dt.grid(row=0, column=0, **grid_dict)
        self.current_pos = tk.Label(current_pos_frame)
        self.current_pos.grid(row=1, column=0, **grid_dict)
        self.btn_modif_current_pos = tk.Button(current_pos_frame, text="Observation", command=self.on_button_new_obs)
        self.btn_modif_current_pos.grid(row=0, column=1, rowspan=2, **grid_dict)

    def on_button_modif_last_pos(self):
        now = datetime.datetime.now().strftime(constants.DATE_FORMATTER)
        self.current_pos.configure(text=now)

    def on_button_modif_course_and_speed(self):
        my_course_and_speed_dlg = CourseSpeedDlg(self, "Course and speed",
                                                     self.data.my_boat.last_waypoint_datetime,
                                                     self.data.my_boat.course, self.data.my_boat.speed)
        if my_course_and_speed_dlg.result:
            new_dt= my_course_and_speed_dlg.result[0].replace ("/", "-")
            new_waypoint_dt = datetime.datetime.strptime(new_dt, constants.DATE_FORMATTER)
            new_waypoint = self.data.my_boat.get_position_at(new_waypoint_dt)
            new_latitude_str = format_angle(new_waypoint.latitude, input_type = INPUT_TYPE_LATITUDE)
            new_longitude_str = format_angle(new_waypoint.longitude, input_type = INPUT_TYPE_LONGITUDE)
            self.data.my_boat.set_new_position(Waypoint ("last position", new_latitude_str, new_longitude_str), new_waypoint_dt)

            new_course = float(my_course_and_speed_dlg.result[1])
            new_speed = float(my_course_and_speed_dlg.result[2])
            self.data.my_boat.set_course_and_speed(new_course, new_speed)
            self.update_display()

    def on_button_new_obs(self):
        self.app_logger.info('Click on button "New obs"')

    def update_display(self):
        self.display_last_position()
        self.display_course_and_speed()
        self.display_current_position()

    def display_course_and_speed(self):
        self.course.configure(text="Course : {}".format(format_angle(self.data.my_boat.course, INPUT_TYPE_AZIMUT)))
        self.speed.configure(text="Speed : {:.1f} Knots".format(self.data.my_boat.speed))

    def display_last_position(self):
        self.last_pos_dt.configure(text=self.data.my_boat.last_waypoint_datetime.strftime(constants.DATE_FORMATTER))
        last_position_str = "{}   {}".format(format_angle(self.data.my_boat.last_waypoint.latitude, INPUT_TYPE_LATITUDE),
                                           format_angle(self.data.my_boat.last_waypoint.longitude, INPUT_TYPE_LONGITUDE))
        self.last_pos.configure(text=last_position_str)

    def display_current_position(self):
        self.current_pos_dt.configure(text=self.data.my_boat.last_waypoint_datetime.strftime(constants.DATE_FORMATTER))
        current_position_str = "{}   {}".format(format_angle(self.data.my_boat.last_waypoint.latitude, INPUT_TYPE_LATITUDE),
                                           format_angle(self.data.my_boat.last_waypoint.longitude, INPUT_TYPE_LONGITUDE))
        self.current_pos.configure(text=current_position_str)
