# -*- coding: utf-8 -*-
import math
import datetime

class Boat:
    def __init__(self, last_waypoint, last_waypoint_datetime, speed, course, app_logger = None):
        self.last_waypoint = last_waypoint
        self.last_waypoint_datetime = last_waypoint_datetime
        self.course = course
        self.speed = speed
        self.app_logger = app_logger

    def format_last_position(self):
        return self.last_waypoint

    def format_current_position(self):
        now = datetime.datetime.now()
        elapsed_time = now - self.last_waypoint_datetime
        nb_second_since_last_pos = elapsed_time.total_seconds()
        distance = self.speed * nb_second_since_last_pos / 3600
        self.app_logger.debug ("%.1f NM run - course %.0f°", distance, self.course)
        return self.last_waypoint.move_to(self.course, distance, "moved")

    def __repr__(self):
        result = "at {} position {}".format(self.last_waypoint_datetime, self.last_waypoint)
        return result
