"""
Utils for live communicating.
Best used with otree-front-live.js

The communication consists of exchening messages each has a type and payload.
Both ends use separate handlers bound to particular message types.

Receiving messages form page::

```
@live_page
class SomePage(Page):

    @staticmethod
    def live_foo(player, payload):
        # handle incoming message of type 'foo'
        ...

    @staticmethod
    def live_bar(player, payload):
        # handle incoming message of type 'bar'
        ...

```

Sending messages back to page:
```
@staticmethod
def live_something(player, payload):
    # a handler can send one or more messages back to the originating player
    yield "foo", data   # send a response of type "foo" and payloaded with the data
    yield "foo"         # send a response without payload
```

Sending messages in multiplayers sessions:
```
@staticmethod
def live_something(player, payload):
    # a handler can send one or more messages to any player in the group of originating player
    ...
    yield player.group, "foo", data  # send a message to all players in the group
    yield player.group, "foo"        # send a message without payload

    another_player = player.group.get_player_by_role(...)  # get reference to another player

    yield another_player, "bar", data   # send a message to another player
    yield another_player, "bar"         # send a message without payload
```

"""

import types
import logging

from otree.api import BasePlayer, BaseGroup


def live_page(cls):
    """Wrapper for page classes to make them smart live pages
    Routes incoming messages to corresponding live_something method
    Collects all yielded responses into { rcpt: [ { type, data }, ...] }
    Preserving order of yields.
    """

    def generic_live_method(player: BasePlayer, payload: dict):
        def route(response):
            "convert yielded responses to (id_in_group, {type, data})"
            match response:
                case (BaseGroup() as g, str() as t):
                    for p in g.get_players():
                        yield p.id_in_group, {"type": t}
                case (BaseGroup() as g, str() as t, data):
                    for p in g.get_players():
                        yield p.id_in_group, {"type": t, "data": data}
                case (BasePlayer() as p, str() as t):
                    yield p.id_in_group, {"type": t}
                case (BasePlayer() as p, str() as t, data):
                    yield p.id_in_group, {"type": t, "data": data}
                case str() as t:
                    yield player.id_in_group, {"type": t}
                case (str() as t, data):
                    yield player.id_in_group, {"type": t, "data": data}
                case _:
                    raise TypeError(
                        f"Handler {handler_name} yielded invalid construction"
                    )

        try:
            assert (
                isinstance(payload, dict) and "type" in payload
            ), "Incoming message should be { type: ... , data: ... }"

            handler_name = "live_" + payload["type"]

            assert hasattr(
                cls, handler_name
            ), f"The page class misses method {handler_name}"
            handler = getattr(cls, handler_name)

            responding = handler(player, payload.get("data"))
            assert isinstance(
                responding, types.GeneratorType
            ), f"Method {handler_name} should yield some responses"

            responses = {}
            for resp in responding:
                for p, msg in route(resp):
                    if p not in responses:
                        responses[p] = [msg]
                    else:
                        responses[p].append(msg)

            return responses

        except Warning as e:
            logging.exception("Exception in live handler")
            return {0: [{"type": "failure", "data": str(e)}]}

        except Exception:
            logging.exception("Exception in live handler")
            return {0: [{"type": "failure", "data": "Some failure on server occured"}]}

    cls.live_method = staticmethod(generic_live_method)

    return cls
