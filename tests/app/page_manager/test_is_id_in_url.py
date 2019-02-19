"""
Unit test for the page_manager.py - is_id_in_url function
"""

import os

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

    page_manager_obj = PageManager(get_resources_path() + '/config_valid.json')

    # test for some valid URLs with page id
    assert page_manager_obj.is_id_in_url(
        "https://buic-confluence.conti.de:8090/pages/viewpage.action?pageId=102948555")
    assert page_manager_obj.is_id_in_url(
        "http://wiki-id.conti.de/pages/viewpage.action?pageId=206572381")


def test_bad_input():
    """these tests should passed with invalid arguments
    """

    page_manager_obj = PageManager(get_resources_path() + '/config_valid.json')

    # test invalid URLs
    assert not page_manager_obj.is_id_in_url("D:\casdev\_git\sw_tools\unittest")
    assert not page_manager_obj.is_id_in_url("path/file/not")
    assert not page_manager_obj.is_id_in_url("invalid_string")
    assert not page_manager_obj.is_id_in_url("git-id.conti.de")
    assert not page_manager_obj.is_id_in_url(
        "http://buic-confluence.conti.de:8090/display/~uidu000x")
    assert not page_manager_obj.is_id_in_url(
        "http://buic-jira.conti.de:8080/secure/Dashboard.jspa")
    assert not page_manager_obj.is_id_in_url(
        "https://buic-jenkins-dpk-1.contiwan.com/job/pipeline_cm_ci/")

