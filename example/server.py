import random

from twirp.asgi import TwirpASGIApp
from twirp.exceptions import InvalidArgument

from . import haberdasher_twirp, haberdasher_pb2

class HaberdasherService(object):
    def MakeHat(self, context, size):
        if size.inches <= 0:
            raise InvalidArgument(argument="inches", error="I can't make a hat that small!")
        return haberdasher_pb2.Hat(
            inches=size.inches,
            color= random.choice(["white", "black", "brown", "red", "blue"]),
            name=random.choice(["bowler", "baseball cap", "top hat", "derby"])
        )


service = haberdasher_twirp.HaberdasherServer(service=HaberdasherService())
app = TwirpASGIApp()
app.add_service(service)