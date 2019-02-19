"""Unit test
unit test for the file_utils.py - DataFile instance
"""

import os
import pytest

from page_generator.utils.file_utils import DataFile


def get_resources_path():
    """Returns the path in which resources are located
    by taking this file as the reference
    """
    rel_resources_path = '../../_resources'
    # build the path taking this file as reference
    path = os.path.normpath(os.path.join(os.path.dirname(__file__), rel_resources_path))
    return path


def test_good_input():
    """These tests should pass
    """
    data_file_obj_normal = DataFile(get_resources_path() + '/template.html')
    data_file_obj_empty = DataFile(get_resources_path() + '/empty.txt')

    # should not be empty
    assert data_file_obj_normal.get_file_content() != ''

    # should start with that string
    assert data_file_obj_normal.get_file_content().startswith("<ac:layout>")

    # this obj should not have content
    assert data_file_obj_empty.get_file_content() == ''


def test_bad_input():
    """These tests should passed with invalid arguments
    """
    with pytest.raises(IOError):
        DataFile('path/not_existing.html')
