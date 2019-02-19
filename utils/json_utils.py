# !/usr/bin/env python
# coding=utf-8
"""
Module to manage json utilities for files in json format
"""

import os
import json


class JsonDataFile(object):
    """Class to create a model from a json file
    """

    def __init__(self, json_file):
        # type: (str) -> JsonDataFile
        """
        :param json_file: path file to existing json file
        """
        self._file_name = None
        self._json_model_dict = {}
        # validate and parse the json file content
        self._load_json_content(json_file)

    @property
    def file_name(self):
        # type: () -> str
        """Returns the file name of the json file

        :return: a string with the json file name
        """
        return self._file_name

    @property
    def json_model_dict(self):
        # type: () -> dict
        """Returns the json model dictionary

        :return:
            a dictionary with the model data
            gotten of the json file
        """
        return self._json_model_dict

    def has_json_attribute(self, json_attribute):
        # type: (str) -> bool
        """Checks if json file content has the given attribute

        :param json_attribute:
            string of the json attribute to search
        :return: True if found, otherwise False
        """
        if json_attribute in self._json_model_dict.keys():
            return True
        return False

    def get_value_from_json_ref(self, json_ref):
        # type: (str) -> str
        """Validates if json model has an attribute
        inside the model, if so it returns the value of it.
        Otherwise, it raises an exception.

        :param json_ref: string value of the attribute to look for
        :return:
        """
        if hasattr(self, json_ref):
            return getattr(self, json_ref)
        else:
            raise AttributeError(
                "json configuration file does not contain "
                "attribute '{0}'. Please check JSON Model".format(json_ref))

    def _break_down_json_data(self, json_data):
        # type: (str) -> dict
        """Iterates over json object in order to find all
        variables an values configured

        :param json_data: json data model gotten from json file
        :return: a dictionary with the json key - value gotten
        """
        temp_dict = {}
        self._reverse_json(json_data, temp_dict)
        return temp_dict

    def _reverse_json(self, json_data, data_model, remaining_key=None):
        # type: (str, dict, str) -> None
        """It parses the json tree model in order to look for
        all attributes until it reaches the last attribute of the tree
        (that is why it has recursive call).

        Then, that attribute is loaded into the dictionary
        of the json model

        :param json_data:
        :param data_model: dictionary with the current data model
        :param remaining_key:
        :return:
        """
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                self._reverse_json(value, data_model, key)
        elif isinstance(json_data, list):
            for value in json_data:
                self._reverse_json(value, data_model, remaining_key)
        else:
            data_model[str(remaining_key)] = str(json_data)

    def _load_json_content(self, json_file_name):
        # type: (str) -> None
        """Validates if the loaded json file exists,
        opens the file and it checks if it is a valid json file.

        Then it breaks down all the json attributes and values
        into a dictionary that will work as a model

        :return: None
        """
        if not os.path.exists(json_file_name):
            raise IOError("File '{0}' does not exist".format(self._file_name))
        try:
            with open(json_file_name) as json_data_file:
                json_data = json.load(json_data_file)
                # once loaded, retrieve the filename
                self._file_name = os.path.basename(json_data_file.name)
            # after parsing and loading the data from json file
            # it is needed to break down the json tree into a dict
            # JsonKey -> JsonValue
            self._json_model_dict = self._break_down_json_data(json_data)
        except Exception as ex:
            raise Exception("Invalid JSON format in '{file}': {exc}".format(
                file=self.file_name,
                exc=ex))

        # generate a dict with json attributes with values configured
        for json_key, json_value in self._json_model_dict.items():
            setattr(self, json_key, json_value)
