# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 17:34:57 2022

@author: jef
"""
import os
import logging
import logging.handlers

import constants
from astro_data import AstroData
from astro_view import AstroTk

NB_ROTATING_LOG = 3
MESSAGE_FORMAT_FILE = '{asctime:s} - {levelname} - {filename:s} - {funcName:s}-{lineno:d} - {message:s}'
MESSAGE_FORMAT_CONSOLE_KK = '{levelname} - {message:s}'
MESSAGE_FORMAT_CONSOLE = '{levelname}{message:s}'

def init_log(app_name):
    log_filename = os.path.join(constants.LOG_DIRECTORY, app_name + ".log")
    app_logger = logging.getLogger(app_name)
    logging.basicConfig(level=logging.DEBUG)
    app_logger.propagate = False
    if app_logger.hasHandlers():
        app_logger.handlers.clear()

    file_log_format = logging.Formatter(fmt=MESSAGE_FORMAT_FILE, datefmt='%d %H:%M:%S', style="{")
    file_log_handler = logging.handlers.RotatingFileHandler(log_filename, mode="a", maxBytes=100000, backupCount=NB_ROTATING_LOG,)
    file_log_handler.setLevel("DEBUG")
    file_log_handler.setFormatter(file_log_format)
    app_logger.addHandler(file_log_handler)

    console_log_format = logging.Formatter(fmt=MESSAGE_FORMAT_CONSOLE, datefmt='%d %H:%M:%S', style="{")
    console_log_handler = logging.StreamHandler()
    console_log_handler.setLevel(constants.DEFAULT_LOG_LEVEL)
    logging.addLevelName(logging.DEBUG, "- ")
    logging.addLevelName(logging.INFO, "")
    logging.addLevelName(logging.WARNING, "!!! ")
    console_log_handler.setFormatter(console_log_format)
    app_logger.addHandler(console_log_handler)
    app_logger.info('Starting %s version %s', app_name, constants.VERSION)
    return app_logger, console_log_handler

def main () :
    os.makedirs(constants.LOG_DIRECTORY, exist_ok=True)
    app_logger, console_log_handler = init_log("astro")
    my_data = AstroData("astro", app_logger, console_log_handler)
    my_data.load_config()
    my_app = AstroTk(None, my_data , app_logger)
    my_app.update_display()
    my_app.mainloop()

if __name__ == "__main__":
    main()
