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
        
        yield player, type1, data1   # send response message to the original player
        yield player, type2         # send another response without data
        yield player2, type3, data3 # send another message to another player
```

The above is equivalent of sending:
```
{
    player.id_in_group: { type1: data1, type2: None },
    player2.id_in_group: { type3: data3 }
}
```


"""

import inspect
import types
import logging

from otree.api import BasePlayer


def expand_recipients(group, response):
    """ Replaces recipients with their player ids,
    handles player instances, 'all', 'others' 
    """

    if 'all' in response:
        if len(list(response.keys())) != 1:
            raise ValueError("Can not address 'all' and someone else")
        return { 0: response['all'] }

    expanded = {}

    expanded.update({
        rcpt: data
        for rcpt, data in response.items() if isinstance(rcpt, int)
    })

    expanded.update({
        rcpt.id_in_group: data
        for rcpt, data in response.items() if isinstance(rcpt, BasePlayer)
    })    

    if 'others' in response:
        msg = response.pop('others')  # type: ignore
        for p in group.get_players():
            id = p.id_in_group
            if id not in expanded:
                expanded[id] = msg

    return expanded


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
        if len(list(message.keys())) != 1:
            raise ValueError("Invalid input message format, expected { type: data }")

        msgtype, msgdata = list(message.items())[0]

        if msgtype not in handlers:
            raise RuntimeError(f"Missing @live_method('{msgtype}')")

        handler = handlers[msgtype]
        handling = handler(player, msgdata)

        if not isinstance(handling, types.GeneratorType):
            raise RuntimeError(f"Expected @live_method('{msgtype}') to `yield` responses.")

        responses = {}
        try:
            for response in handling:
                if len(response) == 3:
                    rcpt, mtype, data = response
                elif len(response) == 2:
                    rcpt, mtype = response
                    data = None
                else:
                    raise RuntimeError(f"Unexpected yield format from handler @live_method('{msgtype}'), expected 2 or 3 elems")
                if rcpt not in responses:
                    responses[rcpt] = {}
                responses[rcpt][mtype] = data
            responses = expand_recipients(player.group, responses)
            return responses
        except:
            logging.exception("Exception in message handler")
            return {
                player.id_in_group: { "error": None }
            }

    cls.live_method = staticmethod(generic_live_method)

    return cls