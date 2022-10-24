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
