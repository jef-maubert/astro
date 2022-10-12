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

from waypoint import Waypoint, format_angle
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
        self.list_of_menu.append({"code": "I", "title":"Initialize Position", "function":self.init_position})
        self.list_of_menu.append({"code": "S", "title":"Set course and speed", "function":self.set_speed_and_course})
        self.list_of_menu.append({"code": "L", "title":"Display last Position", "function":self.display_last_position})
        self.list_of_menu.append({"code": "C", "title":"Display current Pos", "function":self.display_current_position})
        self.list_of_menu.append({"code": "A", "title":"Enter new astro", "function":self.new_astro})
        self.list_of_menu.append({"code": "N", "title":"Caculate new position", "function":self.chapeau})
        self.list_of_menu.append({"code": "E", "title":"Exit", "function":None})
        
    def start_astro(self):
        os.makedirs(constants.LOG_DIRECTORY, exist_ok=True)
        self.init_log()
        self.load_config()
        self.init_menu()

    def run_once(self):
        print("Menu")
        for menu in self.list_of_menu:
            print("  " + menu["code"] + " - " + menu["title"])
        menu_choice = input ("Your choice ? ")
        for menu in self.list_of_menu:
            if menu_choice.upper() == menu["code"].upper():
                if menu["function"]:
                    menu["function"]()
                    return True
                return False
        print("Invalid choice")
        return True

    def enter_date(self):
        date_dt = datetime.datetime.now()
        date_default = date_dt.strftime(constants.DATE_FORMATTER.split(" ")[0]) 
        date_default = date_default.replace("-", "/")
        date_prompt = "Date (dd/mm/yyyy) [" + date_default + "] ? "
        date_input = input (date_prompt)
        new_date = date_input if date_input else date_default 
        new_date = new_date.replace("/", "-")
        print ("new date = {}".format(new_date))
        return new_date 

    def enter_time(self):
        time_prompt = "Time (hh:mm:ss) [now] ? "
        time_input = input (time_prompt)
        time_dt = datetime.datetime.now()
        time_default = time_dt.strftime(constants.DATE_FORMATTER.split(" ")[1]) 
        new_time = time_input if time_input else time_default 
        print ("new time = {}".format(new_time))
        return new_time 
    
    def enter_angle(self, default_value, value_is_longitude=False):
        default_value = format_angle(default_value)
        if value_is_longitude:
            prompt = "Longitude (DDD°mm.m'(W/E)) ["+default_value+"] ? "
        else:
            prompt = "Latitude (DD°mm.m'(N/S)) ["+default_value+"] ? "
        new_angle = input(prompt)
        return new_angle
        
    def init_position(self):
        self.app_logger.info('Initialize the boat position')
        new_date = self.enter_date()
        new_time = self.enter_time()
        new_waypoint_dt = datetime.datetime.strptime(new_date + " " + new_time, constants.DATE_FORMATTER)
        new_latitude = self.enter_angle(self.my_boat.last_waypoint.latitude, value_is_longitude=False)
        new_longitude = self.enter_angle(self.my_boat.last_waypoint.longitude, value_is_longitude=True)
        self.my_boat.set_new_position(Waypoint ("last position", new_latitude, new_longitude), new_waypoint_dt)

    def set_speed_and_course(self):
        self.app_logger.info('Set the course and the speed')

        default_speed = self.my_boat.speed
        prompt = "Speed (xx.x) [{}] ? ".format(default_speed)
        speed_input = input(prompt)
        new_speed = float(speed_input) if speed_input else default_speed

        default_course = self.my_boat.course
        prompt = "Course (xx) [{}] ? ".format(default_course)
        course_input = input(prompt)
        new_course = int(course_input) if course_input else default_course

        self.my_boat.set_speed_and_course(new_speed, new_course)

    def display_last_position(self):
        self.app_logger.info('Display the last recorded position of the boat')
        self.app_logger.info("at %s %s", self.my_boat.last_waypoint_datetime.strftime(constants.DATE_FORMATTER), self.my_boat.format_last_position())

    def display_current_position(self):
        self.app_logger.info('Display the current position of the boat based on last position and course and speed from that time')
        now = datetime.datetime.now()
        now_string = now.strftime(constants.DATE_FORMATTER)
        self.app_logger.info("now (%s) %s", now_string, self.my_boat.format_current_position())

    def new_astro(self):
        self.app_logger.info('Enter a new sun sight, and calculate the height angles azimut and intercept')
        self.app_logger.warning('Not yet implemented')

    def chapeau(self):
        self.app_logger.info('Calculate a new positon based on 2 or 3 couples (azimut, intercept)')
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
