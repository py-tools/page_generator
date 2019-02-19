#!/usr/bin/env python
# coding=utf-8
"""
Module with the ConfluenceClient class that can be instanced
in order to use the API
"""

import abc
import logging
import requests

from page_generator.confluence.exceptions import ConfluenceError
from page_generator.confluence.exceptions import ConfluencePermissionError

# main logger instance
LOGGER = logging.getLogger(__name__)


class ConfluenceClient(object):
    """Confluence Client API class

    An instance of this class is able to interact with the
    Confluence Server API in order to retrieve information
    or submit data into the server.

    This instance should be called within 'with' statement.
    Usage:

    with ConfluenceClient('http://host.com', 'user_x', 'pass_x') as instance:
        instance.get_content(...)
    """

    def __init__(self, confluence_host, user, password):
        # type: (str, str, str) -> ConfluenceClient
        """

        :param confluence_host: confluence host name (with http extension)
            ex: http://wiki-id.conti.de:8080
        :param user: name of the user (existing in the server)
        :param password: password string of the user
        """
        # Host and authentication credentials
        self._confluence_host = confluence_host
        self._user = user
        self._password = password
        self._basic_auth = (user, password)
        # build base API URL with confluence host name
        self._api_base_url = '{0}/rest/api'.format(self._confluence_host)
        self._client = None

    def __enter__(self):
        # type: () -> ConfluenceClient
        """Method to be called when inside 'with' statement
        to create Confluence Client instance

        :return: ConfluenceClient Instance
        """
        self._client = requests.session()
        self._client.auth = self._basic_auth
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Method to be called when exit 'with' statement
        to close the client connection and reset object instance
        """
        if self._client:
            self._client.close()
            self._client = None

    @property
    def client(self):
        # type: () -> requests.session
        """Provides access to an underlying requests alike object
        so that the client can be used in or out of a 'with' block.

        :return: An object which behaves like requests.Session
        """
        # Allow the class to be used without being inside a with block if
        # required.
        return self._client

    @staticmethod
    def _handle_response_errors(path, params, response):
        # type: (str, dict[str, str], requests.Response) -> None
        """Handles the response gotten from requests.Response instance
        to see if there is a problem in order to raise the exact exception

        :param path: path to REST API to content
        :param params: dictionary with the parameters
            that were added to HTTP message.
        :param response: response object from requests.Response
        :return: None

        :raises ConfluenceError: General confluence error
            (check message to verify details)
        :raises ConfluencePermissionError: when the credentials
            were not valid to use resources from REST API in server.

        """
        if response.status_code == 400:
            error_content_obj = ContentError(response.json())
            raise ConfluenceError(
                path, params, response,
                msg='{} (code:{})'.format(
                    error_content_obj.message,
                    error_content_obj.status_code
                )
            )
        elif response.status_code == 403:
            raise ConfluencePermissionError(path, params, response)
        elif response.status_code == 404:
            # raise ConfluenceResourceNotFound(path, params, response)
            Exception(path, params, response)
        elif response.status_code == 409:
            # raise ConfluenceVersionConflict(path, params, response)
            Exception(path, params, response)
        elif response.status_code == 413:
            # raise ConfluenceValueTooLong(path, params, response)
            Exception(path, params, response)

    def _post(self, path, params, data, files=None):
        # type: (str, dict, dict, str) -> dict
        """HTTP POST method for Confluence Client api

        :param path: path to REST API to post content
        :param params: dictionary with the parameters
            to add to POST message.
        :param data: dictionary with the data to post
        :param files:
        :return:
        """
        # build base url with path
        url = "{}/{}".format(self._api_base_url, path)
        headers = {"X-Atlassian-Token": "nocheck"}
        # send POST request over client and expect response
        response = self.client.post(
            url,
            params=params,
            json=data,
            headers=headers,
            files=files,
            auth=self._basic_auth
        )
        #
        self._handle_response_errors(path, params, response)
        return response.json()

    def _get(self, path, params, expand):
        # type: (str, dict[str, str], [list[str]]) -> dict
        """HTTP GET method for Confluence Client api

        :param path: path to REST API to get content
        :param params: dictionary with the parameters
            to add to GET message.
        :param expand:
        :return:
        """
        url = '{}/{}'.format(self._api_base_url, path)
        if expand:
            params['expand'] = ','.join(expand)
        # send GET request over client and expect response
        response = self.client.get(
            url,
            params=params,
            auth=self._basic_auth
        )
        # check HTTP response to handle errors
        self._handle_response_errors(path, params, response)
        return response.json()

    def _delete(self, path, params):
        # type: (str, dict) -> None
        """HTTP DELETE method for Confluence Client api

        :param path: path to REST API to delete content
        :param params: dictionary with the parameters
            to add to DELETE message.
        :return: None
        """
        # build base url with path
        url = "{}/{}".format(self._api_base_url, path)
        headers = {"X-Atlassian-Token": "nocheck"}
        # send POST request over client and expect response
        response = self.client.delete(
            url,
            params=params,
            headers=headers,
            auth=self._basic_auth
        )
        # check HTTP response to handle errors
        self._handle_response_errors(path, params, response)

    def create_page(self, page_title, space_key, page_content,
                    parent_page_id=None, content_type='page'):
        # type: (str, str, str, [str], [str]) -> Page
        """Creates a new page in Confluence inside the space_key given,
        under the parent_page_id as a child page

        :param page_title: String with the title of the page
            that will be created
        :param space_key: String with the space key in confluence
            in which the page will exists.
        :param page_content: HTML String Content of the page
            that will be created
        :param parent_page_id: String with the ID number of the parent page
            in which the page will be created as a child page
        :param content_type: Optional argument for content
            ('page' as default)
        :return: Page Content Object
        :rtype: Page
        """
        # json structure for a new page
        data = {
            'type': content_type,
            'title': page_title,
            'space': {
                'key': space_key
            },
            'body': {
                'storage': {
                    'value': page_content,
                    'representation': 'storage'
                }
            }
        }
        if parent_page_id:
            data['ancestors'] = [{
                'type': content_type,
                'id': parent_page_id
            }]

        response = self._post('content', {}, data)
        # create new page object from response gotten
        new_page = Page(response)
        return new_page

    def delete_content(self, content_id, content_status='current'):
        # type: (str, [str]) -> None
        """Deletes the content in Confluence with the given ID

        :param content_id: String with the ID number of the content
            (ex. page id of confluence page)
        :param content_status: String with the status in which
            content will be deleted / purged
            values: 'current', 'trashed'
        :return: None
        """
        url_delete_content = 'content/{}'.format(content_id)
        #
        self._delete(
            path=url_delete_content,
            params={'status': content_status}
        )

    def get_content(self, content_id, content_status='current', expand=None):
        # type: (str, [str], [list]) -> Page
        """

        :param content_id: id number of the content to search for
            ex. page_id = 1291392
        :param content_status:
        :param expand:
        :return: Page instance
        """
        url_get_content = 'content/{}'.format(content_id)
        # when expand is None, default values should be used
        # in order to retrieve the default page content
        # body.storage contains the HTML content of the page
        if expand is None:
            expand = ['history', 'space', 'version', 'body.storage']

        response = self._get(
            path=url_get_content,
            params={'status': content_status},
            expand=expand
        )
        #
        new_page = Page(response)
        return new_page

    def get_page_from_title(self, page_title, space_key):
        # type: (str, str) -> Page
        """Searches in confluence server for a page that correspond
        to the page title and space key given.

        If the page exists, a new Page instance will be created
        that will have and API to retrieve its content (like HTML)

        :param page_title: title of the page to look for
        :param space_key: space in which the page is located
        :return: Page instance
        """
        # use default values for expand
        # in order to retrieve the default page content
        # body.storage contains the HTML content of the page
        expand = ['history', 'space', 'version', 'body.storage']

        content_params = {
            'title': page_title,
            'spaceKey': space_key
        }

        response = self._get(
            path='content',
            params=content_params,
            expand=expand
        )

        new_page = Page(response)
        return new_page


class Content(object):
    """Base Class for classes related for Confluence Content
    ex. Confluence Page
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, json_data):
        # type: (dict) -> Content
        self._json_data_model = json_data

    @property
    def json_data_model(self):
        # type: () -> dict
        """Returns a dictionary with the json data model
        retrieved from HTTP response
        """
        return self._json_data_model

    @abc.abstractmethod
    def _retrieve_values_from_json(self):
        raise NotImplementedError("abstract method not implemented in child!")


class Page(Content):
    """Class needed to abstract the content of an HTTP json response
    that should contain a Confluence Page which was retrieve from
    Confluence REST API.

    This abstraction will retrieve the metadata from json response and
    it will create properties into Page object mapped to those values.
    """

    def __init__(self, json_data):
        super(Page, self).__init__(json_data)
        self._id = None
        self._title = None
        self._space_key = None
        self._content = None
        self._permanent_link = None
        self._base_url = None
        self._retrieve_values_from_json()
        LOGGER.debug("New Page Object created: %s", self)

    def _retrieve_results_from_json(self):
        # type: () -> dict
        """Validates if json API response contains a dictionary with
        the results with Page data.

        :raises IndexError: in case 'results' is not found in api response
        :return: the json api response with the page data
        """
        # attributes model reference:
        # https://docs.atlassian.com/ConfluenceServer/rest/6.12.1/
        json_api_results = self.json_data_model
        # check if API response is contained inside
        # 'results' json object
        if 'results' in json_api_results.keys():
            # check if results contains any data
            # in order to retrieve values from it
            if json_api_results['results']:
                json_api_results = json_api_results['results'][0]
            else:
                raise IndexError("Page object cannot be instanced because "
                                 "API response 'results' is empty.")
        return json_api_results

    def _validate_links_section(self, json_data_response):
        # type: (dict) -> str
        """Validates and retrieves _links section data
        out of the api response in order to get links data
        """
        missing_value = None
        # links
        if '_links' in json_data_response.keys():
            # permanent link
            if 'tinyui' in json_data_response['_links'].keys():
                self._permanent_link = json_data_response['_links']['tinyui']
            else:
                missing_value = '_links.tinyui'
        else:
            missing_value = '_links'
        return missing_value

    def _validate_body_section(self, json_data_response):
        # type: (dict) -> str
        """Validates and retrieves body section data
        out of the api response in order to get html content
        """
        missing_value = None
        # body.view.value (HTML Content)
        if 'body' in json_data_response.keys():
            if 'storage' in json_data_response['body'].keys():
                if 'value' in json_data_response['body']['storage'].keys():
                    self._content = json_data_response['body']['storage']['value']
                else:
                    missing_value = 'body.storage.value'
            else:
                missing_value = 'body.storage'
        else:
            missing_value = 'body'
        return missing_value

    def _retrieve_values_from_json(self):
        # type: () -> None
        """Retrieves the values from the HTTP response in json format
        that are important for the page object, like id, title,
        space, HTML content, web link.

        If some value is missing, an exception will be raised

        Then, it adds those values to the Page model
        into properties of the instance

        :return: None
        :raises Exception: if a value is not present on json model
        """

        # retrieve base url for the server host from response
        if '_links' in self.json_data_model.keys():
            if 'base' in self.json_data_model['_links'].keys():
                self._base_url = self.json_data_model['_links']['base']

        # retrieve results dictionary with Page data from json api response
        json_data_response = self._retrieve_results_from_json()

        missing_value = None

        # id
        if 'id' in json_data_response.keys():
            self._id_number = json_data_response['id']
        else:
            missing_value = 'id'
        # title
        if 'title' in json_data_response.keys():
            self._title = json_data_response['title']
        else:
            missing_value = 'title'
        # space
        if 'space' in json_data_response.keys():
            # space key
            if 'key' in json_data_response['space'].keys():
                self._space_key = json_data_response['space']['key']
            else:
                missing_value = 'space.key'
        else:
            missing_value = 'space'

        # retrieve body section from API response
        missing_value = self._validate_body_section(json_data_response)

        # retrieve _links section from API response
        missing_value = self._validate_links_section(json_data_response)

        if missing_value is not None:
            raise Exception("Page object cannot be instanced because "
                            "there is a missing value in json data: "
                            "\"{val}\"".format(val=missing_value))


    @property
    def id_number(self):
        # type: () -> str
        """Returns the id number of the Confluence page
        """
        return self._id_number

    @property
    def title(self):
        # type: () -> str
        """Returns the title of the Confluence page
        """
        return self._title

    @property
    def content(self):
        # type: () -> str
        """Returns the HTML content retrieved from Confluence page
        """
        return self._content

    @property
    def space_key(self):
        # type: () -> str
        """Returns the space kay name in which the Confluence page belongs to
        """
        return self._space_key

    @property
    def permanent_link(self):
        # type: () -> str
        """Returns the permanent link of the Confluence Page

        (this link will be always point to that page
        even if it changes it title or location)
        """
        return self._permanent_link

    @property
    def base_url(self):
        # type: () -> str
        """Returns the base url of the server host in which
        the API response was received
        """
        return self._base_url

    def __str__(self):
        # type: () -> str
        """Returns a string representation of the current Page instance
        with metadata like: Type, Id, Space, Title, Link, html content
        """
        status = "Confluence Content - " \
                 "ID: \"{id}\" - " \
                 "SPACE: \"{space}\" - " \
                 "TITLE: \"{title}\" - " \
                 "PERMALINK: \"{permalink}\" - " \
                 "CONTENT: \"{content}\""
        if self.content is None:
            content_string = status.format(
                id=self.id_number,
                space=self.space_key,
                title=self.title,
                permalink=self.permanent_link,
                content="No Content"
            )
        else:
            content_string = status.format(
                id=self.id_number,
                space=self.space_key,
                title=self.title,
                permalink=self.permanent_link,
                content="Yes"
            )
        return content_string


class ContentError(Content):
    """Class needed to abstract the content of an HTTP json response
    that is an ERROR response from Confluence REST API.

    ex. when page does not exist
    """

    def __init__(self, json_data):
        # type: (dict) -> ContentError
        super(ContentError, self).__init__(json_data)
        self._message = None
        self._status_code = None
        self._retrieve_values_from_json()

    def _retrieve_values_from_json(self):
        """Retrieves the values from HTTP json response from REST API
        that are meaningful for Error Content (message and status code)

        :return: None
        :raises Exception: if a value is not present on json model
        """
        missing_value = None
        # message
        if 'message' in self.json_data_model.keys():
            self._message = self.json_data_model['message']
        else:
            missing_value = 'message'
        # statusCode
        if 'statusCode' in self.json_data_model.keys():
            self._status_code = self.json_data_model['statusCode']
        else:
            missing_value = 'statusCode'

        if missing_value is not None:
            raise Exception("ContentError object cannot be instance because "
                            "there is a missing value in json data: "
                            "\"{val}\"".format(val=missing_value))

    @property
    def message(self):
        """Returns the error message of the HTTP error response
        """
        return self._message

    @property
    def status_code(self):
        """Returns the status code of the HTTP error response
        """
        return self._status_code
