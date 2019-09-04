class TwirpHook(object):
    # Called as soon as a request is received, always called
    def request_received(self, *args, ctx):
        pass

    # Called once the request is routed, service name known, only called if request is routable
    def request_routed(self,  *args, ctx):
        pass

    # Called once the response is prepared, not called for error cases
    def response_prepared(self,  *args, ctx):
        pass

    # Called if an error occurs
    def error(self,  *args, ctx, exc):
        pass

    # Called after error is sent, always called
    def response_sent(self,  *args, ctx):
        pass


class ChainHooks(TwirpHook):
    def __init__(self, *hooks):
        for hook in hooks:
            assert isinstance(hook, TwirpHook)
        self._hooks = hooks

    def request_received(self, *args, ctx):
        for hook in self._hooks:
            hook.request_received(ctx=ctx)

    def request_routed(self, *args, ctx):
        for hook in self._hooks:
            hook.request_routed(ctx=ctx)

    def response_prepared(self, *args, ctx):
        for hook in self._hooks:
            hook.response_prepared(ctx=ctx)

    def error(self, *args, ctx, exc):
        for hook in self._hooks:
            hook.error(ctx=ctx, exc=exc)


    def response_sent(self, *args, ctx):
        for hook in self._hooks:
            hook.response_sent(ctx=ctx)