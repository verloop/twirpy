# Twirpy

Python implementation of twirp RPC framework.

This repo contains a protoc plugin that generates sever and client code and a pypi package with common implementation details.

For details about the twirp project, check https://github.com/twitchtv/twirp

## Installation

Grab the protoc plugin with

```
go get -u github.com/verloop/twirpy/protoc-gen-twirpy
```

To add the twirp package to your project
```
pip install twirp
```

## Usage
Use the protoc plugin to generate twirp server and client code.

We'll assume familiarity with the example from the docs. https://twitchtv.github.io/twirp/docs/example.html

```
protoc --twirpy_out=./ ./haberdasher.proto
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
            raise InvalidArgument("inches", "I can't make a hat that small!")
        return haberdasher_pb2.Hat(
            inches=size.inches,
            color= random.choice(["white", "black", "brown", "red", "blue"]),
            name=random.choice(["bowler", "baseball cap", "top hat", "derby"])
        )


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

try:
    response = client.MakeHat(ctx=Context(), request=haberdasher_pb2.Size(inches=12))
    print(response)
except TwirpServerException as e:
    print(e.code, e.message, e.meta, e.to_dict())
```


## Support and community
Python: [#twirp](https://python-community.slack.com/messages/twirp). Join Python community slack [here](https://pythoncommunity.herokuapp.com)

Go: [#twirp](https://gophers.slack.com/messages/twirp). Join Gophers community slack [here](https://invite.slack.golangbridge.org)