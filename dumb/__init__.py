from otree.api import *

from utils.live_utils import live_page


class C(BaseConstants):
    NAME_IN_URL = "dumb"
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES


@live_page
class Main(Page):
    @staticmethod
    def live_ping(player: Player, data: dict):
        yield "pong"

    @staticmethod
    def live_foo(player: Player, data: dict):
        yield "pong"
        yield "feedback", {"ack": True}

    @staticmethod
    def live_bar(player: Player, data: dict):
        yield "all", "pong"
        yield "all", "broadcast", {"ack": True}

    @staticmethod
    def live_baz(player: Player, data: dict):
        yield player, "pong"
        yield "all", "broadcast", {"ack": True}

page_sequence = [Main]
