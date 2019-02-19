"""
Unit test for the api.py - Page instance
"""

import pytest

from page_generator.confluence.api import Page
from _mock_data.confluence_api_data import CONFLUENCE_JSON_API_DATA_1
from _mock_data.confluence_api_data import CONFLUENCE_JSON_API_DATA_2
from _mock_data.confluence_api_data import CONFLUENCE_JSON_API_DATA_3
from _mock_data.confluence_api_data import CONFLUENCE_JSON_API_DATA_4
from _mock_data.confluence_api_data import CONFLUENCE_JSON_API_DATA_5
from _mock_data.confluence_api_data import CONFLUENCE_JSON_API_DATA_7
from _mock_data.confluence_api_data import CONFLUENCE_JSON_API_DATA_8


def test_good_input():
    """these tests should pass
    """
    # test
    page_ok_1 = Page(CONFLUENCE_JSON_API_DATA_1)

    # assert instance properties match json
    assert page_ok_1.id_number == '111655103'
    assert page_ok_1.title == 'Template Test 2'
    assert page_ok_1.space_key == '~uidj5418'
    assert page_ok_1.permanent_link == '/x/v7inBg'
    assert page_ok_1.base_url == 'http://buic-confluence.conti.de:8090'
    assert page_ok_1.content == '<h1>Hello</h1>'

    # json data model should not be empty
    assert page_ok_1.json_data_model

    # test
    page_ok_2 = Page(CONFLUENCE_JSON_API_DATA_2)

    # assert instance properties match json
    assert page_ok_2.id_number == '96511561'
    assert page_ok_2.title == 'Jira Lib'
    assert page_ok_2.space_key == 'SWPT'
    assert page_ok_2.permanent_link == '/x/SabABQ'
    assert page_ok_2.base_url == 'http://buic-confluence.conti.de:8090'
    assert page_ok_2.content == '<p>JIRA Lib...</p>'

    # json data model should not be empty
    assert page_ok_2.json_data_model

    # test
    page_ok_3 = Page(CONFLUENCE_JSON_API_DATA_3)

    # assert instance properties match json
    assert page_ok_3.id_number == '96510230'
    assert page_ok_3.title == 'Git/Gerrit Installation'
    assert page_ok_3.space_key == 'SWPT'
    assert page_ok_3.permanent_link == '/x/FqHABQ'
    assert page_ok_3.base_url == 'http://buic-confluence.conti.de:8090'
    assert page_ok_3.content == '<ac:layout>...'

    # json data model should not be empty
    assert page_ok_3.json_data_model


def test_bad_input():
    """these tests should passed with invalid arguments
    """
    # test with API response with no content, meaning
    # expand parameter was empty, so no body, history was returned
    with pytest.raises(Exception):
        Page(CONFLUENCE_JSON_API_DATA_4)

    # test with API response with when there is no results
    with pytest.raises(IndexError):
        Page(CONFLUENCE_JSON_API_DATA_5)

    # test with API response from an error message
    with pytest.raises(Exception):
        Page(CONFLUENCE_JSON_API_DATA_7)

    # test with API response from an error message
    with pytest.raises(Exception):
        Page(CONFLUENCE_JSON_API_DATA_8)
