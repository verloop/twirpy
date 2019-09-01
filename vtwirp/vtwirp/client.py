import requests
import vcontext

from . import exceptions
from . import errors

class TwirpClient(object):
    def __init__(self, address, timeout=5):
        self._address = address
        self._timeout = timeout
    
    def _make_request(self, *args, url, ctx, request, response_obj, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self._timeout
        headers = vcontext.ExtractHeaders(ctx)
        if 'headers' in kwargs:
            kwargs['headers'] = headers.update(kwargs['headers'])
        kwargs['headers']['Content-Type'] = 'application/protobuf'
        try:
            resp = requests.post(url=self._address+url, body=request.SerializeToString())
            if resp.status_code == 200:
                response = response_obj()
                response.ParseFromString(resp.content)
                return response
            else:
                raise exceptions.TwirpServerException.from_json(resp.json())
            # Todo: handle error
        except requests.exceptions.TimeoutException as e:
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
