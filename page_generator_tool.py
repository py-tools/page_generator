#!/usr/bin/env python
# coding=utf-8
"""
Main script to generate confluence pages from configuration file
"""

import argparse
import logging
from page_generator.app.page_manager import PageManager

# get logger instance
LOGGER = logging.getLogger()


def configure_logger(global_logger, log_level):
    # type: (logging.Logger, str) -> None
    """Configures the main logger object.
    log level is set for logging level.

    :param global_logger: main logger instance
    :param log_level:
        logging level [ error > warning > info > debug > off ]
    :return:
    """
    log_levels = {
        'off': logging.NOTSET,
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    if log_level not in log_levels.keys():
        raise ValueError("Logging level not valid: '{}'".format(log_level))
    else:
        log_level = log_levels[log_level]
    global_logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    file_handler = logging.FileHandler('logs.log')
    file_handler.setLevel(log_level)
    # create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s :%(name)-24s: [%(levelname)s] -> %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    # add the handlers to the logger
    global_logger.addHandler(file_handler)
    global_logger.addHandler(console_handler)


# ---------------
# MAIN
# ---------------
def main():
    """Main Function
    """

    # Script Argument Parser
    parser = argparse.ArgumentParser(description='Confluence API')
    parser.add_argument(
        '-c', '--config_file', required=True,
        help='Script configuration file (JSON Format)')
    parser.add_argument(
        '-l', '--log_level', default="warning",
        help='debugging script log level '
             '[ error > warning > info > debug > off ]')
    args = parser.parse_args()

    # configure logging properties with configuration given
    configure_logger(LOGGER, args.log_level)

    # Create a confluence page manager instance that
    # will read & validate all values from config file.
    # This manager object will work as an API
    # to create, delete, retrieve confluence pages.
    page_manager_obj = PageManager(args.config_file)
    page_manager_obj.generate_page()


if __name__ == "__main__":
    main()
