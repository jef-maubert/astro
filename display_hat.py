# -*- coding: utf-8 -*-
import os
import sys
import logging
import logging.handlers
import configparser
import datetime
import turtle
import constants

NB_ROTATING_LOG = 3
MESSAGE_FORMAT_FILE = '{asctime:s} - {levelname} - {filename:s} - {funcName:s}-{lineno:d} - {message:s}'
MESSAGE_FORMAT_CONSOLE = '{levelname} - {message:s}'
MESSAGE_FORMAT_CONSOLE = '{message:s}'

TURTLE_SIZE_X = 600
TURTLE_SIZE_Y = 600
BIG_PEN = 2
SMALL_PEN = 1
HEIGHT_LINE_COLOR = "black"
LAST_POSITION_COLOR = "blue"
FONT_SIZE = 10
LINE_DOT_NUMBER = 10

class AstroHat:
    def __init__(self):
        self.app_full_name = os.path.basename(sys.argv[0])
        self.app_name = os.path.splitext(self.app_full_name)[0]
        self.app_logger = None
        self.app_config = None
        self.list_of_observations = []
        self.console_log_handler = None
        self.log_level = constants.DEFAULT_LOG_LEVEL
        self.screen = None
        self.tess = None

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
        self.console_log_handler.setFormatter(console_log_format)
        self.app_logger.addHandler(self.console_log_handler)
        self.app_logger.info('Starting %s version %s', self.app_name, constants.VERSION)

    def load_config(self, app_name):
        self.app_config = configparser.ConfigParser()
        my_config_filename = "{}.ini".format(app_name)
        self.app_logger.info('Loading configuration from file "%s"', my_config_filename )
        self.app_config.read(my_config_filename, encoding="utf-8")
        last_pos_dt_str = self.app_config.get('BOAT', 'last_pos_dt', fallback=None)
        self.last_position_time = datetime.datetime.strptime(last_pos_dt_str, constants.DATE_FORMATTER)

        observation_number = 1
        try:
            while(True):
                section_name = 'OBSERVATION_{}'.format(observation_number)
                intercept = float(self.app_config.get(section_name, 'intercept'))
                azimut = float(self.app_config.get(section_name, 'azimut'))
                observation_dt = self.app_config.get(section_name, 'date_time')
                self.list_of_observations.append({"date_time":observation_dt, "azimut":azimut, "intercept": intercept})
                observation_number += 1
        except:
            self.app_logger.info('%d observation(s) loaded from file "%s"', observation_number, my_config_filename )

    def start_turtle (self, image_size):
        turtle.setup(width=TURTLE_SIZE_X, height=TURTLE_SIZE_Y)
        turtle.tracer (10)
        self.screen = turtle.Screen()

        self.screen.setworldcoordinates(-image_size, -image_size, image_size, image_size)
        self.screen.bgcolor("white")
        self.screen.title(self.app_name + " (Version :" + constants.VERSION+ ")")
        self.tess = turtle.Turtle()

        self.tess.pencolor(LAST_POSITION_COLOR)
        self.tess.pensize(BIG_PEN)
        self.tess.hideturtle()
        self.tess.speed("fastest")

    def finish_turtle (self):
        self.screen.exitonclick()
        turtle.bye()

    def draw_last_position(self, position_circle_radius, color=LAST_POSITION_COLOR):
        self.app_logger.info('Drawing last position')
        old_pen = self.tess.pensize()
        old_color = self.tess.pencolor()
        self.tess.pensize(SMALL_PEN)
        self.tess.pencolor(color)
        self.tess.dot()
        self.tess.up()
        self.tess.goto(0,0)
        self.tess.setheading(0)
        self.tess.forward(position_circle_radius)
        self.tess.down()
        self.tess.setheading(90)
        self.tess.circle(position_circle_radius)
        self.tess.up()
        self.tess.setheading(90)
        self.tess.forward(position_circle_radius)
        self.tess.down()
        last_position_time_str = self.last_position_time.strftime(constants.DATE_FORMATTER.split(" ")[1])
        self.tess.write(last_position_time_str, font=("Arial", FONT_SIZE, "normal"), align="left")
        self.tess.up()
        self.tess.goto(0,0)
        self.tess.down()
        self.tess.pencolor(old_color)
        self.tess.pensize(old_pen)

    def draw_legend(self, image_size, color=HEIGHT_LINE_COLOR):
        self.app_logger.info('Drawing legend')
        old_pen = self.tess.pensize()
        old_color = self.tess.pencolor()
        self.tess.pensize(SMALL_PEN)
        self.tess.pencolor(color)
        self.tess.up()
        self.tess.goto(-image_size,image_size - 1)
        self.tess.setheading(0)
        self.tess.down()
        self.tess.forward(1)
        self.tess.write("1 NM", font=("Arial", FONT_SIZE, "normal"), align="left")
        self.tess.up()
        self.tess.goto(0,0)
        self.tess.down()
        self.tess.pencolor(old_color)
        self.tess.pensize(old_pen)
    
    def draw_intercept(self, date_time, azimut, intercept, image_size, color=LAST_POSITION_COLOR):
        self.app_logger.info('Drawing intercept %.1f NM in Az %.0f°', intercept, azimut)
        old_pen = self.tess.pensize()
        old_color = self.tess.pencolor()
        self.tess.pensize(SMALL_PEN)
        self.tess.pencolor(color)
        self.tess.up()
        self.tess.goto(0,0)
        self.tess.down()
        self.tess.setheading(90.0 - azimut)
        dash_length = intercept/ (2.0 * LINE_DOT_NUMBER)
        for dash_index in range (LINE_DOT_NUMBER):
            self.tess.forward(dash_length)
            self.tess.up()
            self.tess.forward(dash_length)
            self.tess.down()
        self.tess.left(90)
        self.tess.pensize(BIG_PEN)
        self.tess.forward(image_size)
        self.tess.backward(2*image_size)
        self.tess.pencolor(old_color)
        self.tess.pensize(old_pen)

    def display_hat(self):
        self.app_logger.info('Display all the observations (azimut, intercept)')
        max_intercept = 1.0
        for observation in self.list_of_observations :
            if max_intercept < abs(observation["intercept"]) :
                max_intercept = abs(observation["intercept"])
        image_size = max_intercept * 3.0
        self.app_logger.debug('image size = %f', image_size)
        self.start_turtle(image_size)
        self.draw_last_position(image_size / 25.0)
        self.draw_legend(image_size)
        for observation in self.list_of_observations :
            self.draw_intercept(observation["date_time"], observation["azimut"], observation["intercept"], image_size)
        self.finish_turtle()

def main () :
    my_app = AstroHat()
    my_app.init_log()
    my_app.load_config("astro")
    my_app.display_hat()

if __name__ == "__main__":
    main()
