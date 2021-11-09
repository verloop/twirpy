from . import logging


class Context(object):
    """Context object for storing context information of 
    request currently being processed.
    """
    def __init__(self, *args, logger = None, headers = None):
        """Create a new Context object

        Keyword arguments:
        logger: Logger that will be used for logging.
        headers: Headers for the request. 
        """
        self._values = {}
        if logger is None:
            logger = logging.get_logger()
        self._logger = logger
        if headers is None:
            headers = {}
        self._headers = headers
        self._response_headers = {}

    def set(self, key, value):
        """Set a Context value
        
        Arguments:
        key: Key for the context key-value pair.
        value: Value to be stored.
        """
        self._values[key] = value

    def get(self, key):
        """Get a Context value
        
        Arguments:
        key: Key for the context key-value pair.
        """
        return self._values[key]

    def get_logger(self):
        """Get current logger used by Context."""
        return self._logger
    
    def set_logger(self, logger):
        """Set logger for this Context
        
        Arguments:
        logger: Logger object to be used.
        """
        self._logger = logger

    def get_headers(self):
        """Get request headers that are currently stored."""
        return self._headers

    def set_header(self, key, value):
        """Set a request header
        
        Arguments:
        key: Key for the header.
        value: Value for the header.
        """
        self._headers[key] = value

    def get_response_headers(self):
        """Get response headers that are currently stored."""
        return self._response_headers

    def set_response_header(self, key, value):
        """Set a response header

        Arguments:
        key: Key for the header.
        value: Value for the header.
        """
        self._response_headers[key] = value
