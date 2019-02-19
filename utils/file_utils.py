"""
Module for utilities needed for different kinds of files
"""
# !/usr/bin/env python
# coding=utf-8

import os
import re
import collections


class DataFile(object):
    """
    Base Class for any file that contains text inside of it
    """

    def __init__(self, filename):
        # type: (str) -> DataFile[object]
        """
        DataFile Constructor

        :param filename: file path on the drive
        """
        self._file = filename
        self._file_content = None
        self._parse_file_content()

    def _parse_file_content(self):
        """
        Validates if it is an existing file.
        If so, it parses the content of the file

        :return: None
        """
        if not os.path.exists(self._file):
            raise IOError("File '{0}' does not exist".format(self._file))
        with open(self._file) as file_obj:
            self._file_content = file_obj.read()

    def get_file_content(self):
        # type: () -> str
        """
        Returns the content of the file

        :return: a string with the file content
        """
        return self._file_content


class ConfluenceHtmlTemplate(DataFile):
    """
    Object to contain the HTML content from confluence
    """

    def __init__(self, template_file):
        # type: (str) -> ConfluenceHtmlTemplate[object]
        super(ConfluenceHtmlTemplate).__init__(template_file)

    def get_template_content(self):
        # type: () -> str
        """
        Returns a string with the current html content from template

        :return: A string with the template content
        :rtype: str
        """
        return self.get_file_content()

    def replace_variable_value(self, variable, new_value):
        # type: (str, str) -> None
        """
        Replaces a variable inside the content
        with a new given value

        :param variable: string to replace
        :param new_value: string value to be a replacement
        :return: None
        """
        if variable in self._file_content:
            self._file_content = self._file_content.replace(
                variable,
                new_value
            )


class VariableMappingFile(DataFile):
    """
    Object to contain variable mapping file abstraction.
    Parses the file and retrieves variables from html ref and json ref.
    A dictionary can be retrieved after with the variables
    """

    # regex to match variables found in mapping file
    # FORMAT:
    # $VariableInsideHTML = json_variable_name
    REGEX_MAPPING_FORMAT = re.compile(r'(\$\w*)\s*=\s*(\w*),?')
    # regex group for html variables position
    REGEX_GROUP_HTML_VAR = 1
    # regex group for json variables position
    REGEX_GROUP_JSON_VAR = 2

    def __init__(self, variable_map_file):
        # type: (str) -> VariableMappingFile[object]
        """

        :param variable_map_file: file path of the mapping file
        :type variable_map_file: str
        """
        super(VariableMappingFile, self).__init__(variable_map_file)
        #
        self._map_variable_dict = collections.OrderedDict()
        #
        self._load_variable_mapping()

    def get_var_mapping_dict(self):
        # type: () -> dict
        """
        Returns a dictionary with the variables that were retrieved
        from variable mapping file (key:html_var, value:json_var)

        :return: A dictionary with the mapped variables (html - json)
        :rtype: dict
        """
        return self._map_variable_dict

    def _load_variable_mapping(self):
        # type: () -> None
        """
        Uses regular expression to find all variables found
        and they are then loaded into the dictionary

        :return: None
        """
        # find all variables by regex
        for match in re.finditer(
                VariableMappingFile.REGEX_MAPPING_FORMAT,
                self.get_file_content(),
                re.MULTILINE
        ):
            # load variables into dictionary (key:html_var, value:json_var)
            self._map_variable_dict[
                match.group(VariableMappingFile.REGEX_GROUP_HTML_VAR)] = \
                match.group(VariableMappingFile.REGEX_GROUP_JSON_VAR)
