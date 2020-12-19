
try:
    import http.client as httplib
except ImportError:
    import httplib

try:
    import ujson as json
except:
    import json

from . import errors



class TwirpServerException(httplib.HTTPException):
    def __init__(self, *args, code, message, meta={}):
        try:
            self._code = errors.Errors(code)
        except ValueError:
            self._code = errors.Errors.Unknown
        self._message = message
        self._meta = meta
        super(TwirpServerException, self).__init__(message)

    @property
    def code(self):
        if isinstance(self._code, errors.Errors):
            return self._code
        return errors.Errors.Unknown

    @property
    def message(self):
        return self._message

    @property
    def meta(self):
        return self._meta

    def to_dict(self):
        err = {
            "code": self._code.value,
            "msg": self._message,
            "meta": {}
        }
        for k, v in self._meta.items():
            err["meta"][k] = str(v)
        return err

    def to_json_bytes(self):
        return json.dumps(self.to_dict()).encode('utf-8')

    @staticmethod
    def from_json(err_dict):
        return TwirpServerException(
            code=err_dict.get('code', errors.Errors.Unknown),
            message=err_dict.get('msg',''),
            meta=err_dict.get('meta',{}),
        )

def InvalidArgument(*args, argument, error):
    return TwirpServerException(
        code=errors.Errors.InvalidArgument,
        message="{} {}".format(argument, error),
        meta={
            "argument":argument
        }
    )

def RequiredArgument(*args, argument):
    return InvalidArgument(
        argument=argument,
        error="is required"
    )
