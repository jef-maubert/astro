# -*- coding: utf-8 -*-
import math
import datetime
import csv

EARTH_RADIUS_KM  = 6400.0

class Observation:
    '''
    class for start calculation, all angles are extressed in degre, minuts
    '''
    def __init__(self, date_time, position, eye_height = 2, app_logger = None):
        self.date_time = date_time
        self.position = position
        self.eye_height = eye_height
        self.app_logger = app_logger
        self.list_of_athmospheric_refraction_minute = []
        self.athmospheric_refraction_minute = 0.0
        self.eye_height_correction_minute = 0.0
        self.sun_half_lumb_minute = 13.0
        self.decl = 0.0
        self.ahv0 = 0.0

        self.height_observed = 0.0
        self.height_corrected = 0.0
        self.height_estimated = 0.0
        self.intercept = 0.0
        self.azimut = 0.0

    def load_ho_249(self):
        return

    def calculate_decl_from_ho249(self):
        self.decl = 40.0

    def calculate_ahv0_from_ho249(self):
        self.ahv0 = 180.0

    def load_athmospheric_refraction_minute_from_file(self):
        with open('atmospheric_refraction.csv', encoding="utf8") as atmospheric_refraction_file:
            dialect = csv.Sniffer().sniff(atmospheric_refraction_file.read(1024))
            atmospheric_refraction_file.seek(0)

            csv_reader = csv.DictReader(atmospheric_refraction_file, dialect=dialect)
            list_of_fields = next(csv_reader)
            # for field in list_of_fields:
            #     self.app_logger.debug('found field :"%s"',field)
            for line in csv_reader:
                self.list_of_athmospheric_refraction_minute.append({"angle":float(line["angle"]), "refraction":float(line["refraction"])})
        return

    def calculate_athmospheric_refraction_minute(self):
        gap_to_exact_value = 999.9
        self.athmospheric_refraction_minute = 0.0
        for athmospheric_refraction_minute in self.list_of_athmospheric_refraction_minute:
            if gap_to_exact_value > abs(self.height_observed - athmospheric_refraction_minute['angle']):
                gap_to_exact_value = abs(self.height_observed - athmospheric_refraction_minute['angle'])
                self.athmospheric_refraction_minute = athmospheric_refraction_minute['refraction']
        self.app_logger.debug("for angle : %.0f°, refraction = %.1f'", float(self.height_observed), float(self.athmospheric_refraction_minute))

    def calculate_horizon_dip_function_of_eye_height(self):
        self.eye_height_correction_minute = 0.0
        self.eye_height_correction_minute = math.sqrt(2.0 * self.eye_height / (EARTH_RADIUS_KM * 1000.0)) * 180.0 * 60.0 / math.pi 
        self.app_logger.debug("for eye height : %.0fm, eye height correction = %.1f'", float(self.eye_height), float(self.eye_height_correction_minute))

    def fixe_angle_function_of_half_lumb(self):
        self.sun_half_lumb_minute = 13.0

    def calculate_he_and_az(self, height_observed):
        self.height_observed = height_observed
        self.calculate_decl_from_ho249()
        self.calculate_ahv0_from_ho249()
        self.load_athmospheric_refraction_minute_from_file()
        self.calculate_athmospheric_refraction_minute()
        self.calculate_horizon_dip_function_of_eye_height()
        self.fixe_angle_function_of_half_lumb()
        self.height_corrected = self.height_observed + (self.sun_half_lumb_minute - self.athmospheric_refraction_minute - self.eye_height_correction_minute) / 60.0

        self.height_estimated = 0.0
        self.azimut = 0.0

        self.intercept = (self.height_estimated - self.height_corrected) * 60.0 

