from google.protobuf import json_format
from werkzeug.wrappers import Request, Response

from . import base
from . import ctxkeys
from . import exceptions
from . import errors


class TwirpWSGIApp(base.TwirpBaseApp):

    def __call__(self, environ, start_response):
        ctx = self._ctx_class()
        try:
            return self.handle_request(ctx, environ, start_response)
        except Exception as e:

            return self.handle_error(ctx, e, environ, start_response)

    def handle_request(self, ctx, environ, start_response):
        request = Request(environ)
        ctx["request"] = request
        self._hook.request_received(ctx=ctx)

        http_method = request.method
        if http_method != "POST":
            raise exceptions.TwirpServerException(
            code=errors.Errors.BadRoute,
            message="unsupported method " + http_method + " (only POST is allowed)",
            meta={"twirp_invalid_route": http_method + " " + scope['path']},
        )
        ctx["http_method"] = "POST"
        ctx["url"] = request.path
        ctx["content-type"] = request.headers["Content-Type"]

        endpoint, func, decode, encode = self.get_endpoint_methods(request)
        ctx["endpoint"] = endpoint
        request_routed.send(ctx)

        input_arg = decode(request)
        ctx["input"] = input_arg
        result = func(input_arg, ctx=ctx)
        ctx["output"] = result
        response = encode(result)
        ctx["response"] = response
        response_prepared.send(ctx)

        ctx["status_code"] = 200
        response_sent.send(ctx)

        return response(environ, start_response)

    def handle_error(self, ctx, exc, environ, start_response):
        base_err = {
            "type": "Internal",
            "msg": ("There was an error but it could not be "
                    "serialized into JSON"),
            "meta": {}
        }
        response = Response()
        response.status_code = 500

        try:
            err = base_err
            if isinstance(exc, TwirpServerException):
                err["code"] = exc.code.value
                err["msg"] = exc.message
                if exc.meta:
                    for k, v in exc.meta.items():
                        err["meta"][k] = str(v)
                response.status_code = Errors.get_status_code(exc.code)
            else:
                err["msg"] = "Internal non-Twirp Error"
                err["code"] = 500
                err["meta"] = {"raw_error": str(exc)}

            for k, v in ctx.items():
                err["meta"][k] = str(v)

            response.set_data(json.dumps(err))
        except Exception as e:
            err = base_err
            err["meta"] = {"original_error": str(exc),
                           "handling_error": str(e)}
            response.set_data(json.dumps(err))

        # Force json for errors.
        response.headers["Content-Type"] = "application/json"

        ctx["status_code"] = response.status_code
        ctx["response"] = response
        ctx["exception"] = exc
        error_occurred.send(ctx)

        return response(environ, start_response)
