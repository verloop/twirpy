import asyncio
import json
import aiohttp

from . import exceptions
from . import errors

class AsyncTwirpClient:
    def __init__(self, address, timeout=5):
        self._address = address
        self._timeout = timeout
        self._session = None

    def __del__(self):
        if self._session:
            asyncio.create_task(self._session.close())

    @property
    def session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession(
                self._address, timeout=aiohttp.ClientTimeout(total=self._timeout))
        return self._session

    async def _make_request(self, *, url, ctx, request, response_obj, session=None, **kwargs):
        headers = ctx.get_headers()
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        kwargs['headers']['Content-Type'] = 'application/protobuf'
        try:
            async with await (session or self.session).post(
                url=url, data=request.SerializeToString(), **kwargs
            ) as resp:
                if resp.status == 200:
                    response = response_obj()
                    response.ParseFromString(await resp.read())
                    return response
                try:
                    raise exceptions.TwirpServerException.from_json(await resp.json())
                except (aiohttp.ContentTypeError, json.JSONDecodeError):
                    raise exceptions.twirp_error_from_intermediary(
                        resp.status, resp.reason, resp.headers, await resp.text()
                    ) from None
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
