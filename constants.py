# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 00:25:41 2022

@author: jef
"""
import platform

VERSION = "V3.1"

LOG_DIRECTORY = "log"
DEFAULT_LOG_LEVEL = "DEBUG"
DATE_SERIAL_FORMATTER = "%d-%m-%Y %H:%M:%S"
DATE_DISPLAY_FORMATTER = "%d/%m/%Y %H:%M:%S"

DEFAULT_LATITUDE = "N45°16.1'"
DEFAULT_LONGITUDE = "E005°52.3'"
DEFAULT_SPEED = 5.0
DEFAULT_COURSE = 0.0
DEFAULT_EYE_HEIGHT = 2.0

def get_os():
    '''
    return the operating system

    Returns
    -------
    str
        the name of the operating system.

    '''
    if platform.system().lower() ==  "windows" :
        return "windows"
    if platform.system().lower() == "linux":
        try :
            platform.system().fredesktop_os_release()
        except:
            return "android"
    return "linux"
