# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 17:34:57 2022

@author: jef
"""
import configparser
from configparser import NoSectionError, DuplicateSectionError
import datetime

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
        self.next_observation_number = 1

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
            last_pos_dt = datetime.datetime.strptime(last_pos_dt_str, constants.DATE_SERIAL_FORMATTER)
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

    def load_observations(self):
        observation_number = 1
        list_of_observations = []
        try:
            while True:
                section_name = 'OBSERVATION_{}'.format(observation_number)
                intercept = float(self.app_config.get(section_name, 'intercept'))
                azimut = float(self.app_config.get(section_name, 'azimut'))
                observation_dt = self.app_config.get(section_name, 'date_time')
                list_of_observations.append({"date_time":observation_dt, "azimut":azimut, "intercept": intercept})
                observation_number += 1
        except NoSectionError:
            self.app_logger.info('%d observation(s) loaded from configuration file', observation_number-1)
        observation_rank = 1
        for observation in list_of_observations :
            self.app_logger.info('%d) %s intercept = %.1f NM, Az = %03.0f°', observation_rank, observation["date_time"],
                                 observation["intercept"], observation["azimut"])
            observation_rank += 1
        return list_of_observations

    def save_config(self):
        try:
            self.app_config.add_section('BOAT')
        except DuplicateSectionError:
            pass
        try:
            self.app_config.add_section('LOG')
        except DuplicateSectionError:
            pass

        self.app_config.set('LOG', 'level',self.log_level)
        self.app_config.set('BOAT', 'last_latitude', self.my_boat.last_waypoint.format_latitude())
        self.app_config.set('BOAT', 'last_longitude', self.my_boat.last_waypoint.format_longitude())
        self.app_config.set('BOAT', 'last_pos_dt', str(self.my_boat.last_waypoint_datetime.strftime(constants.DATE_SERIAL_FORMATTER)))
        self.app_config.set('BOAT', 'course', str(self.my_boat.course))
        self.app_config.set('BOAT', 'speed', str(self.my_boat.speed))
        self.app_config.set('BOAT', 'eye_height', str(self.my_boat.eye_height))

        my_config_filename = "{}.ini".format(self.app_name)
        with open(my_config_filename, 'w', encoding="utf-8") as configfile:
            self.app_config.write(configfile)
        self.app_logger.info('Configuration saved in file %s', my_config_filename)

    def save_observation_in_config(self, observation):
        section_name = 'OBSERVATION_{}'.format(self.next_observation_number)
        try:
            self.app_config.add_section(section_name)
        except NoSectionError:
            pass

        self.app_config.set(section_name, 'intercept', "{:.1f}".format(observation.intercept))
        self.app_config.set(section_name, 'azimut', "{:.1f}".format(observation.azimut))
        self.app_config.set(section_name, 'date_time', observation.date_time.strftime(constants.DATE_SERIAL_FORMATTER))
        self.save_config()

    def remove_all_observations(self):
        observation_index = 1
        while observation_index < self.next_observation_number :
            section_name = 'OBSERVATION_{}'.format(observation_index)
            self.app_logger.info('Removing section "%s"', section_name)
            self.app_config.remove_section(section_name)
            observation_index += 1
        self.next_observation_number = 1
        self.save_config()
