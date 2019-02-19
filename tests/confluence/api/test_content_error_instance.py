"""
Unit test for the api.py - ContentError instance
"""

import pytest

from page_generator.confluence.api import ContentError
from _mock_data.confluence_api_data import CONFLUENCE_JSON_API_DATA_1
from _mock_data.confluence_api_data import CONFLUENCE_JSON_API_DATA_2
from _mock_data.confluence_api_data import CONFLUENCE_JSON_API_DATA_3
from _mock_data.confluence_api_data import CONFLUENCE_JSON_API_DATA_4
from _mock_data.confluence_api_data import CONFLUENCE_JSON_API_DATA_5
from _mock_data.confluence_api_data import CONFLUENCE_JSON_API_DATA_6
from _mock_data.confluence_api_data import CONFLUENCE_JSON_API_DATA_7
from _mock_data.confluence_api_data import CONFLUENCE_JSON_API_DATA_8


def test_good_input():
    """these tests should pass
    """
    # test
    content_error_obj_1 = ContentError(CONFLUENCE_JSON_API_DATA_6)

    # assert instance properties match json
    assert content_error_obj_1.status_code == '404'
    assert content_error_obj_1.message == 'No content found with id: ContentId{id=3965072}'

    # test
    content_error_obj_2 = ContentError(CONFLUENCE_JSON_API_DATA_7)

    # assert instance properties match json
    assert content_error_obj_2.status_code == '404'
    assert content_error_obj_2.message == 'No space with key : TST'

    # test
    content_error_obj_3 = ContentError(CONFLUENCE_JSON_API_DATA_8)

    # assert instance properties match json
    assert content_error_obj_3.status_code == '400'
    assert content_error_obj_3.message == 'A page with this title already exists: ' \
                                          'A page already exists with the title ' \
                                          'TEMPLATE_TEST_PAGE in the space with key ~uidu076z'


def test_bad_input():
    """these tests should passed with invalid arguments
    """
    # test with API response is an error
    with pytest.raises(Exception):
        ContentError(CONFLUENCE_JSON_API_DATA_1)

    # test with API response is an error
    with pytest.raises(Exception):
        ContentError(CONFLUENCE_JSON_API_DATA_2)

    # test with API response is an error
    with pytest.raises(Exception):
        ContentError(CONFLUENCE_JSON_API_DATA_3)

    # test with API response is an error
    with pytest.raises(Exception):
        ContentError(CONFLUENCE_JSON_API_DATA_4)

    # test with API response is an error
    with pytest.raises(Exception):
        ContentError(CONFLUENCE_JSON_API_DATA_5)
