# -*- coding: utf-8 -*-
import math
import os
import sys
import logging
import logging.handlers
import configparser
import datetime
from datetime import timezone
import constants

from waypoint import Waypoint
from boat import Boat

NB_ROTATING_LOG = 3
MESSAGE_FORMAT_FILE = '{asctime:s} - {levelname} - {filename:s} - {funcName:s}-{lineno:d} - {message:s}'
MESSAGE_FORMAT_CONSOLE = '{levelname} - {message:s}'

class AstroApp :
    def __init__(self):
        self.app_full_name = os.path.basename(sys.argv[0])
        self.app_name = os.path.splitext(self.app_full_name)[0]
        self.app_logger = None
        self.app_config = None
        self.my_boat = None
        self.list_of_menu = []

    def init_log(self):
        log_filename = os.path.join(constants.LOG_DIRECTORY, self.app_name + ".log")
        self.app_logger = logging.getLogger(self.app_name)
        logging.basicConfig(level=logging.DEBUG)
        self.app_logger.propagate = False
        if self.app_logger.hasHandlers():
            self.app_logger.handlers.clear()

        file_log_format = logging.Formatter(fmt=MESSAGE_FORMAT_FILE, datefmt='%d %H:%M:%S', style="{")
        file_log_handler = logging.handlers.RotatingFileHandler(log_filename, mode="a", maxBytes=100000, backupCount=NB_ROTATING_LOG,)
        file_log_handler.setLevel("DEBUG")
        file_log_handler.setFormatter(file_log_format)
        self.app_logger.addHandler(file_log_handler)


        console_log_format = logging.Formatter(fmt=MESSAGE_FORMAT_CONSOLE, datefmt='%d %H:%M:%S', style="{")
        console_log_handler = logging.StreamHandler()
        console_log_handler.setLevel("DEBUG")
        console_log_handler.setFormatter(console_log_format)
        self.app_logger.addHandler(console_log_handler)
        self.app_logger.info('Starting %s version %s', self.app_name, constants.VERSION)

    def load_config(self):
        self.app_config = configparser.ConfigParser()
        my_config_filename = "{}.ini".format(self.app_name)
        self.app_logger.info('Loading configuration from file "%s"', my_config_filename )
        self.app_config.read(my_config_filename)
        last_latitude = self.app_config.get('BOAT', 'last_latitude', fallback=constants.DEFAULT_LATITUDE)
        last_longitude = self.app_config.get('BOAT', 'last_longitude', fallback=constants.DEFAULT_LONGITUDE)
        last_pos_dt_str = self.app_config.get('BOAT', 'last_pos_dt', fallback=None)
        if last_pos_dt_str :
            last_pos_dt = datetime.datetime.strptime(last_pos_dt_str, constants.DATE_FORMATTER)
        else:
            last_pos_dt = datetime.datetime.now()
        speed = float(self.app_config.get('BOAT', 'speed', fallback=constants.DEFAULT_SPEED))
        course = self.app_config.getint('BOAT', 'course', fallback=constants.DEFAULT_COURSE)

        last_position = Waypoint("last position", last_latitude, last_longitude)

        self.my_boat = Boat(last_position, last_pos_dt, speed, course, self.app_logger)
        
    def save_config(self):
        try:
            self.app_config.add_section('BOAT')
        except:
            pass
        
        self.app_config.set('BOAT', 'last_latitude', self.my_boat.last_waypoint.format_latitude())
        self.app_config.set('BOAT', 'last_longitude', self.my_boat.last_waypoint.format_longitude())
        self.app_config.set('BOAT', 'last_pos_dt', str(self.my_boat.last_waypoint_datetime.strftime(constants.DATE_FORMATTER)))
        self.app_config.set('BOAT', 'course', str(self.my_boat.course))
        self.app_config.set('BOAT', 'speed', str(self.my_boat.speed))

        my_config_filename = "{}.ini".format(self.app_name)
#        with open(my_config_filename, 'w', encoding="utf-8") as configfile:
        with open(my_config_filename, 'w') as configfile:
            self.app_config.write(configfile)

    def init_menu(self):
        self.list_of_menu.append({"code": "I", "title":"[I]nitialize Position", "function":self.init_position})
        self.list_of_menu.append({"code": "L", "title":"Display [L]ast Position", "function":self.display_last_position})
        self.list_of_menu.append({"code": "C", "title":"Display [C]urrent Pos", "function":self.display_current_position})
        self.list_of_menu.append({"code": "A", "title":"Enter new [A]stro", "function":self.new_astro})
        self.list_of_menu.append({"code": "H", "title":"Caculate c[H]apeau", "function":self.chapeau})
        self.list_of_menu.append({"code": "E", "title":"[E]xit", "function":None})

    def start_astro(self):
        os.makedirs(constants.LOG_DIRECTORY, exist_ok=True)
        self.init_log()
        self.load_config()
        self.init_menu()

    def run_once(self):
        print("Menu")
        for menu in self.list_of_menu:
            print("  "+menu["title"])
        menu_choice = input ("Your choice : ")
        for menu in self.list_of_menu:
            if menu_choice.upper() == menu["code"].upper():
                if menu["function"]:
                    menu["function"]()
                    return True
                return False
        print("Invalid choice")
        return True

    def init_position(self):
        self.app_logger.warning('Not yet implemented')

    def display_last_position(self):
        self.app_logger.info("at %s %s", self.my_boat.last_waypoint_datetime.strftime(constants.DATE_FORMATTER), self.my_boat.format_last_position())

    def display_current_position(self):
        now = datetime.datetime.now()
        now_string = now.strftime(constants.DATE_FORMATTER)
        self.app_logger.info("now (%s) %s", now_string, self.my_boat.format_current_position())

    def new_astro(self):
        self.app_logger.warning('Not yet implemented')

    def chapeau(self):
        self.app_logger.warning('Not yet implemented')

    
def main () :
    my_app = AstroApp()
    my_app.start_astro()
    while(True):
        if not my_app.run_once():
            break
    my_app.save_config()

if __name__ == "__main__":
    main()
