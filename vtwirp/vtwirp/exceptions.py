
try:
    import http.client as httplib
except ImportError:
    import httplib

import ujson as json

from . import errors



class TwirpServerException(httplib.HTTPException):
    def __init__(self, *args, code, message, meta={}):
        if isinstance(code, errors.Errors):
            self._code = code
        else:
            self._code = errors.Errors.Unknown
        self._message = message
        self._meta = meta
        super(TwirpServerException, self).__init__(message)

    def to_dict(self):
        err = {
            "code": self._code,
            "msg": self._message,
            "meta": {}
        }
        for k, v in self._meta.items():
            err["meta"][k] = str(v)
        return err

    def to_json_bytes(self):
        return json.dumps(self.to_dict()).encode('utf-8')

    @staticmethod
    def from_json_bytes(data):
        err_dict = json.loads(data.decode('utf-8'))
        return TwirpServerException(
            code=err_dict.get('code', errors.Errors.Unknown),
            message=err_dict.get('msg',''),
            meta=err_dict.get('meta',{}),
        )
