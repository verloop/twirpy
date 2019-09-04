import requests

from . import exceptions
from . import errors

class TwirpClient(object):
    def __init__(self, address, timeout=5):
        self._address = address
        self._timeout = timeout

    def _make_request(self, *args, url, ctx, request, response_obj, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self._timeout
        headers = ctx.get_headers()
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        kwargs['headers']['Content-Type'] = 'application/protobuf'
        try:
            resp = requests.post(url=self._address+url, data=request.SerializeToString(), **kwargs)
            if resp.status_code == 200:
                response = response_obj()
                response.ParseFromString(resp.content)
                return response
            else:
                raise exceptions.TwirpServerException.from_json(resp.json())
            # Todo: handle error
        except requests.exceptions.Timeout as e:
            raise exceptions.TwirpServerException(
                code=errors.Errors.DeadlineExceeded,
                message=e.message,
                meta={"original_exception": e},
            )
        except requests.exceptions.ConnectionError as e:
            raise exceptions.TwirpServerException(
                code=errors.Errors.Unavailable,
                message=e.message,
                meta={"original_exception": e},
            )
