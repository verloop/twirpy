import functools
from collections import namedtuple

from google.protobuf import json_format
from google.protobuf import symbol_database as _symbol_database


from vcontext import context

from . import service
from . import exceptions
from . import errors

_sym_lookup = _symbol_database.Default().GetSymbol

Endpoint = namedtuple("Endpoint", ["name", "function", "input", "output"])


class TwirpBaseApp(object):
    def __init__(self, prefix="", ctx_class=None):
        self._prefix = prefix
        self._services = {}
        if ctx_class is None:
            ctx_class = context.Context
        assert issubclass(ctx_class, context.Context)
        self._ctx_class = ctx_class

    def add_service(self, svc: service.TwirpService):
        self._services[self._prefix+svc.prefix] = svc

    def _get_endpoint(self, path):
        svc = self._services.get(path.rsplit("/", 1)[0], None)
        if svc is None:
            raise exceptions.TwirpServerException(
                code=errors.Errors.NotFound,
                message="not found"
            )

        return svc.get_endpoint_methods(path[len(self._prefix):])

    @staticmethod
    def json_decoder(request, data_obj=None):
        body = request.get_data(as_text=False)
        data = data_obj()
        json_format.Parse(body, data)
        return data

    @staticmethod
    def json_encoder(value, data_obj=None):
        if not isinstance(value, data_obj):
            raise exceptions.TwirpServerException(
                code=errors.Errors.Internal,
                message=("bad service response type " + str(type(value)) +
                 ", expecting: " + data_obj.DESCRIPTOR.full_name))

        return json_format.MessageToJson(value, preserving_proto_field_name=True), ("Content-Type", "application/json")

    @staticmethod
    def proto_decoder(request, data_obj=None):
        body = request.get_data(as_text=False)
        data = data_obj()
        data.ParseFromString(body)
        return data

    @staticmethod
    def proto_encoder(value, data_obj=None):
        if not isinstance(value, data_obj):
            raise exceptions.TwirpServerException(
                code=errors.Errors.Internal,
                message=("bad service response type " + str(type(value)) +
                 ", expecting: " + data_obj.DESCRIPTOR.full_name))

        return value.SerializeToString(), ("Content-Type", "application/protobuf")

    def _get_encoder_decoder(self, endpoint, headers):
        ctype = headers['content-type']
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
