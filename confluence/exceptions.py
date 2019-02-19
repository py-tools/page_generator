"""
Module with Exception definitions
"""


class ConfluenceError(Exception):
    """Corresponds to 413 errors on the REST API.
    """

    def __init__(self, path, params, response, msg=None):
        # type: (str, dict, requests.Response, [str]) -> None
        if not msg:
            msg = 'General resource error accessing path {}'.format(path)
        self.path = path
        self.params = params
        self.response = response
        super(ConfluenceError, self).__init__(msg)


class ConfluencePermissionError(ConfluenceError):
    """Corresponds to 403 errors on the REST API.
    """

    def __init__(self, path, params, response):
        # type: (str, dict, requests.Response) -> None
        msg = 'User has insufficient permissions to perform ' \
              'that operation on the path {}'.format(path)
        super(ConfluencePermissionError, self).__init__(path, params, response, msg)
