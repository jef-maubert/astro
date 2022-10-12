# -*- coding: utf-8 -*-
import math

DDD_FORMAT = 0
DMM_FORMAT = 1
DMS_FORMAT = 2

NAUTICAL_MILLE = 1852.0
DEFAULT_SPEED = 5

def format_time(duration):
    nb_days = int(duration/24)
    nb_hours = int(duration - nb_days*24)
    return  "{}d {}Hr".format(nb_days, nb_hours)

def azimut_to_trigo(azimut):
    trigo_degree = 90 - azimut
    if trigo_degree < 0:
        trigo_degree = trigo_degree + 360
    trigo_radian = (trigo_degree * math.pi / 180.0)
    return trigo_radian

def scan_degree(angle_input, verbose=False):
    angle_as_string = angle_input.upper().replace(" ", "")

    #Define the sence
    value_is_negatif = False

    if 'W' in angle_as_string:
        value_is_negatif = True
    if 'S' in angle_as_string:
        value_is_negatif = True

    for cardinale in ("N", "S", "E", "W"):
        angle_as_string = angle_as_string.replace(cardinale, "")

    full_degree = angle_as_string.split("°")[0].replace(",",".")
    part_degree = angle_as_string.split("°")[1].replace(",",".")

    #if value is expressed as ° ' "
    decimal_of_angle = 0.0
    if '"' in part_degree:
        minutes_of_angle = float(part_degree.split("'")[0])
        second_of_angle = float(part_degree.split("'")[1].split('"')[0])
        decimal_of_angle = minutes_of_angle/60 +  second_of_angle/3600

    #if value is expressed as ° '
    elif "'" in part_degree:
        minutes_of_angle = float(part_degree.split("'")[0])
        decimal_of_angle = minutes_of_angle/60

    #if value is expressed as °
    else:
        decimal_of_angle = 0.0

    value_as_float = float(full_degree) + decimal_of_angle
    if value_is_negatif:
        value_as_float = -value_as_float

    if  verbose:
        print('float of ({}) = {:9.5f}'.format(angle_input, value_as_float))
    return value_as_float

def format_angle(angle_value, output_format=DMM_FORMAT, value_is_longitude=False):
    if value_is_longitude:
        cardinal_letter = "E" if angle_value>=0 else "W"
    else:
        cardinal_letter = "N" if angle_value>=0 else "S"
    angle_value = abs(angle_value)

    angle_formatted = ""
    if output_format == DDD_FORMAT:
        if value_is_longitude:
            angle_formatted= "{:09.5f}°{}".format(angle_value, cardinal_letter)
        else:
            angle_formatted= "{:08.5f}°{}".format(angle_value, cardinal_letter)

    if output_format == DMM_FORMAT:
        decimal_part, integer_part = math.modf(angle_value)
        decimal_part = decimal_part*60.0
        integer_part = int(integer_part)
        if value_is_longitude:
            angle_formatted= "{:03d}°{:04.1f}'{}".format(integer_part, decimal_part, cardinal_letter)
        else:
            angle_formatted= "{:02d}°{:04.1f}'{}".format(integer_part, decimal_part, cardinal_letter)

    return angle_formatted

class Waypoint:
    def __init__(self, name, latitude, longitude, speed = DEFAULT_SPEED):
        self.name =name
        self.latitude = scan_degree(latitude)
        self.longitude = scan_degree(longitude)
        self.speed = speed

    def __repr__(self):
        result = "{} : ({} , {})".format(self.name,
            format_angle(self.latitude, output_format=DMM_FORMAT, value_is_longitude=False),
            format_angle(self.longitude, output_format=DMM_FORMAT, value_is_longitude=True))
        return result

    def __repr0__(self):
        result = "{}; {}; {}".format(self.name,
            format_angle(self.latitude, output_format=DMM_FORMAT, value_is_longitude=False),
            format_angle(self.longitude, output_format=DMM_FORMAT, value_is_longitude=True))
        return result

    def format_latitude(self):
        return format_angle(self.latitude, output_format=DMM_FORMAT, value_is_longitude=False)

    def format_longitude(self):
        return format_angle(self.longitude, output_format=DMM_FORMAT, value_is_longitude=True)

    def display_coord(self):
        result = "{}; {}".format(
            format_angle(self.latitude, output_format=DMM_FORMAT, value_is_longitude=False),
            format_angle(self.longitude, output_format=DMM_FORMAT, value_is_longitude=True))
        return result

    def get_coord(self):
        return ([self.latitude, self.longitude])

    def distance_to(self, waypoint_2):
        mean_phi = (waypoint_2.latitude + self.latitude)/2
        delta_phi = waypoint_2.latitude - self.latitude
        delta_g = waypoint_2.longitude - self.longitude
        dist_phi = delta_phi * 60
        dist_g = delta_g * 60 * math.cos(mean_phi * math.pi / 180.0)
        return math.sqrt(dist_phi*dist_phi + dist_g*dist_g)

    def azimut_to(self, waypoint_2):
        mean_phi = (waypoint_2.latitude + self.latitude)/2
        delta_phi = waypoint_2.latitude - self.latitude
        delta_g = waypoint_2.longitude - self.longitude
        dist_phi = delta_phi * 60
        dist_g = delta_g * 60 * math.cos(mean_phi * math.pi / 180.0)
        dist_total = math.sqrt(dist_phi*dist_phi + dist_g*dist_g)
        try:
            ratio = dist_g / dist_phi
            azimut = math.atan(ratio) * 180.0 /math.pi
        except ZeroDivisionError:
            azimut = 90.0
        if azimut <= 0:
            azimut += 180.0
        if delta_g < 0:
            azimut += 180.0
        return dist_total, azimut

    def move_to(self, azimut, distance, name="moved"):
        trigo_angle = azimut_to_trigo (azimut)
        distance_x = distance * math.cos(trigo_angle)
        distance_y = distance * math.sin(trigo_angle)
        delta_phi = distance_y / 60.0
        new_latitude = self.latitude + delta_phi
        mean_latitude = (self.latitude + new_latitude) / 2.0
        delta_g = distance_x / 60.0 / math.cos(mean_latitude * math.pi / 180.0)

        new_longitude = self.longitude + delta_g
        return Waypoint(name,
                        format_angle(new_latitude, output_format=DMM_FORMAT, value_is_longitude=False),
                        format_angle(new_longitude, output_format=DMM_FORMAT, value_is_longitude=True))
