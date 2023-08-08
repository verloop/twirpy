try:
    import asyncio
except ModuleNotFoundError:
    pass

from twirp.context import Context
from twirp.exceptions import TwirpServerException

from generated import haberdasher_twirp, haberdasher_pb2


def main():
    client = haberdasher_twirp.HaberdasherClient("http://localhost:3000")

    try:
        response = client.MakeHat(
            ctx=Context(),
            request=haberdasher_pb2.Size(inches=12),
            server_path_prefix="/twirpy",
        )
        if not response.HasField("name"):
            print("We didn't get a name!")
        print(response)
    except TwirpServerException as e:
        print(e.code, e.message, e.meta, e.to_dict())


async def async_main():
    client = haberdasher_twirp.AsyncHaberdasherClient("http://localhost:3000")

    try:
        response = await client.MakeHat(
            ctx=Context(),
            request=haberdasher_pb2.Size(inches=12),
            server_path_prefix="/twirpy",
        )
        if not response.HasField("name"):
            print("We didn't get a name!")
        print(response)
    except TwirpServerException as e:
        print(e.code, e.message, e.meta, e.to_dict())


if __name__ == "__main__":
    if hasattr(haberdasher_twirp, "AsyncHaberdasherClient"):
        print("using async client")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(async_main())
    else:
        main()
