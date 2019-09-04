import os
import logging
import sys

import structlog
from structlog.stdlib import LoggerFactory, add_log_level

from google.protobuf import message
from google.protobuf.json_format import MessageToDict



def stackdriver_hacks(_, __, event_dict):
    def rename(old, new, default=""):
        event_dict[new] = event_dict.pop(old, event_dict.get(new, default))
    rename("event", "message", "")
    rename("level", "severity", "info")

    def convert_protopuf_to_dict(obj):
        new_obj = obj
        if isinstance(obj, dict):
            new_obj = {}
            for key in obj:
                new_obj[key] = convert_protopuf_to_dict(obj[key])
        elif isinstance(obj, list):
            new_obj = []
            new_obj = [convert_protopuf_to_dict(item) for item in obj]
        elif isinstance(obj, message.Message):
            new_obj = MessageToDict(obj)
        return new_obj

    event_dict = convert_protopuf_to_dict(event_dict)

    return event_dict


_configured = False


def configure(force=False):
    global _configured
    if _configured and not force:
        return
    debug = os.environ.get("VADER_DEBUG", False)
    if debug:
        lvl = logging.DEBUG
    else:
        lvl = logging.INFO
    logging.basicConfig(
        level=lvl,
        #stream=sys.stdout,
        format="%(message)s",
    )

    structlog.configure(
        logger_factory=LoggerFactory(),
        processors=[
            add_log_level,
            structlog.processors.TimeStamper("iso"),
            stackdriver_hacks,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]
    )


def get_logger(**kwargs):
    configure()
    if 'version' not in kwargs:
        kwargs['version'] =  os.environ.get("VERSION", "unknown")
    return structlog.get_logger(**kwargs)
