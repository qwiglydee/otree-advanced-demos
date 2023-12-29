""" Utils for advanced live page messaging

The messages carry a type and some data. Each message is processed by a handler of corresponding type.

Messages from server can be adressed to several players,
addressed by player instance, player id, string "other" for non-adressed players, or "all" for all players.

# Usage

```
@live_page
class SomePage(Page):

    def live_msgtype(player, data):
        # handle incoming message of type 'msgtype'
        ...

        yield type, dict(...)  # send response of type 'type' and data back to the original player
        yield type             # send response without data

        # in multiplayer setup:
        yield player2, type, dict(...)  # send response message to another player
        yield player2, type             # send another response without data
        yield "all", type, data         # send message to all players in a group
        yield "all", type               # send message w/out data to all players in a group
```

"""

import types
import logging

from otree.api import BasePlayer, BaseGroup


def live_page(cls):
    def generic_live_method(player: BasePlayer, message: dict):
        try:
            if len(list(message.keys())) != 1:
                raise RuntimeError("Invalid input message format, expected single { type: data }")

            msgtype, msgdata = list(message.items())[0]

            methodname = f'live_{msgtype}'

            if not hasattr(cls, methodname):
                raise RuntimeError(f"Missing method {methodname}")

            handler = getattr(cls, methodname)
            handling = handler(player, msgdata)

            if not isinstance(handling, types.GeneratorType):
                raise RuntimeError(f"Expected {methodname} to `yield` responses.")

            responses = handle_responses(handling)
            result = expand_recipients(responses, player)
            return result

        except Exception:
            logging.exception("Exception in message handler")
            return {
                0: { "failure": "Critical failure occured." }
            }


    cls.live_method = staticmethod(generic_live_method)

    return cls


def parse_response(response):
    if not isinstance(response, (str, tuple)):
        raise RuntimeError("Invalid yielded response")

    # case str
    if isinstance(response, str):
        return None, response, None

    # case str, dict
    if len(response) == 2 and isinstance(response[0], str) and isinstance(response[1], dict):
        return None, response[0], response[1]

    # case "all", str
    if len(response) == 2 and response[0] == "all" and isinstance(response[1], str):
        return 0, response[1], None

    # case "all", str, dict
    if len(response) == 3 and response[0] == "all" and isinstance(response[1], str)  and isinstance(response[2], dict):
        return 0, response[1], response[2]

    # case player, str
    if len(response) == 2 and isinstance(response[0], BasePlayer) and isinstance(response[1], str):
        return response[0], response[1], None

    # case player, str, dict
    if len(response) == 3 and isinstance(response[0], BasePlayer) and isinstance(response[1], str)  and isinstance(response[2], dict):
        return response[0], response[1], response[2]

    raise RuntimeError("Unrecognized yielded response")


def handle_responses(handling):
    responses = {}

    for response in handling:
        rcpt, msgtype, data = parse_response(response)
        if rcpt not in responses:
            responses[rcpt] = {}
        if msgtype in responses[rcpt]:
            raise RuntimeError(f"overriding response {msgtype}")
        responses[rcpt][msgtype] = data

    return responses


def expand_recipients(responses, player):
    """Replaces recipients with player ids"""
    result = {}

    def put(p: BasePlayer, data):
        pid = p.id_in_group
        if pid not in result:
            result[pid] = {}
        result[pid].update(data)

    if 0 in responses:
        data = responses.pop(0)
        if len(responses) == 0: # no other recipients
            result[0] = data
        else: # all + other
            for p in player.group.get_players():
                put(p, data)

    for rcpt, data in responses.items():
        if rcpt is None:
            put(player, data)
        if isinstance(rcpt, BasePlayer):
            put(rcpt, data)

    return result
