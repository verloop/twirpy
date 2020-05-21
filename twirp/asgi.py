import asyncio
import functools
import typing
import traceback

try:
    import ujson as json
except:
    import json

from . import base
from . import ctxkeys
from . import errors
from . import exceptions



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

def thread_pool_runner(func):
    async def run(ctx, request):
        return await run_in_threadpool(func, ctx, request)
    return run

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

            headers = {k.decode('utf-8'): v.decode('utf-8') for (k,v) in scope['headers']}
            ctx.set(ctxkeys.RAW_REQUEST_PATH, scope['path'])
            ctx.set(ctxkeys.RAW_HEADERS, headers)
            self._hook.request_received(ctx=ctx)

            endpoint = self._get_endpoint(scope['path'])
            encoder, decoder = self._get_encoder_decoder(endpoint, headers)
            # add headers from request into context
            
            ctx.set(ctxkeys.SERVICE_NAME, endpoint.service_name)
            ctx.set(ctxkeys.METHOD_NAME, endpoint.name)
            ctx.set(ctxkeys.RESPONSE_STATUS, 200)
            self._hook.request_routed(ctx=ctx)
            raw_receive = await receive()
            request = decoder(raw_receive.get('body'))
            response_data = await self._with_middlewares(func=endpoint.function, ctx=ctx, request=request)
            self._hook.response_prepared(ctx=ctx)

            body_bytes, headers = encoder(response_data)
            # Todo: middleware
            await self._respond(
                send=send,
                status=200,
                headers=headers,
                body_bytes=body_bytes
            )
            self._hook.response_sent(ctx=ctx)
        except Exception as e:
            await self.handle_error(ctx, e, scope, receive, send)

    def _with_middlewares(self, *args, func, ctx, request):
        chain = iter(self._middlewares + (func,))
        def bind(fn):
            if not asyncio.iscoroutinefunction(fn):
                fn = thread_pool_runner(fn)
            async def nxt(ctx, request):
                try:
                    cur = next(chain)
                    return await fn(ctx, request, bind(cur))
                except StopIteration:
                    pass
                return await fn(ctx, request)
            return nxt
        return bind(next(chain))(ctx,request)


    async def handle_error(self, ctx, exc, scope, receive, send):
        status = 500
        body_bytes = b'{}'
        logger = ctx.get_logger()
        error_data = {}
        ctx.set(ctxkeys.ORIGINAL_EXCEPTION, exc)
        try:
            if not isinstance(exc, exceptions.TwirpServerException):
                error_data['raw_error'] = str(exc)
                error_data['raw_trace'] = traceback.format_exc()
                logger.exception("got non-twirp exception while processing request",**error_data)
                exc = exceptions.TwirpServerException(
                    code=errors.Errors.Internal,
                    message="Internal non-Twirp Error"
                )

            body_bytes = exc.to_json_bytes()
            status = errors.Errors.get_status_code(exc.code)
        except Exception as e:
            exc = exceptions.TwirpServerException(
                    code=errors.Errors.Internal,
                    message="There was an error but it could not be serialized into JSON"
            )
            error_data['raw_error'] = str(exc)
            error_data['raw_trace'] = traceback.format_exc()
            logger.exception("got exception while processing request",**error_data)
            body_bytes = exc.to_json_bytes()

        ctx.set_logger(logger.bind(**error_data))
        ctx.set(ctxkeys.RESPONSE_STATUS, status)
        self._hook.error(ctx=ctx, exc=exc)
        await self._respond(
            send=send,
            status=status,
            headers={'Content-Type':'application/json'},
            body_bytes=body_bytes
            )
        self._hook.response_sent(ctx=ctx)

    async def _respond(self, *args, send, status, headers, body_bytes):
        headers['Content-Length'] = str(len(body_bytes))
        resp_headers = [(k.encode('utf-8'),v.encode('utf-8')) for (k,v) in headers.items()]
        await send({
                'type': 'http.response.start',
                'status': status,
                'headers': resp_headers,
        })
        await send({
             'type': 'http.response.body',
             'body': body_bytes,
        })
