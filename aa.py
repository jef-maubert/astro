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
from astro_data import AstroData
from astro_view import AstroTk
from waypoint import Waypoint, format_angle
from waypoint import INPUT_TYPE_LATITUDE, INPUT_TYPE_LONGITUDE, INPUT_TYPE_AZIMUT
from boat import Boat
from observation import Observation
from display_hat import DisplayHat

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

    def on_button_new_obs(self):
        self.app_logger.info('Click on button "New obs"')
     
    def init_display(self):
        self.display_last_position()
        self.display_course_and_speed()

    def display_course_and_speed(self):
        self.course.configure(text="Course : {}".format(format_angle(self.data.my_boat.course, INPUT_TYPE_AZIMUT)))
        self.speed.configure(text="Speed : {} knots".format(self.data.my_boat.speed))
    
    def display_last_position(self):
        self.last_pos_dt.configure(text=self.data.my_boat.last_waypoint_datetime.strftime(constants.DATE_FORMATTER))
        last_position_str = "{}   {}".format(format_angle(self.data.my_boat.last_waypoint.latitude, INPUT_TYPE_LATITUDE), 
                                           format_angle(self.data.my_boat.last_waypoint.longitude, INPUT_TYPE_LONGITUDE))
        self.last_pos.configure(text=last_position_str)
         
class AstroData ():
    def __init__(self, app_name, app_logger, console_log_handler):
        self.app_name = app_name
        self.app_logger = app_logger
        self.console_log_handler = console_log_handler
        self.app_config = None
        self.my_boat = None
        self.last_pos = "45°25.3'N 004°54.5'E"
        self.last_pos_dt = "25/01/2022 18:42:30"

    def load_config(self):
        self.app_config = configparser.ConfigParser()
        my_config_filename = "{}.ini".format(self.app_name)
        self.app_logger.info('Loading configuration from file "%s"', my_config_filename )
        self.app_config.read(my_config_filename, encoding="utf-8")
        log_level = self.app_config.get('LOG', 'level', fallback=constants.DEFAULT_LOG_LEVEL).upper()
        if log_level in ("DEBUG", "INFO"):
            self.log_level = log_level
            self.console_log_handler.setLevel(self.log_level)
        self.app_logger.debug('log level set to "%s"', self.log_level)
        last_latitude = self.app_config.get('BOAT', 'last_latitude', fallback=constants.DEFAULT_LATITUDE)
        last_longitude = self.app_config.get('BOAT', 'last_longitude', fallback=constants.DEFAULT_LONGITUDE)
        last_pos_dt_str = self.app_config.get('BOAT', 'last_pos_dt', fallback=None)
        if last_pos_dt_str :
            last_pos_dt = datetime.datetime.strptime(last_pos_dt_str, constants.DATE_FORMATTER)
        else:
            last_pos_dt = datetime.datetime.now()
        speed = float(self.app_config.get('BOAT', 'speed', fallback=constants.DEFAULT_SPEED))
        course = float(self.app_config.get('BOAT', 'course', fallback=constants.DEFAULT_COURSE))
        eye_height = float(self.app_config.get('BOAT', 'eye_height', fallback=constants.DEFAULT_EYE_HEIGHT))

        last_position = Waypoint("last position", last_latitude, last_longitude)

        self.my_boat = Boat(last_position, last_pos_dt, speed, course, eye_height, self.app_logger)
        self.next_observation_number = 1
        try:
            while True:
                section_name = 'OBSERVATION_{}'.format(self.next_observation_number)
                # tip : check if the section exist
                self.app_config.get(section_name, 'intercept')
                self.next_observation_number += 1
        except NoSectionError:
            self.app_logger.info('%d observation(s) loaded from file "%s"', self.next_observation_number-1, my_config_filename )

NB_ROTATING_LOG = 3
MESSAGE_FORMAT_FILE = '{asctime:s} - {levelname} - {filename:s} - {funcName:s}-{lineno:d} - {message:s}'
MESSAGE_FORMAT_CONSOLE_KK = '{levelname} - {message:s}'
MESSAGE_FORMAT_CONSOLE = '{levelname}{message:s}'

def init_log(app_name):
    log_filename = os.path.join(constants.LOG_DIRECTORY, app_name + ".log")
    app_logger = logging.getLogger(app_name)
    logging.basicConfig(level=logging.DEBUG)
    app_logger.propagate = False
    if app_logger.hasHandlers():
        app_logger.handlers.clear()

    file_log_format = logging.Formatter(fmt=MESSAGE_FORMAT_FILE, datefmt='%d %H:%M:%S', style="{")
    file_log_handler = logging.handlers.RotatingFileHandler(log_filename, mode="a", maxBytes=100000, backupCount=NB_ROTATING_LOG,)
    file_log_handler.setLevel("DEBUG")
    file_log_handler.setFormatter(file_log_format)
    app_logger.addHandler(file_log_handler)

    console_log_format = logging.Formatter(fmt=MESSAGE_FORMAT_CONSOLE, datefmt='%d %H:%M:%S', style="{")
    console_log_handler = logging.StreamHandler()
    console_log_handler.setLevel(constants.DEFAULT_LOG_LEVEL)
    logging.addLevelName(logging.DEBUG, "- ")
    logging.addLevelName(logging.INFO, "")
    logging.addLevelName(logging.WARNING, "!!! ")
    console_log_handler.setFormatter(console_log_format)
    app_logger.addHandler(console_log_handler)
    app_logger.info('Starting %s version %s', app_name, constants.VERSION)
    return app_logger, console_log_handler

def main () :
    os.makedirs(constants.LOG_DIRECTORY, exist_ok=True)
    app_logger, console_log_handler = init_log("astro")
    my_data = AstroData("astro", app_logger, console_log_handler)
    my_data.load_config()
    my_app = AstroTk(None, my_data , app_logger)
    my_app.init_display()
    my_app.mainloop()

if __name__ == "__main__":
    main()
