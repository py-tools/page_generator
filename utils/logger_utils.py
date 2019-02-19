#!/usr/bin/env python
# coding=utf-8
"""
Module to use custom logger utilities
"""

import logging
import sys


class Logger(object):
    """Logger class to use logging API
    """

    # default formats for both logging string and file output
    DEFAULT_FORMAT = "%(asctime)s - %(name)-30s [%(levelname)s] -> %(message)s"
    DEFAULT_FL_HANDLER_FORMAT = "%(asctime)s - %(name)-20s [%(levelname)s] -> %(message)s"

    LOG_LEVEL_DEBUG = "debug"
    LOG_LEVEL_INFO = "info"
    LOG_LEVEL_ERROR = "error"
    LOG_LEVEL_OFF = "off"

    LOGGER_INSTANCE = None

    @staticmethod
    def get_logger_instance(name):
        """Returns the singleton logger instance

        :param name: sets the current name for the singleton logger
            instance in order to know the module name
        :return:
        """
        if Logger.LOGGER_INSTANCE is None:
            Logger.LOGGER_INSTANCE = Logger(logger_name=name)
        else:
            Logger.LOGGER_INSTANCE.set_module_name(name)
        return Logger.LOGGER_INSTANCE

    def __init__(self, logger_name="Logger", log_file_name='logs.log', logger_format=None):
        # type: ([str], [str], [str]) -> Logger
        """Constructor method

        :param logger_name: name of the logger to identify
        :param log_file_name: name of the logging file
        :param logger_format: format for logging
            if None, use default logging format set
        """
        # create logger
        self._logger = logging.getLogger(logger_name)  # logger
        self._logger.setLevel(logging.DEBUG)

        # configure file handler
        self._fl_handler = logging.FileHandler(log_file_name)
        self._fl_handler_format = logging.Formatter(Logger.DEFAULT_FL_HANDLER_FORMAT)
        self._fl_handler.setFormatter(self._fl_handler_format)

        # configure console handler
        self._ch_handler = logging.StreamHandler()
        self._ch_handler.setLevel(logging.DEBUG)

        # create formatter
        if logger_format is None:
            self._format = logging.Formatter(Logger.DEFAULT_FORMAT)
        else:
            self._format = logging.Formatter(logger_format)
        self._ch_handler.setFormatter(self._format)

        # add handlers
        self._logger.addHandler(self._ch_handler)
        self._logger.addHandler(self._fl_handler)

        self._logger_name = logger_name

        # handling in case of an error (exit or exception)
        self._exit_on_error = True

    def set_module_name(self, module_name):
        """Sets the module name as the logger name

        :param module_name: new module name to set
        :return:
        """
        self._logger_name = module_name

    def activate_exit_on_error(self):
        """Activate logger to exit the system on ERROR log
        """
        self._exit_on_error = True

    def deactivate_exit_on_error(self):
        """Deactivate logger to exit the system on ERROR log
        """
        self._exit_on_error = False

    def set_logging_level(self, level):
        # type: (str) -> None
        """Configures the logging level to manage at the instance

        Available values:
            debug
            info
            warning
            error
            off

        :param level: value of the logging level to set
        :return:
        """
        # level - debug
        if level.lower() == Logger.LOG_LEVEL_DEBUG:
            self._logger.setLevel(logging.DEBUG)
            self._ch_handler.setLevel(logging.DEBUG)
        # level - info
        elif level.lower() == Logger.LOG_LEVEL_INFO:
            self._logger.setLevel(logging.INFO)
            self._ch_handler.setLevel(logging.INFO)
        # level - error
        elif level.lower() == Logger.LOG_LEVEL_ERROR:
            self._logger.setLevel(logging.ERROR)
            self._ch_handler.setLevel(logging.ERROR)
        # level - off
        elif level.lower() == Logger.LOG_LEVEL_OFF:
            self._logger.setLevel(logging.NOTSET)
            self._ch_handler.setLevel(logging.NOTSET)
        # level - warning (default)
        else:
            self._logger.setLevel(logging.WARNING)
            self._ch_handler.setLevel(logging.WARNING)

    def error(self, msg, *args, **kwargs):
        # type: (str, *object, **object) -> None
        """log error message

        :param msg: message to log
        :param args: extra args
        :param kwargs: extra args
        :return: None
        """
        self._logger.error(msg, *args, **kwargs)
        if self._exit_on_error:
            sys.exit("Stop by error...")
        raise Exception(msg % args)

    def debug(self, msg, *args, **kwargs):
        # type: (str, *object, **object) -> None
        """log debug message

        :param msg: message to log
        :param args: extra args
        :param kwargs: extra args
        :return: None
        """
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        # type: (str, *object, **object) -> None
        """log info message

        :param msg: message to log
        :param args: extra args
        :param kwargs: extra args
        :return: None
        """
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        # type: (str, *object, **object) -> None
        """log warning message

        :param msg: message to log
        :param args: extra args
        :param kwargs: extra args
        :return: None
        """
        self._logger.warning(msg, *args, **kwargs)
