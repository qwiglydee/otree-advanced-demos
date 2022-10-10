""" Utils for advanced live page messaging

# Messaging:

The messages are dicts of form `{ type: data }`.
Requests from pages can only contain one message of one type. Use severals sendLive() for more.
Responses from server can combine several messages of different types `{ type1: data1, type2: data2 }`.

# Addressing

Responses can contain several messages, adressed to several users.
Players can be adressed by `Player` class instance, player id, string "other" for all non-adressed players, or "all" for all players.


# Usage

Mark a page as live_page, and all methods as live_method

```
@live_page
class SomePage(Page):
    
    @live_method('answer')
    def handle_answer(player, data):
        # proceed message of type 'answer'

```


"""

import inspect

from otree.api import BasePlayer


def expand_recipients(group, response):
    """ Replaces recipients with their player ids,
    handles player instances, 'all', 'other' """

    if 'all' in response:
        if len(list(response.keys())) != 1:
            raise ValueError("Cann not address 'all' and someone else")
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

    if 'other' in response:
        msg = response.pop('other')  # type: ignore
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
        getattr(meth, "__live_handler"): meth
        for (name, meth) in inspect.getmembers(cls, lambda m: inspect.isfunction(m) and hasattr(m, "__live_handler"))
    }

    def generic_live_method(player: BasePlayer, message: dict):
        if len(list(message.keys())) != 1:
            raise NotImplementedError("Combo messages not supported, use singular { type: data } dict")

        msgtype, msgdata = list(message.items())[0]

        if msgtype not in handlers:
            raise NotImplementedError(f"Missing @live_method('{msgtype}')")

        handler = handlers[msgtype]
        response = handler(player, msgdata)
        response = expand_recipients(player.group, response)

        return response

    cls.live_method = staticmethod(generic_live_method)

    return cls