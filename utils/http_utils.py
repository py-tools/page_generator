#!/usr/bin/env python
# coding=utf-8
"""
Module to use utils from HTTP, like authentication
"""

import requests
from requests.auth import HTTPBasicAuth

# https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml
HTTP_CODE_OK = 200


class Auth(object):
    """Main Class for HTTP utils
    """

    def __init__(self):
        pass

    @staticmethod
    def authenticate(host, user, password):
        # type: (str, str, str) -> bool
        """Performs an HTTP GET request into the host given
        with the user and password

        :param host: server host to make http request
        :param user: name of the user
        :param password: password of the user
        :return: True if authentication has succeeded.
        Otherwise, returns False
        """
        # Test User Authentication at Host
        auth_request = requests.get(
            host,
            auth=HTTPBasicAuth(user, password)
        )
        # Check HTTP code status
        if auth_request.status_code != HTTP_CODE_OK:
            return False
        return True
