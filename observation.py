# -*- coding: utf-8 -*-
'''
to be used with file coming from https://navastro.com/downloads/catalogue.php
'''
import math
import time
import csv
import constants
from waypoint import format_angle
from waypoint import INPUT_TYPE_DECL, INPUT_TYPE_AHV, INPUT_TYPE_HEIGHT, INPUT_TYPE_AZIMUT
EARTH_RADIUS_KM  = 6366.0

def convert_ho249_angle_to_angle(ho249_angle, display_trace=False):
    ho249_angle = ho249_angle.strip(" ")
    ho249_angle = ho249_angle.replace ("  ", " ")
    degree_part = ho249_angle.split(" ")[0]
    minute_part = ho249_angle.split(" ")[1]
    if display_trace:
        print("degree_part = {},  minute_part = {}".format(degree_part, minute_part))
    angle = float(degree_part)+float(minute_part)/60.0
    return angle

def radian2degree (angle_radian):
    return angle_radian * 180.0 / math.pi

def degree2radian (angle_degree):
    return angle_degree * math.pi / 180.0

def sign_of (value):
    return 1 if value > 0 else -1

RESULT_WARNING_TEXT = "!!! "
RESULT_HEADER_TEXT = "==> "
RESULT_TEXT_TEXT = "    "
class Observation:
    '''
    class for start calculation, all angles are extressed in degre, minuts
    '''
    def __init__(self, date_time, position, eye_height, app_logger = None):
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
        self.ahvg = 0.0

        self.height_observed = 0.0
        self.height_corrected = 0.0
        self.height_estimated = 0.0
        self.intercept = 0.0
        self.azimut = 0.0
        self.result = ""
        
    def result_warning_append(self, result_line):
        self.result += "{}{}\n".format(RESULT_WARNING_TEXT, result_line)

    def result_header_append(self, result_line):
        self.result += "{}{}\n".format(RESULT_HEADER_TEXT, result_line)

    def result_text_append(self, result_line):
        self.result += "{}{}\n".format(RESULT_TEXT_TEXT, result_line)

    def extract_ephemerides_from_ho249(self):
        month_name_french = ["", "Jan", "Fev", "Mar", "Avr", "Mai", "Jun", "Jul", "Aou", "Sep", "Oct", "Nov", "Dec"]
        ho249_file_name = "Ephemerides {}.txt".format(self.date_time.year)
        date_target = "{:4d} {} {:2d}".format (self.date_time.year, month_name_french[self.date_time.month].upper(), self.date_time.day)
        ho249_results = dict()
        with open(ho249_file_name, encoding="cp1256") as ho249_file:
            for line in ho249_file.readlines():
                list_of_fields = line.split("|")
                if len(list_of_fields) < 10 :
                    continue
                if list_of_fields[1].upper().strip(" ") == date_target:
                    ahv0 = convert_ho249_angle_to_angle(list_of_fields[3])
                    ho249_results.update({"ahv0":ahv0})

                    ahv0_var = float(list_of_fields[4].strip(" "))
                    ho249_results.update({"ahv0_var":ahv0_var})

                    decl_raw = list_of_fields[5]
                    decl_sign = -1.0 if "S" in decl_raw else 1.0
                    decl_raw = decl_raw.replace("S", "").replace("N", "")
                    decl = decl_sign * convert_ho249_angle_to_angle(decl_raw)
                    ho249_results.update({"decl":decl})

                    decl_var = float(list_of_fields[6].strip(" "))
                    sign_decl_bool = (decl>0) * (decl_var>0)
                    if not sign_decl_bool:
                        decl_var *= -1.0
                    ho249_results.update({"decl_var":decl_var})
                    self.result_header_append ('at {} 00:00:00'.format(date_target))
                    self.result_text_append ('decl = {} (var {})'.format(format_angle(decl, INPUT_TYPE_DECL), decl_var))
                    self.result_text_append ('ahv0 = {} (var {})'.format(format_angle(ahv0, INPUT_TYPE_DECL), ahv0_var))
                    self.app_logger.debug ('at %s 00:00:00 : decl = %s (var %s\'),  ahv0 = %s(var %s°)',
                                          date_target,
                                          format_angle(decl, INPUT_TYPE_DECL), decl_var,
                                          format_angle(ahv0, INPUT_TYPE_AHV), ahv0_var)
                    return ho249_results
                # else:
                #     self.app_logger.debug('skipping entry for "%s"', list_of_fields[1])
        self.result_warning_append ('Can\'t find any entry for "{}" in file "{}"'.format(date_target, ho249_file_name))
        self.app_logger.warning('Can\'t find any entry for "%s" in file "%s"', date_target, ho249_file_name)
        return None

    def calculate_nb_utc_hour_since_midnight(self):
        nb_local_hour_since_midnight = self.date_time.hour + self.date_time.minute/60.0 + self.date_time.second/3600.0
        utc_offset_hour = time.timezone/3600.0
        utc_offset_hour -= time.localtime().tm_isdst
        self.result_header_append ('at {}'.format(self.date_time.strftime(constants.DATE_DISPLAY_FORMATTER)))
        self.app_logger.debug ('utc_offset_hour = %d hours', utc_offset_hour)
        self.result_text_append ('utc_offset_hour = {} hours'.format(utc_offset_hour))
        nb_utc_hour_since_midnight = nb_local_hour_since_midnight + utc_offset_hour
        self.app_logger.debug ('utc_time = %.5f hours', nb_utc_hour_since_midnight)
        return nb_utc_hour_since_midnight

    def calculate_decl_from_ho249(self, ho249_results, nb_utc_hour_since_midnight):
        time_target = self.date_time.strftime("%H:%M:%S")
        self.decl = ho249_results["decl"] + (ho249_results["decl_var"] * nb_utc_hour_since_midnight) / 60.0
        self.result_text_append ('decl = ' + format_angle(self.decl, INPUT_TYPE_DECL))
        self.app_logger.info ('at %s decl = %s', time_target, format_angle(self.decl, INPUT_TYPE_DECL))

    def calculate_ahv0_from_ho249(self, ho249_results, nb_utc_hour_since_midnight):
        time_target = self.date_time.strftime("%H:%M:%S")
        self.ahv0 = ho249_results["ahv0"] + ho249_results["ahv0_var"] * nb_utc_hour_since_midnight
        while self.ahv0 > 360.0:
            self.ahv0 -= 360.0
        self.ahvg = self.ahv0 + self.position.longitude
        while self.ahvg > 360.0 :
            self.ahvg -= 360.0
        self.result_text_append ('ahv0 = {}, ahvg = {}'.format(
            format_angle(self.ahv0, INPUT_TYPE_AHV), 
            format_angle(self.ahvg, INPUT_TYPE_AHV)))
        self.app_logger.info ('At %s ahv0 = %s, ahvg = %s',
                              time_target,
                              format_angle(self.ahv0, INPUT_TYPE_AHV),
                              format_angle(self.ahvg, INPUT_TYPE_AHV))

    def calculate_athmospheric_refraction_minute_by_tan(self):
        self.athmospheric_refraction_minute = 1.0 / math.tan(degree2radian(self.height_observed))
        self.app_logger.debug("for angle : %.0f°, refraction = %.1f'", float(self.height_observed), float(self.athmospheric_refraction_minute))

    def calculate_horizon_dip_function_of_eye_height(self):
        self.eye_height_correction_minute = 0.0
        self.eye_height_correction_minute = radian2degree(math.sqrt(2.0 * self.eye_height / (EARTH_RADIUS_KM * 1000.0))) * 60.0
        self.app_logger.debug("for eye height : %.0f m, eye height correction = %.1f'", float(self.eye_height), float(self.eye_height_correction_minute))

    def calculate_half_sun_lumb_angle(self):
        self.sun_half_lumb_minute = 16.0
        self.app_logger.debug("half_sun_lumb_angle = %.1f'", float(self.sun_half_lumb_minute))

    def calculate_he(self):
        sin_phi  = math.sin(degree2radian(self.position.latitude))
        sin_decl = math.sin(degree2radian(self.decl))
        cos_phi  = math.cos(degree2radian(self.position.latitude))
        cos_decl = math.cos(degree2radian(self.decl))
        cos_ahvg = math.cos(degree2radian(self.ahvg))
        self.height_estimated = radian2degree(math.asin(sin_phi * sin_decl + cos_phi * cos_decl * cos_ahvg))

        self.app_logger.info("Height estimated : %s ", format_angle(self.height_estimated, INPUT_TYPE_HEIGHT))

    def calculate_az(self):
        sin_ahvg = math.sin(degree2radian(self.ahvg))
        tan_decl = math.tan(degree2radian(self.decl))
        cos_phi  = math.cos(degree2radian(self.position.latitude))
        sin_phi  = math.sin(degree2radian(self.position.latitude))
        cos_ahvg = math.cos(degree2radian(self.ahvg))
        azimut_by_atan = radian2degree(math.atan(sin_ahvg/(tan_decl*cos_phi - sin_phi*cos_ahvg)))

        cos_decl = math.cos(degree2radian(self.decl))
        cos_he   = math.cos(degree2radian(self.height_estimated))
        azimut_by_asin = radian2degree(math.asin(sin_ahvg*cos_decl/cos_he))
        # Magic formula found by jef in 1983 !!!
        self.azimut = 90 * (sign_of(azimut_by_atan) + sign_of(azimut_by_asin) +2 ) - azimut_by_atan
        self.app_logger.debug("Azimut by asin : %s ", format_angle(azimut_by_asin, INPUT_TYPE_AZIMUT))
        self.app_logger.debug("Azimut by atan : %s ", format_angle(azimut_by_atan, INPUT_TYPE_AZIMUT))
        self.app_logger.info("Azimut : %s ", format_angle(self.azimut, INPUT_TYPE_AZIMUT))

    def calculate_he_and_az(self, height_observed):
        self.height_observed = height_observed
        ho249_results = self.extract_ephemerides_from_ho249()
        if ho249_results:
            nb_utc_hour_sdince_midnight = self.calculate_nb_utc_hour_since_midnight()
            self.calculate_decl_from_ho249(ho249_results, nb_utc_hour_sdince_midnight)
            self.calculate_ahv0_from_ho249(ho249_results, nb_utc_hour_sdince_midnight)
            self.calculate_athmospheric_refraction_minute_by_tan()
            self.calculate_horizon_dip_function_of_eye_height()
            self.calculate_half_sun_lumb_angle()
            self.height_corrected = self.height_observed + (self.sun_half_lumb_minute - self.athmospheric_refraction_minute - self.eye_height_correction_minute) / 60.0
            self.app_logger.info("Sextant height observed %s - corrected : %s ", 
                                 format_angle(self.height_observed, INPUT_TYPE_HEIGHT),
                                 format_angle(self.height_corrected, INPUT_TYPE_HEIGHT))

            self.calculate_he()
            self.calculate_az()

            self.intercept = (self.height_corrected - self.height_estimated) * 60.0
            self.app_logger.info("Intercept : %.1f NM", self.intercept )
        