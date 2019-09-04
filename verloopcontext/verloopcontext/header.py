class headersKey:
    pass

HEADERS_KEY = headersKey()

VERLOOP_CLIENT_ID_HEADER = 'x-verloop-client-id'
VERLOOP_ENTITY_ID_HEADER = 'x-verloop-entity-id'
VERLOOP_CALLER_IDENTITY_HEADER = 'x-verloop-caller-identity'

class Headers(dict):

    def set_client_id(self, client_id):
        dict.__setitem__(self, VERLOOP_CLIENT_ID_HEADER, client_id)

    @property
    def client_id(self):
        cl_id =  dict.__getitem__(self, VERLOOP_CLIENT_ID_HEADER)
        if not cl_id:
            raise KeyError(VERLOOP_CLIENT_ID_HEADER)
        return cl_id

    @property
    def entity_id(self):
        try:
            return dict.__getitem__(self, VERLOOP_ENTITY_ID_HEADER)
        except KeyError:
            return ""

    @property
    def caller_identity(self):
        try:
            return dict.__getitem__(self, VERLOOP_CALLER_IDENTITY_HEADER)
        except KeyError:
            return ""

    def to_grpc_metadata(self):
        return ((k,v) for k,v in self.items())