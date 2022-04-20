import random

from twirp.asgi import TwirpASGIApp
from twirp.exceptions import InvalidArgument

from generated import haberdasher_twirp, haberdasher_pb2

class HaberdasherService(object):
    def MakeHat(self, context, size):
        if size.inches <= 0:
            raise InvalidArgument(argument="inches", error="I can't make a hat that small!")
        response = haberdasher_pb2.Hat(
            size=size.inches,
            color=random.choice(["white", "black", "brown", "red", "blue"]),
        )
        if random.random() > 0.5:
            response.name = random.choice(["bowler", "baseball cap", "top hat", "derby"])

        return response


service = haberdasher_twirp.HaberdasherServer(
	service=HaberdasherService(), server_path_prefix="/twirpy")
app = TwirpASGIApp()
app.add_service(service)
