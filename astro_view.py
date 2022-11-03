# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 17:34:57 2022

@author: jef
"""
import tkinter as tk
import datetime
import platform

import constants
from waypoint import Waypoint, format_angle
from waypoint import INPUT_TYPE_LATITUDE, INPUT_TYPE_LONGITUDE, INPUT_TYPE_AZIMUT, INPUT_TYPE_HEIGHT
from observation import Observation
from display_hat import DisplayHat
from course_speed_dlg import CourseSpeedDlg
from init_pos_dlg import InitPosDlg
from observation_dlg import ObservationdDlg
from fix_position_dlg import FixPositionDlg
from display_observations_dlg import DisplayObservationsDlg

PADX_STD = 2
PADY_STD = 4

class AstroTk(tk.Tk):

    def __init__(self, parent, data, app_logger):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.data = data
        self.app_logger = app_logger
        self.turtle_already_started = False
        self.initialize()

    def initialize(self):
        self.title("Astro {}".format(constants.VERSION))
        self.grid()
        self.grid_columnconfigure(0, weight=1)

        next_row = 0
        title = tk.Label(self, text="Astro {}".format (constants.VERSION), background="green")
        title.grid(row=next_row, column=0, columnspan=2, padx=PADX_STD, sticky="NSEW")
        self.grid_rowconfigure(next_row, weight=1)

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
        self.btn_modif_last_pos = tk.Button(last_pos_frame, text="Modify", command=self.on_button_init_last_pos)
        self.btn_modif_last_pos.grid(row=0, column=1, rowspan=2, **grid_dict)
        self.grid_rowconfigure(next_row, weight=1)

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
        self.grid_rowconfigure(next_row, weight=1)

        next_row += 1
        current_pos_frame = tk.LabelFrame(self, text="Current position", borderwidth=2, relief=tk.GROOVE)
        current_pos_frame.grid(column=0, row=next_row, **grid_dict)
        current_pos_frame.grid_columnconfigure(0, weight=1)
        current_pos_frame.grid_columnconfigure(1, weight=0)
        self.current_pos_dt = tk.Label(current_pos_frame)
        self.current_pos_dt.grid(row=0, column=0, **grid_dict)
        self.current_pos = tk.Label(current_pos_frame)
        self.current_pos.grid(row=1, column=0, **grid_dict)
        self.btn_refresh_current_pos = tk.Button(current_pos_frame, text="Refresh", command=self.on_button_refresh_pos)
        self.btn_refresh_current_pos.grid(row=0, column=1, rowspan=2, **grid_dict)
        self.grid_rowconfigure(next_row, weight=1)

        next_row += 1
        self.btn_modif_current_pos = tk.Button(self, text="New Observation", command=self.on_button_new_observation)
        self.btn_modif_current_pos.grid(column=0, row=next_row, **grid_dict)
        self.grid_rowconfigure(next_row, weight=4)

        next_row += 1
        self.btn_modif_current_pos = tk.Button(self, text="Display all observations", command=self.on_button_display_all_observations)
        self.btn_modif_current_pos.grid(column=0, row=next_row, **grid_dict)
        self.grid_rowconfigure(next_row, weight=4)

        next_row += 1
        self.btn_modif_current_pos = tk.Button(self, text="Fix position", command=self.on_button_fix_position)
        self.btn_modif_current_pos.grid(column=0, row=next_row, **grid_dict)
        self.grid_rowconfigure(next_row, weight=1)

        next_row += 1
        self.btn_quit = tk.Button(self, text="Quit", command=self.on_button_quit)
        self.btn_quit.grid(column=0, row=next_row, **grid_dict)
        self.grid_rowconfigure(next_row, weight=1)

    def on_button_quit(self):
        self.destroy()

    def on_button_init_last_pos(self):
        my_last_pos_dlg = InitPosDlg(self, "Course and speed",
                                                     self.data.my_boat.last_waypoint_datetime,
                                                     self.data.my_boat.last_waypoint)
        if my_last_pos_dlg.result:
            new_dt_str = my_last_pos_dlg.result[0]
            new_waypoint_dt = datetime.datetime.strptime(new_dt_str, constants.DATE_DISPLAY_FORMATTER)
            new_latitude_str = my_last_pos_dlg.result[1]
            new_longitude_str = my_last_pos_dlg.result[2]
            self.data.my_boat.set_new_position(Waypoint ("last position", new_latitude_str, new_longitude_str), new_waypoint_dt)
            self.update_display()

    def on_button_modif_course_and_speed(self):
        my_course_and_speed_dlg = CourseSpeedDlg(self, "Course and speed",
                                                     self.data.my_boat.last_waypoint_datetime,
                                                     self.data.my_boat.course, self.data.my_boat.speed)
        if my_course_and_speed_dlg.result:
            new_dt_str = my_course_and_speed_dlg.result[0]
            new_waypoint_dt = datetime.datetime.strptime(new_dt_str, constants.DATE_DISPLAY_FORMATTER)
            new_waypoint = self.data.my_boat.get_position_at(new_waypoint_dt)
            new_latitude_str = format_angle(new_waypoint.latitude, input_type = INPUT_TYPE_LATITUDE)
            new_longitude_str = format_angle(new_waypoint.longitude, input_type = INPUT_TYPE_LONGITUDE)
            self.data.my_boat.set_new_position(Waypoint ("last position", new_latitude_str, new_longitude_str), new_waypoint_dt)

            new_course = float(my_course_and_speed_dlg.result[1])
            new_speed = float(my_course_and_speed_dlg.result[2])
            self.data.my_boat.set_course_and_speed(new_course, new_speed)
            self.update_display()

    def on_button_refresh_pos(self):
        self.update_display()

    def on_button_new_observation(self):
        my_observation_dlg = ObservationdDlg(self, "New sun observation")
        if my_observation_dlg.result:
            new_dt_str = my_observation_dlg.result[0]
            observation_dt = datetime.datetime.strptime(new_dt_str, constants.DATE_DISPLAY_FORMATTER)
            self.data.my_boat.eye_height = my_observation_dlg.result[1]

            obs_height = my_observation_dlg.result[2]
            self.app_logger.debug('At %s with eye height = %dm, Height observed = %s', 
                                 observation_dt.strftime(constants.DATE_DISPLAY_FORMATTER), 
                                 self.data.my_boat.eye_height,
                                 format_angle(obs_height, INPUT_TYPE_HEIGHT))
            self.update_display()
            observation_position = self.data.my_boat.get_position_at(observation_dt)
            my_observation = Observation (observation_dt, observation_position, self.data.my_boat.eye_height, app_logger = self.app_logger)
            my_observation.calculate_he_and_az(obs_height)
            result_displayed = my_observation.result + "\nDo you want to save it ?"
            confirm_before_saving = tk.messagebox.askyesno("Result", result_displayed)
            if confirm_before_saving :
                self.data.save_observation_in_config(my_observation)


    def on_button_display_all_observations(self):
        list_of_observations = self.data.load_observations()
        my_display_observations_dlg = DisplayObservationsDlg(self, "All sun observations", self.data.my_boat, list_of_observations)
        return
#TOFIX
#TODO how to launch turtle twice
        turtle_available = True
        if platform.system().lower()  == "windows" :
            turtle_available = True
        elif platform.system().lower()  == "linux":
            try :
                platform.system().fredesktop_os_release()
            except AttributeError:
                turtle_available = False

        if self.turtle_already_started : 
            turtle_available = False

        self.data.load_observations()

        self.turtle_already_started = True 
        if turtle_available:
            my_hat_display = DisplayHat(verbose=False)
            my_hat_display.launch_display_hat(self.app_logger, self.data.app_name)
        else:
            tk.messagebox.showinfo("Info", 'Please quit and launch "display_hat.py"')

    def on_button_fix_position(self):
        my_hat_display = DisplayHat(verbose=False)
        list_of_observations = self.data.load_observations()
        suggested_fix = {"azimut":0.0, "distance":0.0}
        if (len(list_of_observations)):
            suggested_fix = my_hat_display.calculate_intersection (list_of_observations, self.app_logger)
        my_fix_position = FixPositionDlg(self, "Fix position", suggested_fix["azimut"], suggested_fix["distance"]) 
        if my_fix_position.result:
            new_dt_str = my_fix_position.result[0]
            new_waypoint_dt = datetime.datetime.strptime(new_dt_str, constants.DATE_DISPLAY_FORMATTER)
            azimut = my_fix_position.result[1]
            distance = my_fix_position.result[2]
            new_position = self.data.my_boat.last_waypoint.move_to(azimut, distance, "estimated")
    
            new_latitude_str = format_angle(new_position.latitude, input_type = INPUT_TYPE_LATITUDE)
            new_longitude_str = format_angle(new_position.longitude, input_type = INPUT_TYPE_LONGITUDE)
            self.data.my_boat.set_new_position(Waypoint ("last position", new_latitude_str, new_longitude_str), new_waypoint_dt)

            self.data.remove_all_observations()
            self.update_display()

    def update_display(self):
        self.display_last_position()
        self.display_course_and_speed()
        self.display_current_position()

    def display_course_and_speed(self):
        self.course.configure(text="Course : {}".format(format_angle(self.data.my_boat.course, INPUT_TYPE_AZIMUT)))
        self.speed.configure(text="Speed : {:.1f} Knots".format(self.data.my_boat.speed))

    def display_last_position(self):
        last_position_str = "{}   {}".format(format_angle(self.data.my_boat.last_waypoint.latitude, INPUT_TYPE_LATITUDE),
                                           format_angle(self.data.my_boat.last_waypoint.longitude, INPUT_TYPE_LONGITUDE))
        self.last_pos.configure(text=last_position_str)
        self.last_pos_dt.configure(text=self.data.my_boat.last_waypoint_datetime.strftime(constants.DATE_DISPLAY_FORMATTER))

    def display_current_position(self):
        now = datetime.datetime.now()
        now_string = now.strftime(constants.DATE_DISPLAY_FORMATTER)
        self.current_pos_dt.configure(text=now_string)
        current_position_wp = self.data.my_boat.format_current_position()
        current_position_str = "{}   {}".format(format_angle(current_position_wp.latitude, INPUT_TYPE_LATITUDE),
                                           format_angle(current_position_wp.longitude, INPUT_TYPE_LONGITUDE))
        self.current_pos.configure(text=current_position_str)
