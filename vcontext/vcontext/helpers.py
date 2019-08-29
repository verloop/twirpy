from . import context

def WithHeaders(headers, ctx=None):
    if ctx is None:
        ctx = context.Context()

    return