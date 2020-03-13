from verloopcontext.header import VERLOOP_CLIENT_ID_HEADER

from .. import exceptions
from .. import errors
from .. import ctxkeys
from .. import hook


class ClientIDFromHeadersHook(hook.TwirpHook):
    def request_routed(self, *args, ctx):
        hdrs = ctx.get(ctxkeys.RAW_HEADERS)
        ctx.get_headers().update(hdrs)
        try:
            ctx.client_id
        except KeyError:
            raise exceptions.RequiredArgument(argument=VERLOOP_CLIENT_ID_HEADER)

