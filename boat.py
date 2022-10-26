# -*- coding: utf-8 -*-
import datetime

class Boat:
    def __init__(self, last_waypoint, last_waypoint_datetime, speed, course, eye_height, app_logger = None):
        self.last_waypoint = last_waypoint
        self.last_waypoint_datetime = last_waypoint_datetime
        self.course = course
        self.speed = speed
        self.eye_height = eye_height
        self.app_logger = app_logger

    def set_new_position(self, new_waypoint, new_waypoint_datetime):
        self.last_waypoint = new_waypoint
        self.last_waypoint_datetime = new_waypoint_datetime

    def set_course_and_speed(self, course, speed):
        self.course = course
        self.speed = speed

    def format_last_position(self):
        return self.last_waypoint

    def get_position_at(self, observation_dt):
        elapsed_time = observation_dt - self.last_waypoint_datetime
        nb_second_since_last_pos = elapsed_time.total_seconds()
        distance = self.speed * nb_second_since_last_pos / 3600
        self.app_logger.debug ("%.1f NM since last position at %.1f Knots - course %.0f°", distance, self.speed, self.course)
        return self.last_waypoint.move_to(self.course, distance, "estimated")

    def format_current_position(self):
        now = datetime.datetime.now()
        elapsed_time = now - self.last_waypoint_datetime
        nb_second_since_last_pos = elapsed_time.total_seconds()
        distance = self.speed * nb_second_since_last_pos / 3600
        self.app_logger.debug ("%.1f NM since last position at %.1f Knots - course %.0f°", distance, self.speed, self.course)
        return self.last_waypoint.move_to(self.course, distance, "estimated")

    def __repr__(self):
        result = "at {} position {}".format(self.last_waypoint_datetime, self.last_waypoint)
        return result
