# -*- coding: utf-8 -*-
import math
import datetime
import time
import csv
from waypoint import format_angle
'''
to be used with file coming from https://navastro.com/downloads/catalogue.php
'''
EARTH_RADIUS_KM  = 6400.0

def convert_ho249_angle_to_angle(ho249_angle, display_trace=False):
    ho249_angle = ho249_angle.strip(" ")
    ho249_angle = ho249_angle.replace ("  ", " ")
    degree_part = ho249_angle.split(" ")[0]
    minute_part = ho249_angle.split(" ")[1]
    if display_trace:
        print("degree_part = {},  minute_part = {}".format(degree_part, minute_part))
    angle = float(degree_part)+float(minute_part)/60.0
    return angle

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

        self.height_observed = 0.0
        self.height_corrected = 0.0
        self.height_estimated = 0.0
        self.intercept = 0.0
        self.azimut = 0.0

    def extract_ephemerides_from_ho249(self):
        month_name_french = ["", "Jan", "Fev", "Mar", "Avr", "Mai", "Jun", "Jul", "Aou", "Sep", "Oct", "Nov", "Dec"] 
        ho249_file_name = "Ephemerides {}.txt".format(self.date_time.year)
        date_target = "{:4d} {} {:2d}".format (self.date_time.year, month_name_french[self.date_time.month].upper(), self.date_time.day)
        ho249_results = dict()
        with open(ho249_file_name, encoding="ansi") as ho249_file:
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
                    decl = decl_sign * convert_ho249_angle_to_angle(decl_raw.strip(" "))
                    ho249_results.update({"decl":decl})
 
                    decl_var = float(list_of_fields[6].strip(" "))
                    sign_decl_bool = (decl>0) * (decl_var>0) 
                    if not sign_decl_bool:
                        decl_var *= -1.0 
                    ho249_results.update({"decl_var":decl_var})
                    
                    self.app_logger.debug ('At %s 00:00:00 : decl = %s (var %s\'),  ahv0 = %s(var %s°)', 
                                          date_target, 
                                          format_angle(decl), decl_var,
                                          format_angle(ahv0, value_is_longitude=True)[:-1], ahv0_var) 
                    
                    return ho249_results
                # else:
                #     self.app_logger.debug('skipping entry for "%s"', list_of_fields[1]) 
        self.app_logger.warning('Can\'t find any entry for "%s" in file "%s"', date_target, ho249_file_name) 
        return None
    
    def calculate_nb_utc_hour_since_midnight(self):
        now = self.date_time
        nb_local_hour_since_midnight = now.hour + now.minute/60.0 + now.second/3600.0 
        utc_offset_hour = time.timezone/3600.0
        utc_offset_hour -= time.localtime().tm_isdst
        self.app_logger.debug ('utc_offset_hour = %d hours', utc_offset_hour)
        nb_utc_hour_since_midnight = nb_local_hour_since_midnight + utc_offset_hour
        self.app_logger.debug ('utc_time = %.5f hours', nb_utc_hour_since_midnight)
        return nb_utc_hour_since_midnight
        
    def calculate_decl_from_ho249(self, ho249_results, nb_utc_hour_since_midnight):
        time_target = self.date_time.strftime("%H:%M:%S")
        self.decl = ho249_results["decl"] + (ho249_results["decl_var"] * nb_utc_hour_since_midnight) / 60.0 
        self.app_logger.info ('at %s decl = %s ', time_target, format_angle(self.decl)) 

    def calculate_ahv0_from_ho249(self, ho249_results, nb_utc_hour_since_midnight):
        time_target = self.date_time.strftime("%H:%M:%S")
        self.ahv0= ho249_results["ahv0"] + ho249_results["ahv0_var"] * nb_utc_hour_since_midnight 
        self.app_logger.info ('At %s ahv0 = %s ', time_target, format_angle(self.ahv0, value_is_longitude=True)[:-1]) 

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
        self.app_logger.debug("for eye height : %.0f m, eye height correction = %.1f'", float(self.eye_height), float(self.eye_height_correction_minute))

    def fixe_angle_function_of_half_lumb(self):
        self.sun_half_lumb_minute = 13.0

    def calculate_he_and_az(self, height_observed):
        self.height_observed = height_observed
        ho249_results = self.extract_ephemerides_from_ho249()
        if ho249_results:
            nb_utc_hour_sdince_midnight = self.calculate_nb_utc_hour_since_midnight()
            self.calculate_decl_from_ho249(ho249_results, nb_utc_hour_sdince_midnight)
            self.calculate_ahv0_from_ho249(ho249_results, nb_utc_hour_sdince_midnight)
            self.load_athmospheric_refraction_minute_from_file()
            self.calculate_athmospheric_refraction_minute()
            self.calculate_horizon_dip_function_of_eye_height()
            self.fixe_angle_function_of_half_lumb()
            self.height_corrected = self.height_observed + (self.sun_half_lumb_minute - self.athmospheric_refraction_minute - self.eye_height_correction_minute) / 60.0
    
            self.height_estimated = 0.0
            self.azimut = 0.0
    
            self.intercept = (self.height_estimated - self.height_corrected) * 60.0 

