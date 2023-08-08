try:
    import asyncio
    import aiohttp
except ModuleNotFoundError:
    pass

from twirp.context import Context
from twirp.exceptions import TwirpServerException

from generated import haberdasher_twirp, haberdasher_pb2


server_url = "http://localhost:3000"
timeout_s = 5


def main():
    client = haberdasher_twirp.HaberdasherClient(server_url, timeout_s)

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
    client = haberdasher_twirp.AsyncHaberdasherClient(server_url, timeout_s)

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


async def async_with_session():
    # It is optional but recommended to provide your own ClientSession to the twirp client
    # either on init or per request, and ensure it is closed properly on app shutdown.
    # Otherwise, the client will create its own session to use, which it will attempt to
    # close in its __del__ method, but has no control over how or when that will get called.

    # NOTE: ClientSession may only be created (or closed) within a coroutine.
    session = aiohttp.ClientSession(
        server_url, timeout=aiohttp.ClientTimeout(total=timeout_s)
    )

    # If session is provided, session controls the timeout. Timeout parameter to client init is unused
    client = haberdasher_twirp.AsyncHaberdasherClient(server_url, session=session)

    try:
        response = await client.MakeHat(
            ctx=Context(),
            request=haberdasher_pb2.Size(inches=12),
            server_path_prefix="/twirpy",
            # Optionally provide a session per request
            # session=session,
        )
        if not response.HasField("name"):
            print("We didn't get a name!")
        print(response)
    except TwirpServerException as e:
        print(e.code, e.message, e.meta, e.to_dict())
    finally:
        # Close the session (could also use a context manager)
        await session.close()


if __name__ == "__main__":
    if hasattr(haberdasher_twirp, "AsyncHaberdasherClient"):
        print("using async client")
        asyncio.run(async_main())
    else:
        main()
