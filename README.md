# Twirpy

Python implementation of Twirp RPC framework (supports [Twirp Wire Protocol v7](https://twitchtv.github.io/twirp/docs/spec_v7.html)).

This repo contains a protoc plugin that generates sever and client code and a pypi package with common implementation details.

For details about the twirp project, check https://github.com/twitchtv/twirp

## Installation

Grab the protoc plugin to generate files with

```
go get -u github.com/verloop/twirpy/protoc-gen-twirpy
```

Add the twirp package to your project
```
pip install twirp
```

You'll also need [uvicorn](https://www.uvicorn.org/) to run the server.

## Generate and run
Use the protoc plugin to generate twirp server and client code.

We'll assume familiarity with the example from the docs. https://twitchtv.github.io/twirp/docs/example.html

```
protoc --python_out=./ --twirpy_out=./ ./haberdasher.proto
```

### Server code
```python
# server.py
import random

from twirp.asgi import TwirpASGIApp
from twirp.exceptions import InvalidArgument

from . import haberdasher_twirp, haberdasher_pb2

class HaberdasherService(object):
    def MakeHat(self, context, size):
        if size.inches <= 0:
            raise InvalidArgument(argument="inches", error="I can't make a hat that small!")
        return haberdasher_pb2.Hat(
            size=size.inches,
            color= random.choice(["white", "black", "brown", "red", "blue"]),
            name=random.choice(["bowler", "baseball cap", "top hat", "derby"])
        )


# if you are using a custom prefix, then pass it as `server_path_prefix`
# param to `HaberdasherServer` class.
service = haberdasher_twirp.HaberdasherServer(service=HaberdasherService())
app = TwirpASGIApp()
app.add_service(service)
```

Run the server with
```
uvicorn twirp_server:app --port=3000
```

### Client code

```python
# client.py
from twirp.context import Context
from twirp.exceptions import TwirpServerException

from . import haberdasher_twirp, haberdasher_pb2

client = haberdasher_twirp.HaberdasherClient("http://localhost:3000")

# if you are using a custom prefix, then pass it as `server_path_prefix`
# param to `MakeHat` class.
try:
    response = client.MakeHat(ctx=Context(), request=haberdasher_pb2.Size(inches=12))
    print(response)
except TwirpServerException as e:
    print(e.code, e.message, e.meta, e.to_dict())
```

## Twirp Wire Protocol (v7)

Twirpy generates the code based on the protocol v7. This is a breaking change from the previous v5 and you can see the changes [here](https://twitchtv.github.io/twirp/docs/spec_v7.html#differences-with-v5).

This new version comes with flexibility to use any prefix for the server URLs and defaults to `/twirp`. To use an empty prefix or any custom prefix like `/my/custom/prefix`, pass it as a `server_path_prefix` param to server and clients. Check the example directory, which uses `/twirpy` as a custom prefix.

If you want to use the server and clients of v5, then use the [0.0.1](https://github.com/verloop/twirpy/releases/tag/0.0.1) release.

### Message Body Length

Currently, message body length limit is set to 100kb, you can override this by passing `max_receive_message_length` to the server constructor.

## Support and community
Python: [#twirp](https://python-community.slack.com/messages/twirp). Join Python community slack [here](https://pythoncommunity.herokuapp.com)

Go: [#twirp](https://gophers.slack.com/messages/twirp). Join Gophers community slack [here](https://invite.slack.golangbridge.org)

## Standing on the shoulders of giants

- The initial version of twirpy was made from an internal copy of https://github.com/daroot/protoc-gen-twirp_python_srv
- The `run_in_threadpool` method comes from https://github.com/encode/starlette
