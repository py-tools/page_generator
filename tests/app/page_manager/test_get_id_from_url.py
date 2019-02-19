"""
Unit test for the page_manager.py - get_id_from_url function
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


@pytest.fixture(scope='module')
def page_manager_object():
    """Returns an instance of PageManager with valid configuration
    """
    return PageManager(get_resources_path() + '/config_valid.json')


def test_good_input(page_manager_object):
    """these tests should pass
    """

    # test valid URL to retrieve confluence space
    assert page_manager_object.get_id_from_url(
        'http://buic-confluence.conti.de:8090'
        '/pages/viewpage.action?pageId=102948555') == '102948555'
    assert page_manager_object.get_id_from_url(
        'http://wiki-id.conti.de'
        '/pages/viewpage.action?pageId=206572381') == '206572381'


def test_bad_input(page_manager_object):
    """these tests should passed with invalid arguments
    """

    # test invalid URLs
    with pytest.raises(Exception):
        page_manager_object.get_id_from_url(
            'http://buic-confluence.conti.de:8090/display/~uidj5418/Page+1')
    with pytest.raises(Exception):
        page_manager_object.get_id_from_url(
            'http://buic-confluence.conti.de:8090/display/SWPT/Gerrit+Sandbox')
    with pytest.raises(Exception):
        page_manager_object.get_id_from_url(
            'http://buic-confluence:8090/display/AHU/FordAHU_1.00.05')
    with pytest.raises(Exception):
        page_manager_object.get_id_from_url(
            'http://buic-confluence.conti.de:8090/display/TS/Automated+Release')
    with pytest.raises(Exception):
        page_manager_object.get_id_from_url(
            'http://wiki-id.conti.de/display/CIPS/CIPS+V02.01.00')
    with pytest.raises(Exception):
        page_manager_object.get_id_from_url(
            'http://buic-confluence.conti.de:8090/display/ATP/Automation')
    with pytest.raises(Exception):
        page_manager_object.get_id_from_url(
            'http://buic-confluence.conti.de:8090/display/DFSSN/DFSS+Network')
    with pytest.raises(Exception):
        page_manager_object.get_id_from_url(
            'http://buic-confluence.conti.de:8090/display/GO/SW+Sync')
    with pytest.raises(Exception):
        page_manager_object.get_id_from_url(
            'http://buic-confluence.conti.de:8090/display/IIC/I+IC')
    with pytest.raises(Exception):
        page_manager_object.get_id_from_url(
            'http://buic-confluence.conti.de:8090')
    with pytest.raises(Exception):
        page_manager_object.get_id_from_url(
            'https://buic-jenkins-dpk-1.contiwan.com/job/pipeline_cm_ci/')
    with pytest.raises(Exception):
        page_manager_object.get_id_from_url(
            'http://buic-confluence.conti.de:8090/display/')
