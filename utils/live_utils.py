""" Utils for advanced live page messaging

The messages carry a type and some data. Each message is processed by a handler of corresponding type.

Messages from server can be adressed to several players, 
addressed by player instance, player id, string "other" for non-adressed players, or "all" for all players.

# Usage

```
@live_page
class SomePage(Page):
    
    @live_method('sometype')
    def handle_msg(player, data):
        # handle message of type 'sometype'
        ...
        
        yield type1, dict(...)   # send response message of type 'type1' and data back to the original player
        yield type2              # send response without data

        # in multiplayer setup:
        yield player2, type3, dict(...)  # send response message to another player
        yield player2, type3             # send another response without data
        yield group, type4, data         # send message to all players in a group
```

"""

import inspect
import types
import logging

from otree.api import BasePlayer, BaseGroup


def live_method(name):
    def augmenter(method):
        method.__live_handler = name
        return staticmethod(method)

    return augmenter


def live_page(cls):
    handlers = {
        getattr(method, "__live_handler"): method
        for (_, method) in inspect.getmembers(cls, lambda m: inspect.isfunction(m) and hasattr(m, "__live_handler"))
    }

    def generic_live_method(player: BasePlayer, message: dict):
        try:
            if len(list(message.keys())) != 1:
                raise RuntimeError("Invalid input message format, expected { type: data }")

            msgtype, msgdata = list(message.items())[0]

            if msgtype not in handlers:
                raise RuntimeError(f"Missing @live_method('{msgtype}')")

            handler = handlers[msgtype]
            handling = handler(player, msgdata)

            if not isinstance(handling, types.GeneratorType):
                raise RuntimeError(f"Expected @live_method('{msgtype}') to `yield` responses.")

            responses = {}

            for rcpt, mtype, data in parse_yielding(handling):
                if rcpt is None:
                    rcpt = player
                if rcpt not in responses:
                    responses[rcpt] = {}
                responses[rcpt][mtype] = data
        except Exception:
            logging.exception("Exception in message handler")
            return {
                0: { "failure": "Critical failure occured." }
            }
        responses = expand_recipients(responses)

        return responses

    cls.live_method = staticmethod(generic_live_method)

    return cls


def parse_yielding(yielding):
    for yielded in yielding:
        if not isinstance(yielded, tuple):
            yielded = (yielded,)

        if isinstance(yielded[0], BasePlayer) or isinstance(yielded[0], BaseGroup):
            rcpt = yielded[0]
            yielded = yielded[1:]
        else:
            rcpt = None

        if len(yielded) == 1:
            mtype, data = yielded[0], None
        elif len(yielded) == 2:
            mtype, data = yielded
        else:
            raise RuntimeError(f"Unexpected yield format from handler @live_method('{msgtype}')")

        yield rcpt, mtype, data


def expand_recipients(responses):
    """Replaces recipients Player or Group with player ids"""
    result = {}

    def update(player, data):
        pid = player.id_in_group
        if player not in result:
            result[pid] = data
        else:
            result[pid].update(data)

    for group in filter(lambda k: isinstance(k, BaseGroup), responses.keys()):
        for player in group.get_players():
            update(player, responses[group])

    for player in filter(lambda k: isinstance(k, BasePlayer), responses.keys()):
        update(player, responses[player])
            
    return result
