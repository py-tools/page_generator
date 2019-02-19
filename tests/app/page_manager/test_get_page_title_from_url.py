"""
Unit test for the page_manager.py - get_page_title_from_url function
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

    # test
    assert page_manager_object.get_page_title_from_url(
        'http://buic-confluence.conti.de:8090/display/~uidj5418/Page+1') == 'Page 1'
    assert page_manager_object.get_page_title_from_url(
        'http://buic-confluence.conti.de:8090/display/~uidj5418/90+-+Git') == '90 - Git'
    assert page_manager_object.get_page_title_from_url(
        'http://buic-confluence:8090/display/AHU/FordAHU_1.00.05') == 'FordAHU_1.00.05'
    assert page_manager_object.get_page_title_from_url(
        'http://buic-confluence:8090/display/AHU/Quality+Assurance') == 'Quality Assurance'
    assert page_manager_object.get_page_title_from_url(
        'http://buic-confluence.conti.de:8090/display/SWPT/Jira+Lib') == 'Jira Lib'

    assert page_manager_object.get_page_title_from_url(
        'http://buic-confluence.conti.de:8090/display/~uidj5418/Page+1',
        formatted=False) == 'Page+1'

    assert page_manager_object.get_page_title_from_url(
        'http://buic-confluence.conti.de:8090/display/~uidj5418/90+-+Git',
        formatted=False) == '90+-+Git'

    assert page_manager_object.get_page_title_from_url(
        'http://buic-confluence:8090/display/AHU/FordAHU_1.00.05',
        formatted=False) == 'FordAHU_1.00.05'

    assert page_manager_object.get_page_title_from_url(
        'http://buic-confluence:8090/display/AHU/Quality+Assurance',
        formatted=False) == 'Quality+Assurance'

    assert page_manager_object.get_page_title_from_url(
        'http://buic-confluence.conti.de:8090/display/SWPT/Jira+Lib',
        formatted=False) == 'Jira+Lib'


def test_bad_input(page_manager_object):
    """these tests should passed with invalid arguments
    """

    # test invalid URLs
    with pytest.raises(Exception):
        page_manager_object.get_page_title_from_url(
            'http://buic-confluence.conti.de:8090')

    with pytest.raises(Exception):
        page_manager_object.get_page_title_from_url(
            'https://buic-jenkins-dpk-1.contiwan.com/job/pipeline_cm_ci/')

    with pytest.raises(Exception):
        page_manager_object.get_page_title_from_url(
            'http://buic-confluence.conti.de:8090/pages/viewpage.action?pageId=102948555')
