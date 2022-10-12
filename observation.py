# -*- coding: utf-8 -*-
import math
import datetime

class Observation:
    '''
    class for start calculation, all angles are extressed in degre, minuts
    '''
    def __init__(self, date_time, position, eye_height = 2, app_logger = None):
        self.date_time = date_time
        self.position = position
        self.eye_height = eye_height
        self.app_logger = app_logger
        self.ho = 0.0
        self.hc = 0.0
        self.he = 0.0
        self.intercept = 0.0
        self.azimut = 0.0

    def load_ho_249(self):
        return

    def calculate_decl_from_ho249(self):
        return
    
    def calculate_ahv0_from_ho249(self):
        return

    def fixe_angle_with_eye_height(self):
        return

    def fixe_angle_with_half_lumb(self):
        return

    def fixe_angle_with_athmosperic_distortion(self):
        return
    
    def calculate_he(self):
        return
    
    def calculate_az(self):
        return
    