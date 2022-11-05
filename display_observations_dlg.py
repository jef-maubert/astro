# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 21:35:57 2022

canvas tutiorial : http://pascal.ortiz.free.fr/contents/tkinter/tkinter/le_canevas.html

@author: jef
"""

import math
import tkinter as tk
from waypoint import format_angle, INPUT_TYPE_AZIMUT
import constants


BIG_PEN = 2
SMALL_PEN = 1

LEGEND_COLOR = "black"
LAST_POSITION_COLOR = "black"
TARGET_COLOR = "lightgrey"
RATIO_IMAGE_INTERCEPT = 3

DEF_SCREEN_SIZE_X = 900
DEF_SCREEN_SIZE_Y = 900
if constants.get_os() == "android":
    FONT = "Arial 6"
    CLOSE_BUTTON_HEIGHT = 100
else:
    FONT = "Arial 10"
    CLOSE_BUTTON_HEIGHT = 50


def degree2radian (angle_degree):
    return angle_degree * math.pi / 180.0

class DisplayObservationsDlg(tk.Toplevel):

    def __init__(self, astro_view, title, my_boat, list_of_observations):
        self.astro_view = astro_view
        self.app_logger = self.astro_view.app_logger
        self.my_boat = my_boat

        tk.Toplevel.__init__(self, astro_view)
        self.transient(astro_view)

        if title:
            self.title(title)
        self.list_of_observations = list_of_observations
        self.min_map_size = 20.0
        self.legend_x = -self.min_map_size 
        self.legend_y = -self.min_map_size 
        self.zoom_factor = 1.0
        self.scale_length = 1.0
        self.map_size_x = self.min_map_size
        self.map_size_y = self.min_map_size
        self.screen_width = DEF_SCREEN_SIZE_X
        self.screen_height = DEF_SCREEN_SIZE_Y
        self.list_of_intercept_color = ["blue", "orange", "green", "red", "violet"]

        dlg_body = tk.Frame(self)
        
        self.calculate_map_size()
        self.calculate_screen_size()

        self.create_dlg_body(dlg_body)
        self.display_hat_by_canvas()
        dlg_body.pack(padx=5, pady=5)
        self.add_close_buttons()

        self.drawing_canvas.scale("all", 0, 0, self.zoom_factor, self.zoom_factor)

        self.grab_set()
        self.wait_window(self)

    def calculate_map_size(self):
        max_intercept = 1.0
        for observation in self.list_of_observations :
            if max_intercept < abs(observation["intercept"]) :
                max_intercept = abs(observation["intercept"])
        self.min_map_size = max_intercept * RATIO_IMAGE_INTERCEPT
        self.app_logger.debug('min map size = %.1fNM', self.min_map_size)
        
    def calculate_screen_size(self):
        self.screen_width = self.astro_view.winfo_screenwidth()
        self.screen_height = self.astro_view.winfo_screenheight()
        self.app_logger.debug("screen width = %d, screen height = %d", self.screen_width,  self.screen_height)
        ratio_x_y = float(self.screen_width) / float(self.screen_height)
        if ratio_x_y >1:
            self.map_size_x = self.min_map_size * ratio_x_y
            self.map_size_y =self.min_map_size
        else:
            self.map_size_x = self.min_map_size
            self.map_size_y = self.min_map_size / ratio_x_y
        self.app_logger.debug('map size %.1f NM * %.1f NM', self.map_size_x , self.map_size_y)
        self.legend_x = -self.map_size_x * 0.95
        self.legend_y = -self.map_size_y * 0.90
        self.zoom_factor = self.screen_width / (2.0*self.map_size_x)
        
    def create_dlg_body(self, master):
        self.attributes("-fullscreen", True)
        width = self.screen_width
        height = self.screen_height - CLOSE_BUTTON_HEIGHT
        # self.drawing_canvas = tk.Canvas(master, scrollregion =(-self.screen_width/2, -self.screen_height/2, self.screen_width/2, self.screen_height/2),
        #                                 width = self.screen_width, height = self.screen_height - CLOSE_BUTTON_HEIGHT)
        self.drawing_canvas = tk.Canvas(master, scrollregion =(-width/2, -height/2, width/2, height/2),
                                        width = width, height = height)
        self.drawing_canvas.pack(side=tk.LEFT)

    def add_close_buttons(self):
        box = tk.Frame(self)
        close_button = tk.Button(box, text="Close", width=10, command=self.on_close_button)
        close_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Escape>", self.on_close_button)
        box.pack()

    def on_close_button(self, event=None):
        # put focus back to the astro_view window
        self.astro_view.focus_set()
        self.destroy()

    def draw_last_position(self, square_size):
        self.drawing_canvas.create_rectangle((-square_size/2, -square_size/2, square_size/2, square_size/2),
                                             outline = LAST_POSITION_COLOR, width = SMALL_PEN)
        self.drawing_canvas.create_rectangle((0, 0, 0, 0),
                                             outline = LAST_POSITION_COLOR, width = SMALL_PEN)
        last_position_time_str = self.my_boat.last_waypoint_datetime.strftime(constants.DATE_DISPLAY_FORMATTER.split(" ")[1])
        text_pos = (square_size, -square_size)
        self.drawing_canvas.create_text(text_pos, anchor=tk.W, text=last_position_time_str, font=FONT)

    def draw_scale(self):
        # TODO : could dependf on "self.min_map_size"
        # self.scale_length = int(self.min_map_size / 10)
        self.scale_length = 1.0
        start_scale_point = (self.legend_x, self.legend_y)
        end_scale_point = (self.legend_x + self.scale_length, self.legend_y)
        self.drawing_canvas.create_line(start_scale_point, end_scale_point, width = SMALL_PEN, fill = LEGEND_COLOR)

        scale_text = " {:.0f} NM".format(self.scale_length)
        self.drawing_canvas.create_text(end_scale_point, anchor=tk.W, text=scale_text, font=FONT)
        self.legend_y += 1.0

    def draw_intercept(self, observation_rank, date_time, azimut, intercept, verbose = False):
        if verbose:
            self.app_logger.info('Drawing intercept %.1f NM in Az %03.0f°', intercept, azimut)
        pen_color = self.list_of_intercept_color[(observation_rank-1) % len(self.list_of_intercept_color)]
        angle = degree2radian(azimut - 90.0)
        center = (0,0)
        ending_point = (intercept * math.cos(angle),intercept * math.sin(angle))
        self.drawing_canvas.create_line(center, ending_point, fill=pen_color, width=SMALL_PEN)

        line_length = 10 * self.min_map_size
        start_point = ending_point
        angle = degree2radian(azimut)
        ending_point = (line_length * math.cos(angle),line_length * math.sin(angle))
        self.drawing_canvas.create_line(start_point, ending_point, fill=pen_color, width=BIG_PEN)
        ending_point = (-line_length* math.cos(angle),-line_length* math.sin(angle))
        self.drawing_canvas.create_line(start_point, ending_point, fill=pen_color, width=BIG_PEN)

        date_time_str = date_time.split(" ")[1]
        observation_title = "{} : {:.1f} NM / {:03.0f}°".format(date_time_str, intercept, azimut)
        legend_point = (self.legend_x, self.legend_y)
        self.drawing_canvas.create_text(legend_point, anchor=tk.W, text=observation_title, font=FONT, fill=pen_color)
        self.legend_y += 1

    def calculate_intersection (self, list_of_observations, app_logger):
        self.app_logger = app_logger
        self.list_of_observations = list_of_observations
        # Calculate linear_equation
        for observation in self.list_of_observations :
            azimut = degree2radian(observation["azimut"])
            lin_eq_a = -math.tan(azimut)
            lin_eq_b = observation["intercept"] / math.cos(azimut)
            observation.update({"lin_eq_a": lin_eq_a})
            observation.update({"lin_eq_b": lin_eq_b})
            self.app_logger.debug('linear equation of observation %s : y = %f * x + %f ', observation["date_time"], observation["lin_eq_a"], observation["lin_eq_b"])

        # calculate intersection points (x,y)
        observation_index = 0
        nb_observations = len(self.list_of_observations)
        sum_cross_point_x = 0.0
        sum_cross_point_y = 0.0
        for observation_index in range (nb_observations):
            observation_1 = self.list_of_observations[observation_index]
            observation_2 = self.list_of_observations[(observation_index+1) % nb_observations]
            #self.app_logger.debug('calculate intersection of observations %s and %s', observation_1["date_time"], observation_2["date_time"])
            line_1_a = observation_1["lin_eq_a"]
            line_1_b = observation_1["lin_eq_b"]
            line_2_a = observation_2["lin_eq_a"]
            line_2_b = observation_2["lin_eq_b"]

            cross_point_x = (line_2_b-line_1_b) / (line_1_a - line_2_a)
            cross_point_y = (line_1_a * line_2_b -line_1_b * line_2_a) / (line_1_a - line_2_a)
            sum_cross_point_x += cross_point_x
            sum_cross_point_y += cross_point_y
        cross_point_x = sum_cross_point_x / nb_observations
        cross_point_y = sum_cross_point_y / nb_observations

        # calculate suggested fix (distance, azimut)
        azimut = 0.0
        try:
            ratio = cross_point_x / cross_point_y
            azimut = math.atan(ratio) * 180.0 /math.pi
        except ZeroDivisionError:
            azimut = 90.0
        if azimut <= 0:
            azimut += 180.0
        if cross_point_x < 0:
            azimut += 180.0

        suggested_fix = dict()
        suggested_fix.update({"distance" : math.sqrt(cross_point_x * cross_point_x + cross_point_y * cross_point_y)})
        suggested_fix.update({"azimut" : azimut})
        return suggested_fix

    def display_intersection (self, suggested_fix, radius):
        angle = degree2radian(suggested_fix["azimut"]- 90.0)
        distance = suggested_fix["distance"]
        suggested_point = (distance * math.cos(angle), distance * math.sin(angle))
        self.drawing_canvas.create_rectangle(suggested_point, suggested_point, outline = LAST_POSITION_COLOR, width = BIG_PEN)

        bottom_left_x = suggested_point[0]-radius
        bottom_left_y = suggested_point[1]+radius
        upper_right_x = suggested_point[0]+radius
        upper_right_y = suggested_point[1]-radius
        bottom_left = (bottom_left_x, bottom_left_y)
        upper_right = (upper_right_x, upper_right_y)
        self.drawing_canvas.create_oval(bottom_left, upper_right, outline = LAST_POSITION_COLOR, width = BIG_PEN)

        fix_summary = "{:.1f} NM / {}".format(suggested_fix["distance"], format_angle(suggested_fix["azimut"], INPUT_TYPE_AZIMUT))
        self.drawing_canvas.create_text (upper_right, anchor=tk.W, text=fix_summary,
                                         font=FONT, fill=LAST_POSITION_COLOR)

    def display_hat_by_canvas(self):
        for index in range(1,21):
            radius = index * self.scale_length
            pen_size = BIG_PEN if radius % 5 == 0 else SMALL_PEN
            self.drawing_canvas.create_oval((-radius,-radius), (radius, radius), outline=TARGET_COLOR, width = pen_size)
        AZIMUT_SPACE = 10.0
        AZIMUT_LENGTH = 100
        nb_azimut = 360.0 / AZIMUT_SPACE
        center = (0,0)
        for i in range(int(nb_azimut)):
            pen_size = BIG_PEN if i % 3 == 0 else SMALL_PEN
            angle = degree2radian(i * AZIMUT_SPACE - 90)
            ending_point = (AZIMUT_LENGTH * math.cos(angle),AZIMUT_LENGTH * math.sin(angle))
            self.drawing_canvas.create_line(center, ending_point, fill=TARGET_COLOR, width=pen_size)
        self.draw_last_position(self.min_map_size / 25.0)    # (min_map_size / 25.0) matches a small square for the estimate point

        observation_rank = 1
        self.draw_scale()
        for observation in self.list_of_observations :
            self.draw_intercept(observation_rank, observation["date_time"], observation["azimut"], observation["intercept"])
            observation_rank += 1
        suggested_fix = self.calculate_intersection (self.list_of_observations, self.app_logger)
        self.display_intersection (suggested_fix, self.min_map_size / 25.0 / 2)
