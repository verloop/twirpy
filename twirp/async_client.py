import json
import aiohttp

from . import exceptions
from . import errors


class AsyncTwirpClient:
    def __init__(self, address, timeout=5):
        self._address = address
        self._timeout = timeout
        self._http_session = None

    @property
    def http_session(self) -> aiohttp.ClientSession:
        if self._http_session is None:
            self._http_session = aiohttp.ClientSession(
                self._address, timeout=aiohttp.ClientTimeout(total=self._timeout))
        return self._http_session

    async def _make_request(self, *args, url, ctx, request, response_obj, **kwargs):
        headers = ctx.get_headers()
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        kwargs['headers']['Content-Type'] = 'application/protobuf'
        try:
            resp = await self.http_session.post(url=url, data=request.SerializeToString(), **kwargs)
            if resp.status == 200:
                response = response_obj()
                response.ParseFromString(resp.content)
                return response
            try:
                raise exceptions.TwirpServerException.from_json(await resp.json())
            except (aiohttp.ContentTypeError, json.JSONDecodeError):
                raise exceptions.twirp_error_from_intermediary(
                    resp.status, resp.reason, resp.headers, await resp.text) from None
            # Todo: handle error
        except aiohttp.ServerTimeoutError as e:
            raise exceptions.TwirpServerException(
                code=errors.Errors.DeadlineExceeded,
                message=str(e),
                meta={"original_exception": e},
            )
        except aiohttp.ServerConnectionError as e:
            raise exceptions.TwirpServerException(
                code=errors.Errors.Unavailable,
                message=str(e),
                meta={"original_exception": e},
            )
