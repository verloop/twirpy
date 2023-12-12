import asyncio
import json
from typing import Optional

import aiohttp

from . import exceptions
from . import errors


class AsyncTwirpClient:
    def __init__(
        self, address: str, session: Optional[aiohttp.ClientSession] = None
    ) -> None:
        self._address = address
        self._session = session

    async def _make_request(
        self, *, url, ctx, request, response_obj, session=None, **kwargs
    ):
        headers = ctx.get_headers()
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        kwargs["headers"]["Content-Type"] = "application/protobuf"

        if session is None:
            session = self._session
        if not isinstance(session, aiohttp.ClientSession):
            raise TypeError(f"invalid session type '{type(session).__name__}'")

        try:
            async with await session.post(
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
        except asyncio.TimeoutError as e:
            raise exceptions.TwirpServerException(
                code=errors.Errors.DeadlineExceeded,
                message=str(e) or "request timeout",
                meta={"original_exception": e},
            )
        except aiohttp.ServerConnectionError as e:
            raise exceptions.TwirpServerException(
                code=errors.Errors.Unavailable,
                message=str(e),
                meta={"original_exception": e},
            )
