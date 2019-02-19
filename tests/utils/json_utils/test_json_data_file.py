"""
Unit test for the json_utils.py - JsonDataFile function
"""

import os
import pytest

from page_generator.utils.json_utils import JsonDataFile


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
    json_data_obj = JsonDataFile(get_resources_path() + '/config_valid.json')

    assert json_data_obj.file_name == 'config_valid.json'
    assert json_data_obj.has_json_attribute('user')
    assert json_data_obj.has_json_attribute('$MyVariable')

    assert json_data_obj.json_model_dict

    assert json_data_obj.get_value_from_json_ref('parent_page_id') == '102956449'
    assert json_data_obj.get_value_from_json_ref('user') == 'my_user'


def test_bad_input():
    """these tests should passed with invalid arguments
    """
    # test a json file with bad json format
    with pytest.raises(Exception):
        JsonDataFile(get_resources_path() + '/config_bad_format.json')

    # test other file extensions for json
    with pytest.raises(Exception):
        JsonDataFile(get_resources_path() + '/empty.txt')

    # test a file that does not exist
    with pytest.raises(IOError):
        JsonDataFile('path/not_existing_file.json')

    # test invalid input from valid json file
    json_data_obj = JsonDataFile(get_resources_path() + '/config_valid.json')

    assert not json_data_obj.has_json_attribute('not_valid')

    with pytest.raises(AttributeError):
        json_data_obj.get_value_from_json_ref('not_valid')
