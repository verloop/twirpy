import asyncio
import functools
import typing

import ujson as json

from . import base
from . import exceptions
from . import errors

try:
    import contextvars  # Python 3.7+ only.
except ImportError:  # pragma: no cover
    contextvars = None  # type: ignore

# Lifted from starlette.concurrency
async def run_in_threadpool(func: typing.Callable, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
    loop = asyncio.get_event_loop()
    if contextvars is not None:  # pragma: no cover
        # Ensure we run in the same context
        child = functools.partial(func, *args, **kwargs)
        context = contextvars.copy_context()
        func = context.run
        args = (child,)
    elif kwargs:  # pragma: no cover
        # loop.run_in_executor doesn't accept 'kwargs', so bind them in here
        func = functools.partial(func, **kwargs)
    return await loop.run_in_executor(None, func, *args)

class TwirpASGIApp(base.TwirpBaseApp):

    async def __call__(self, scope, receive, send):
        assert scope['type'] == 'http'
        ctx = self._ctx_class()
        try:
            http_method = scope['method']
            if http_method != "POST":
                raise exceptions.TwirpServerException(
                code=errors.Errors.BadRoute,
                message="unsupported method " + http_method + " (only POST is allowed)",
                meta={"twirp_invalid_route": http_method + " " + scope['path']},
            )

            
            endpoint = self._get_endpoint(scope['path'])

            headers = {k.decode('utf-8'): v.decode('utf-8') for (k,v) in scope['headers']}
            decoder, encoder = self._get_encoder_decoder(endpoint, headers)
            body = await receive()
            # Todo: middlewares
            request = decoder(body)
            if asyncio.iscoroutinefunction(endpoint.function):
                response_data = await endpoint.function(ctx, request)
            else:
                response_data = run_in_threadpool(endpoint.function, ctx, request)
            
            body_bytes, headers = encoder(response_data)
            # Todo: middleware
            await self._respond(send,200,headers,body_bytes)
        except Exception as e:
            await self.handle_error(ctx, e, scope, receive, send)



    async def handle_error(self, ctx, exc, scope, receive, send):
        status = 500
        body_bytes = b'{}'

        try:
            if not isinstance(exc, exceptions.TwirpServerException):
                exc = exceptions.TwirpServerException(
                    code=errors.Errors.Internal,
                    message= "Internal non-Twirp Error"
                )

            body_bytes = exc.to_json_bytes()
            status = errors.Errors.get_status_code(exc.code)
        except Exception as e:
            exc = exceptions.TwirpServerException(
                    code=errors.Errors.Internal,
                    message="There was an error but it could not be serialized into JSON"
            )
            body_bytes = exc.to_json_bytes()

        # todo: middlewares
        await self._respond(send,status,{'Content-Type':'application/json'},body_bytes)

    async def _respond(self, send, status, headers, body_bytes):
        headers['Content-Length'] = str(len(body_bytes)).encode('utf-8')
        resp_headers = [{k.encode('utf-8'):v.encode('utf-8')} for (k,v) in headers.items()]
        await send({
                'type': 'http.response.start',
                'status': status,
                'headers': resp_headers,
        })
        await send({
             'type': 'http.response.body',
             'body': body_bytes,
        })
