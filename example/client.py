from twirp.context import Context
from twirp.exceptions import TwirpServerException

from generated import haberdasher_twirp, haberdasher_pb2

client = haberdasher_twirp.HaberdasherClient("http://localhost:3000")

try:
    response = client.MakeHat(
    	ctx=Context(), request=haberdasher_pb2.Size(inches=12), server_path_prefix="/twirpy")
    print(response)
except TwirpServerException as e:
    print(e.code, e.message, e.meta, e.to_dict())
