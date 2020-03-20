
class Headers(dict):
    """
    Headers dict for storing request headers
    """

    def set_header(self, key, value):
        """
        Sets the header with given value
        """
        dict.__setitem__(self, key, value)

    def to_grpc_metadata(self):
        return ((k,v) for k,v in self.items())

