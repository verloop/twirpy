from . import exceptions
from . import errors


class TwirpServer(object):

    def __init__(self, *args, service):
        self.service = service
        self._endpoints = {}
        self._prefix = ""

    @property
    def prefix(self):
        return self._prefix

    def get_endpoint(self, path):
        (_, url_pre, rpc_method) = path.rpartition(self._prefix + "/")
        if not url_pre or not rpc_method:
            raise exceptions.TwirpServerException(
                code=errors.Errors.BadRoute,
                message="no handler for path " + path,
                meta={"twirp_invalid_route": "POST " + path},
            )

        endpoint = self._endpoints.get(rpc_method, None)
        if not endpoint:
            raise exceptions.TwirpServerException(
                code=errors.Errors.Unimplemented,
                message="service has no endpoint " + rpc_method,
                meta={"twirp_invalide_route": "POST " + path})


        return endpoint

