from . import logging
from . import header


class Context(object):
    def __init__(self, *args, logger=None, headers=None):
        self._values = {}
        if logger is None:
            logger = logging.get_logger()
        self._logger = logger
        if headers is None:
            headers = header.Headers()
        self._headers = headers

    def set(self, key, value):
        self._values[key] = value

    def get(self, key):
        return self._values[key]

    def get_logger(self):
        return self._logger
    
    def set_logger(self, logger):
        self._logger = logger

    def get_headers(self):
        return self._headers

    def set_header(self, key, value):
        self._headers.set_header(key, value)

