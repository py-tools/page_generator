"""
Unit test for the json_utils.py - JsonDataFile class
"""

import os
import pytest

from page_generator.app.config_utils import Config


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

    # common config file
    config_obj = Config(get_resources_path() + '/config_valid.json')

    # template var dictionary should contain data
    assert config_obj.template_variables

    # assert all configuration values
    assert config_obj.get_host_url() == 'http://buic-confluence.conti.de:8090'
    assert config_obj.get_user() == 'my_user'
    assert config_obj.get_password() == 'my_password'
    assert config_obj.get_source() == 'http://buic-confluence.conti.de:8090/display/space/page'
    assert config_obj.get_parent_page_id() == '102956449'
    assert config_obj.get_page_title() == 'TEMPLATE_TEST_PAGE'
    assert config_obj.template_variables['$MyVariable'] == 'var'

    # config file with no variables defined (but valid)
    config_obj = Config(get_resources_path() + '/config_no_variables.json')

    # template var dictionary should be empty
    assert not config_obj.template_variables

    # assert some configurations from no variable config
    assert config_obj.get_host_url() == 'http://buic-confluence.conti.de:8090'
    assert config_obj.get_user() == 'env.USER'
    assert config_obj.get_password() == 'env.PASS'


def test_bad_input():
    """these tests should passed with invalid arguments
    """
    # test a file that is not a config file
    with pytest.raises(Exception):
        Config(get_resources_path() + '/empty.txt')

    # test a file that does not exist
    with pytest.raises(IOError):
        Config('not_existing_file.json')

    # test a config file with invalid config structure
    with pytest.raises(AttributeError):
        Config(get_resources_path() + '/config_invalid.json')

    # test a json file with bad json format
    with pytest.raises(Exception):
        Config(get_resources_path() + '/config_bad_format.json')
