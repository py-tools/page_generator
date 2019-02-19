#!/usr/bin/env python
# coding=utf-8
"""
Module with the main API object for confluence page management
"""

import logging
import re
import os
from functools import wraps
from collections import defaultdict

from page_generator.app import config_utils
from page_generator.confluence import api
from page_generator.utils.http_utils import Auth
from page_generator.utils import file_utils

# get main logger instance
LOGGER = logging.getLogger(__name__)


# -----------------
# Decorators
# -----------------
def authenticate(function_to_decorate):
    """Decorator for functions that requires to authenticate
    the credentials before doing any action required to be done
    on the Server side.

    If the user is already authenticated, no authentication
    process is required.

    :param function_to_decorate:
        function that requires authentication to the server
        before being called.
    :return: function called
    """
    @wraps(function_to_decorate)
    def wrapper(self, *args, **kwargs):
        """Wrapper for decorated function
        """
        if self.is_authenticated:
            return function_to_decorate(self, *args, **kwargs)
        # Test Authentication User@Host
        LOGGER.info("Trying Basic Authentication - %s@%s",
                    self.get_user(),
                    self.config_obj.get_host_url())
        if Auth.authenticate(
                self.config_obj.get_host_url(),
                self.get_user(),
                self._credentials['password']):
            LOGGER.debug("Basic Authentication Successful! - %s@%s",
                         self.get_user(),
                         self.config_obj.get_host_url())
            # authentication complete
            self.is_authenticated = True
            return function_to_decorate(self, *args, **kwargs)
        else:
            self.is_authenticated = False
            error_msg = "Authentication Error: check that user and password are correct"
            LOGGER.error(error_msg)
            raise AssertionError(error_msg)

    return wrapper


class PageManager(object):
    """Main Class to handle confluence page creation, deletion
    depending on the configuration file in which this class
    is instanced from.
    """

    ENV_PREFIX = "env."

    def __init__(self, config_file):
        # type: (str) -> PageManager
        """PageManager Constructor method

        :param config_file: path to the json config file
        """
        self._config_file = config_file
        # templates
        self._template_source = None
        self._html_template = None
        # authentication credentials dict
        self._credentials = {}
        # object handlers
        self.config_obj = None
        self.template_obj = None
        # flag for authentication
        self.is_authenticated = False
        # private methods to load files
        self._load_config_file(config_file)
        self._load_template()

    def get_user(self):
        # type: () -> str
        """Returns the username used to authenticate
        to the confluence server
        """
        return self._credentials['user']

    def _load_template(self):
        # type: () -> None
        """Loads the source value of the configuration file gotten from the source value of the
        configuration file,
        :return:
        """
        template_source = self.config_obj.get_source()
        # check that source is either an URL or a file
        if not self.is_url(template_source) and not os.path.exists(template_source):
            raise Exception("")
        self._template_source = template_source

    def _load_config_file(self, config_file):
        # type: (str) -> None
        """Creates a Config instance which will validate
        the configuration parameters.

        After that, it will user that instance API to check the
        configured user and password in order to validate if their values
        should be retrieved from the OS system variables

        format ex. 'user' : 'env.OS_VAR_USER'
        format ex. 'user' : 'env.OS_VAR_PASS'

        This mechanism is useful to avoid setting the user credentials
        as plain text in json file and that way it is hidden.

        :param config_file: Configuration file name in json format
        :return: None
        """
        LOGGER.info("Parsing Configuration file: \"%s\"", config_file)
        self.config_obj = config_utils.Config(config_file)

        # check if config_obj has environment variable for USER
        if PageManager.ENV_PREFIX in self.config_obj.get_user().lower().strip():
            env_user = self.config_obj.get_user().strip().replace(PageManager.ENV_PREFIX, "")
            LOGGER.debug("Retrieving value from environment variable: \"%s\"", env_user)
            self._credentials['user'] = os.environ.get(env_user)
            if self._credentials['user'] is None:
                raise AssertionError(
                    "Environment variable \"{0}\" does not exist. "
                    "Please configure it with the confluence credentials".format(env_user))
        else:
            self._credentials['user'] = self.config_obj.get_user()

        # check if config_obj has environment variable for PASSWORD
        if PageManager.ENV_PREFIX in self.config_obj.get_password().lower().strip():
            env_pass = self.config_obj.get_password().strip().replace(PageManager.ENV_PREFIX, "")
            LOGGER.debug("Retrieving value from environment variable: \"%s\"", env_pass)
            self._credentials['password'] = os.environ.get(env_pass)
            if self._credentials['password'] is None:
                raise AssertionError(
                    "Environment variable \"{0}\" does not exist. "
                    "Please configure it with the confluence credentials".format(env_pass))
        else:
            self._credentials['password'] = self.config_obj.get_password()

    def load_template_from_file(self, html_template_file):
        # type: (str) -> None
        """Loads html template from a source file

        :param html_template_file: path to html template file
        :return: None
        """
        LOGGER.info("Parsing HTML template file: \"%s\"", html_template_file)
        # Read HTML Template for Confluence
        self.template_obj = file_utils.ConfluenceHtmlTemplate(html_template_file)

    def _replace_variables_in_template(self):
        # type: () -> None
        """Replace variables configured in config file into the HTML template
        :return: None
        """
        LOGGER.debug("Replacing variables in HTML Template")
        for template_key, value in self.config_obj.template_variables.items():
            if template_key in self._html_template:
                self._html_template = self._html_template.replace(template_key, value)
            else:
                LOGGER.warning("Variable to replace was not found "
                               "in template: \"%s\"", template_key)

    @staticmethod
    def get_space_from_url(url):
        # type: (str) -> str
        """Retrieves the space from a normal confluence page URL.
        This function will not accept URLs with page ID in it.

        Ex: http://buic-confluence.conti.de:8090/display/IIC/I+IC
        will return 'IIC' as the space

        :param url: full url of the confluence page to look for
        :return: a string with the confluence space
        """
        url_pattern = re.compile(r'https?://[-\w_.]*:?\d{0,5}(.*)')
        url_data_pattern = re.compile(r'/display/([-\w_?~]*)/(.*)')

        if re.search(url_pattern, url):
            url_data = re.match(url_pattern, url).group(1)
            space = re.match(url_data_pattern, url_data).group(1)
        else:
            raise Exception("Confluence space not found in URL: \"{0}\"".format(url))
        return space

    @staticmethod
    def get_page_title_from_url(url, formatted=True):
        # type: (str, bool) -> str
        """Retrieves the page title from a normal confluence page URL.
        This function will not accept URLs with page ID in it.

        if 'formatted' is set to True, it will replace all '+' characters for spaces

        formatted=True:
        Ex: http://buic-confluence.conti.de:8090/display/~uidj5418/My+Page+1
        will return 'My Page 1' as the page title

        formatted=False:
        Ex: http://buic-confluence.conti.de:8090/display/~uidj5418/My+Page+1
        will return 'My+Page+1' as the page title

        :param url: full url of the confluence page to look for
        :param formatted:
            flag to indicated if '+' characters should be replace for spaces
        :return:
        """

        url_pattern = re.compile(r'https?://[-\w_.]*:?\d{0,5}(.*)')
        url_data_pattern = re.compile(r'/display/([-\w_?~]*)/(.*)')

        if re.search(url_pattern, url):
            url_data = re.match(url_pattern, url).group(1)
            title = re.match(url_data_pattern, url_data).group(2)
            if formatted:
                title = title.replace('+', ' ')
        else:
            raise Exception("Confluence page title not found in URL: \"{0}\"".format(url))
        return title

    @staticmethod
    def is_url(url):
        # type: (str) -> bool
        """Returns True if a given string is a valid URL
        ex. http://buic-confluence.conti.de:8090/display/page
        ex. http://buic-confluence.conti.de:8090/pages/viewpage.action?pageId=102948555

        :param url:     string with the url
        :return: True if valid URL is given. Otherwise returns False
        :rtype: bool
        """
        url_pattern = re.compile(r'https?://[-\w_.]*:?\d{0,5}(.*)')
        if url_pattern.match(url):
            return True
        return False

    @staticmethod
    def is_id_in_url(url):
        # type: (str) -> bool
        """Returns True if a given URL has page id in it
        ex. http://buic-confluence.conti.de:8090/pages/viewpage.action?pageId=102948555

        :param url:     string with the url
        :return: True if URL has page id in it. Otherwise returns False
        :rtype: bool
        """
        id_pattern = re.compile(r'.*pageId=(\d+)$')
        if id_pattern.match(url):
            return True
        return False

    @staticmethod
    def get_id_from_url(url):
        # type: (str) -> str
        """Retrieves the page id number from a confluence page URL
        that has the format with 'pageId' variable.

        Ex: http://buic-confluence.conti.de:8090/pages/viewpage.action?pageId=102948555
        will return '102948555' as the page id

        :param url: full url of the confluence page to look for
        :return: a string with the confluence space
        """
        url_pattern = re.compile(r'https?://[-\w_.]*:?\d{0,5}(.*)')
        url_id_pattern = re.compile(r'.*pageId=(\d+)$')

        if re.search(url_pattern, url):
            url_data = re.match(url_pattern, url).group(1)
            page_id = re.match(url_id_pattern, url_data).group(1)
        else:
            raise Exception("pageId not found in URL: \"{0}\"".format(url))
        return page_id

    def _setup_html_template(self):
        # type: () -> None
        """

        :return: None
        """
        if self._html_template is None:
            self._html_template = self.get_page_content_by_url(self._template_source)
        self._replace_variables_in_template()

    @authenticate
    def generate_page(self):
        # type: () -> api.Page
        """Generates a confluence page in the server
        depending on the configuration set

        HTML template source will be parsed from configuration
        in order to know if it will be retrieved from another
        confluence page or from a file.

        After having the HTML content, this will be posted into a new
        confluence page created by this function

        :return: None
        """

        self._setup_html_template()

        confluence_page = None
        # Start Confluence API
        with api.ConfluenceClient(
            self.config_obj.get_host_url(),
            self._credentials['user'],
            self._credentials['password']
        ) as confluence_instance:

            LOGGER.info("Creating Confluence Page: \"%s\" inside Space: \"%s\"",
                        self.config_obj.get_page_title(),
                        self.config_obj.get_space_key())

            # Create confluence page with HTML template content
            try:
                confluence_page = confluence_instance.create_page(
                    self.config_obj.get_page_title(),
                    self.config_obj.get_space_key(),
                    self._html_template,
                    self.config_obj.get_parent_page_id()
                )
            except Exception as ex:
                raise AssertionError("ERROR: Confluence page could not be created: {0}".format(ex))

            gen_page_url = "{host}{page_link}".format(
                host=confluence_page.base_url,
                page_link=confluence_page.permanent_link)

            LOGGER.info("Confluence Page successfully created: %s", gen_page_url)
        return confluence_page

    @authenticate
    def delete_page(self, page_id):
        # type: (str) -> None
        """Deletes a confluence page that matches the given page_id number.

        :param page_id: id number of the confluence page to delete
        :return:
        """
        # Start Confluence API
        with api.ConfluenceClient(
            self.config_obj.get_host_url(),
            self._credentials['user'],
            self._credentials['password']
        ) as confluence_instance:

            LOGGER.info("Delete Confluence Page with ID: \"%s\" inside Space: \"%s\"",
                        page_id,
                        self.config_obj.get_space_key())
            try:
                confluence_instance.delete_content(page_id)
            except Exception as ex:
                raise AssertionError("Confluence page could not be deleted: {0}".format(ex))

    @authenticate
    def get_page_content_by_id(self, page_id, encoding='ascii'):
        # type: (str, [str]) -> str
        """Retrieves de HTML content from a confluence page
        that matches the given page_id number.
        ex. 102948555

        :param page_id: id number of the confluence page
        :param encoding:
            the html content retrieved is unicode, so ascii (default value)
            is recommended for the conversion of the content
        :return: string with the html content of the page
        """
        # Start Confluence API
        with api.ConfluenceClient(
            self.config_obj.get_host_url(),
            self._credentials['user'],
            self._credentials['password']
        ) as confluence_instance:
            LOGGER.debug("Getting Content from Page with ID: \"%s\"", page_id)

            try:
                page = confluence_instance.get_content(page_id)
                content = page.content
                if encoding == 'ascii':
                    content = str(content)
                return content
            except Exception as ex:
                raise AssertionError(
                    "Confluence page with ID \"{id}\" could not "
                    "be retrieved from Server: {error}".format(
                        id=page_id,
                        error=ex))

    @authenticate
    def get_page_content_by_url(self, page_url, encoding='ascii'):
        # type: (str, str) -> str
        """Retrieves de HTML content from a confluence page that matches
        the given URL.

        This URL can be in 2 formats, with pageID or with space and title.
        ex. http://buic-confluence.conti.de:8090/display/page
        ex. http://buic-confluence.conti.de:8090/pages/viewpage.action?pageId=102948555

        :param page_url: URL of the confluence page to look for
        :param encoding:
            the html content retrieved is unicode, so ascii (default value)
            is recommended for the conversion of the content
        :return: string with the html content of the page
        """
        # validate URL
        if not self.is_url(page_url):
            raise Exception("Given value is not a valid URL: "
                            "\"{url}\" ".format(url=page_url))

        # -----------------------------
        # URL with page ID
        # -----------------------------
        if self.is_id_in_url(page_url):
            # retrieve id from url and try to search
            # for the corresponding confluence page
            page_id = self.get_id_from_url(page_url)
            page_content = self.get_page_content_by_id(page_id)
        # -----------------------------
        # URL with space and title
        # -----------------------------
        else:
            # retrieve space and page title from url
            # in order to search for the confluence page
            space_key = self.get_space_from_url(page_url)
            page_title = self.get_page_title_from_url(page_url)
            page_content = self.get_page_content_by_title(
                page_title,
                space_key,
                encoding)

        return page_content

    def get_page_content_by_title(self, title, space, encoding='ascii'):
        # type: (str, str, [str]) -> str
        """Retrieves de HTML content from a confluence page that
        that is contained inside 'space' and matches with the 'title'

        :param title: title of the confluence page
        :param space: space in which the confluence page is contained
        :param encoding:
            the html content retrieved is unicode, so ascii (default value)
            is recommended for the conversion of the content
        :return: string with the html content of the page
        """
        # Start Confluence API
        with api.ConfluenceClient(
            self.config_obj.get_host_url(),
            self._credentials['user'],
            self._credentials['password']
        ) as confluence_instance:

            # try to search the confluence page in that space
            # with that title, if not found None will be returned
            page_to_search = confluence_instance.get_page_from_title(title, space)

            if page_to_search is None:
                raise Exception(
                    "Confluence page with title \"{title}\" "
                    "in space \"{space}\" could not be found.".format(
                        title=title,
                        space=space))

            page_content = page_to_search.content
            if encoding == 'ascii':
                page_content = str(page_content)

        return page_content
