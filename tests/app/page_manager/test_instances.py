"""
Unit test for the page_manager.py - PageManager instances
"""

import os
import pytest

from page_generator.app.page_manager import PageManager


def get_resources_path():
    """Returns the path in which resources are located
    by taking this file as the reference
    """
    rel_resources_path = '../../_resources'
    # build the path taking this file as reference
    path = os.path.normpath(os.path.join(os.path.dirname(__file__), rel_resources_path))
    return path


def test_good_input():
    """these tests should pass
    """

    # test valid instances with different valid config files
    page_manager_obj = PageManager(get_resources_path() + '/config_valid.json')
    page_manager_obj = PageManager(get_resources_path() + '/config_valid_other.json')


def test_bad_input():
    """these tests should passed with invalid arguments
    """

    # test a file that is not a config file
    with pytest.raises(Exception):
        PageManager(get_resources_path() + '/empty.txt')

    # test a file that does not exist
    with pytest.raises(IOError):
        PageManager('not_existing_file.json')

    # test a config file with invalid config structure
    with pytest.raises(AttributeError):
        PageManager(get_resources_path() + '/config_invalid.json')

    # test a json file with bad json format
    with pytest.raises(Exception):
        PageManager(get_resources_path() + '/config_bad_format.json')


