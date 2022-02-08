import functools
from collections import namedtuple

from google.protobuf import json_format
from google.protobuf import message
from google.protobuf import symbol_database as _symbol_database


from . import context

from . import server
from . import exceptions
from . import errors
from . import hook as vtwirp_hook

_sym_lookup = _symbol_database.Default().GetSymbol

Endpoint = namedtuple("Endpoint", ["service_name", "name", "function", "input", "output"])


class TwirpBaseApp(object):
    def __init__(self, *middlewares, hook=None, prefix="", max_receive_message_length=1024*100*100, ctx_class=None):
        self._prefix = prefix
        self._services = {}
        self._max_receive_message_length = max_receive_message_length
        if ctx_class is None:
            ctx_class = context.Context
        assert issubclass(ctx_class, context.Context)
        self._ctx_class = ctx_class
        self._middlewares = middlewares
        if hook is None:
            hook = vtwirp_hook.TwirpHook()
        assert isinstance(hook, vtwirp_hook.TwirpHook)
        self._hook = hook

    def add_service(self, svc: server.TwirpServer):
        self._services[self._prefix+svc.prefix] = svc

    def _get_endpoint(self, path):
        svc = self._services.get(path.rsplit("/", 1)[0], None)
        if svc is None:
            raise exceptions.TwirpServerException(
                code=errors.Errors.NotFound,
                message="not found"
            )

        return svc.get_endpoint(path[len(self._prefix):])

    @staticmethod
    def json_decoder(body, data_obj=None):
        data = data_obj()
        try:
            json_format.Parse(body, data)
        except json_format.ParseError as exc:
            raise exceptions.TwirpServerException(
                code=errors.Errors.Malformed,
                message="the json request could not be decoded",
            ) from exc
        return data

    @staticmethod
    def json_encoder(value, data_obj=None):
        if not isinstance(value, data_obj):
            raise exceptions.TwirpServerException(
                code=errors.Errors.Internal,
                message=("bad service response type " + str(type(value)) +
                 ", expecting: " + data_obj.DESCRIPTOR.full_name))

        return json_format.MessageToJson(value, preserving_proto_field_name=True).encode('utf-8'), {"Content-Type": "application/json"}

    @staticmethod
    def proto_decoder(body, data_obj=None):
        data = data_obj()
        try:
            data.ParseFromString(body)
        except message.DecodeError as exc:
            raise exceptions.TwirpServerException(
                code=errors.Errors.Malformed,
                message="the protobuf request could not be decoded",
            ) from exc
        return data

    @staticmethod
    def proto_encoder(value, data_obj=None):
        if not isinstance(value, data_obj):
            raise exceptions.TwirpServerException(
                code=errors.Errors.Internal,
                message=("bad service response type " + str(type(value)) +
                 ", expecting: " + data_obj.DESCRIPTOR.full_name))

        return value.SerializeToString(), {"Content-Type": "application/protobuf"}

    def _get_encoder_decoder(self, endpoint, headers):
        ctype = headers.get('content-type', None)
        if "application/json" == ctype:
            decoder = functools.partial(self.json_decoder, data_obj=endpoint.input)
            encoder = functools.partial(self.json_encoder, data_obj=endpoint.output)
        elif "application/protobuf" == ctype:
            decoder = functools.partial(self.proto_decoder, data_obj=endpoint.input)
            encoder = functools.partial(self.proto_encoder, data_obj=endpoint.output)
        else:
            raise exceptions.TwirpServerException(
                code=errors.Errors.BadRoute,
                message="unexpected Content-Type: " + ctype
            )
        return encoder, decoder
