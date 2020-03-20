
class Headers(dict):
    """
    Headers dict for storing request headers
    """

    def set_header(self, key, value):
        """
        Sets the header with given value

        Arguments:
        key: Key for the header.
        value: Value for the header.
        """
        dict.__setitem__(self, key, value)

    def to_grpc_metadata(self):
        return ((k,v) for k,v in self.items())

