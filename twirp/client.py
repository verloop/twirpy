import json
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
            try:
                raise exceptions.TwirpServerException.from_json(resp.json())
            except json.JSONDecodeError:
                raise self._twirp_error_from_intermediary(resp) from None
            # Todo: handle error
        except requests.exceptions.Timeout as e:
            raise exceptions.TwirpServerException(
                code=errors.Errors.DeadlineExceeded,
                message=str(e),
                meta={"original_exception": e},
            )
        except requests.exceptions.ConnectionError as e:
            raise exceptions.TwirpServerException(
                code=errors.Errors.Unavailable,
                message=str(e),
                meta={"original_exception": e},
            )

    @staticmethod
    def _twirp_error_from_intermediary(resp):
        # see https://twitchtv.github.io/twirp/docs/errors.html#http-errors-from-intermediary-proxies
        meta = {
            'http_error_from_intermediary': 'true',
            'status_code': str(resp.status_code),
        }

        if resp.is_redirect:
            # twirp uses POST which should not redirect
            code = errors.Errors.Internal
            location = resp.headers.get('location')
            message = 'unexpected HTTP status code %d "%s" received, Location="%s"' % (
                resp.status_code,
                resp.reason,
                location,
            )
            meta['location'] = location

        else:
            code = {
                400: errors.Errors.Internal,  # JSON response should have been returned
                401: errors.Errors.Unauthenticated,
                403: errors.Errors.PermissionDenied,
                404: errors.Errors.BadRoute,
                429: errors.Errors.ResourceExhausted,
                502: errors.Errors.Unavailable,
                503: errors.Errors.Unavailable,
                504: errors.Errors.Unavailable,
            }.get(resp.status_code, errors.Errors.Unknown)

            message = 'Error from intermediary with HTTP status code %d "%s"' % (
                resp.status_code,
                resp.reason,
            )
            meta['body'] = resp.text

        return exceptions.TwirpServerException(code=code, message=message, meta=meta)
