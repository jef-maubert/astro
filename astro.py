# -*- coding: utf-8 -*-
import os
import sys
import re
import logging
import logging.handlers
import configparser
import datetime
import platform
import constants

from waypoint import Waypoint, format_angle
from waypoint import INPUT_TYPE_LATITUDE, INPUT_TYPE_LONGITUDE, INPUT_TYPE_AZIMUT
from boat import Boat
from observation import Observation
from display_hat import DisplayHat

NB_ROTATING_LOG = 3
MESSAGE_FORMAT_FILE = '{asctime:s} - {levelname} - {filename:s} - {funcName:s}-{lineno:d} - {message:s}'
MESSAGE_FORMAT_CONSOLE_KK = '{levelname} - {message:s}'
MESSAGE_FORMAT_CONSOLE = '{levelname}{message:s}'

TURTLE_SIZE_X = 600
TURTLE_SIZE_Y = 600
BIG_PEN = 3
SMALL_PEN = 1
HEIGHT_LINE_COLOR = "black"
LAST_POSITION_COLOR = "blue"
FONT_SIZE = 10
LINE_DOT_NUMBER = 10

class AstroApp:
    def __init__(self):
        self.app_full_name = os.path.basename(sys.argv[0])
        self.app_name = os.path.splitext(self.app_full_name)[0]
        self.app_logger = None
        self.app_config = None
        self.my_boat = None
        self.list_of_menu = []
        self.console_log_handler = None
        self.log_level = constants.DEFAULT_LOG_LEVEL
        self.next_observation_number = 1

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
        self.console_log_handler = logging.StreamHandler()
        self.console_log_handler.setLevel(self.log_level)
        logging.addLevelName(logging.DEBUG, "")
        logging.addLevelName(logging.INFO, "")
        logging.addLevelName(logging.WARNING, "!!! ")
        self.console_log_handler.setLevel(self.log_level)
        self.console_log_handler.setFormatter(console_log_format)
        self.app_logger.addHandler(self.console_log_handler)
        self.app_logger.info('Starting %s version %s', self.app_name, constants.VERSION)

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
        except:
            self.app_logger.info('%d observation(s) loaded from file "%s"', self.next_observation_number-1, my_config_filename )

    def save_config(self):
        try:
            self.app_config.add_section('BOAT')
        except:
            pass
        try:
            self.app_config.add_section('LOG')
        except:
            pass

        self.app_config.set('LOG', 'level',self.log_level)
        self.app_config.set('BOAT', 'last_latitude', self.my_boat.last_waypoint.format_latitude())
        self.app_config.set('BOAT', 'last_longitude', self.my_boat.last_waypoint.format_longitude())
        self.app_config.set('BOAT', 'last_pos_dt', str(self.my_boat.last_waypoint_datetime.strftime(constants.DATE_FORMATTER)))
        self.app_config.set('BOAT', 'course', str(self.my_boat.course))
        self.app_config.set('BOAT', 'speed', str(self.my_boat.speed))
        self.app_config.set('BOAT', 'eye_height', str(self.my_boat.eye_height))

        my_config_filename = "{}.ini".format(self.app_name)
        with open(my_config_filename, 'w', encoding="utf-8") as configfile:
            self.app_config.write(configfile)

    def save_observation_in_config(self, observation):
        section_name = 'OBSERVATION_{}'.format(self.next_observation_number)
        try:
            self.app_config.add_section(section_name)
        except:
            pass

        self.app_config.set(section_name, 'intercept', "{:.1f}".format(observation.intercept))
        self.app_config.set(section_name, 'azimut', "{:.1f}".format(observation.azimut))
        self.app_config.set(section_name, 'date_time', observation.date_time.strftime(constants.DATE_FORMATTER))
        self.save_config()

    def init_menu(self):
        self.list_of_menu.append({"code": "I", "title":"Initialize Position", "function":self.init_position})
        self.list_of_menu.append({"code": "S", "title":"Set course and speed", "function":self.set_speed_and_course})
        self.list_of_menu.append({"code": "L", "title":"Display last Position", "function":self.display_last_position})
        self.list_of_menu.append({"code": "C", "title":"Display current Position", "function":self.display_current_position})
        self.list_of_menu.append({"code": "A", "title":"Enter new astro", "function":self.new_astro})
        self.list_of_menu.append({"code": "D", "title":"Display all observations", "function":self.chapeau})
        self.list_of_menu.append({"code": "E", "title":"Exit", "function":None})

    def start_astro(self):
        os.makedirs(constants.LOG_DIRECTORY, exist_ok=True)
        self.init_log()
        self.load_config()
        self.init_menu()

    def run_once(self):
        print("")
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

    def enter_date(self, date_default=None):
        if not date_default :
            date_dt = datetime.datetime.now()
            date_default = date_dt.strftime(constants.DATE_FORMATTER.split(" ")[0])
            date_default = date_default.replace("-", "/")
        year_default = int(date_default[-4:])
        date_prompt = "Date (dd/mm/yyyy) [{}] ? ".format(date_default)
        regex_for_validation = "\d{1,2}\/\d{1,2}(\/\d{2,4})?"
        while True:
            date_input = input (date_prompt)
            new_date = date_input if date_input else date_default
            if re.match (regex_for_validation, new_date):
                break
        new_date = new_date.replace("/", "-")
        new_date_day = int(new_date.split("-")[0])
        new_date_month = int(new_date.split("-")[1])
        try:
            new_date_year = int(new_date.split("-")[2])
        except IndexError:
            new_date_year = year_default
        new_date_year = new_date_year+2000 if new_date_year < 100 else new_date_year
        new_date = "{:02d}-{:02d}-{:04d}".format(new_date_day, new_date_month, new_date_year)
        self.app_logger.debug("New date = %s",new_date)
        return new_date

    def enter_time(self, time_default=None):
        if not time_default:
            time_default= "now"
        time_prompt = "Time (hh:mm:ss) [{}] ? ".format(time_default)
        regex_for_validation = "\d{1,2}:\d{1,2}:\d{1,2}"
        while True:
            time_input = input (time_prompt)
            time_dt = datetime.datetime.now()
            if time_default == "now":
                time_default = time_dt.strftime(constants.DATE_FORMATTER.split(" ")[1])
            new_time = time_input if time_input else time_default
            if re.match (regex_for_validation, new_time):
                break
        self.app_logger.debug("New time = %s",new_time)
        return new_time

    def enter_position_coordinate(self, default_value, input_type):
        default_value = format_angle(default_value, input_type)
        if input_type == INPUT_TYPE_LATITUDE:
            prompt = "Latitude (DD°mm.m'(N/S)) ["+default_value+"] ? "
            regex_for_validation = "\d{1,2}°\d{1,2}.\d'[NS]?"
        elif input_type == INPUT_TYPE_LONGITUDE:
            prompt = "Longitude (DDD°mm.m'(W/E)) ["+default_value+"] ? "
            regex_for_validation = "\d{1,3}°\d{1,2}.\d'[WE]?"
        while True:
            angle_input = input(prompt)
            new_angle = angle_input if angle_input else default_value
            if re.match (regex_for_validation, new_angle):
                break
        return new_angle

    def enter_ho(self):
        prompt = "Sextant angle (DD.mm) ? "
        regex_for_validation = "\d{1,2}(.\d)?"
        while True:
            new_ho_str = input(prompt)
            if re.match (regex_for_validation, new_ho_str):
                break
        return float(new_ho_str)

    def enter_boolean (self, prompt, default_value= True):
        default_value_str = "Y" if default_value else "N"
        prompt = "{} (Y/N) [{}]? ".format(prompt, default_value_str)
        regex_for_validation = "[yYnN]"
        while True:
            bool_str = input(prompt)
            bool_str = bool_str if bool_str else default_value_str
            if re.match (regex_for_validation, bool_str):
                break
        return bool_str in ("Y", "y")

    def enter_eye_height(self):
        eye_height_default = str(self.my_boat.eye_height)
        eye_height_prompt = "Eye height (hh)m [{}] ? ".format(eye_height_default)
        regex_for_validation = "\d{1,2}"
        while True:
            eye_height_input = input (eye_height_prompt)
            eye_height_input = eye_height_input if eye_height_input else eye_height_default
            if re.match (regex_for_validation, eye_height_input):
                break
        new_eye_height = float(eye_height_input)
        self.app_logger.debug("New eye_height = %.0f m", new_eye_height)
        return new_eye_height

    def init_position(self):
        self.app_logger.info('Initialize the boat position')
        new_date = self.enter_date()
        new_time = self.enter_time()
        new_waypoint_dt = datetime.datetime.strptime(new_date + " " + new_time, constants.DATE_FORMATTER)
        new_latitude = self.enter_position_coordinate(self.my_boat.last_waypoint.latitude, INPUT_TYPE_LATITUDE)
        new_longitude = self.enter_position_coordinate(self.my_boat.last_waypoint.longitude, INPUT_TYPE_LONGITUDE)
        self.my_boat.set_new_position(Waypoint ("last position", new_latitude, new_longitude), new_waypoint_dt)

    def set_speed_and_course(self):
        self.app_logger.info('Set the course and the speed')

        last_posit_date = self.my_boat.last_waypoint_datetime.strftime(constants.DATE_FORMATTER).split(" ")[0].replace ("-", "/")
        last_posit_time = self.my_boat.last_waypoint_datetime.strftime(constants.DATE_FORMATTER).split(" ")[1]
        new_date = self.enter_date(date_default = last_posit_date)
        new_time = self.enter_time(time_default = last_posit_time)
        new_waypoint_dt = datetime.datetime.strptime(new_date + " " + new_time, constants.DATE_FORMATTER)

        default_speed = self.my_boat.speed
        prompt = "Speed (xx.x) [{}] ? ".format(default_speed)
        regex_for_validation = "\d{1,2}.?\d?"
        while True:
            speed_input = input (prompt)
            speed_input  = speed_input if speed_input else str(default_speed)
            if re.match (regex_for_validation, speed_input):
                break
        new_speed = float(speed_input) if speed_input else default_speed

        default_course = int(self.my_boat.course)
        prompt = "Course (xxx) [{}] ? ".format(default_course)
        regex_for_validation = "\d{1,3}"
        while True:
            course_input = input(prompt)
            course_input  = course_input if course_input else str(default_course)
            if re.match (regex_for_validation, course_input):
                break
        new_course = int(course_input) if course_input else default_course

        new_waypoint = self.my_boat.get_position_at(new_waypoint_dt)
        new_latitude_str = format_angle(new_waypoint.latitude, input_type = INPUT_TYPE_LATITUDE)
        new_longitude_str = format_angle(new_waypoint.longitude, input_type = INPUT_TYPE_LONGITUDE)
        self.my_boat.set_new_position(Waypoint ("last position", new_latitude_str, new_longitude_str), new_waypoint_dt)
        self.my_boat.set_speed_and_course(new_speed, new_course)

    def display_last_position(self):
        self.app_logger.info('Last recorded position of the boat')
        self.app_logger.info("at %s %s", self.my_boat.last_waypoint_datetime.strftime(constants.DATE_FORMATTER), self.my_boat.format_last_position())

    def display_current_position(self):
        self.app_logger.info('Current position of the boat based on last position and course and speed from that time')
        now = datetime.datetime.now()
        now_string = now.strftime(constants.DATE_FORMATTER)
        self.app_logger.info("running %.1f knots in the %s", self.my_boat.speed, format_angle(self.my_boat.course, input_type = INPUT_TYPE_AZIMUT))
        self.app_logger.info("now (%s) %s", now_string, self.my_boat.format_current_position())

    def new_astro(self):
        self.app_logger.info('Enter a new sun sight, and calculate the height angles, azimut and intercept')
        new_date = self.enter_date()
        new_time = self.enter_time()
        self.my_boat.eye_height = self.enter_eye_height()
        new_ho = self.enter_ho()

        observation_dt = datetime.datetime.strptime(new_date + " " + new_time, constants.DATE_FORMATTER)
        observation_position = self.my_boat.get_position_at(observation_dt)

        my_observation = Observation (observation_dt, observation_position, self.my_boat.eye_height, app_logger = self.app_logger)
        my_observation.calculate_he_and_az(new_ho)
        if self.enter_boolean ("Save it"):
            self.save_observation_in_config(my_observation)

    def load_observations(self):
        observation_number = 1
        list_of_observations = []
        try:
            while(True):
                section_name = 'OBSERVATION_{}'.format(observation_number)
                intercept = float(self.app_config.get(section_name, 'intercept'))
                azimut = float(self.app_config.get(section_name, 'azimut'))
                observation_dt = self.app_config.get(section_name, 'date_time')
                list_of_observations.append({"date_time":observation_dt, "azimut":azimut, "intercept": intercept})
                observation_number += 1
        except:
            self.app_logger.info('%d observation(s) loaded from configuration file', observation_number-1)
        observation_rank = 1
        for observation in list_of_observations :
            self.app_logger.info('%d) %s intercept = %.1f NM, Az = %03.0f°', observation_rank, observation["date_time"],
                                 observation["intercept"], observation["azimut"])
            observation_rank += 1

    def chapeau(self):
        self.app_logger.info('Display all the observations (azimut, intercept)')
        turtle_available = True
        if platform.system().lower()  == "windows" :
            turtle_available = True
        elif platform.system().lower()  == "linux":
            try :
                platform.system().fredesktop_os_release()
            except:
                turtle_available = False

        self.load_observations()
        if turtle_available:
            my_hat_display = DisplayHat(verbose=False)
            my_hat_display.launch_display_hat(self.app_logger, self.app_name)
        else:
            self.app_logger.info('Please launch "display_hat.py"')

def main () :
    my_app = AstroApp()
    my_app.start_astro()
    while True:
        if not my_app.run_once():
            break
    my_app.save_config()

if __name__ == "__main__":
    main()
