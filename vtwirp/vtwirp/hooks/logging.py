import time
import datetime

from .. import ctxkeys
from .. import hook

from verloopcontext import logging

logging.configure()

LOGGING_START_TIME_KEY = 'logging_start_time_key'

class LoggingHook(hook.TwirpHook):
    def request_received(self, *args, ctx):
        start = time.time()
        ctx.set(LOGGING_START_TIME_KEY, start)
        ctx.set_logger(ctx.get_logger().bind(start_time=datetime.datetime.now().isoformat()))

    def request_routed(self, *args, ctx):
       
        headers = ctx.get_headers()
        log_data = {
            "service": ctx.get(ctxkeys.SERVICE_NAME),
            "method":  ctx.get(ctxkeys.METHOD_NAME),
            "client_id": ctx.client_id,
            "entity_id": headers.entity_id,
            "caller_identity": headers.caller_identity,
        }
        
        ctx.set_logger(ctx.get_logger().bind(**log_data))
    
    def error(self, *args, ctx, exc):
        error_data = {
            'error': exc.message,
            'error_code': exc.code.value,
            'error_meta': exc.meta
        }
        ctx.set_logger(ctx.get_logger().bind(**error_data))

    def response_sent(self, *args, ctx):
        start = ctx.get(LOGGING_START_TIME_KEY)
        resp_data = {
            "status_code": ctx.get(ctxkeys.RESPONSE_STATUS),
            "time_taken":int((time.time() - start) * 100000) / 100,
        }
        ctx.get_logger().info("twirp request processed", **resp_data)

