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

LEGEND_COLOR = "black"
LAST_POSITION_COLOR = "black"
TARGET_COLOR = "grey"
FONT_SIZE = 10
RATIO_IMAGE_INTERCEPT = 3
LINE_DOT_NUMBER = 10

class DisplayHat:
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
        self.list_of_intercept_color = ["blue", "orange", "green", "red", "violet"]
        self.map_size_x = 20.0
        self.map_size_x = 20.0

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

    def start_turtle (self, min_map_size):
        self.screen = turtle.Screen()

        screenTk = self.screen.getcanvas().winfo_toplevel()
        screenTk.attributes("-fullscreen", True)

        #tip : turtle.Screen().getcanvas() is equivalant to tkinter.root
        screen_width = self.screen.getcanvas().winfo_screenwidth()
        screen_height = self.screen.getcanvas().winfo_screenheight()
        self.app_logger.debug("screen width = %d, screen_height = %d", screen_width,  screen_height)
        ratio_x_y = float(screen_width) / float(screen_height)
#        self.screen.setup(width=TURTLE_SIZE_X, height=TURTLE_SIZE_Y)
        self.screen.tracer (10)

        if ratio_x_y >1:
            self.map_size_x = min_map_size * ratio_x_y
            self.map_size_y =min_map_size
        else:
            self.map_size_x = min_map_size
            self.map_size_y =min_map_size * ratio_x_y
        self.app_logger.debug('map size %.1f NM * %.1f NM', self.map_size_x , self.map_size_y)

        self.screen.setworldcoordinates(-self.map_size_x, -self.map_size_y, self.map_size_x, self.map_size_y)
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

    def draw_last_position(self, square_size, color=LAST_POSITION_COLOR):
        self.app_logger.debug('Drawing last position')
        old_pen = self.tess.pensize()
        old_color = self.tess.pencolor()
        self.tess.pensize(SMALL_PEN)
        self.tess.pencolor(color)
        self.tess.dot()
        self.tess.up()
        self.tess.goto(0,0)
        self.tess.goto(square_size/2, square_size/2)
        self.tess.down()
        self.tess.setheading(180)
        last_position_time_str = self.last_position_time.strftime(constants.DATE_FORMATTER.split(" ")[1])
        self.tess.write(last_position_time_str, font=("Arial", FONT_SIZE, "normal"), align="left")
        for i in range(4):
            self.tess.forward(square_size)
            self.tess.left(90)
        self.tess.up()
        self.tess.goto(0,0)
        self.tess.down()
        self.tess.pencolor(old_color)
        self.tess.pensize(old_pen)

    def draw_target_circle(self, radius, pen_size, color=TARGET_COLOR):
        self.app_logger.debug('Drawing circle %.0f NM', radius)
        old_pen = self.tess.pensize()
        old_color = self.tess.pencolor()
        self.tess.pensize(pen_size)
        self.tess.pencolor(color)
        self.tess.dot()
        self.tess.up()
        self.tess.goto(0,0)
        self.tess.setheading(0)
        self.tess.forward(radius)
        self.tess.down()
        self.tess.setheading(90)
        self.tess.circle(radius, steps=50)
        self.tess.up()
        self.tess.goto(0,0)
        self.tess.down()
        self.tess.pencolor(old_color)
        self.tess.pensize(old_pen)

    def calculate_legende_size(self, min_map_size):
        self.legend_length = 1.0
        
    def draw_legend(self, color=LEGEND_COLOR):
        self.app_logger.debug('Drawing legend')
        old_pen = self.tess.pensize()
        old_color = self.tess.pencolor()
        self.tess.pensize(SMALL_PEN)
        self.tess.pencolor(color)
        self.tess.up()
        self.tess.goto(-self.map_size_x, self.map_size_y * 0.95)
        self.tess.setheading(0)
        self.tess.down()
        self.tess.forward(self.legend_length)
        self.tess.write("{:.0f} NM".format(self.legend_length), font=("Arial", FONT_SIZE, "normal"), align="left")
        self.tess.up()
        self.tess.goto(0,0)
        self.tess.down()
        self.tess.pencolor(old_color)
        self.tess.pensize(old_pen)
    
    def draw_intercept(self, observation_rank, date_time, azimut, intercept):
        self.app_logger.info('Drawing intercept %.1f NM in Az %.0f°', intercept, azimut)
        old_pen = self.tess.pensize()
        self.tess.pensize(SMALL_PEN)
        old_color = self.tess.pencolor()
        self.tess.pencolor(self.list_of_intercept_color[(observation_rank-1) % len(self.list_of_intercept_color)])

        self.tess.up()
        self.tess.goto(0,0)
        self.tess.down()
        self.tess.setheading(90.0 - azimut)
        self.tess.forward(intercept)
        self.tess.left(90)
        self.tess.pensize(BIG_PEN)
        intercept_length = max(self.map_size_x, self.map_size_y)
        self.tess.forward(intercept_length)
        self.tess.backward(2.0 * intercept_length)

        self.tess.up()
        self.tess.goto(-self.map_size_x, self.map_size_y * (1.0 - (observation_rank+1)*0.05)) 
        self.tess.setheading(0)
        self.tess.down()
        date_time_str = date_time.split(" ")[1]
        observation_title = "{} : {:.1f} NM / {:.1f}°".format(date_time_str, intercept, azimut)
        self.tess.write(observation_title, font=("Arial", FONT_SIZE, "normal"), align="left")

        self.tess.pensize(old_pen)
        self.tess.pencolor(old_color)

    def display_hat(self):
        max_intercept = 1.0
        for observation in self.list_of_observations :
            if max_intercept < abs(observation["intercept"]) :
                max_intercept = abs(observation["intercept"])
        min_map_size = max_intercept * RATIO_IMAGE_INTERCEPT
        self.app_logger.debug('min map size = %.1fNM', min_map_size)

        self.calculate_legende_size(min_map_size)
        self.start_turtle(min_map_size)
        for i in range(10):
            pen_size = BIG_PEN if i % 5 == 4 else SMALL_PEN
            self.draw_target_circle(i, pen_size)
        self.draw_last_position(min_map_size / 25.0)    # (min_map_size / 25.0) matches a small square for the estimate point
        observation_rank = 1
        for observation in self.list_of_observations :
            self.draw_intercept(observation_rank, observation["date_time"], observation["azimut"], observation["intercept"])
            observation_rank += 1
        self.draw_legend()
        self.finish_turtle()

    def launch_display_hat(self, app_logger, config_name) :
        self.app_logger = app_logger
        self.load_config(config_name)
        self.display_hat()

def main () :
    my_app = DisplayHat()
    my_app.init_log()
    my_app.load_config("astro")
    my_app.display_hat()

if __name__ == "__main__":
    main()
